#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全サイト index.html の FAQPage JSON-LD を past_questions.csv から再生成する。"""

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

TOOL = "build_index_faq_ldjson.py"


def sync_tool(site_dir: Path) -> None:
    tools = site_dir / "tools"
    tools.mkdir(exist_ok=True)
    src = ROOT / "tools" / TOOL
    (tools / TOOL).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    dry = "--dry-run" in sys.argv
    py = sys.executable
    for site in SITES:
        site_dir = PROJECTS / site
        if not (site_dir / "index.html").is_file():
            continue
        sync_tool(site_dir)
        args = [py, f"tools/{TOOL}"]
        if dry:
            args.append("--dry-run")
        if site == "exam-site-shell":
            args.append("--remove-if-empty")
        print(f"\n>>> {site}")
        code = subprocess.call(args, cwd=site_dir)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
