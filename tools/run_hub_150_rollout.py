#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""知識ハブ 150件/種: write_*_hub_data → repair → validate(hub) → HTML 再ビルド。"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

SHELL = Path(__file__).resolve().parents[1]
PROJECTS = Path.home() / "Projects"

DEFAULT_SITES = (
    "boiler-master.jp",
    "kangyou-master",
    "mentalhealth-master",
    "takken-master",
)


def hub_counts(root: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    for name in ("comparisons.csv", "numbers.csv", "mistakes.csv"):
        p = root / "data" / name
        if p.is_file():
            out[name] = sum(1 for _ in csv.DictReader(p.open(encoding="utf-8-sig")))
    return out


def run(cmd: list[str], *, cwd: Path, env: dict) -> bool:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, env=env).returncode == 0


def rollout_site(name: str, *, skip_build: bool) -> tuple[bool, str]:
    root = PROJECTS / name
    if not root.is_dir():
        return False, "missing"
    py = sys.executable
    env = {**dict(__import__("os").environ), "EXAM_SITE_ROOT": str(root), "PYTHONPATH": str(root)}

    print(f"\n=== {name} ===")
    hub_scripts = sorted(root.glob("tools/write_*_hub_data.py"))
    if not hub_scripts:
        return False, "no write_*_hub_data.py"
    if not run([py, str(hub_scripts[0])], cwd=root, env=env):
        return False, "hub_data"

    repair = SHELL / "tools/repair_csv_for_validate.py"
    if repair.is_file():
        if not run([py, str(repair), "--root", str(root)], cwd=SHELL, env=env):
            return False, "repair_csv"

    enrich = root / "tools/hub_pro_enrich.py"
    if enrich.is_file():
        for csv_name in ("comparisons.csv", "numbers.csv", "mistakes.csv"):
            p = root / "data" / csv_name
            if p.is_file():
                code = (
                    "import sys; sys.path.insert(0, %r); "
                    "from tools.hub_pro_enrich import enrich_csv; "
                    "from pathlib import Path; "
                    "p=Path('data')/%r; print(f'enriched {enrich_csv(p)} rows')"
                ) % (str(root), csv_name)
                run([py, "-c", code], cwd=root, env=env)

    validate = root / "tools/validate_csv.py"
    if validate.is_file():
        proc = subprocess.run(
            [py, str(validate), "--scope", "hub", "--summary"],
            cwd=root,
            env=env,
        )
        if proc.returncode != 0:
            return False, "validate hub"

    counts = hub_counts(root)
    ok = all(n >= 150 for n in counts.values()) and len(counts) == 3
    print(f"  counts: {counts} target150={'OK' if ok else 'NG'}")

    if skip_build:
        return ok, "OK" if ok else "count"

    for step in ("tools/build_compare_pages.py", "tools/build_numbers_mistakes_pages.py"):
        p = root / step
        if p.is_file() and not run([py, step], cwd=root, env=env):
            return False, step

    if not run([py, "tools/build_sitemap.py"], cwd=root, env=env):
        return False, "sitemap"
    return ok, "OK" if ok else "count"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", action="append")
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()
    sites = args.site or list(DEFAULT_SITES)
    failures: list[str] = []
    for name in sites:
        ok, msg = rollout_site(name, skip_build=args.skip_build)
        if not ok:
            failures.append(f"{name}: {msg}")
    if failures:
        print("\nFailed:", ", ".join(failures), file=sys.stderr)
        return 1
    print("\nHub rollout complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
