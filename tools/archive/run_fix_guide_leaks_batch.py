#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全サイトで試験ガイドの内部用語漏れを修正しビルドする。"""

from __future__ import annotations

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
    "guide_catalog_batch.py",
    "fix_guide_leaked_tokens.py",
    "editorial_quality.py",
)


def sync_tools(site_dir: Path) -> None:
    tools = site_dir / "tools"
    tools.mkdir(exist_ok=True)
    for name in SYNC_TOOLS:
        src = ROOT / "tools" / name
        if src.is_file():
            (tools / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def run(cmd: list[str], cwd: Path) -> int:
    print(f"\n>>> {' '.join(cmd)}  (cwd={cwd.name})")
    return subprocess.call(cmd, cwd=cwd)


def main() -> int:
    dry = "--dry-run" in sys.argv
    for site in SITES:
        site_dir = PROJECTS / site
        if not (site_dir / "data" / "guide_articles.csv").is_file():
            continue
        sync_tools(site_dir)
        py = sys.executable
        args = [py, "tools/fix_guide_leaked_tokens.py"]
        if dry:
            args.append("--dry-run")
        code = run(args, site_dir)
        if code != 0:
            return code
        if not dry:
            run([py, "tools/build_article_pages.py"], site_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
