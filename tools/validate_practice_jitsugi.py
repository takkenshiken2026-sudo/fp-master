#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""実技の実践演習（tags に「実技」）の追加チェック。バッチ追記後に実行する。"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_past_question_pages import build_materials_html, parse_correct
from tools.correct_answer_format import collect_choice_texts
from tools.fp_table_parser import norm
from tools.past_question_subject import parse_tags, subject_from_row

PRACTICE_CSV = ROOT / "data" / "practice_questions.csv"
PAST_CSV = ROOT / "data" / "past_questions.csv"
DIAGRAM_DIR = ROOT / "data" / "question_diagrams"


def load_practice() -> list[dict]:
    with PRACTICE_CSV.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_past_by_ref() -> dict[str, dict]:
    out: dict[str, dict] = {}
    with PAST_CSV.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if "実技" not in (row.get("tags") or ""):
                continue
            ref = f"{row['exam_year']}-jitsugi-{int(row['question_no']):02d}"
            out[ref] = row
    return out


def zen_num(s: str) -> str:
    return s.translate(str.maketrans("０１２３４５６７８９，．", "0123456789,."))


def diagram_has_content(diagram_id: str) -> bool:
    path = DIAGRAM_DIR / f"{diagram_id}.json"
    if not path.is_file():
        return False
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    sections = data.get("sections") or []
    return bool(sections)


def explanation_states_correct(explanation: str, correct_idx: int) -> bool:
    exp = norm(explanation)
    return f"正解は{correct_idx}" in exp or f"正解は{correct_idx}です" in exp


def validate() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    rows = load_practice()
    past = load_past_by_ref()
    jitsugi_rows = [r for r in rows if "実技" in (r.get("tags") or "")]

    if not jitsugi_rows:
        warns.append("実技の実践演習が0問です")
        return errors, warns

    for i, row in enumerate(rows, start=2):
        tags = parse_tags(norm(row.get("tags")))
        if "実技" not in tags:
            continue
        line = f"practice_questions.csv line {i} q={row.get('question_no')}"
        qno = int(row["question_no"])

        if subject_from_row(row, qno=qno) != "jitsugi":
            errors.append(f"{line}: subject が jitsugi ではありません")
        if "学科" in tags:
            errors.append(f"{line}: tags に「学科」が含まれています（実技バッチでは不可）")

        ref = norm(row.get("source_ref"))
        if not ref or "jitsugi" not in ref:
            errors.append(f"{line}: source_ref が実技形式ではありません: {ref!r}")

        diagram_id = norm(row.get("diagram_id"))
        past_row = past.get(ref)
        if past_row:
            past_diag = norm(past_row.get("diagram_id"))
            if past_diag and diagram_has_content(past_diag) and not diagram_id:
                errors.append(f"{line}: 出典 {ref} は図表ありですが diagram_id がありません")
            if diagram_id and not (DIAGRAM_DIR / f"{diagram_id}.json").is_file():
                errors.append(f"{line}: diagram_id の JSON がありません: {diagram_id}")
            past_stem = norm(past_row.get("stem"))
            stem = norm(row.get("stem"))
            if stem == past_stem:
                warns.append(f"{line}: 問題文が過去問と同一です（演習としては許容するが要確認）")

        if diagram_id:
            html = build_materials_html(row)
            if not html.strip():
                errors.append(f"{line}: diagram_id があるのに資料 HTML が空です")
            static_path = ROOT / "q" / "practice" / f"p{qno:03d}" / "index.html"
            if static_path.is_file() and "q-materials" not in static_path.read_text(encoding="utf-8"):
                errors.append(
                    f"{line}: 静的ページに q-materials がありません（build_practice_ichimon を再実行）"
                )

        opts = collect_choice_texts(row)
        cor = parse_correct(row.get("correct"), max_choice=len(opts))
        if cor is None:
            errors.append(f"{line}: correct が無効です")
            continue
        if not explanation_states_correct(norm(row.get("explanation")), cor):
            errors.append(f"{line}: explanation が「正解は{cor}」と一致しません")

        ans_text = opts[cor - 1]
        exp = norm(row.get("explanation"))
        # 数値正答が explanation に含まれるか（円・万円）
        ans_digits = re.sub(r"[^\d]", "", zen_num(ans_text))
        if ans_digits and ans_digits not in re.sub(r"[^\d]", "", zen_num(exp)):
            warns.append(
                f"{line}: 正答肢の数値が explanation 内で確認しづらいです（手計算の再確認を推奨）"
            )

    return errors, warns


def main() -> int:
    errors, warns = validate()
    for w in warns:
        print(f"WARN: {w}")
    if errors:
        print(f"validate_practice_jitsugi: NG ({len(errors)} 件)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    n = sum(1 for r in load_practice() if "実技" in (r.get("tags") or ""))
    print(f"validate_practice_jitsugi: OK ({n} 問実技, {len(warns)} 警告)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
