#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FP3級 学科・実技 JSON → fp-master の data/*.csv へ取り込む。

  python3 tools/import_fp3_past_questions.py
  python3 tools/import_fp3_past_questions.py --gakka /path/to/fp3_gakka_past_questions_all.json \\
      --jitsugi /path/to/fp3_jitsugi_past_questions_all.json

過去問 CSV の番号体系（年度ごと）:
  問1〜30  … 学科・三答択（元データ問31〜60）
  問31〜50 … 実技・三答択（元データ問1〜20）

一問一答 CSV:
  学科・正誤式（元データ問1〜30）→ id {year}-05-{seq:02d}
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

from tools.fp3_family_trees import source_id_to_diagram_id

DEFAULT_GAKKA = Path.home() / "Desktop/FP3級学科過去問データ/fp3_gakka_past_questions_all.json"
DEFAULT_JITSUGI = Path.home() / "Desktop/FP3級実技過去問データ/fp3_jitsugi_past_questions_all.json"

PAST_CSV = ROOT / "data" / "past_questions.csv"
ICHIMON_CSV = ROOT / "data" / "ichimon_questions.csv"
SOURCE_DIR = ROOT / "data" / "source" / "fp3"
DIAGRAM_MANIFEST = SOURCE_DIR / "diagram_manifest.json"

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

ICHIMON_COLUMNS = [
    "id",
    "question",
    "answer",
    "explanation",
    "explanation_summary",
    "explanation_correct",
    "explanation_opposite",
    "explanation_point",
    "category",
    "tags",
    "source",
    "note",
]

WAREKI = {2024: "令和6年度", 2025: "令和7年度", 2026: "令和8年度"}


def norm(s: object) -> str:
    return str(s or "").strip()


def parse_year_from_id(qid: str) -> int:
    m = re.search(r"_(\d{4})\d{2}_", qid)
    if not m:
        raise ValueError(f"year を id から解釈できません: {qid!r}")
    return int(m.group(1))


def split_stem_preamble(prompt: str, materials_text: str) -> tuple[str, str]:
    """設問文と資料（表・図表テキスト）を分離。図表は preamble に載せる。"""
    from tools.fp_table_parser import split_question_and_materials

    prompt = norm(prompt)
    materials = norm(materials_text)
    stem, tail = split_question_and_materials(prompt)
    if tail:
        return stem, tail
    if materials and materials != prompt:
        lead = prompt
        if materials.startswith(prompt[: min(80, len(prompt))]):
            lead = prompt.split("\n\n")[0] if "\n\n" in prompt else ""
        return lead or prompt.split("＜")[0].strip(), materials
    idx = prompt.find("＜")
    if idx > 0 and "が下記のとおり" not in prompt[: idx + 20]:
        return prompt[:idx].strip(), prompt[idx:].strip()
    idx = prompt.find("経過年数")
    if idx > 0:
        return prompt[:idx].strip(), prompt[idx:].strip()
    return prompt, ""


def diagram_note(diagram: dict | None, qid: str) -> str:
    if not diagram:
        return ""
    kind = norm(diagram.get("kind"))
    dtype = norm(diagram.get("type"))
    status = norm(diagram.get("status"))
    parts = [f"source_id={qid}"]
    if dtype:
        parts.append(f"diagram_type={dtype}")
    if kind:
        parts.append(f"diagram_kind={kind}")
    if status:
        parts.append(f"diagram_status={status}")
    if dtype == "needs_svg":
        parts.append("html_reproduction=planned")
    return "; ".join(parts)


