#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP2級 実践演習 CSV 用の共通列定義・行ビルダー。"""

from __future__ import annotations

PRACTICE_COLUMNS = [
    "question_no",
    "type",
    "category",
    "tags",
    "source_ref",
    "diagram_id",
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
    "explanation",
    "explanation_summary",
    "explanation_correct",
    "explanation_choices",
    "explanation_point",
]

TAG_BASE = "FP2級;学科;実践演習;四答択"


def practice_row(**kwargs) -> dict:
    base = {c: "" for c in PRACTICE_COLUMNS}
    base["type"] = "single"
    base.update(kwargs)
    return base


def tags(source_key: str, variant: int) -> str:
    return f"{TAG_BASE};source:{source_key}-v{variant}"
