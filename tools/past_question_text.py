#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""過去問 CSV の設問・選択肢テキスト整形（PDF由来の改行など）。"""

from __future__ import annotations

import re

from tools.fp_table_parser import format_stem_display_text, normalize_jp_linebreaks, norm


def clean_past_field(text: str, kind: str = "inline") -> str:
    """
    kind:
      stem … 設問文（段落整形）
      material … 資料ブロック（表行の改行を維持）
      inline … 選択肢・○×肢（1行に結合）
    """
    t = norm(text)
    if not t:
        return t
    t = normalize_jp_linebreaks(t)
    if kind == "stem":
        return format_stem_display_text(t)
    if kind == "material":
        return t
    return re.sub(r"(?<!\n)\n(?!\n)", "", t)


def clean_past_row_fields(row: dict) -> dict:
    """past_questions.csv 行のテキスト列を一括整形。"""
    out = dict(row)
    if out.get("stem"):
        out["stem"] = clean_past_field(out["stem"], "stem")
    if out.get("preamble"):
        out["preamble"] = clean_past_field(out["preamble"], "material")
    for key in ("statement_a", "statement_b", "statement_c", "statement_d"):
        if out.get(key):
            out[key] = clean_past_field(out[key], "inline")
    for i in range(1, 9):
        key = f"choice_{i}"
        if out.get(key):
            out[key] = clean_past_field(out[key], "inline")
    return out
