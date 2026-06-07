#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 キャッシュフロー表の構造化データ（試験資料の列レイアウトに合わせた手整備）。"""

from __future__ import annotations

from typing import Any

# 列: ラベル(2) + 基準年 + 1〜4年後 + 変動率 = 8列
# セルは str または {"text": ..., "colspan": n, "rowspan": n, "class": ...}

def _cf(
    title: str,
    *,
    unit: str = "（単位：万円）",
    rows: list[list[Any]],
    notes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "type": "fp_table",
        "layout": "cashflow",
        "title": title,
        "unit": unit,
        "rows": rows,
        "notes": notes or [],
    }


def _hdr() -> list[Any]:
    return [
        {"text": "経過年数", "colspan": 2, "class": "cf-corner"},
        {"text": "基準年", "class": "cf-year-head"},
        {"text": "１年後", "class": "cf-year-head"},
        {"text": "２年後", "class": "cf-year-head"},
        {"text": "３年後", "class": "cf-year-head"},
        {"text": "４年後", "class": "cf-year-head"},
        "",
    ]


def _family_hdr() -> list[Any]:
    return [
        {"text": "家族・", "class": "cf-label"},
        {"text": "年齢", "class": "cf-label"},
        "",
        "",
        "",
        "",
        "",
        "",
    ]


def _member(name: str, role: str, ages: list[str]) -> list[Any]:
    return [name, role, *ages, ""]


def _section(label: str) -> list[Any]:
    return [{"text": label, "colspan": 8, "class": "cf-section"}]


def _amount(label: str, rate: str, years: list[str]) -> list[Any]:
    while len(years) < 5:
        years.append("")
    return [label, "", *years[:5], rate]


