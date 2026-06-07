#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""past_questions.csv の stem 列から diagram 用資料の混入を除去する。"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "past_questions.csv"

sys.path.insert(0, str(ROOT))

from tools.fp_table_parser import strip_embedded_materials_from_stem  # noqa: E402


def main() -> int:
    rows: list[dict[str, str]] = []
    changed = 0
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for row in reader:
            diagram_id = (row.get("diagram_id") or "").strip()
            if diagram_id:
                old = row.get("stem") or ""
                new = strip_embedded_materials_from_stem(old)
                if new != old:
                    row["stem"] = new
                    changed += 1
                    print(
                        f"  cleaned {row.get('exam_year')}-q{row.get('question_no')} "
                        f"({len(old)} -> {len(new)} chars)"
                    )
            rows.append(row)

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {changed} row(s) in {CSV_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
