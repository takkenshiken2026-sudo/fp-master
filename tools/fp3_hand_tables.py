#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 — 公表PDFに合わせて手整備した資料表（パーサーでは再現しにくいもの）。"""

from __future__ import annotations

from typing import Any

from tools.fp3_family_trees import source_id_to_diagram_id


def _bs_template() -> dict[str, Any]:
    return {
        "type": "fp_table",
        "title": "山本家のバランスシート",
        "unit": "（単位：万円）",
        "dense": True,
        "headers": ["［資産］", "×××", "［負債］", "×××"],
        "rows": [
            ["", "", "負債合計", "×××"],
            ["", "", "［純資産］", "（ ア ）"],
            ["資産合計", "×××", "負債・純資産合計", "×××"],
        ],
    }


def _assets_table(title: str, rows: list[list[str]]) -> dict[str, Any]:
    return {
        "type": "fp_table",
        "title": title,
        "unit": "（単位：万円）",
        "dense": True,
        "rows": rows,
    }


FP3_HAND_MATERIALS: dict[str, list[dict[str, Any]]] = {
    "fp3-jitsugi-202405-q003": [
        _assets_table(
            "保有財産（時価）",
            [
                ["金融資産", ""],
                ["普通預金", "４００"],
                ["定期預金", "８００"],
                ["投資信託", "１００"],
                ["上場株式", "２００"],
                ["生命保険（解約返戻金相当額）", "８０"],
                ["不動産（自宅マンション）", "３,０００"],
                ["［負債残高］", ""],
                ["住宅ローン（自宅マンション）", "２,２００万円"],
            ],
        ),
        _bs_template(),
    ],
    "fp3-jitsugi-202505-q003": [
        _assets_table(
            "保有財産（時価）",
            [
                ["金融資産", ""],
                ["普通預金", "３００"],
                ["定期預金", "１,５００"],
                ["投資信託", "２００"],
                ["生命保険（解約返戻金相当額）", "１００"],
                ["自動車", "１５０"],
                ["不動産（自宅マンション）", "４,０００"],
                ["［負債残高］", ""],
                ["住宅ローン（自宅マンション）", "３,２００万円"],
            ],
        ),
        _bs_template(),
    ],
    "fp3-jitsugi-202605-q003": [
        _assets_table(
            "保有財産（時価）",
            [
                ["金融資産", ""],
                ["普通預金", "３００"],
                ["定期預金", "１,０００"],
                ["有価証券", "２００"],
                ["投資信託", "１００"],
                ["生命保険（解約返戻金相当額）", "８０"],
                ["不動産（自宅マンション）", "３,８００"],
                ["［負債残高］", ""],
                ["住宅ローン（自宅マンション）", "２,８００万円"],
            ],
        ),
        _bs_template(),
    ],
}


def hand_material_sections(source_id: str) -> list[dict[str, Any]] | None:
    from tools.fp3_material_tables import material_sections_for

    did = source_id_to_diagram_id(source_id)
    material = material_sections_for(source_id)
    if material is not None:
        return material
    sections = FP3_HAND_MATERIALS.get(did)
    if sections:
        return [dict(s) for s in sections]
    return None