def iter_questions(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[dict] = []
    for qset in data.get("questionSets") or []:
        for q in qset.get("questions") or []:
            out.append(q)
    return out


def gakka_to_ichimon_row(q: dict) -> dict:
    year = parse_year_from_id(q["id"])
    qno = int(q["questionNo"])
    if qno > 30:
        raise ValueError(f"一問一答対象外の問番: {q['id']}")
    published = norm(q.get("published"))
    return {
        "id": f"{year}-05-{qno:02d}",
        "question": norm(q.get("prompt")),
        "answer": norm(q.get("answer")),
        "explanation": norm(q.get("explanation")),
        "explanation_summary": "",
        "explanation_correct": "",
        "explanation_opposite": "",
        "explanation_point": "",
        "category": norm(q.get("category")),
        "tags": "FP3級;学科;正誤式",
        "source": published or f"FP3級学科 {year}",
        "note": q["id"],
    }


def mc_to_past_row(
    q: dict,
    *,
    exam_kind: str,
    question_no: int,
    wareki_suffix: str,
) -> dict:
    year = parse_year_from_id(q["id"])
    choices = q.get("choices") or []
    stem, preamble = split_stem_preamble(norm(q.get("prompt")), norm(q.get("materialsText")))
    diagram = q.get("diagram") or {}
    diagram_id = ""
    if diagram.get("type") in {"html_table", "needs_svg"}:
        diagram_id = source_id_to_diagram_id(q["id"])
        if preamble:
            from tools.fp_table_parser import preamble_is_materials

            if preamble_is_materials(preamble):
                idx = preamble.find("＜")
                if idx > 0:
                    stem = norm(stem) + "\n\n" + preamble[:idx].strip()
            else:
                stem = norm(stem) + "\n\n" + preamble
            preamble = ""
    row = {col: "" for col in PAST_COLUMNS}
    row.update(
        {
            "exam_year": str(year),
            "exam_wareki": f"{WAREKI.get(year, str(year) + '年')}{wareki_suffix}",
            "question_no": str(question_no),
            "type": "single",
            "category": norm(q.get("category")),
            "tags": f"FP3級;{exam_kind};三答択",
            "stem": stem,
            "preamble": preamble,
            "correct": norm(q.get("answer")),
            "is_exempt": "FALSE",
            "is_invalidated": "FALSE",
            "note": diagram_note(diagram, q["id"]),
            "diagram_id": diagram_id,
            "explanation": norm(q.get("explanation")),
        }
    )
    for i, ch in enumerate(choices[:4], start=1):
        row[f"choice_{i}"] = norm(ch.get("text"))
    return row


def build_diagram_manifest(jitsugi: list[dict]) -> list[dict]:
    manifest: list[dict] = []
    for q in jitsugi:
        diagram = q.get("diagram")
        if not diagram:
            continue
        manifest.append(
            {
                "questionId": q["id"],
                "type": diagram.get("type"),
                "kind": diagram.get("kind"),
                "status": diagram.get("status"),
                "htmlReproduction": "planned",
            }
        )
    return manifest


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="FP3級 JSON → past/ichimon CSV")
    parser.add_argument("--gakka", type=Path, default=DEFAULT_GAKKA)
    parser.add_argument("--jitsugi", type=Path, default=DEFAULT_JITSUGI)
    parser.add_argument("--no-copy-source", action="store_true")
    args = parser.parse_args()

    if not args.gakka.is_file():
        print(f"ERROR: 学科 JSON が見つかりません: {args.gakka}", file=sys.stderr)
        return 1
    if not args.jitsugi.is_file():
        print(f"ERROR: 実技 JSON が見つかりません: {args.jitsugi}", file=sys.stderr)
        return 1

    gakka = iter_questions(args.gakka)
    jitsugi = iter_questions(args.jitsugi)

    ichimon_rows: list[dict] = []
    past_rows: list[dict] = []

    for q in gakka:
        qtype = norm(q.get("questionType"))
        if qtype == "true_false":
            ichimon_rows.append(gakka_to_ichimon_row(q))
        elif qtype == "multiple_choice_3":
            src_no = int(q["questionNo"])
            past_rows.append(
                mc_to_past_row(
                    q,
                    exam_kind="学科",
                    question_no=src_no - 30,
                    wareki_suffix="（学科・三答択）",
                )
            )
        else:
            raise ValueError(f"未対応の学科 questionType: {qtype!r} ({q['id']})")

    for q in jitsugi:
        if norm(q.get("questionType")) != "multiple_choice_3":
            raise ValueError(f"未対応の実技 questionType: {q.get('questionType')!r}")
        src_no = int(q["questionNo"])
        past_rows.append(
            mc_to_past_row(
                q,
                exam_kind="実技",
                question_no=src_no + 30,
                wareki_suffix="（実技）",
            )
        )

    ichimon_rows.sort(key=lambda r: r["id"])
    past_rows.sort(key=lambda r: (int(r["exam_year"]), int(r["question_no"])))

    write_csv(ICHIMON_CSV, ICHIMON_COLUMNS, ichimon_rows)
    write_csv(PAST_CSV, PAST_COLUMNS, past_rows)

    if not args.no_copy_source:
        SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.gakka, SOURCE_DIR / "fp3_gakka_past_questions_all.json")
        shutil.copy2(args.jitsugi, SOURCE_DIR / "fp3_jitsugi_past_questions_all.json")
        manifest = build_diagram_manifest(jitsugi)
        DIAGRAM_MANIFEST.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"ichimon_questions.csv: {len(ichimon_rows)} 行")
    print(f"past_questions.csv: {len(past_rows)} 行（学科三答択 {len([q for q in gakka if q.get('questionType')=='multiple_choice_3'])} + 実技 {len(jitsugi)}）")
    print(f"source: {SOURCE_DIR}")
    print("次: python3 tools/build_all.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
