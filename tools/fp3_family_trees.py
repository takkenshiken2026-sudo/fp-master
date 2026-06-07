#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 親族関係図の構造化データ（試験解説・資料テキストに基づく手整備）。"""

from __future__ import annotations

# layout: 上から下へ行、各行は左から人物ボックス
# join: "marriage" で横並び配偶者、"sibling_group" で兄弟姉妹行

FP3_FAMILY_TREES: dict[str, dict] = {
    "fp3-jitsugi-202405-q018": {
        "type": "family_tree",
        "title": "親族関係図",
        "footnotes": [
            "※妙子さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "rows": [
            [{"name": "妙子", "suffix": "※"}],
            [
                {"name": "森 隆男", "sub": "（被相続人）", "role": "decedent"},
                {"name": "綾子", "join": "marriage"},
            ],
            [
                {"name": "龍子"},
                {"name": "元貴"},
                {"name": "吉春", "sub": "（すでに死亡）", "role": "deceased"},
            ],
        ],
    },
    "fp3-jitsugi-202405-q019": {
        "type": "family_tree",
        "title": "親族関係図",
        "footnotes": [],
        "rows": [
            [
                {"name": "良枝"},
                {"name": "藤田 信二", "sub": "（被相続人）", "role": "decedent", "join": "marriage"},
            ],
            [{"name": "桜子"}, {"name": "咲江"}],
        ],
    },
    "fp3-jitsugi-202505-q018": {
        "type": "family_tree",
        "title": "親族関係図",
        "footnotes": [
            "※幹夫さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "rows": [
            [{"name": "綾子"}],
            [{"name": "森 隆男", "sub": "（被相続人）", "role": "decedent"}],
            [
                {"name": "夏帆"},
                {
                    "name": "（子）",
                    "sub": "すでに死亡",
                    "role": "deceased",
                    "below": [{"name": "真奈", "sub": "代襲相続"}],
                },
            ],
            [
                {"name": "武志"},
                {"name": "百合"},
                {"name": "幹夫", "suffix": "※"},
            ],
        ],
    },
    "fp3-jitsugi-202505-q019": {
        "type": "family_tree",
        "title": "親族関係図",
        "footnotes": [],
        "rows": [
            [
                {"name": "良枝"},
                {"name": "藤田 信二", "sub": "（被相続人）", "role": "decedent", "join": "marriage"},
            ],
            [{"name": "誠也"}, {"name": "桜子"}, {"name": "咲江"}],
        ],
    },
    "fp3-jitsugi-202605-q018": {
        "type": "family_tree",
        "title": "親族関係図",
        "footnotes": [
            "※幹夫さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "rows": [
            [{"name": "綾子"}],
            [{"name": "森 隆男", "sub": "（被相続人）", "role": "decedent"}],
            [
                {"name": "夏帆"},
                {
                    "name": "（子）",
                    "sub": "すでに死亡",
                    "role": "deceased",
                    "below": [{"name": "真奈", "sub": "代襲相続"}],
                },
            ],
            [
                {"name": "武志"},
                {"name": "百合"},
                {"name": "幹夫", "suffix": "※", "below": [{"name": "寛太"}]},
            ],
        ],
    },
    "fp3-jitsugi-202605-q019": {
        "type": "family_tree",
        "title": "親族関係図",
        "footnotes": [
            "※桜子さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "rows": [
            [{"name": "麗子"}],
            [
                {"name": "良枝"},
                {"name": "藤田 信二", "sub": "（被相続人）", "role": "decedent", "join": "marriage"},
            ],
            [
                {"name": "誠也"},
                {"name": "桜子", "suffix": "※"},
                {"name": "咲江"},
            ],
        ],
    },
}


def source_id_to_diagram_id(source_id: str) -> str:
    """fp3_202405_q018 → fp3-jitsugi-202405-q018"""
    return source_id.replace("fp3_", "fp3-jitsugi-").replace("_", "-")
