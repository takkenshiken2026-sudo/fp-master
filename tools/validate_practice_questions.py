#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data/practice_questions.csv の整合性チェック。"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_past_question_pages import parse_correct
from tools.correct_answer_format import collect_choice_texts
from tools.csv_to_exam_site_past_js import practice_row_to_obj
from tools.fp_table_parser import norm
from tools.site_config import category_to_field_map, extended_correct_answers

PRACTICE_CSV = ROOT / "data" / "practice_questions.csv"
MIN_CHOICE_NOTE_LEN = 72
REQUIRED_TAGS = ("FP3級", "実践演習")


def load_rows() -> list[dict]:
    if not PRACTICE_CSV.is_file():
        raise FileNotFoundError(PRACTICE_CSV)
    with PRACTICE_CSV.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def parse_explanation_choices(raw: str) -> dict[int, str]:
    from tools.q_explanation import parse_explanation_choices as parse

    return parse(raw)


def check_portfolio_expected_return(stem: str, correct_idx: int, opts: list[str]) -> str | None:
    m = re.search(
        r"([0-9.]+)％.*組入れたポートフォリオの期待収益率",
        stem.replace("\n", ""),
    )
    if not m:
        return None
    ra = re.search(r"Ａ資産の期待収益率が([0-9.]+)％", stem)
    rb = re.search(r"Ｂ資産の期待収益率が([0-9.]+)％", stem)
    wa = re.search(r"Ａ資産を([0-9.]+)％", stem)
    wb = re.search(r"Ｂ資産を([0-9.]+)％", stem)
    if not (ra and rb and wa and wb):
        return None
    expected = float(ra.group(1)) * float(wa.group(1)) / 100 + float(rb.group(1)) * float(wb.group(1)) / 100
    exp_str = f"{expected:g}％"
    actual = opts[correct_idx - 1] if 1 <= correct_idx <= len(opts) else ""
    if exp_str not in actual.replace(" ", ""):
        return f"ポートフォリオ期待収益率の検算不一致: 期待≈{exp_str}, 正答肢={actual!r}"
    return None


def validate() -> list[str]:
    errors: list[str] = []
    rows = load_rows()
    seen_no: set[int] = set()
    seen_stem: dict[str, int] = {}
    min_choices = 2 if extended_correct_answers() else 3

    for i, row in enumerate(rows, start=2):
        if norm(row.get("is_invalidated", "")).upper() == "TRUE":
            continue
        line = f"practice_questions.csv line {i}"

        try:
            qno = int(row["question_no"])
        except (KeyError, ValueError):
            errors.append(f"{line}: question_no が無効")
            continue

        if qno in seen_no:
            errors.append(f"{line}: question_no={qno} が重複")
        seen_no.add(qno)

        cat = norm(row.get("category"))
        if cat not in category_to_field_map():
            errors.append(f"{line}: 未対応 category={cat!r}")

        tags = norm(row.get("tags"))
        for t in REQUIRED_TAGS:
            if t not in tags:
                errors.append(f"{line}: tags に {t!r} がありません")

        if not norm(row.get("source_ref")):
            errors.append(f"{line}: source_ref が空です")

        stem = norm(row.get("stem"))
        if not stem:
            errors.append(f"{line}: stem が空です")
        elif stem in seen_stem:
            errors.append(f"{line}: stem が line {seen_stem[stem]} と重複")
        else:
            seen_stem[stem] = i

        opts = collect_choice_texts(row)
        if len(opts) < min_choices:
            errors.append(f"{line}: 選択肢が不足 no={qno}")

        cor = parse_correct(row.get("correct"), max_choice=len(opts))
        if cor is None:
            errors.append(f"{line}: correct が無効 no={qno}")

        try:
            practice_row_to_obj(row, i)
        except ValueError as e:
            errors.append(f"{line}: {e}")

        if not norm(row.get("explanation")):
            errors.append(f"{line}: explanation が空です")
        if not norm(row.get("explanation_correct")):
            errors.append(f"{line}: explanation_correct が空です")

        parsed = parse_explanation_choices(norm(row.get("explanation_choices")))
        if cor is not None:
            for j in range(1, len(opts) + 1):
                if j == cor:
                    continue
                note = parsed.get(j, "")
                if len(note) < MIN_CHOICE_NOTE_LEN:
                    errors.append(
                        f"{line}: 選択肢（{j}）の explanation_choices が短すぎます"
                        f"（{len(note)}文字 < {MIN_CHOICE_NOTE_LEN}）"
                    )

        if cor is not None and opts:
            pf_err = check_portfolio_expected_return(stem, cor, opts)
            if pf_err:
                errors.append(f"{line}: {pf_err}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print(f"validate_practice_questions: NG ({len(errors)} 件)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    rows = [r for r in load_rows() if norm(r.get("is_invalidated", "")).upper() != "TRUE"]
    print(f"validate_practice_questions: OK ({len(rows)} 問)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
