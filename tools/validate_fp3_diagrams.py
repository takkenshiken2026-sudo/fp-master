#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 diagram JSON・表示 HTML の品質チェック。"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fp3_family_trees import source_id_to_diagram_id
from tools.fp_table_parser import (
    materials_text_to_diagram,
    norm,
    preamble_is_materials,
    split_question_and_materials,
)
from tools.question_diagram import diagram_body_html

SOURCE = ROOT / "data" / "source" / "fp3" / "fp3_jitsugi_past_questions_all.json"
PAST_CSV = ROOT / "data" / "past_questions.csv"
DIAGRAMS_DIR = ROOT / "data" / "question_diagrams"

# 資料図なし（設問文のみ）の diagram 登録
TEXT_ONLY_DIAGRAM_IDS = {
    "fp3_202405_q013",
    "fp3_202405_q014",
    "fp3_202505_q014",
}

LAND_DIAGRAM_IDS = {
    "fp3-jitsugi-202405-q009",
    "fp3-jitsugi-202505-q009",
    "fp3-jitsugi-202505-q020",
    "fp3-jitsugi-202605-q009",
}


def _errors_for_sections(source_id: str, sections: list[dict]) -> list[str]:
    out: list[str] = []
    if not sections:
        if source_id in TEXT_ONLY_DIAGRAM_IDS:
            return []
        return [f"{source_id}: sections が空"]
    for s in sections:
        stype = s.get("type")
        if stype == "fp_table":
            title = str(s.get("title") or "")
            rows = s.get("rows") or []
            if not rows:
                out.append(f"{source_id}: 空の表 ({title})")
            elif title == "遺族が受け取った生命保険の死亡保険金":
                bad = any(
                    "車両" in str(c) or "満期" in str(c) or "約款" in str(c)
                    for r in rows
                    for c in (r if isinstance(r, list) else [r])
                )
                if bad:
                    out.append(f"{source_id}: 死亡保険金表の誤分類 ({title})")
                elif rows and isinstance(rows[0], list) and len(rows[0]) < 2:
                    out.append(f"{source_id}: 死亡保険金表が1列化")
        if stype == "fp_text_block":
            body = str(s.get("body") or "")
            if "幅員" in body and "ｍ" in body and "市道" in body:
                out.append(f"{source_id}: 土地配置が平文のまま (land diagram 化が必要)")
        if stype == "land_diagram" and str(s.get("diagram_id") or "") not in LAND_DIAGRAM_IDS:
            out.append(f"{source_id}: 未登録の land_diagram ({s.get('diagram_id')})")
    return out


def _errors_for_rendered_html(source_id: str, diagram_id: str) -> list[str]:
    out: list[str] = []
    if source_id in TEXT_ONLY_DIAGRAM_IDS:
        return out
    html = diagram_body_html(diagram_id) or ""
    if not html:
        return [f"{source_id}: diagram HTML が空 ({diagram_id})"]
    if "速算表" in html and "<table" not in html:
        out.append(f"{source_id}: 速算表が HTML 表になっていない")
    if diagram_id in LAND_DIAGRAM_IDS and "<svg" not in html:
        out.append(f"{source_id}: 土地配置図の SVG がない")
    return out


def _errors_for_csv_rows() -> list[str]:
    out: list[str] = []
    if not PAST_CSV.is_file():
        return out
    with PAST_CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if "実技" not in row.get("tags", ""):
                continue
            preamble = norm(row.get("preamble"))
            diagram_id = norm(row.get("diagram_id"))
            if preamble and not diagram_id and preamble_is_materials(preamble):
                out.append(
                    f"CSV {row['exam_year']} q{row['question_no']}: "
                    "preamble あり diagram_id なし（資料が平文表示になる）"
                )
    return out


def main() -> int:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    errors: list[str] = []
    for qset in data.get("questionSets") or []:
        for q in qset.get("questions") or []:
            diagram = q.get("diagram") or {}
            if diagram.get("type") not in {"html_table", "needs_svg"}:
                continue
            sid = q["id"]
            text = norm(q.get("materialsText"))
            if not text:
                _, text = split_question_and_materials(q.get("prompt") or "")
            payload = materials_text_to_diagram(sid, text, kind=str(diagram.get("kind") or ""))
            errors.extend(_errors_for_sections(sid, payload.get("sections") or []))
            did = source_id_to_diagram_id(sid)
            errors.extend(_errors_for_rendered_html(sid, did))
            path = DIAGRAMS_DIR / f"{did}.json"
            if not path.is_file():
                errors.append(f"{sid}: diagram JSON なし ({did}.json)")

    errors.extend(_errors_for_csv_rows())

    if errors:
        for e in errors:
            print("ERROR:", e)
        print(f"合計 {len(errors)} 件")
        return 1
    print("validate_fp3_diagrams: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
