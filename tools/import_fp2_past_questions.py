#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FP2級 学科・実技 JSON → fp2/data/past_questions.csv へ取り込む。

  python3 tools/import_fp2_past_questions.py
  python3 tools/import_fp2_past_questions.py --gakka ~/Desktop/.../fp2_gakka_past_questions_all.json \\
      --jitsugi ~/Desktop/.../fp2_jitsugi_past_questions_all.json

過去問 CSV の番号体系（年度ごと）:
  問1〜60  … 学科・四答択
  問61〜100 … 実技（四択・○×・記述計算）

実技は正解未収録の問が含まれる場合、tags に「正解未収録」を付与し問題閲覧のみ公開します。
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

from tools.past_question_subject import (
    FP2_JITSUGI_QUESTION_START,
    PENDING_ANSWER_TAG,
    subject_from_row,
)
from tools.past_question_text import clean_past_field, clean_past_row_fields

DESKTOP_GAKKA = Path.home() / "Desktop/FP2級学科過去問データ/merged/fp2_gakka_past_questions_all.json"
DESKTOP_JITSUGI = Path.home() / "Desktop/FP2級実技過去問データ/merged/fp2_jitsugi_past_questions_all.json"
FP2_DATA = ROOT / "fp2" / "data"
PAST_CSV = FP2_DATA / "past_questions.csv"
SOURCE_DIR = ROOT / "data" / "source" / "fp2"
REPO_GAKKA = SOURCE_DIR / "fp2_gakka_past_questions_all.json"
REPO_JITSUGI = SOURCE_DIR / "fp2_jitsugi_past_questions_all.json"
DEFAULT_GAKKA = DESKTOP_GAKKA if DESKTOP_GAKKA.is_file() else REPO_GAKKA
DEFAULT_JITSUGI = DESKTOP_JITSUGI if DESKTOP_JITSUGI.is_file() else REPO_JITSUGI

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
GAKKA_EXPLANATION = (
    "（解説は順次追加予定です。正答は日本FP協会の公表資料に基づきます。）"
)
JITSUGI_PENDING_EXPLANATION = (
    "（正解・解説は解答資料の公表後に追加予定です。現時点では問題文の確認用に掲載しています。）"
)

STATEMENT_KEYS = ("statement_a", "statement_b", "statement_c", "statement_d")


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


def is_tf_open_answer(prompt: str) -> bool:
    text = norm(prompt)
    return "\n（ア）" in text and ("○" in text or "×" in text)


def split_tf_prompt(prompt: str) -> tuple[str, list[str]]:
    text = norm(prompt)
    labels = ("ア", "イ", "ウ", "エ")
    statements: list[str] = []
    stem = text
    for i, lab in enumerate(labels):
        marker = f"\n（{lab}）"
        idx = text.find(marker)
        if idx == -1:
            if i == 0:
                return text, []
            continue
        if i == 0:
            stem = text[:idx].strip()
        start = idx + len(marker)
        if i + 1 < len(labels):
            next_marker = f"\n（{labels[i + 1]}）"
            end = text.find(next_marker, start)
            if end == -1:
                end = len(text)
        else:
            end = len(text)
        statements.append(text[start:end].strip())
    return stem, statements


def empty_past_row() -> dict:
    return {col: "" for col in PAST_COLUMNS}


def read_existing_gakka_rows() -> list[dict]:
    if not PAST_CSV.is_file():
        return []
    with PAST_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out: list[dict] = []
    for row in rows:
        if subject_from_row(row) == "gakka":
            out.append(row)
        elif int(row.get("question_no") or 0) < FP2_JITSUGI_QUESTION_START:
            out.append(row)
    return out


def read_existing_jitsugi_rows() -> list[dict]:
    if not PAST_CSV.is_file():
        return []
    with PAST_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out: list[dict] = []
    for row in rows:
        if subject_from_row(row) == "jitsugi":
            out.append(row)
        elif int(row.get("question_no") or 0) >= FP2_JITSUGI_QUESTION_START:
            out.append(row)
    return out


def resolve_import_json(cli_path: Path, repo_path: Path) -> Path:
    if cli_path.is_file():
        return cli_path
    if repo_path.is_file():
        return repo_path
    return cli_path


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

    row = empty_past_row()
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
            "explanation": norm(q.get("explanation")) or GAKKA_EXPLANATION,
        }
    )
    for i, ch in enumerate(choices[:4], start=1):
        row[f"choice_{i}"] = clean_past_field(norm(ch.get("text")), "inline")
    return clean_past_row_fields(row)


