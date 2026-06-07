#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_csv をスキップしてサイト全体を再ビルドし、統合・リンク検証まで実行する。"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1]
PROJECTS = Path.home() / "Projects"

DEFAULT_SITES = (
    "eisei1shu-master",
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

OPTIONAL_STEPS = (
    "tools/build_compare_pages.py",
    "tools/build_numbers_mistakes_pages.py",
)


def run_step(py: str, cwd: Path, name: str, *, optional: bool = False) -> bool:
    path = cwd / name
    if not path.is_file():
        if name in OPTIONAL_STEPS:
            print(f"  skip (missing): {name}")
            return True
        print(f"  skip (missing): {name}", file=sys.stderr)
        return optional
    print(f"  + {name}")
    proc = subprocess.run([py, name], cwd=cwd)
    if proc.returncode != 0:
        print(f"  FAIL: {name} exit {proc.returncode}", file=sys.stderr)
        return False
    return True


def hub_enrich(py: str, cwd: Path) -> None:
    enrich = TEMPLATE / "tools" / "hub_pro_enrich.py"
    if not enrich.is_file():
        return
    for csv_name in ("comparisons.csv", "numbers.csv"):
        csv_path = cwd / "data" / csv_name
        if not csv_path.is_file():
            continue
        print(f"  + hub_pro_enrich ({csv_name})")
        code = (
            "import sys; sys.path.insert(0, %r); "
            "from tools.hub_pro_enrich import enrich_csv; "
            "from pathlib import Path; "
            "p=Path('data')/%r; print(f'enriched {enrich_csv(p)} rows in {p}')"
        ) % (str(TEMPLATE), csv_name)
        subprocess.run([py, "-c", code], cwd=cwd, check=False)


def gh_pages_sync(cwd: Path) -> None:
    script = cwd / "tools" / "sync_gh_pages_branch.sh"
    if script.is_file():
        subprocess.run(["bash", str(script)], cwd=cwd, check=False)


def build_site(name: str, *, skip_hub: bool, gh_pages: bool) -> tuple[bool, str]:
    cwd = PROJECTS / name
    if not cwd.is_dir():
        return False, "missing dir"
    py = sys.executable
    env = {**os.environ, "PYTHONPATH": f"{TEMPLATE}:{cwd}"}

    print(f"\n=== {name} ===")
    if not skip_hub:
        hub_enrich(py, cwd)

    steps = [
        "tools/apply_site_config.py",
        "tools/csv_to_exam_site_past_js.py",
        "tools/csv_to_exam_site_ichimondou_js.py",
        "tools/build_past_question_pages.py",
        "tools/build_article_pages.py",
        "tools/validate_guide_html_coherence.py",
        "tools/build_glossary_pages.py",
        *OPTIONAL_STEPS,
        "tools/build_practice_ichimon_pages.py",
        "tools/build_sitemap.py",
    ]
    for step in steps:
        optional = step.endswith("validate_guide_html_coherence.py")
        if not run_step(py, cwd, step, optional=optional):
            if optional:
                continue
            return False, f"failed at {step}"

    for validator in (
        "tools/validate_site_integration.py",
        "tools/validate_internal_links.py",
    ):
        print(f"  + {validator}")
        proc = subprocess.run([py, validator], cwd=cwd, env=env)
        if proc.returncode != 0:
            return False, f"failed at {validator}"

    if gh_pages:
        gh_pages_sync(cwd)
    return True, "OK"


def main() -> int:
    parser = argparse.ArgumentParser(description="全サイト再ビルド（統合・リンク検証付き）")
    parser.add_argument("--site", action="append")
    parser.add_argument("--skip-hub-enrich", action="store_true")
    parser.add_argument("--gh-pages", action="store_true", help="成功後 gh-pages に push")
    args = parser.parse_args()

    sites = args.site or list(DEFAULT_SITES)
    failures: list[str] = []
    for name in sites:
        ok, msg = build_site(name, skip_hub=args.skip_hub_enrich, gh_pages=args.gh_pages)
        if not ok:
            failures.append(f"{name}: {msg}")

    if failures:
        print("\nFailed:", ", ".join(failures), file=sys.stderr)
        return 1
    print("\nAll sites built and validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
