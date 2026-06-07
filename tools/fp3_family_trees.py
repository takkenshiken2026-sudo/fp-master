#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 親族関係図（公表過去問PDFに合わせた構造化データ）。"""

from __future__ import annotations

# layout: genogram — tools/fp3_genogram.py で HTML 化
# spouse: 被相続人を左、配偶者を右（PDF と同じ）
# child_units: 子世代（単独 person または spouse + descendants）

FP3_FAMILY_TREES: dict[str, dict] = {
    "fp3-jitsugi-202405-q018": {
        "type": "family_tree",
        "layout": "genogram",
        "title": "親族関係図",
        "footnotes": [
            "※妙子さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "above": {"name": "妙子", "suffix": "※"},
        "spouse": {
            "left": {"name": "森 隆男", "sub": "（被相続人）", "role": "decedent"},
            "right": {"name": "綾子"},
        },
        "child_units": [
            {"person": {"name": "龍子"}},
            {"person": {"name": "元貴"}},
            {"person": {"name": "吉春", "sub": "（すでに死亡）", "role": "deceased"}},
        ],
    },
    "fp3-jitsugi-202405-q019": {
        "type": "family_tree",
        "layout": "genogram",
        "title": "親族関係図",
        "footnotes": [],
        "spouse": {
            "left": {"name": "藤田 信二", "sub": "（被相続人）", "role": "decedent"},
            "right": {"name": "良枝"},
        },
        "child_units": [
            {"person": {"name": "桜子"}},
            {"person": {"name": "咲江"}},
        ],
    },
    "fp3-jitsugi-202505-q018": {
        "type": "family_tree",
        "layout": "genogram",
        "title": "親族関係図",
        "footnotes": [
            "※幹夫さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "spouse": {
            "left": {"name": "森 隆男", "sub": "（被相続人）", "role": "decedent"},
            "right": {"name": "綾子"},
        },
        "child_units": [
            {
                "spouse": {
                    "left": {"name": "幹夫", "suffix": "※"},
                    "right": {"name": "麗子"},
                },
            },
            {"person": {"name": "夏帆"}},
            {
                "spouse": {
                    "left": {"role": "deceased", "sub": "（すでに死亡）"},
                    "right": {"name": "武志"},
                },
                "descendants": [{"name": "真奈"}],
            },
        ],
    },
    "fp3-jitsugi-202505-q019": {
        "type": "family_tree",
        "layout": "genogram",
        "title": "親族関係図",
        "footnotes": [],
        "spouse": {
            "left": {"name": "藤田 信二", "sub": "（被相続人）", "role": "decedent"},
            "right": {"name": "良枝"},
        },
        "child_units": [
            {"person": {"name": "誠也"}},
            {"person": {"name": "桜子"}},
            {"person": {"name": "咲江"}},
        ],
    },
    "fp3-jitsugi-202605-q018": {
        "type": "family_tree",
        "layout": "genogram",
        "title": "親族関係図",
        "footnotes": [
            "※幹夫さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "spouse": {
            "left": {"name": "森 隆男", "sub": "（被相続人）", "role": "decedent"},
            "right": {"name": "綾子"},
        },
        "child_units": [
            {
                "spouse": {
                    "left": {"name": "幹夫", "suffix": "※"},
                    "right": {"name": "麗子"},
                },
                "descendants": [{"name": "寛太"}],
            },
            {"person": {"name": "夏帆"}},
            {
                "spouse": {
                    "left": {"role": "deceased", "sub": "（すでに死亡）"},
                    "right": {"name": "武志"},
                },
                "descendants": [{"name": "真奈"}],
            },
        ],
    },
    "fp3-jitsugi-202605-q019": {
        "type": "family_tree",
        "layout": "genogram",
        "title": "親族関係図",
        "footnotes": [
            "※桜子さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "spouse": {
            "left": {"name": "藤田 信二", "sub": "（被相続人）", "role": "decedent"},
            "right": {"name": "良枝"},
        },
        "child_units": [
            {"person": {"name": "咲江"}},
            {"person": {"name": "誠也"}},
            {"person": {"name": "桜子", "suffix": "※"}},
        ],
    },
}


def source_id_to_diagram_id(source_id: str) -> str:
    """fp3_202405_q018 → fp3-jitsugi-202405-q018"""
    return source_id.replace("fp3_", "fp3-jitsugi-").replace("_", "-")
