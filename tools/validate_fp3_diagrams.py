#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 diagram JSON の品質チェック。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fp3_family_trees import source_id_to_diagram_id
from tools.fp_table_parser import materials_text_to_diagram, norm, split_question_and_materials

SOURCE = ROOT / "data" / "source" / "fp3" / "fp3_jitsugi_past_questions_all.json"

# 資料図なし（設問文のみ）の diagram 登録
TEXT_ONLY_DIAGRAM_IDS = {
    "fp3_202405_q013",
    "fp3_202405_q014",
    "fp3_202505_q014",
}


def _errors_for_sections(source_id: str, sections: list[dict]) -> list[str]:
    out: list[str] = []
    if not sections:
        if source_id in TEXT_ONLY_DIAGRAM_IDS:
            return []
        return [f"{source_id}: sections が空"]
    for s in sections:
        if s.get("type") == "fp_table":
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
    if errors:
        for e in errors:
            print("ERROR:", e)
        print(f"合計 {len(errors)} 件")
        return 1
    print("validate_fp3_diagrams: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