FP3_CASHFLOW_TABLES: dict[str, dict[str, Any]] = {
    "fp3-jitsugi-202405-q002": _cf(
        "東条家のキャッシュフロー表",
        rows=[
            _hdr(),
            _family_hdr(),
            _member("東条 義雄", "本人", ["３７歳", "３８歳", "３９歳", "４０歳", "４１歳"]),
            _member("　　八重", "妻", ["３５歳", "３６歳", "３７歳", "３８歳", "３９歳"]),
            _member("　　泰彦", "長男", ["　７歳", "　８歳", "　９歳", "１０歳", "１１歳"]),
            [
                {"text": "ライフイベント", "colspan": 2, "class": "cf-label"},
                "",
                {"text": "泰彦\n小学校入学", "class": "cf-event"},
                "",
                {"text": "海外旅行", "class": "cf-event"},
                "",
                {"text": "変動率", "class": "cf-rate-head"},
            ],
            _section("収入"),
            _amount("給与収入（本人）", "１％", ["４３０", "", "", "", ""]),
            _amount("給与収入（妻）", "－", ["－", "５０", "７０", "７０", "７０"]),
            _amount("収入合計", "－", ["－", "４８０", "５０４", "５０９", ""]),
            _section("支出"),
            _amount("基本生活費", "２％", ["２４０", "", "", "", "（ ア ）"]),
            _amount("住宅関連費", "－", ["１５６", "１５６", "１５６", "１５６", "１５６"]),
            _amount("教育費", "－", ["５０", "４０", "４０", "５０", "６０"]),
            _amount("保険料", "－", ["１８", "１８", "１８", "１８", "１８"]),
            _amount("一時的支出", "－", ["－", "", "", "１２０", ""]),
            _amount("その他支出", "－", ["１２", "１２", "１２", "１２", "１２"]),
            _amount("支出合計", "－", ["４７６", "４７１", "５９６", "４９１", ""]),
            _amount("年間収支", "", ["", "（ イ ）", "２２", "", "１１"]),
            _amount("金融資産残高", "１％", ["６８０", "", "６４０", "（ ウ ）", ""]),
        ],
        notes=[
            "※年齢および金融資産残高は各年１２月３１日現在のものとする。",
            "※給与収入は可処分所得で記載している。",
            "※記載されている数値は正しいものとする。また、問題作成の都合上、一部を空欄にしてある。",
        ],
    ),
    "fp3-jitsugi-202505-q002": _cf(
        "東条家のキャッシュフロー表",
        rows=[
            _hdr(),
            _family_hdr(),
            _member("東条 義雄", "本人", ["３１歳", "３２歳", "３３歳", "３４歳", "３５歳"]),
            _member("　　八重", "妻", ["３０歳", "３１歳", "３２歳", "３３歳", "３４歳"]),
            _member("　　泰彦", "長男", ["　３歳", "　４歳", "　５歳", "　６歳", "　７歳"]),
            [
                {"text": "ライフイベント", "colspan": 2, "class": "cf-label"},
                "",
                {"text": "自動車\n購入", "class": "cf-event"},
                {"text": "泰彦\n小学校入学", "class": "cf-event"},
                "",
                "",
                {"text": "変動率", "class": "cf-rate-head"},
            ],
            _section("収入"),
            _amount("給与収入（本人）", "１％", ["４３０", "", "", "", ""]),
            _amount("給与収入（妻）", "１％", ["３６０", "", "", "", ""]),
            _amount("収入合計", "－", ["７９０", "", "", "", ""]),
            _section("支出"),
            _amount("基本生活費", "２％", ["２８０", "", "", "", "（ ア ）"]),
            _amount("住宅関連費", "－", ["１８０", "１８０", "１８０", "１８０", "１８０"]),
            _amount("教育費", "－", ["１２", "１５", "１５", "１５", "２４"]),
            _amount("保険料", "－", ["２４", "２４", "２４", "２４", "２４"]),
            _amount("一時的支出", "－", ["", "３００", "", "２０", ""]),
            _amount("その他支出", "－", ["４８", "", "", "", ""]),
            _amount("支出合計", "－", ["５４４", "", "８５８", "", ""]),
            _amount("年間収支", "", ["", "２４５", "（ イ ）", "", ""]),
            _amount("金融資産残高", "１％", ["６８０", "（ ウ ）", "", "", ""]),
        ],
        notes=[
            "※年齢および金融資産残高は各年１２月３１日現在のものとする。",
            "※給与収入は可処分所得で記載している。",
            "※記載されている数値は正しいものとする。また、問題作成の都合上、一部を空欄にしてある。",
        ],
    ),
    "fp3-jitsugi-202605-q002": _cf(
        "東条家のキャッシュフロー表",
        rows=[
            _hdr(),
            _family_hdr(),
            _member("東条 義雄", "本人", ["３１歳", "３２歳", "３３歳", "３４歳", "３５歳"]),
            _member("　　八重", "妻", ["３０歳", "３１歳", "３２歳", "３３歳", "３４歳"]),
            _member("　　泰彦", "長男", ["　５歳", "　６歳", "　７歳", "　８歳", "　９歳"]),
            [
                {"text": "ライフイベント", "colspan": 2, "class": "cf-label"},
                "",
                {"text": "泰彦私立\n小学校入学", "class": "cf-event"},
                "",
                {"text": "海外旅行", "class": "cf-event"},
                "",
                {"text": "変動率", "class": "cf-rate-head"},
            ],
            _section("収入"),
            _amount("給与収入（本人）", "１％", ["６３０", "", "", "", ""]),
            _amount("給与収入（妻）", "－", ["８０", "８０", "８０", "８０", "８０"]),
            _amount("収入合計", "－", ["７１０", "７１６", "", "", ""]),
            _section("支出"),
            _amount("基本生活費", "２％", ["２６０", "", "", "（ ア ）", ""]),
            _amount("住宅関連費", "－", ["１８０", "１８０", "１８０", "１８０", "１８０"]),
            _amount("教育費", "－", ["２０", "２０", "２６０", "１６０", "１６０"]),
            _amount("保険料", "－", ["２４", "２４", "２４", "２４", "２４"]),
            _amount("一時的支出", "－", ["", "", "１００", "", ""]),
            _amount("その他支出", "－", ["２４", "２４", "２４", "２４", "２４"]),
            _amount("支出合計", "－", ["５０８", "５１３", "", "", ""]),
            _amount("年間収支", "", ["", "（ イ ）", "", "", "６７"]),
            _amount("金融資産残高", "１％", ["６８０", "", "８３７", "（ ウ ）", ""]),
        ],
        notes=[
            "※年齢および金融資産残高は各年１２月３１日現在のものとする。",
            "※給与収入は可処分所得で記載している。",
            "※記載されている数値は正しいものとする。また、問題作成の都合上、一部を空欄にしてある。",
            "※変動率が記載されている各項目の計算に当たっては基準年の金額に変動率を適用し、端数を残して算出するものとするが、表中に記入の際に万円未満を四捨五入すること。ただし、金融資産残高は各年ごとに端数を残さず、万円未満を四捨五入のうえ計算すること。",
            "※収入合計と支出合計、年間収支は表中に記載の整数または記入すべき整数を使用して計算すること。",
        ],
    ),
}


def source_id_to_diagram_id(source_id: str) -> str:
    return source_id.replace("fp3_", "fp3-jitsugi-").replace("_", "-")


def get_cashflow_table(source_id: str) -> dict[str, Any] | None:
    return FP3_CASHFLOW_TABLES.get(source_id_to_diagram_id(source_id))
