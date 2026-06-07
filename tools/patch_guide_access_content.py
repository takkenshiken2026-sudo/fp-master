#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""archive/*_guide_content_lib.py の会場アクセス本文を具体化する。"""

from __future__ import annotations

import re
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parent / "archive"
LIBS = sorted(ARCHIVE.glob("*_guide_content_lib.py"))

ACCESS_FN = '''def _heading_試験会場アクセス(topic: str, _slug: str, _genre: str, _ctx: dict) -> str:
    from tools.guide_content_shared import exam_venue_access_prose

    return exam_venue_access_prose(official=OFFICIAL, topic=topic)


'''

ACCESS_OLD = re.compile(
    r"def _heading_試験会場アクセス\(topic: str, _slug: str, _genre: str, _ctx: dict\) -> str:\n"
    r"    return two_paragraphs\(\n"
    r"        f\"受験票記載の会場、または\{OFFICIAL\}の会場案内で、所在地・交通アクセスを確認してください。\"\n"
    r"        f\"試験当日は公共交通のダイヤ変更や駐車場の有無も含め、前日までにルートを確定しておくと安心です。\",\n"
    r"        f\"初めて訪れる場合は地図アプリで試験開始30分前到着までの所要時間に余裕を持たせ、当日の遅延リスクを減らしてください。\",\n"
    r"    \)\n",
    re.MULTILINE,
)

VENUE_OLD = re.compile(
    r"def _heading_申込手順会場\(topic: str, _slug: str, _genre: str, _ctx: dict\) -> str:\n"
    r"    return two_paragraphs\(\n"
    r"        f\"申込フォームでは、氏名・受験地・連絡先を正確に入力します。\"\n"
    r"        f\"会場は都市ごとに設定されるため、交通手段と試験当日の所要時間を前もって確認してください。\",\n"
    r"        f\"受験票に記載される持ち物（筆記用具、身分証など）は要項どおりに準備し、\"\n"
    r"        f\"前日にカバンに入れておくと当日のミスを減らせます。\",\n"
    r"    \)\n",
    re.MULTILINE,
)

VENUE_NEW = '''def _heading_申込手順会場(topic: str, _slug: str, _genre: str, _ctx: dict) -> str:
    from tools.guide_content_shared import exam_application_venue_prose

    return exam_application_venue_prose(official=OFFICIAL, topic=topic)


'''

KEYWORD_OLD_A = re.compile(
    r'\(\("アクセス", "センター", "会場"\), _heading_当日タイムライン\),'
)
KEYWORD_OLD_B = re.compile(
    r'\(\("アクセス", "センター"\), _heading_試験会場アクセス\),'
)
KEYWORD_NEW = '        (("アクセス", "センター"), _heading_試験会場アクセス),'


def patch_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    changes: list[str] = []
    new = text

    if ACCESS_OLD.search(new):
        new = ACCESS_OLD.sub(ACCESS_FN, new, count=1)
        changes.append("access_fn")
    elif "_heading_試験会場アクセス" not in new:
        anchor = "def _heading_申込手順会場"
        if anchor in new:
            new = new.replace(anchor, ACCESS_FN + anchor, 1)
            changes.append("access_fn_added")

    if VENUE_OLD.search(new):
        new = VENUE_OLD.sub(VENUE_NEW, new, count=1)
        changes.append("venue_fn")

    if KEYWORD_OLD_A.search(new):
        new = KEYWORD_OLD_A.sub(KEYWORD_NEW, new, count=1)
        changes.append("keyword_fix")
    elif "_heading_試験会場アクセス" in new and not KEYWORD_OLD_B.search(new):
        # eisei2shu 等: タイムライン行の直後にアクセス行が無ければ追加
        tl = re.search(
            r'(\(\("タイムライン",\), _heading_当日タイムライン\),\n)',
            new,
        )
        if tl and KEYWORD_NEW.strip() not in new:
            new = new.replace(tl.group(1), tl.group(1) + KEYWORD_NEW + "\n", 1)
            changes.append("keyword_add")

    if new != text:
        path.write_text(new, encoding="utf-8")
    return changes


def main() -> int:
    for path in LIBS:
        ch = patch_file(path)
        print(f"{path.name}: {ch or 'unchanged'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
