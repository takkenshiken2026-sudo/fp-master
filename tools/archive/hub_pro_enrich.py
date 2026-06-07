#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識ハブ CSV の article_lead / FAQ をプロ水準へ拡張する。

原則: 同一行の既存フィールドだけを使い、新しい数値・条文は足さない。
十分な長さがある行は変更しない（品質優先）。
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

CONCRETE = re.compile(
    r"\d|％|%|年|月|日|条|項|科目|分野|公式|例えば|例：|たとえば|しかし|一方で|具体的|"
    r"原則|上限|下限|問|点|円|時間|義務|禁止|試験|法令|協議会|www|管理|契約"
)

MIN_LEAD = 80
MIN_FAQ = 100
TARGET_FAQ = 110


def split_semicolon(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(";") if x.strip()]


def _join_sentences(parts: list[str]) -> str:
    out: list[str] = []
    for p in parts:
        p = p.strip().rstrip("。")
        if not p:
            continue
        if out and (p in out[-1] or out[-1] in p):
            continue
        if any(p in x or x in p for x in out):
            continue
        out.append(p)
    if not out:
        return ""
    return "。".join(out) + "。"


def _context_faq_suffix(row: dict[str, str]) -> str:
    title = (row.get("title") or "この論点").strip()
    return (
        f"『{title}』は本ページの表と用語集の関連リンクを往復し、"
        "肢のキーワードが定義・要件・効果のどれを問うかを見極めてください。"
    )


def enrich_lead(row: dict[str, str]) -> str:
    lead = (row.get("article_lead") or "").strip()
    if len(lead) >= MIN_LEAD and CONCRETE.search(lead):
        return lead

    parts: list[str] = []
    if lead:
        parts.append(lead.rstrip("。"))
    summary = (row.get("summary") or "").strip().rstrip("。")
    if summary and summary not in lead:
        parts.append(summary)
    points = split_semicolon(row.get("exam_points", ""))
    if points:
        parts.append("試験では特に、" + "、".join(points[:3]) + "の区別が問われます")
    highlight = (row.get("highlight") or "").strip().rstrip("。")
    if highlight and highlight not in "。".join(parts):
        parts.append(f"数値の早見ポイントは「{highlight}」です")
    return _join_sentences(parts) or lead


def enrich_faq_answer(answer: str, row: dict[str, str]) -> str:
    text = (answer or "").strip()
    if len(text) >= TARGET_FAQ:
        return text

    parts: list[str] = []
    if text:
        parts.append(text.rstrip("。"))

    for point in split_semicolon(row.get("exam_points", "")):
        if len(_join_sentences(parts)) >= TARGET_FAQ:
            break
        if point and point not in text and "試験では特に" not in point:
            parts.append(point)

    tip = (row.get("memory_tip") or "").strip().rstrip("。")
    if tip and len(_join_sentences(parts)) < TARGET_FAQ and tip not in text:
        parts.append(tip)

    result = _join_sentences(parts)
    if len(result) < MIN_FAQ:
        suffix = _context_faq_suffix(row)
        if suffix not in result:
            result = result.rstrip("。") + "。" + suffix
    return result if len(result) >= len(text) else text


def enrich_row(row: dict[str, str]) -> dict[str, str]:
    row = dict(row)
    row["article_lead"] = enrich_lead(row)
    for n in range(1, 5):
        key = f"faq_{n}_answer"
        if row.get(key):
            row[key] = enrich_faq_answer(row[key], row)
    return row


def enrich_csv(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])
        rows = list(reader)
    changed = 0
    new_rows = []
    for row in rows:
        old_lead = row.get("article_lead", "")
        old_faqs = [row.get(f"faq_{i}_answer", "") for i in range(1, 5)]
        enriched = enrich_row(row)
        if enriched.get("article_lead") != old_lead or [
            enriched.get(f"faq_{i}_answer") for i in range(1, 5)
        ] != old_faqs:
            changed += 1
        new_rows.append(enriched)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, lineterminator="\n")
        w.writeheader()
        w.writerows(new_rows)
    return changed


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data = root / "data"
    total = 0
    for name in ("comparisons.csv", "numbers.csv", "mistakes.csv"):
        p = data / name
        if p.exists():
            n = enrich_csv(p)
            print(f"{name}: enriched {n} rows")
            total += n
    print(f"done, {total} rows updated")


if __name__ == "__main__":
    main()
