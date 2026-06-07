#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手書き batch（5本目安）を適用し、enrich なしで品質ゲートを通す。"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.apply_guide_rewrite_batch import apply_rewrites, load_rewrites_module  # noqa: E402
from tools.editorial_quality import is_published_guide, norm  # noqa: E402
from tools.guide_article_rules import check_guide_row  # noqa: E402
from tools.strip_generic_guide_padding import strip_row  # noqa: E402


def _run(cmd: list[str], *, root: Path) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=root, check=True)


def validate_slugs(root: Path, slugs: set[str]) -> int:
    csv_path = root / "data" / "guide_articles.csv"
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8-sig")))
    slug_set = {norm(r.get("slug")) for r in rows}
    errors = 0
    for idx, row in enumerate(rows, start=2):
        slug = norm(row.get("slug"))
        if slug not in slugs:
            continue
        for issue in check_guide_row(row, slug_set=slug_set, line=idx):
            if issue.level == "ERROR":
                print(f"ERROR {slug} [{issue.column}] {issue.message}", file=sys.stderr)
                errors += 1
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="5本 batch 品質ゲート付き適用")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--batch", type=Path, required=True)
    ap.add_argument("--build", action="store_true", help="build_all.py まで実行")
    ap.add_argument("--skip-audit", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    mod = load_rewrites_module(args.batch.resolve())
    rewrites = getattr(mod, "REWRITES")
    slugs = set(rewrites.keys())
    print(f"batch slugs ({len(slugs)}): {', '.join(sorted(slugs))}")

    csv_path = root / "data" / "guide_articles.csv"
    n = apply_rewrites(csv_path, rewrites)
    print(f"applied: {n} rows")

    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    changed = 0
    for row in rows:
        if norm(row.get("slug")) in slugs and strip_row(row):
            changed += 1
    if changed:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    print(f"stripped padding: {changed} rows")

    py = sys.executable
    _run([py, "tools/validate_csv.py"], root=root)
    err = validate_slugs(root, slugs)
    if err:
        print(f"slug-specific ERROR: {err}", file=sys.stderr)
        return 1
    if not args.skip_audit:
        _run([py, "tools/audit_guide_prose_quality.py", "--root", str(root), "--strict"], root=root)
    if args.build:
        _run([py, "tools/build_all.py"], root=root)
    print("OK: quality batch passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
