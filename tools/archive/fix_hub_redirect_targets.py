#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hub_redirects.json の canonical 不在ターゲットを、同一 prefix の CSV slug に差し替える。"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def _load_slugs(csv_path: Path) -> set[str]:
    if not csv_path.is_file():
        return set()
    return {
        (row.get("slug") or "").strip()
        for row in csv.DictReader(csv_path.open(encoding="utf-8-sig"))
        if (row.get("slug") or "").strip()
    }


def fix_hub_redirects(root: Path, *, dry_run: bool = False) -> int:
    hr_path = root / "data" / "hub_redirects.json"
    if not hr_path.is_file():
        return 0
    data = json.loads(hr_path.read_text(encoding="utf-8"))
    comp_slugs = _load_slugs(root / "data" / "comparisons.csv")
    num_slugs: set[str] = set()
    for name in ("numbers.csv", "number_facts.csv"):
        num_slugs |= _load_slugs(root / "data" / name)
    mis_slugs = _load_slugs(root / "data" / "mistakes.csv")

    changes = 0
    for section, canon in (
        ("compare", comp_slugs),
        ("numbers", num_slugs),
        ("mistakes", mis_slugs),
    ):
        mapping = data.get(section) or {}
        if not mapping or not canon:
            continue
        for target in sorted(set(mapping.values())):
            if target in canon:
                continue
            prefix = target.split("-", 1)[0] if "-" in target else target[:3]
            candidates = sorted(s for s in canon if s.startswith(prefix)) or sorted(canon)
            replacement = candidates[0]
            for key, value in list(mapping.items()):
                if value == target:
                    mapping[key] = replacement
            changes += 1
        data[section] = mapping

    if changes and not dry_run:
        hr_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    n = fix_hub_redirects(args.target.resolve(), dry_run=args.dry_run)
    print(f"{'would fix' if args.dry_run else 'fixed'} {n} redirect target group(s) in {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
