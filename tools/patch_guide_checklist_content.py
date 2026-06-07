#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""archive/*_guide_content_lib.py のチェックリスト・当日流れを具体化する。"""

from __future__ import annotations

import re
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parent / "archive"
LIBS = sorted(ARCHIVE.glob("*_guide_content_lib.py"))

FINAL_OLD = re.compile(
    r"def _heading_最終確認リスト\(topic: str, _slug: str, _genre: str, _ctx: dict\) -> str:\n"
    r"    return two_paragraphs\(\n"
    r"        f\"試験前日までに、\{OFFICIAL\}の受験要項と受験票で\{topic\}を最終確認してください。\"\n"
    r"        f\"持ち物（鉛筆・消しゴム・身分証など）、会場・開始時刻、禁止物品の有無をチェックリストに書き出します。\",\n"
    r"        f\"学習面では新しい教材を増やさず、誤答ノートと頻出用語だけを短時間で見直します。\"\n"
    r"        f\"睡眠を優先し、当日朝のルートと所要時間も前日に確定しておくと安心です。\",\n"
    r"    \)\n",
    re.MULTILINE,
)

FINAL_NEW = '''def _heading_最終確認リスト(topic: str, _slug: str, _genre: str, _ctx: dict) -> str:
    from tools.guide_content_shared import exam_day_forget_checklist_prose

    return exam_day_forget_checklist_prose(official=OFFICIAL, topic=topic)

'''

TIMELINE_OLD_A = re.compile(
    r"def _heading_当日タイムライン\(topic: str, _slug: str, _genre: str, _ctx: dict\) -> str:\n"
    r"    return two_paragraphs\(\n"
    r"        f\"「\{topic\}」の当日は、起床から会場到着（開始30分前目安）、受付、着席、解答、退場までの流れを想定して行動します。\"\n"
    r"        f\"前日準備した持ち物をそのまま持参し、会場到着後は係員の指示に従ってください。\",\n"
    r"        \"開始直前は長時間の暗記より、呼吸を整えて問題文を最後まで読む習慣を意識します。\"\n"
    r"        \"時間配分は演習で慣れたペースを維持し、見直し用に5〜10分を確保できるよう調整してください。\",\n"
    r"    \)\n",
    re.MULTILINE,
)

TIMELINE_OLD_B = re.compile(
    r"def _heading_当日タイムライン\(topic: str, _slug: str, _genre: str, _ctx: dict\) -> str:\n"
    r"    return two_paragraphs\(\n"
    r"        \"試験当日は、起床から会場到着（開始30分前目安）、受付、着席、解答、退場までの流れを想定して行動します。\"\n"
    r"        \"前日準備した持ち物をそのまま持参し、会場到着後は係員の指示に従ってください。\",\n"
    r"        \"開始直前は長時間の暗記より、呼吸を整えて問題文を最後まで読む習慣を意識します。\"\n"
    r"        \"時間配分は演習で慣れたペースを維持し、見直し用に5〜10分を確保できるよう調整してください。\",\n"
    r"    \)\n",
    re.MULTILINE,
)

TIMELINE_NEW = '''def _heading_当日タイムライン(topic: str, _slug: str, _genre: str, _ctx: dict) -> str:
    from tools.guide_content_shared import exam_day_timeline_prose

    return exam_day_timeline_prose(official=OFFICIAL, topic=topic)

'''

ITEMS_OLD = re.compile(
    r"def _heading_持ち物と時間配分\(topic: str, _slug: str, _genre: str, _ctx: dict\) -> str:\n"
    r"    return two_paragraphs\(\n"
    r"        f\"受験票・要項に記載された持ち物（HB程度の黒い鉛筆、消しゴム、必要なら身分証）を前日に準備します。\"\n"
    r"        f\"筆記用具は予備を用意し、スマートフォン・参考書・計算機など禁止物品は持ち込まないでください。\",\n"
    r"        f\"(?:「\{topic\}」の)?解答時間は\{OFFICIAL\}の要項で確認し、1問あたりの目安時間を演習で身につけたペースに合わせます。\"\n"
    r"        f\"見直し時間を確保しつつ、長文問題は設問文の条件を読み落とさないよう注意してください。\",\n"
    r"    \)\n",
    re.MULTILINE,
)

ITEMS_NEW = '''def _heading_持ち物と時間配分(topic: str, _slug: str, _genre: str, _ctx: dict) -> str:
    from tools.guide_content_shared import exam_day_items_and_time_prose

    return exam_day_items_and_time_prose(official=OFFICIAL, topic=topic)

'''

APPLY_OLD = re.compile(
    r"def _heading_申込前チェック\(topic: str, _slug: str, _genre: str, _ctx: dict\) -> str:\n"
    r"    return two_paragraphs\(\n"
    r"        f\"申込前チェック：①受験資格の該当 ②申込期間内 ③受験料の支払 ④受験地の選択 ⑤\"\n"
    r"        f\"公式テキストの版・3分野の学習進捗 ⑥演習問題で弱点分野の把握。\"\n"
    r"        f\"\{topic\}について不明点があれば、申込前に\{OFFICIAL\}で解消してください。\",\n"
    r"        f\"申込直後は、試験日までの週次計画を試験ガイドの学習計画記事を参考に立て直すと、\"\n"
    r"        f\"残り期間を無駄なく使えます。\",\n"
    r"    \)\n",
    re.MULTILINE,
)

APPLY_NEW = '''def _heading_申込前チェック(topic: str, _slug: str, _genre: str, _ctx: dict) -> str:
    from tools.guide_content_shared import application_precheck_prose

    return application_precheck_prose(official=OFFICIAL, topic=topic)

'''


def patch_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    changes: list[str] = []
    new = text

    if FINAL_OLD.search(new):
        new = FINAL_OLD.sub(FINAL_NEW, new, count=1)
        changes.append("final_checklist")

    if TIMELINE_OLD_A.search(new):
        new = TIMELINE_OLD_A.sub(TIMELINE_NEW, new, count=1)
        changes.append("timeline_a")
    elif TIMELINE_OLD_B.search(new):
        new = TIMELINE_OLD_B.sub(TIMELINE_NEW, new, count=1)
        changes.append("timeline_b")

    if ITEMS_OLD.search(new):
        new = ITEMS_OLD.sub(ITEMS_NEW, new, count=1)
        changes.append("items_time")

    if APPLY_OLD.search(new):
        new = APPLY_OLD.sub(APPLY_NEW, new, count=1)
        changes.append("apply_precheck")

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
