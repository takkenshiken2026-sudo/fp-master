#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FP2級 学科 JSON → fp2/data/past_questions.csv へ取り込む。

  python3 tools/import_fp2_past_questions.py
  python3 tools/import_fp2_past_questions.py --gakka ~/Desktop/.../fp2_gakka_past_questions_all.json

過去問 CSV の番号体系（年度ごと）:
  問1〜60 … 学科・四答択

実技（記述・○×混在）は正解データ未収録のため、学科のみ取り込みます。
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_GAKKA = Path.home() / "Desktop/FP2級学科過去問データ/merged/fp2_gakka_past_questions_all.json"
FP2_DATA = ROOT / "fp2" / "data"
PAST_CSV = FP2_DATA / "past_questions.csv"
SOURCE_DIR = ROOT / "data" / "source" / "fp2"

PAST_COLUMNS = [
    "exam_year",
    "exam_wareki",
    "question_no",
    "type",
    "category",
    "tags",
    "stem",
    "preamble",
    "statement_a",
    "statement_b",
    "statement_c",
    "statement_d",
    "choice_1",
    "choice_2",
    "choice_3",
    "choice_4",
    "correct",
    "is_exempt",
    "is_invalidated",
    "note",
    "explanation",
    "explanation_summary",
    "explanation_correct",
    "explanation_choices",
    "explanation_point",
    "related_links",
    "diagram_id",
]

WAREKI = {2025: "令和7年度", 2026: "令和8年度"}
DEFAULT_EXPLANATION = (
    "（解説は順次追加予定です。正答は日本FP協会の公表資料に基づきます。）"
)


def norm(s: object) -> str:
    return str(s or "").strip()


def parse_year_from_id(qid: str) -> int:
    m = re.search(r"_(\d{4})\d{2}_", qid)
    if not m:
        raise ValueError(f"year を id から解釈できません: {qid!r}")
    return int(m.group(1))


def iter_questions(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data.get("questions"), list):
        return data["questions"]
    out: list[dict] = []
    for qset in data.get("questionSets") or []:
        for q in qset.get("questions") or []:
            out.append(q)
    return out


def split_stem_preamble(prompt: str, materials_text: str) -> tuple[str, str]:
    from tools.fp_table_parser import split_question_and_materials

    prompt = norm(prompt)
    materials = norm(materials_text)
    stem, tail = split_question_and_materials(prompt)
    if tail:
        return stem, tail
    if materials and materials != prompt:
        return prompt.split("\n\n")[0].strip() or prompt, materials
    return prompt, ""


def gakka_to_past_row(q: dict) -> dict:
    year = parse_year_from_id(q["id"])
    qno = int(q["questionNo"])
    if qno > 60:
        raise ValueError(f"学科の問番が60を超えています: {q['id']}")
    qtype = norm(q.get("questionType"))
    if qtype != "multiple_choice_4":
        raise ValueError(f"未対応の学科 questionType: {qtype!r} ({q['id']})")

    choices = q.get("choices") or []
    stem, preamble = split_stem_preamble(norm(q.get("prompt")), norm(q.get("materialsText")))
    answer = norm(q.get("answer"))
    if not answer:
        raise ValueError(f"正答がありません: {q['id']}")

    row = {col: "" for col in PAST_COLUMNS}
    row.update(
        {
            "exam_year": str(year),
            "exam_wareki": f"{WAREKI.get(year, str(year) + '年')}（学科）",
            "question_no": str(qno),
            "type": "single",
            "category": norm(q.get("category")),
            "tags": "FP2級;学科;四答択",
            "stem": stem,
            "preamble": preamble,
            "correct": answer,
            "is_exempt": "FALSE",
            "is_invalidated": "FALSE",
            "note": q["id"],
            "explanation": norm(q.get("explanation")) or DEFAULT_EXPLANATION,
        }
    )
    for i, ch in enumerate(choices[:4], start=1):
        row[f"choice_{i}"] = norm(ch.get("text"))
    return row


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="FP2級 学科 JSON → past_questions.csv")
    parser.add_argument("--gakka", type=Path, default=DEFAULT_GAKKA)
    parser.add_argument("--no-copy-source", action="store_true")
    args = parser.parse_args()

    if not args.gakka.is_file():
        print(f"ERROR: 学科 JSON が見つかりません: {args.gakka}", file=sys.stderr)
        return 1

    gakka = iter_questions(args.gakka)
    past_rows = [gakka_to_past_row(q) for q in gakka]
    past_rows.sort(key=lambda r: (int(r["exam_year"]), int(r["question_no"])))

    write_csv(PAST_CSV, PAST_COLUMNS, past_rows)

    if not args.no_copy_source:
        SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.gakka, SOURCE_DIR / "fp2_gakka_past_questions_all.json")

    years = sorted({int(r["exam_year"]) for r in past_rows})
    print(f"past_questions.csv: {len(past_rows)} 行（学科・四答択 / {', '.join(map(str, years))}年）")
    print(f"出力: {PAST_CSV}")
    print("次: python3 tools/build_fp2_site.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
