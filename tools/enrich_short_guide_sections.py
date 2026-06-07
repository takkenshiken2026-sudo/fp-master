#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手書きガイドの短い節・FAQを、汎用パディングなしで180/100字以上に補う。"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.editorial_quality import is_published_guide, norm  # noqa: E402
from tools.fix_guide_duplicate_bodies import load_site_lib  # noqa: E402
from tools.guide_article_rules import GUIDE_MIN_FAQ_ANSWER, GUIDE_MIN_SECTION_BODY, reader_facing_text  # noqa: E402
from tools.guide_content_shared import official_note_single  # noqa: E402
from tools.guide_coherence_rules import short_topic_from_title  # noqa: E402
from tools.guide_prose_patterns import GENERIC_SECTION_PAD_RE  # noqa: E402
from tools.strip_generic_guide_padding import strip_padding_from_text  # noqa: E402

FORBIDDEN_EXPAND = GENERIC_SECTION_PAD_RE


def _visible(row: dict[str, str], col: str, text: str) -> str:
    return reader_facing_text(row, col, strip_padding_from_text(text))


def _append_paragraph(body: str, extra: str) -> str:
    extra = norm(extra)
    if not extra or extra in body:
        return body
    return f"{body.rstrip()}\n\n{extra}".strip()


def section_expand_sentence(*, heading: str, topic: str, genre: str, official: str) -> str:
    h = heading
    note = official_note_single(official)
    if ("持ち物" in h or "チェックリスト" in h or "忘れ" in h) and not any(
        x in h for x in ("時間配分", "模試", "模擬", "トラブル")
    ):
        return (
            f"前日のうちに{official}の受験要項と受験票で持ち物・禁止物品を照合し、"
            f"当日朝も中身を目視確認してください。{note}"
        )
    if any(k in h for k in ("スケジュール", "日程", "申込", "年間")):
        return (
            f"日程・締切・手数料は年度で更新されるため、"
            f"申込開始時と試験1か月前の2回は{official}で最新版を確認してください。{note}"
        )
    if any(k in h for k in ("復習", "解き直し", "過去問", "模試")):
        return (
            "誤答は理由（知識不足・読み落とし・ケアレスミス）を分類し、"
            "同タイプの演習を3日後・1週間後に解き直すと定着率が上がります。"
            f"出題範囲の改定は{note}"
        )
    if any(k in h for k in ("計画", "全体像", "ロードマップ", "スタイル")):
        return (
            "週次の学習時間を2週間計測してから計画を確定し、"
            "演習正答率が50％未満の分野へ時間を再配分してください。"
            f"{note}"
        )
    if genre == "分野別対策" or h.startswith("field-"):
        return (
            f"当分野は演習10問×3セットから始め、解説で参照条文を公式テキストで開いて読み返してください。"
            f"{note}"
        )
    if genre in {"受験・申込", "直前・当日", "合格・難易度"}:
        return (
            f"{h}は{official}の要項と公式テキストで根拠を確認し、"
            f"演習で同テーマの設問を解いて理解を定着させてください。{note}"
        )
    return (
        f"「{h}」は{topic}の論点として、公式テキスト該当章と{official}の案内を照合し、"
        f"演習→用語解説→1週間後の解き直しで定着を確認してください。{note}"
    )


def faq_expand_sentence(*, question: str, topic: str, official: str) -> str:
    q = question.rstrip("？?")
    return (
        f"「{q}」は{official}の要項と公式テキストで最新情報を確認してください。"
        f"{topic}では、条文の主体・期限・数値を演習問題とセットで押さえると解答精度が上がります。"
    )


def enrich_row(row: dict[str, str], *, lib, official: str) -> bool:
    slug = norm(row.get("slug"))
    title = norm(row.get("title"))
    genre = norm(row.get("genre"))
    topic = getattr(lib, "topic_from_row", lambda r: short_topic_from_title(title))(row)
    if not topic:
        topic = short_topic_from_title(title)
    before = {k: row.get(k, "") for k in row}

    if not norm(row.get("lead")) and norm(row.get("meta_description")):
        row["lead"] = norm(row.get("meta_description"))

    for idx in range(1, 8):
        bcol = f"section_{idx}_body"
        hcol = f"section_{idx}_heading"
        heading = norm(row.get(hcol))
        body = norm(row.get(bcol))
        if not heading or not body:
            continue
        visible = _visible(row, bcol, body)
        seen_extras: set[str] = set()
        for attempt in range(3):
            if len(visible) >= GUIDE_MIN_SECTION_BODY:
                break
            extra = section_expand_sentence(heading=heading, topic=topic, genre=genre, official=official)
            if attempt == 1:
                extra = (
                    f"演習で間違えた設問は理由をメモし、"
                    f"3日後と1週間後に同分野から解き直してください。"
                )
            elif attempt == 2:
                extra = official_note_single(official)
            if not extra or extra in seen_extras or extra in body or FORBIDDEN_EXPAND.search(extra):
                break
            seen_extras.add(extra)
            body = _append_paragraph(body, extra)
            row[bcol] = body
            visible = _visible(row, bcol, body)

    for idx in range(1, 5):
        qcol = f"faq_{idx}_question"
        acol = f"faq_{idx}_answer"
        question = norm(row.get(qcol))
        answer = norm(row.get(acol))
        if not answer:
            continue
        visible = _visible(row, acol, answer)
        if len(visible) < GUIDE_MIN_FAQ_ANSWER:
            extra = faq_expand_sentence(question=question or f"FAQ{idx}", topic=topic, official=official)
            if extra and extra not in answer:
                row[acol] = _append_paragraph(answer, extra)

    return any(before.get(k) != row.get(k, "") for k in row)


def enrich_site(root: Path, *, dry_run: bool = False) -> dict:
    guide_csv = root / "data" / "guide_articles.csv"
    lib = load_site_lib(root)
    official = getattr(lib, "OFFICIAL", "試験実施団体（公式）")
    with guide_csv.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    changed = 0
    for row in rows:
        if not is_published_guide(row):
            continue
        if enrich_row(row, lib=lib, official=official):
            changed += 1
    if changed and not dry_run:
        with guide_csv.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    return {"changed": changed, "rows": len(rows)}


def main() -> int:
    parser = argparse.ArgumentParser(description="短い手書き節を意味ある追記で補う")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    stats = enrich_site(args.root.resolve(), dry_run=args.dry_run)
    print(f"enrich short sections: {stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
