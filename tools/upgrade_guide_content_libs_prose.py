#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""archive/*_guide_content_lib.py の prose 生成を共通ヘルパーへ揃える（一括パッチ）。"""

from __future__ import annotations

import re
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parent / "archive"
LIBS = sorted(ARCHIVE.glob("*_guide_content_lib.py"))

OFFICIAL_NOTE_OLD = re.compile(
    r"def _official_note\(\) -> str:\n"
    r"    return \(\n"
    r"        f\"数値・日程・合格基準は年度で更新されるため、学習前と申込前には\{OFFICIAL\}で\"\n"
    r"        f\"\{ORG\}の最新案内を確認してください。\"\n"
    r"    \)"
)

OFFICIAL_NOTE_NEW = '''def _official_note() -> str:
    from tools.guide_content_shared import official_note_single

    return official_note_single(OFFICIAL)'''

FALLBACK_OLD = re.compile(
    r"    return two_paragraphs\(\n"
    r"        f\"「\{heading\}」では、\{EXAM\}の\{topic\}について、.*?\"\n"
    r"        f\"公式テキストの該当章を開きながら読むと、演習問題の解説とも対応づけやすくなります。\",?\n"
    r"        f\"\{_official_note\(\)\} \{_practice_note\(topic\)\}\",?\n"
    r"    \)",
    re.DOTALL,
)

FALLBACK_NEW = '''    from tools.guide_content_shared import keyword_fallback_default

    return keyword_fallback_default(
        heading,
        topic,
        exam=EXAM,
        exam_short=EXAM_SHORT,
        official=OFFICIAL,
        official_note_fn=_official_note,
        practice_note_fn=_practice_note,
        two_paragraphs_fn=two_paragraphs,
    )'''

SECTION_TAIL_OLD = re.compile(
    r"    tail = f\"\{topic\}の「\{heading\}」は\{OFFICIAL\}と演習解説で必ず照合してください。\""
)

SECTION_TAIL_NEW = '''    from tools.guide_content_shared import section_body_tail

    tail = section_body_tail(heading, OFFICIAL)'''

EXAM_DAY_INSERT = '''        (("持参", "必ず持", "持ち物"), _heading_持ち物と時間配分),
        (("禁止", "持込", "持ち込み"), _heading_持ち物と時間配分),
        (("タイムライン",), _heading_当日タイムライン),
        (("アクセス", "センター", "会場"), _heading_当日タイムライン),
        (("チェックリスト", "忘れ物"), _heading_最終確認リスト),
'''

TOPIC_STRIP_MARKER = "from tools.guide_topic_normalize import strip_exam_prefix"


def patch_topic_from_row(text: str) -> str:
    if TOPIC_STRIP_MARKER in text:
        return text
    # after bracket strip line if present
    m = re.search(
        r"(    title = re\.sub\(r\"\^\(\.\+\?\)【\^】】\$\", r\"\\1\", title\)\.strip\(\)\n)",
        text,
    )
    if m:
        insert = (
            m.group(1)
            + "    from tools.guide_topic_normalize import strip_exam_prefix\n\n"
            + "    title = strip_exam_prefix(title, EXAM, EXAM_SHORT)\n"
        )
        return text.replace(m.group(1), insert, 1)
    # before prefix loop
    m2 = re.search(r"(    for prefix in \(f\"\{EXAM\}の\")", text)
    if m2:
        insert = (
            "    from tools.guide_topic_normalize import strip_exam_prefix\n\n"
            "    title = strip_exam_prefix(title, EXAM, EXAM_SHORT)\n"
            + m2.group(1)
        )
        return text.replace(m2.group(1), insert, 1)
    return text


def patch_exam_day_checks(text: str) -> str:
    if '("タイムライン",), _heading_当日タイムライン)' in text:
        return text
    anchor = re.search(r"(\s+\(\(\"直前\",)", text)
    if anchor:
        return text.replace(anchor.group(1), "\n" + EXAM_DAY_INSERT + anchor.group(1), 1)
    anchor2 = re.search(r"(\s+\(\(\"睡眠\",)", text)
    if anchor2:
        return text.replace(anchor2.group(1), "\n" + EXAM_DAY_INSERT + anchor2.group(1), 1)
    return text


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    text = OFFICIAL_NOTE_OLD.sub(OFFICIAL_NOTE_NEW, text)
    text = FALLBACK_OLD.sub(FALLBACK_NEW, text)
    text = SECTION_TAIL_OLD.sub(SECTION_TAIL_NEW, text)
    text = patch_topic_from_row(text)
    text = patch_exam_day_checks(text)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = 0
    for path in LIBS:
        if patch_file(path):
            print("patched:", path.name)
            changed += 1
        else:
            print("skip:", path.name)
    print(f"done: {changed}/{len(LIBS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
