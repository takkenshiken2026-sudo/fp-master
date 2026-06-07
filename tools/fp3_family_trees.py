#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 親族関係図（公表過去問PDFと同一構造）。"""

from __future__ import annotations

# layout: svg — tools/fp3_genogram.py が公表PDFレイアウトを SVG で描画
# 各 diagram の nodes / edges は PDF（j3_YYYY05_q.pdf 問18・19）に合わせた座標

FP3_FAMILY_TREES: dict[str, dict] = {
    # 2024 問18: 光貴×—妙子※ → 吉春・龍子・森隆男(被相続人)—綾子
    "fp3-jitsugi-202405-q018": {
        "type": "family_tree",
        "layout": "svg",
        "title": "親族関係図",
        "view_w": 500,
        "view_h": 200,
        "footnotes": [
            "※妙子さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "nodes": [
            {"id": "ko", "name": "光貴", "deceased": True, "x": 48, "y": 20},
            {"id": "ta", "name": "妙子", "suffix": "※", "x": 168, "y": 22},
            {"id": "yo", "name": "吉春", "x": 55, "y": 118},
            {"id": "ry", "name": "龍子", "x": 175, "y": 118},
            {"id": "mo", "name": "森 隆男", "role": "decedent", "sub": "（被相続人）", "x": 295, "y": 108},
            {"id": "ay", "name": "綾子", "x": 405, "y": 118},
        ],
        "edges": [
            {"type": "marriage", "a": "ko", "b": "ta"},
            {"type": "parent_bus", "from": ("ko", "ta"), "to": ["yo", "ry", "mo"]},
            {"type": "marriage", "a": "mo", "b": "ay"},
        ],
    },
    # 2024 問19: 藤田信二—良枝 → 咲江・桜子
    "fp3-jitsugi-202405-q019": {
        "type": "family_tree",
        "layout": "svg",
        "title": "親族関係図",
        "view_w": 360,
        "view_h": 160,
        "footnotes": [],
        "nodes": [
            {"id": "fu", "name": "藤田 信二", "role": "decedent", "sub": "（被相続人）", "x": 55, "y": 18},
            {"id": "yo", "name": "良枝", "x": 195, "y": 28},
            {"id": "sa", "name": "咲江", "x": 95, "y": 118},
            {"id": "sk", "name": "桜子", "x": 245, "y": 118},
        ],
        "edges": [
            {"type": "marriage", "a": "fu", "b": "yo"},
            {"type": "parent_bus", "from": ("fu", "yo"), "to": ["sa", "sk"]},
        ],
    },
    # 2025 問18: 森隆男—綾子 → 幹夫※・夏帆・×—武志→真奈（麗子・寛太なし）
    "fp3-jitsugi-202505-q018": {
        "type": "family_tree",
        "layout": "svg",
        "title": "親族関係図",
        "view_w": 480,
        "view_h": 210,
        "footnotes": [
            "※幹夫さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "nodes": [
            {"id": "mo", "name": "森 隆男", "role": "decedent", "sub": "（被相続人）", "x": 130, "y": 18},
            {"id": "ay", "name": "綾子", "x": 270, "y": 28},
            {"id": "mi", "name": "幹夫", "suffix": "※", "x": 55, "y": 118},
            {"id": "ka", "name": "夏帆", "x": 200, "y": 118},
            {"id": "dx", "deceased": True, "x": 310, "y": 108},
            {"id": "ta", "name": "武志", "x": 400, "y": 118},
            {"id": "ma", "name": "真奈", "x": 355, "y": 178},
        ],
        "edges": [
            {"type": "marriage", "a": "mo", "b": "ay"},
            {"type": "parent_bus", "from": ("mo", "ay"), "to": ["mi", "ka", "dx"]},
            {"type": "marriage", "a": "dx", "b": "ta"},
            {"type": "child", "from": ("dx", "ta"), "to": "ma"},
        ],
    },
    # 2025 問19: 藤田信二—良枝 → 咲江・誠也・桜子
    "fp3-jitsugi-202505-q019": {
        "type": "family_tree",
        "layout": "svg",
        "title": "親族関係図",
        "view_w": 420,
        "view_h": 160,
        "footnotes": [],
        "nodes": [
            {"id": "fu", "name": "藤田 信二", "role": "decedent", "sub": "（被相続人）", "x": 55, "y": 18},
            {"id": "yo", "name": "良枝", "x": 215, "y": 28},
            {"id": "sa", "name": "咲江", "x": 55, "y": 118},
            {"id": "se", "name": "誠也", "x": 175, "y": 118},
            {"id": "sk", "name": "桜子", "x": 295, "y": 118},
        ],
        "edges": [
            {"type": "marriage", "a": "fu", "b": "yo"},
            {"type": "parent_bus", "from": ("fu", "yo"), "to": ["sa", "se", "sk"]},
        ],
    },
    # 2026 問18: 森隆男—綾子 → 幹夫※—麗子→寛太・夏帆・×—武志→真奈
    "fp3-jitsugi-202605-q018": {
        "type": "family_tree",
        "layout": "svg",
        "title": "親族関係図",
        "view_w": 500,
        "view_h": 220,
        "footnotes": [
            "※幹夫さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "nodes": [
            {"id": "mo", "name": "森 隆男", "role": "decedent", "sub": "（被相続人）", "x": 140, "y": 18},
            {"id": "ay", "name": "綾子", "x": 280, "y": 28},
            {"id": "mi", "name": "幹夫", "suffix": "※", "x": 35, "y": 118},
            {"id": "re", "name": "麗子", "x": 125, "y": 118},
            {"id": "ka", "name": "夏帆", "x": 230, "y": 118},
            {"id": "dx", "deceased": True, "x": 330, "y": 108},
            {"id": "ta", "name": "武志", "x": 420, "y": 118},
            {"id": "ka2", "name": "寛太", "x": 80, "y": 188},
            {"id": "ma", "name": "真奈", "x": 375, "y": 188},
        ],
        "edges": [
            {"type": "marriage", "a": "mo", "b": "ay"},
            {"type": "parent_bus", "from": ("mo", "ay"), "to": ["mi", "ka", "dx"]},
            {"type": "marriage", "a": "mi", "b": "re"},
            {"type": "child", "from": ("mi", "re"), "to": "ka2"},
            {"type": "marriage", "a": "dx", "b": "ta"},
            {"type": "child", "from": ("dx", "ta"), "to": "ma"},
        ],
    },
    # 2026 問19: 藤田信二—良枝 → 咲江・誠也・桜子※
    "fp3-jitsugi-202605-q019": {
        "type": "family_tree",
        "layout": "svg",
        "title": "親族関係図",
        "view_w": 420,
        "view_h": 160,
        "footnotes": [
            "※桜子さんは期限内に家庭裁判所で手続きを行い、適法に相続を放棄した。",
        ],
        "nodes": [
            {"id": "fu", "name": "藤田 信二", "role": "decedent", "sub": "（被相続人）", "x": 55, "y": 18},
            {"id": "yo", "name": "良枝", "x": 215, "y": 28},
            {"id": "sa", "name": "咲江", "x": 55, "y": 118},
            {"id": "se", "name": "誠也", "x": 175, "y": 118},
            {"id": "sk", "name": "桜子", "suffix": "※", "x": 295, "y": 118},
        ],
        "edges": [
            {"type": "marriage", "a": "fu", "b": "yo"},
            {"type": "parent_bus", "from": ("fu", "yo"), "to": ["sa", "se", "sk"]},
        ],
    },
}


def source_id_to_diagram_id(source_id: str) -> str:
    """fp3_202405_q018 → fp3-jitsugi-202405-q018"""
    return source_id.replace("fp3_", "fp3-jitsugi-").replace("_", "-")
