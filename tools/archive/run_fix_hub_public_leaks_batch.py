#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全サイトで知識ハブの Sxx 表記漏れ・早見表重複を修正しビルドする。"""

from __future__ import annotations

import shutil
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
    "hub_strip_batch_suffix.py",
    "hub_matrix_repair.py",
    "fix_hub_public_leaks.py",
    "build_numbers_mistakes_pages.py",
    "knowledge_hub_seo.py",
)


def sync_tools(site_dir: Path) -> None:
    tools = site_dir / "tools"
    tools.mkdir(exist_ok=True)
    for name in SYNC_TOOLS:
        src = ROOT / "tools" / name
        dst = tools / name
        if src.is_file() and src.resolve() != dst.resolve():
            shutil.copy2(src, dst)


def run(cmd: list[str], cwd: Path) -> int:
    print(f"\n>>> {' '.join(cmd)}  (cwd={cwd.name})")
    return subprocess.call(cmd, cwd=cwd)


def main() -> int:
    dry = "--dry-run" in sys.argv
    for site in SITES:
        site_dir = PROJECTS / site
        if not (site_dir / "data").is_dir():
            continue
        sync_tools(site_dir)
        args = [sys.executable, "tools/fix_hub_public_leaks.py"]
        if dry:
            args.append("--dry-run")
        else:
            args.extend(["--apply", "--rebuild"])
        code = run(args, site_dir)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
