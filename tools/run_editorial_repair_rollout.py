#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全本番サイト: glossary 修復 → ガイド duplicate 修復 → 再ビルド → 編集品質監査。"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SHELL = Path(__file__).resolve().parents[1]
PROJECTS = Path.home() / "Projects"

DEFAULT_SITES = (
    "eisei2shu-master",
    "boiler-master.jp",
    "unkan-master",
    "kikenbutsu-master",
    "mentalhealth-master",
    "mankan-master",
    "kangyou-master",
    "chintaikanrishi-master",
    "takken-master",
)


def run(cmd: list[str], *, cwd: Path, env: dict | None = None) -> bool:
    proc = subprocess.run(cmd, cwd=cwd, env=env)
    return proc.returncode == 0


def repair_site(name: str, *, skip_build: bool, skip_glossary: bool) -> tuple[bool, str]:
    root = PROJECTS / name
    if not root.is_dir():
        return False, "missing"
    py = sys.executable
    env = {**dict(__import__("os").environ), "PYTHONPATH": f"{SHELL}:{root}"}

    print(f"\n=== {name} ===")
    repair_cmd = [py, str(SHELL / "tools/repair_csv_for_validate.py"), "--root", str(root)]
    if skip_glossary:
        repair_cmd.append("--skip-glossary")
    if not run(repair_cmd, cwd=SHELL):
        return False, "repair_csv"

    for tool, label, accept_codes in (
        ("fix_tier_a_guide_articles.py", "fix_tier_a", (0, 1)),
        ("fix_guide_duplicate_bodies.py", "fix_duplicates", (0, 1)),
    ):
        path = SHELL / "tools" / tool
        if not path.is_file():
            continue
        proc = subprocess.run(
            [py, str(path), "--root", str(root)],
            cwd=root,
            env=env,
        )
        if proc.returncode not in accept_codes:
            return False, label

    if skip_build:
        audit = subprocess.run(
            [py, str(SHELL / "tools/audit_editorial_quality.py")],
            cwd=root,
            env=env,
        )
        return audit.returncode == 0, "audit"

    steps = [
        "tools/build_article_pages.py",
        "tools/build_glossary_pages.py",
        "tools/build_compare_pages.py",
        "tools/build_numbers_mistakes_pages.py",
    ]
    for step in steps:
        if not (root / step).is_file() and not (SHELL / step).is_file():
            continue
        print(f"  + {step}")
        if not run([py, step], cwd=root, env=env):
            return False, step

    audit = subprocess.run(
        [py, "tools/audit_editorial_quality.py"],
        cwd=root,
        env=env,
    )
    if audit.returncode != 0:
        return False, "audit ERROR"
    return True, "OK"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", action="append")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-glossary", action="store_true")
    args = parser.parse_args()
    sites = args.site or list(DEFAULT_SITES)
    failures: list[str] = []
    for name in sites:
        ok, msg = repair_site(name, skip_build=args.skip_build, skip_glossary=args.skip_glossary)
        if not ok:
            failures.append(f"{name}: {msg}")
    if failures:
        print("\nFailed:", ", ".join(failures), file=sys.stderr)
        return 1
    print("\nAll sites repaired.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