def jitsugi_to_past_row(q: dict) -> dict:
    year = parse_year_from_id(q["id"])
    src_no = int(q["questionNo"])
    if src_no > 40:
        raise ValueError(f"実技の問番が40を超えています: {q['id']}")
    question_no = FP2_JITSUGI_QUESTION_START - 1 + src_no

    qtype = norm(q.get("questionType"))
    prompt = norm(q.get("prompt"))
    materials = norm(q.get("materialsText"))
    answer = norm(q.get("answer"))
    pending = not answer

    row = empty_past_row()
    row.update(
        {
            "exam_year": str(year),
            "exam_wareki": f"{WAREKI.get(year, str(year) + '年')}（実技）",
            "question_no": str(question_no),
            "category": norm(q.get("category")),
            "is_exempt": "FALSE",
            "is_invalidated": "FALSE",
            "note": q["id"],
            "explanation": norm(q.get("explanation")) or JITSUGI_PENDING_EXPLANATION,
        }
    )

    if pending:
        row["tags"] = f"FP2級;実技;{PENDING_ANSWER_TAG}"
        row["correct"] = ""
    else:
        row["correct"] = answer

    if qtype == "multiple_choice_4":
        row["type"] = "single"
        if not pending:
            row["tags"] = "FP2級;実技;四答択"
        else:
            row["tags"] = f"FP2級;実技;四答択;{PENDING_ANSWER_TAG}"
        stem, preamble = split_stem_preamble(prompt, materials)
        row["stem"] = stem
        row["preamble"] = preamble
        for i, ch in enumerate((q.get("choices") or [])[:4], start=1):
            row[f"choice_{i}"] = clean_past_field(norm(ch.get("text")), "inline")
    elif qtype == "open_answer":
        if is_tf_open_answer(prompt):
            row["type"] = "truefalse"
            row["tags"] = f"FP2級;実技;○×;{PENDING_ANSWER_TAG}" if pending else "FP2級;実技;○×"
            stem, statements = split_tf_prompt(prompt)
            row["stem"] = stem
            for key, stmt in zip(STATEMENT_KEYS, statements[:4]):
                row[key] = stmt
        else:
            row["type"] = "open"
            row["tags"] = (
                f"FP2級;実技;記述;{PENDING_ANSWER_TAG}" if pending else "FP2級;実技;記述"
            )
            stem, preamble = split_stem_preamble(prompt, materials)
            row["stem"] = stem
            row["preamble"] = preamble
    else:
        raise ValueError(f"未対応の実技 questionType: {qtype!r} ({q['id']})")

    return clean_past_row_fields(row)


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="FP2級 学科・実技 JSON → past_questions.csv")
    parser.add_argument("--gakka", type=Path, default=DEFAULT_GAKKA)
    parser.add_argument("--jitsugi", type=Path, default=DEFAULT_JITSUGI)
    parser.add_argument("--no-copy-source", action="store_true")
    args = parser.parse_args()

    gakka_path = resolve_import_json(args.gakka, REPO_GAKKA)
    jitsugi_path = resolve_import_json(args.jitsugi, REPO_JITSUGI)

    gakka_rows: list[dict] = []
    if gakka_path.is_file():
        gakka_rows = [gakka_to_past_row(q) for q in iter_questions(gakka_path)]
    else:
        gakka_rows = read_existing_gakka_rows()
        if not gakka_rows:
            print(f"ERROR: 学科 JSON が見つかりません: {args.gakka}", file=sys.stderr)
            return 1
        print(
            f"SKIP: 学科 JSON が見つかりません（{args.gakka}）。"
            f" 既存 CSV から学科 {len(gakka_rows)} 行を維持します。",
            file=sys.stderr,
        )

    jitsugi_rows: list[dict] = []
    if jitsugi_path.is_file():
        jitsugi_rows = [jitsugi_to_past_row(q) for q in iter_questions(jitsugi_path)]
    else:
        jitsugi_rows = read_existing_jitsugi_rows()
        if jitsugi_rows:
            print(
                f"SKIP: 実技 JSON が見つかりません（{args.jitsugi}）。"
                f" 既存 CSV から実技 {len(jitsugi_rows)} 行を維持します。",
                file=sys.stderr,
            )
        else:
            print(
                f"SKIP: 実技 JSON が見つかりません（{args.jitsugi}）。実技は取り込みません。",
                file=sys.stderr,
            )

    past_rows = gakka_rows + jitsugi_rows
    past_rows.sort(key=lambda r: (int(r["exam_year"]), int(r["question_no"])))

    write_csv(PAST_CSV, PAST_COLUMNS, past_rows)

    if not args.no_copy_source:
        SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        if gakka_path.is_file() and gakka_path != REPO_GAKKA:
            shutil.copy2(gakka_path, REPO_GAKKA)
        if jitsugi_path.is_file() and jitsugi_path != REPO_JITSUGI:
            shutil.copy2(jitsugi_path, REPO_JITSUGI)

    years = sorted({int(r["exam_year"]) for r in past_rows})
    jitsugi_count = len(jitsugi_rows)
    gakka_count = len(gakka_rows)
    print(
        f"past_questions.csv: {len(past_rows)} 行"
        f"（学科 {gakka_count} + 実技 {jitsugi_count} / {', '.join(map(str, years))}年）"
    )
    print(f"出力: {PAST_CSV}")
    print("次: python3 tools/build_fp2_site.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
