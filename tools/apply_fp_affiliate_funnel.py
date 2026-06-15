#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""学習系ガイドへ公開済み affiliate 比較記事の導線を追加する（FP3級）。"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "guide_articles.csv"

AFFILIATE_TITLES = {
    "affiliate-online-course-compare": "FP3級オンライン講座比較【オンスク.JP vs 資格スクエア】独学との併用",
}

BODY = {
    "affiliate-online-course-compare": (
        "週の学習時間が足りない場合は、affiliate-online-course-compare でオンスク.JPと資格スクエアの演習設計を比較し、当サイト演習量は維持したまま1社に絞ると続きやすいです。"
    ),
}

GUIDE_AFFILIATE: dict[str, tuple[str, int]] = {
    "compare-self-study-vs-correspondence": ("affiliate-online-course-compare", 2),
    "compare-textbook-vs-app": ("affiliate-online-course-compare", 2),
    "attr-zero-knowledge-start": ("affiliate-online-course-compare", 2),
    "faq-study-hours": ("affiliate-online-course-compare", 2),
    "compare-past-questions-only": ("affiliate-online-course-compare", 2),
    "attr-parental-leave": ("affiliate-online-course-compare", 2),
    "attr-side-business-freelance": ("affiliate-online-course-compare", 2),
}


def _split_related(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(";") if x.strip()]


def _append_related(value: str, token: str) -> str:
    parts = _split_related(value)
    slug = token.split(":", 1)[0]
    if any(p.split(":", 1)[0] == slug for p in parts):
        return ";".join(parts)
    parts.append(token)
    return ";".join(parts)


def _append_body(body: str, aff_slug: str) -> str:
    sentence = BODY[aff_slug]
    if aff_slug in (body or ""):
        return body
    text = (body or "").rstrip()
    if not text:
        return sentence
    if not text.endswith("。"):
        text += "。"
    return text + sentence


def apply_guide_updates(rows: list[dict[str, str]]) -> int:
    by_slug = {r["slug"]: r for r in rows}
    changed = 0
    for slug, (aff_slug, sec_n) in GUIDE_AFFILIATE.items():
        row = by_slug.get(slug)
        if not row or (row.get("content_status") or "").strip() != "published":
            continue
        body_key = f"section_{sec_n}_body"
        old_body = row.get(body_key, "")
        new_body = _append_body(old_body, aff_slug)
        if new_body != old_body:
            row[body_key] = new_body

        token = f"{aff_slug}:{AFFILIATE_TITLES[aff_slug]}"
        new_rl = _append_related(row.get("related_links", ""), token)
        if new_rl != row.get("related_links", "") or new_body != old_body:
            row["related_links"] = new_rl
            changed += 1
    return changed


def main() -> None:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if not fieldnames:
        raise SystemExit("guide_articles.csv: no header")

    changed = apply_guide_updates(rows)

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Guide funnel: {len(GUIDE_AFFILIATE)} targets, {changed} row(s) updated")


if __name__ == "__main__":
    main()
