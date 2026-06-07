#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eisei2_past_questions.csv → テンプレ形式 data/past_questions.csv（本番 root で実行）。

  cd /path/to/eisei2shu-master
  python3 /path/to/exam-site-shell/sites/eisei2shu-master/migrate_past_questions.py

既存 tools/csv_to_eisei2_master.py と同じプール年・科目マッピングを使う。
生成後は validate_csv / build_all の前に diff を確認すること。
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_ROOT = SCRIPT_DIR.parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="本番サイトルート（既定: カレント）",
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    src = root / "data" / "eisei2_past_questions.csv"
    dst = root / "data" / "past_questions.csv"
    if not src.is_file():
        print(f"error: missing {src}", file=sys.stderr)
        return 1

    tools = root / "tools"
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    from csv_to_eisei2_master import (  # type: ignore
        discover_pool_years,
        era_western_label,
        normalize_era,
        month_key_for_pool,
        FIELD_MAP,
    )

    with src.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    pool_year, labels = discover_pool_years(rows)

    out_rows: list[dict[str, str]] = []
    for row in rows:
        科目 = (row.get("科目") or "").strip()
        if 科目 not in FIELD_MAP:
            print(f"skip: unknown 科目 {科目!r}", file=sys.stderr)
            continue
        era = normalize_era(row.get("開催年数") or "")
        bk = month_key_for_pool(row)
        year = pool_year[(era, bk)]
        num = int(str(row.get("問番号") or "").strip())
        wareki = labels.get(year, era)
        opts = [(row.get(f"({i})") or "").strip() for i in range(1, 6)]
        ans = str(row.get("正答番号") or "").strip()
        stem = (row.get("問") or "").strip()
        exp = (row.get("解説") or "").strip() or f"正解は選択肢{ans}。"
        out_rows.append(
            {
                "exam_year": str(year),
                "exam_wareki": wareki,
                "question_no": str(num),
                "type": "single",
                "category": 科目,
                "tags": "",
                "stem": stem,
                "preamble": "",
                "statement_a": "",
                "statement_b": "",
                "statement_c": "",
                "statement_d": "",
                "choice_1": opts[0],
                "choice_2": opts[1],
                "choice_3": opts[2],
                "choice_4": opts[3],
                "choice_5": opts[4],
                "correct": ans,
                "is_exempt": "FALSE",
                "is_invalidated": "FALSE",
                "note": "",
                "explanation": exp,
                "explanation_summary": "",
                "explanation_correct": "",
                "explanation_choices": "",
                "explanation_point": "",
                "related_links": "",
            }
        )

    fieldnames = list(out_rows[0].keys()) if out_rows else []
    print(f"rows: {len(out_rows)} -> {dst}")
    if args.dry_run:
        return 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    print(f"wrote {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
