#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1サイト分のロードマップパイプライン（CSV修復 → 品質修正 → build → 検証）。"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SHELL = Path(__file__).resolve().parents[1]
PROJECTS = Path.home() / "Projects"

TOOLS_TO_SYNC = (
    "glossary_past_questions.py",
    "fix_editorial_auto.py",
    "fix_hub_titles.py",
    "hub_pro_enrich.py",
    "audit_hub_quality.py",
    "validate_publish_gate.py",
    "knowledge_hub_seo.py",
    "build_article_pages.py",
    "guide_section_resolve.py",
    "guide_topic_normalize.py",
    "guide_prose_patterns.py",
    "audit_guide_prose_quality.py",
)


def run(cmd: list[str], *, cwd: Path, env: dict | None = None, optional: bool = False) -> bool:
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=cwd, env=env, text=True)
    if proc.returncode != 0:
        if optional:
            return True
        print(f"FAIL exit {proc.returncode}", file=sys.stderr)
        return False
    return True


def sync_tools(site: Path) -> None:
    dst = site / "tools"
    for name in TOOLS_TO_SYNC:
        src = SHELL / "tools" / name
        if src.is_file():
            dst.joinpath(name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def process_site(name: str, *, push: bool, skip_build: bool) -> dict:
    site = PROJECTS / name
    if not site.is_dir():
        return {"site": name, "ok": False, "error": "missing dir"}

    py = sys.executable
    env = {
        **os.environ,
        "EXAM_SITE_ROOT": str(site),
        "PYTHONPATH": str(site),
    }
    sync_tools(site)
    run(["git", "-C", str(site), "checkout", "--", "data/"], cwd=site, optional=True)

    steps: list[tuple[list[str], bool]] = [
        ([py, str(SHELL / "tools/repair_csv_for_validate.py"), "--root", str(site)], False),
        ([py, str(SHELL / "tools/fix_tier_a_guide_articles.py"), "--root", str(site)], True),
        ([py, str(SHELL / "tools/fix_guide_duplicate_bodies.py"), "--root", str(site)], False),
        ([py, str(SHELL / "tools/hub_pro_enrich.py"), "--root", str(site)], False),
        ([py, str(SHELL / "tools/fix_hub_titles.py"), "--root", str(site)], False),
        ([py, str(SHELL / "tools/fix_editorial_auto.py"), "--root", str(site)], False),
        ([py, str(SHELL / "tools/repair_csv_for_validate.py"), "--root", str(site)], True),
        ([py, "tools/validate_csv.py"], False),
    ]
    for cmd, optional in steps:
        if not run(cmd, cwd=site, env=env, optional=optional):
            return {"site": name, "ok": False, "error": " ".join(cmd[-2:])}

    if not skip_build:
        if not run([py, "tools/build_all.py"], cwd=site, env=env):
            return {"site": name, "ok": False, "error": "build_all"}

    audit = subprocess.run([py, "tools/audit_editorial_quality.py"], cwd=site, env=env, capture_output=True, text=True)
    hub = subprocess.run([py, str(site / "tools/audit_hub_quality.py")], cwd=site, env=env, capture_output=True, text=True)
    report = {"site": name, "ok": True}
    import re

    m = re.search(r"編集品質: ERROR (\d+) / WARN (\d+)", audit.stdout + audit.stderr)
    if m:
        report["editorial"] = {"error": int(m.group(1)), "warn": int(m.group(2))}
    summary = site / "reports/hub_audit/summary.json"
    if summary.is_file():
        report["hub"] = json.loads(summary.read_text(encoding="utf-8"))

    if push:
        if subprocess.run(["git", "-C", str(site), "status", "--porcelain"], capture_output=True, text=True).stdout.strip():
            run(["git", "-C", str(site), "add", "-A"], cwd=site)
            run(
                [
                    "git",
                    "-C",
                    str(site),
                    "commit",
                    "-m",
                    "build: ロードマップ（ハブ品質・編集WARN・リンク修復・再ビルド）",
                ],
                cwd=site,
                optional=True,
            )
            run(["git", "-C", str(site), "push", "origin", "HEAD"], cwd=site, optional=True)
            gh = site / "tools/sync_gh_pages_branch.sh"
            if gh.is_file():
                run(["bash", str(gh)], cwd=site, optional=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()
    report = process_site(args.site, push=args.push, skip_build=args.skip_build)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
