#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""過去問 CSV の学科・実技ラベル抽出。"""

from __future__ import annotations

import re

SUBJECT_LABELS = {"gakka": "学科", "jitsugi": "実技"}


def parse_tags(raw: str | list[str]) -> list[str]:
    """CSV tags（; 区切りが多い）。一覧表示用の内部タグは除外。"""
    if isinstance(raw, list):
        return [str(t).strip() for t in raw if str(t).strip()]
    skip_prefixes = ("otsu4-sample-", "kikenbutsu_", "p")
    skip_exact = {"過去問", "乙4", "要確認"}
    out: list[str] = []
    for t in re.split(r"[,、/|;]+", raw or ""):
        t = t.strip()
        if not t or t in skip_exact:
            continue
        if any(t.startswith(p) for p in skip_prefixes if p != "p"):
            continue
        if re.fullmatch(r"p\d+", t):
            continue
        if t.endswith(".pdf"):
            continue
        out.append(t)
    return out


def subject_from_tags(tags: list[str]) -> str:
    if "実技" in tags:
        return "jitsugi"
    if "学科" in tags:
        return "gakka"
    return ""


def subject_from_row(row: dict, *, qno: int | None = None) -> str:
    raw = row.get("tags") or ""
    tags = parse_tags(raw) if not isinstance(raw, list) else [str(t) for t in raw]
    subject = subject_from_tags(tags)
    if subject:
        return subject
    num = qno if qno is not None else int(row.get("question_no") or 0)
    if num >= 31:
        return "jitsugi"
    if num >= 1:
        return "gakka"
    return ""


def subject_display(subject: str) -> str:
    return SUBJECT_LABELS.get(subject, subject)
