#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全サイトで配置監査・修正・ビルドを実行する。"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ROOT.parent

SITES = [
    "exam-site-shell",
    "takken-master",
    "boiler-master.jp",
    "mentalhealth-master",
    "chintaikanrishi-master",
    "eisei1shu-master",
    "eisei2shu-master",
    "kangyou-master",
    "kikenbutsu-master",
    "unkan-master",
    "mankan-master",
]

SYNC_TOOLS = (
    "content_placement_rules.py",
    "fix_content_placement.py",
    "audit_content_placement.py",
    "migrate_guide_to_hub.py",
    "migrate_hub_admin_to_guide.py",
)


def exam_label(site_dir: Path) -> str:
    cfg = site_dir / "site-config.json"
    if not cfg.is_file():
        return "対象試験"
    data = json.loads(cfg.read_text(encoding="utf-8"))
    name = (data.get("examName") or data.get("brandName") or "対象試験").replace("（プレースホルダー）", "")
    name = name.replace("◯◯", "").strip()
    return name or "対象試験"


SYNC_BUILD = ("build_numbers_mistakes_pages.py",)


def sync_tools(site_dir: Path) -> None:
    tools = site_dir / "tools"
    tools.mkdir(exist_ok=True)
    for name in (*SYNC_TOOLS, *SYNC_BUILD):
        src = ROOT / "tools" / name
        if src.is_file():
            (tools / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def run(cmd: list[str], cwd: Path) -> int:
    print(f"\n>>> {' '.join(cmd)}  (cwd={cwd.name})")
    return subprocess.call(cmd, cwd=cwd)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "audit"
    audit_csv = ROOT / "docs" / "content-placement-audit.csv"

    if mode == "audit":
        rows: list[str] = []
        for site in SITES:
            site_dir = PROJECTS / site
            if not (site_dir / "data" / "guide_articles.csv").is_file():
                continue
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "audit_content_placement.py"), "--target", str(site_dir)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            for line in proc.stdout.splitlines():
                if line.strip():
                    rows.append(f"{site}\t{line}")
            for line in proc.stderr.splitlines():
                if line.strip() and not line.startswith("summary:"):
                    rows.append(f"{site}\t{line}")
        audit_csv.write_text("\n".join(rows) + "\n", encoding="utf-8")
        print(f"Wrote {audit_csv} ({len(rows)} lines)")
        return 0

    if mode in ("fix-all", "fix-bridge", "fix-hub-admin"):
        confidence = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else "high"
        for site in SITES:
            site_dir = PROJECTS / site
            if not (site_dir / "data" / "guide_articles.csv").is_file():
                continue
            sync_tools(site_dir)
            label = exam_label(site_dir)
            py = sys.executable
            if mode == "fix-all":
                run([py, "tools/fix_content_placement.py", "--bridge-duplicates", "--confidence", confidence, "--exam-label", label], site_dir)
                run([py, "tools/fix_content_placement.py", "--migrate-to-hub", "--exam-label", label], site_dir)
                run([py, "tools/fix_content_placement.py", "--clear-glossary-misplaced"], site_dir)
            elif mode == "fix-bridge":
                run([py, "tools/fix_content_placement.py", "--bridge-duplicates", "--confidence", confidence, "--exam-label", label], site_dir)
            if mode in ("fix-all", "fix-hub-admin"):
                run([py, "tools/fix_content_placement.py", "--migrate-from-hub"], site_dir)
            run([py, "tools/build_article_pages.py"], site_dir)
            if (site_dir / "tools/build_compare_pages.py").is_file():
                run([py, "tools/build_compare_pages.py"], site_dir)
            if (site_dir / "tools/build_numbers_mistakes_pages.py").is_file():
                run([py, "tools/build_numbers_mistakes_pages.py"], site_dir)
            if site != "exam-site-shell":
                run([py, "tools/build_glossary_pages.py"], site_dir)
        return 0

    print("Usage: run_content_placement_batch.py [audit|fix-bridge|fix-hub-admin|fix-all [confidence]]", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
