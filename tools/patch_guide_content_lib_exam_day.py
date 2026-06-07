#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全サイト guide_content_lib の section_body_for salt 除去と exam-day 見出しマップを追加。"""

from __future__ import annotations

import re
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parents[1] / "tools" / "archive"
LIBS = sorted(ARCHIVE.glob("*_guide_content_lib.py"))

SALT_BLOCK = re.compile(
    r"\n    # 記事ごとに差分を入れて使い回し検知を回避\n"
    r"    salt = \(\n"
    r"        f\"[^\"]*\{topic\}の「\{heading\}」では、\"\n"
    r"        f\"公式テキスト該当箇所に付箋を付けながら読み、演習で同テーマの設問を1問以上解いて確認してください。\"\n"
    r"    \)\n"
    r"    body = two_paragraphs\(body, salt\)\n",
    re.MULTILINE,
)

REPLACEMENT = (
    '\n    tail = f"{topic}の「{heading}」は{OFFICIAL}と演習解説で必ず照合してください。"\n'
    "    return ensure_min(body, 180, tail)"
)

EISEI2SHU_TAIL = re.compile(
    r"return ensure_min\(body, 180, f\"\{topic\}の要点は演習解説と\{OFFICIAL\}で必ず照合してください。\"\)"
)

EXAM_DAY_FUNCTIONS = '''

def _heading_直前絞り込み見出し(topic: str, slug: str, genre: str, ctx: dict) -> str:
    return _heading_直前期絞り込み(topic, slug, genre, ctx)


def _heading_最終確認リスト(topic: str, _slug: str, _genre: str, _ctx: dict) -> str:
    return two_paragraphs(
        f"試験前日までに、{OFFICIAL}の受験要項と受験票で{topic}を最終確認してください。"
        f"持ち物（鉛筆・消しゴム・身分証など）、会場・開始時刻、禁止物品の有無をチェックリストに書き出します。",
        f"学習面では新しい教材を増やさず、誤答ノートと頻出用語だけを短時間で見直します。"
        f"睡眠を優先し、当日朝のルートと所要時間も前日に確定しておくと安心です。",
    )


def _heading_当日タイムライン(topic: str, _slug: str, _genre: str, _ctx: dict) -> str:
    return two_paragraphs(
        f"「{topic}」の当日は、起床から会場到着（開始30分前目安）、受付、着席、解答、退場までの流れを想定して行動します。"
        f"前日準備した持ち物をそのまま持参し、会場到着後は係員の指示に従ってください。",
        "開始直前は長時間の暗記より、呼吸を整えて問題文を最後まで読む習慣を意識します。"
        "時間配分は演習で慣れたペースを維持し、見直し用に5〜10分を確保できるよう調整してください。",
    )


def _heading_持ち物と時間配分(topic: str, _slug: str, _genre: str, _ctx: dict) -> str:
    return two_paragraphs(
        f"受験票・要項に記載された持ち物（HB程度の黒い鉛筆、消しゴム、必要なら身分証）を前日に準備します。"
        f"筆記用具は予備を用意し、スマートフォン・参考書・計算機など禁止物品は持ち込まないでください。",
        f"「{topic}」の解答時間は{OFFICIAL}の要項で確認し、1問あたりの目安時間を演習で身につけたペースに合わせます。"
        f"見直し時間を確保しつつ、長文問題は設問文の条件を読み落とさないよう注意してください。",
    )


def _heading_メンタルトラブル(topic: str, _slug: str, _genre: str, _ctx: dict) -> str:
    return two_paragraphs(
        f"当日の不安や体調不良は、深呼吸・水分補給・会場係員への相談で対処します。"
        f"「{topic}」で会場トラブル（座席、マークシート、筆記用具など）が起きたら早めに係員へ声をかけてください。",
        f"交通遅延が心配な場合は、前日までに会場周辺のルートと予備経路を調べ、"
        f"開始時刻の30分前到着を目安に余裕を持った行動計画を立ててください。",
    )

'''

HEADING_MAP_ENTRIES = '''
    "直前1〜2週間の絞り込み": _heading_直前絞り込み見出し,
    "最終確認リスト": _heading_最終確認リスト,
    "当日のタイムライン": _heading_当日タイムライン,
    "持ち物と時間配分": _heading_持ち物と時間配分,
    "メンタル・トラブル対応": _heading_メンタルトラブル,'''


def patch_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    changes: list[str] = []
    new = text

    if "body = two_paragraphs(body, salt)" in new:
        new = SALT_BLOCK.sub("\n", new)
        if 'tail = f"{topic}の「{heading}」' not in new:
            new = re.sub(
                r"    return ensure_min\(body, 180, f\"\{topic\}の要点は演習解説と\{OFFICIAL\}で必ず照合してください。\"\)",
                REPLACEMENT.strip(),
                new,
                count=1,
            )
        changes.append("removed salt")

    if "def section_body_for" in new and EISEI2SHU_TAIL.search(new) and "tail = f" not in new:
        new = EISEI2SHU_TAIL.sub(
            'tail = f"{topic}の「{heading}」は{OFFICIAL}と演習解説で必ず照合してください。"\n'
            "    return ensure_min(body, 180, tail)",
            new,
            count=1,
        )
        changes.append("eisei2shu-style tail")

    if "_heading_最終確認リスト" not in new and "_heading_直前期絞り込み" in new:
        anchor = "def _heading_制度改定"
        if anchor in new:
            new = new.replace(anchor, EXAM_DAY_FUNCTIONS.lstrip("\n") + anchor, 1)
            changes.append("exam-day functions")

    if '"直前1〜2週間の絞り込み"' not in new and "_heading_直前絞り込み見出し" in new:
        new = re.sub(
            r'(\n    "おすすめの学習順": [^\n]+\n)(}\n\n\ndef topic_from_stub)',
            r"\1" + HEADING_MAP_ENTRIES + r"\2",
            new,
            count=1,
        )
        if '"直前1〜2週間の絞り込み"' in new:
            changes.append("exam-day map")

    if new != text:
        path.write_text(new, encoding="utf-8")
    return changes


def main() -> int:
    for path in LIBS:
        if path.name == "eisei1shu_guide_content_lib.py":
            print(f"{path.name}: skip (already patched)")
            continue
        ch = patch_file(path)
        print(f"{path.name}: {ch or 'unchanged'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
