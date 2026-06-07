#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FP3級実技 JSON から data/question_diagrams/*.json を生成する。

  python3 tools/build_fp3_question_diagrams.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fp3_family_trees import source_id_to_diagram_id
from tools.fp_table_parser import materials_text_to_diagram, split_question_and_materials

SOURCE = ROOT / "data" / "source" / "fp3" / "fp3_jitsugi_past_questions_all.json"
OUT_DIR = ROOT / "data" / "question_diagrams"
MANIFEST = ROOT / "data" / "source" / "fp3" / "diagram_manifest.json"


def iter_jitsugi_questions() -> list[dict]:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    out: list[dict] = []
    for qset in data.get("questionSets") or []:
        out.extend(qset.get("questions") or [])
    return out


def main() -> int:
    if not SOURCE.is_file():
        print(f"ERROR: {SOURCE} がありません", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for q in iter_jitsugi_questions():
        diagram = q.get("diagram") or {}
        dtype = diagram.get("type")
        if dtype not in {"html_table", "needs_svg"}:
            continue
        source_id = q["id"]
        diagram_id = source_id_to_diagram_id(source_id)
        kind = str(diagram.get("kind") or "")
        from tools.fp_table_parser import strip_leading_question_from_materials

        text = (q.get("materialsText") or "").strip()
        if not text:
            _, text = split_question_and_materials(q.get("prompt") or "")
        text = strip_leading_question_from_materials(text.strip())
        payload = materials_text_to_diagram(source_id, text, kind=kind)
        path = OUT_DIR / f"{diagram_id}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written += 1
        print("wrote", diagram_id)
    print(f"question_diagrams: {written} files → {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
