#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""takken data/mistakes.csv の管理組合テンプレ行を宅建向け本文に差し替える。"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.archive.takken_hub_mistakes_content import (  # noqa: E402
    content_for_slug,
    is_condo_stub,
)


def upgrade_row(row: dict[str, str]) -> bool:
    slug = (row.get("slug") or "").strip()
    if not slug or not is_condo_stub(row):
        return False
    content = content_for_slug(slug)
    if not content:
        return False
    for key, value in content.items():
        if key == "pattern_rows":
            row["pattern_rows"] = json.dumps(value, ensure_ascii=False)
        elif key in row or key in (
            "title",
            "summary",
            "confusion_point",
            "article_title",
            "article_lead",
            "exam_points",
            "common_mistakes",
            "memory_tip",
            "related_terms",
            "faq_1_question",
            "faq_1_answer",
            "faq_2_question",
            "faq_2_answer",
            "faq_3_question",
            "faq_3_answer",
            "faq_4_question",
            "faq_4_answer",
        ):
            row[key] = value
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--target",
        type=Path,
        default=Path.cwd(),
        help="takken-master ルート（data/mistakes.csv があるディレクトリ）",
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    csv_path = args.target.resolve() / "data" / "mistakes.csv"
    if not csv_path.is_file():
        print(f"ERROR: not found: {csv_path}", file=sys.stderr)
        return 1

    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    updated = 0
    skipped: list[str] = []
    for row in rows:
        if is_condo_stub(row):
            if upgrade_row(row):
                updated += 1
            else:
                skipped.append(row.get("slug", ""))

    print(f"Updated {updated} mistake rows in {csv_path}")
    if skipped:
        print(f"WARN: condo stub but no content ({len(skipped)}): {', '.join(skipped[:10])}")

    if args.dry_run:
        print("dry-run: not writing")
        return 0

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
