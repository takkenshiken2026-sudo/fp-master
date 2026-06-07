#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 — 土地利用・路線価の配置図（公表PDFレイアウトの SVG）。"""

from __future__ import annotations

import html

FONT = "YuMincho, 'Hiragino Mincho ProN', 'Noto Serif JP', serif"
LINE = 1.2


def _esc(s: str) -> str:
    return html.escape(s or "")


def _dim_bracket_h(x1: float, x2: float, y: float, label: str) -> str:
    mid = (x1 + x2) / 2
    return (
        f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#111" stroke-width="{LINE}"/>'
        f'<line x1="{x1}" y1="{y - 4}" x2="{x1}" y2="{y + 4}" stroke="#111" stroke-width="{LINE}"/>'
        f'<line x1="{x2}" y1="{y - 4}" x2="{x2}" y2="{y + 4}" stroke="#111" stroke-width="{LINE}"/>'
        f'<text x="{mid}" y="{y - 8}" text-anchor="middle" font-family="{FONT}" font-size="12">{_esc(label)}</text>'
    )


def _dim_bracket_v(x: float, y1: float, y2: float, label: str) -> str:
    mid = (y1 + y2) / 2
    return (
        f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="#111" stroke-width="{LINE}"/>'
        f'<line x1="{x - 4}" y1="{y1}" x2="{x + 4}" y2="{y1}" stroke="#111" stroke-width="{LINE}"/>'
        f'<line x1="{x - 4}" y1="{y2}" x2="{x + 4}" y2="{y2}" stroke="#111" stroke-width="{LINE}"/>'
        f'<text x="{x - 10}" y="{mid + 4}" text-anchor="end" font-family="{FONT}" font-size="12">{_esc(label)}</text>'
    )


def _road(y_top: float, y_bot: float, x1: float, x2: float, label: str) -> str:
    mid_y = (y_top + y_bot) / 2
    mid_x = (x1 + x2) / 2
    return (
        f'<line x1="{x1}" y1="{y_top}" x2="{x2}" y2="{y_top}" stroke="#111" stroke-width="{LINE}"/>'
        f'<line x1="{x1}" y1="{y_bot}" x2="{x2}" y2="{y_bot}" stroke="#111" stroke-width="{LINE}"/>'
        f'<line x1="{mid_x - 30}" y1="{mid_y}" x2="{mid_x + 30}" y2="{mid_y}" stroke="#111" stroke-width="1"/>'
        f'<line x1="{mid_x - 30}" y1="{mid_y - 3}" x2="{mid_x - 30}" y2="{mid_y + 3}" stroke="#111" stroke-width="1"/>'
        f'<line x1="{mid_x + 30}" y1="{mid_y - 3}" x2="{mid_x + 30}" y2="{mid_y + 3}" stroke="#111" stroke-width="1"/>'
        f'<text x="{mid_x}" y="{mid_y + 4}" text-anchor="middle" font-family="{FONT}" font-size="11">{_esc(label)}</text>'
    )


def _info_box(x: float, y: float, w: float, h: float, lines: list[str]) -> str:
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="{LINE}"/>'
    ]
    ty = y + 20
    for line in lines:
        parts.append(
            f'<text x="{x + 10}" y="{ty}" font-family="{FONT}" font-size="12">{_esc(line)}</text>'
        )
        ty += 18
    return "".join(parts)


def _svg_wrap(view_w: int, view_h: int, inner: str, *, title: str = "") -> str:
    cap = f'<figcaption class="q-materials-title">{_esc(title)}</figcaption>' if title else ""
    return (
        '<figure class="q-land-diagram q-land-diagram--svg" role="group">'
        f"{cap}"
        f'<div class="q-land-svg-wrap"><svg class="q-land-svg" viewBox="0 0 {view_w} {view_h}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{_esc(title or "土地利用図")}">'
        f'<rect width="100%" height="100%" fill="#fff"/>'
        f"{inner}</svg></div></figure>"
    )


def render_202405_q009() -> str:
    x, y, w, h = 40, 30, 150, 75
    inner = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="{LINE}"/>'
        f'<text x="{x + w / 2}" y="{y + h / 2 + 5}" text-anchor="middle" font-family="{FONT}" font-size="14">４５０ｍ²</text>'
        + _dim_bracket_h(x, x + w, y - 14, "３０ｍ")
        + _dim_bracket_v(x + w + 14, y, y + h, "１５ｍ")
        + _road(y + h, y + h + 22, 20, 220, "幅員　６ｍ　市道")
        + _info_box(
            260,
            28,
            220,
            96,
            [
                "・ 近隣商業地域",
                "・ 指定建蔽率　６０％",
                "・ 指定容積率　４００％",
                "・ 前面道路の幅員に対する法定乗数　６／１０",
            ],
        )
    )
    return _svg_wrap(500, 150, inner, title="資料")


def render_202505_q009() -> str:
    note = (
        "※甲土地・乙土地が面する道路は建築基準法第４２条第２項に該当する道路で、"
        "甲土地・乙土地はともにセットバックを要する。また、道路の中心線は現況道路の中心に位置するものとする。"
        "なお、特定行政庁が指定する幅員６ｍ指定区域ではない。"
    )
    inner = (
        f'<text x="10" y="16" font-family="{FONT}" font-size="10">{_esc(note)}</text>'
        f'<rect x="50" y="50" width="70" height="55" fill="none" stroke="#111" stroke-width="{LINE}"/>'
        f'<text x="85" y="82" text-anchor="middle" font-family="{FONT}" font-size="12">（甲土地）</text>'
        f'<text x="85" y="98" text-anchor="middle" font-family="{FONT}" font-size="11">１８０ｍ²</text>'
        + _dim_bracket_h(50, 120, 38, "１０ｍ")
        + _dim_bracket_v(128, 50, 105, "１８ｍ")
        + _road(105, 127, 30, 200, "幅員　３ｍ　市道")
        + f'<rect x="140" y="50" width="70" height="55" fill="none" stroke="#111" stroke-width="{LINE}"/>'
        + f'<text x="175" y="82" text-anchor="middle" font-family="{FONT}" font-size="12">（乙土地）</text>'
    )
    return _svg_wrap(520, 145, inner, title="資料")


def render_202505_q020() -> str:
    x, y, w, h = 60, 25, 120, 96
    inner = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="{LINE}"/>'
        f'<text x="{x + w / 2}" y="{y + h / 2 + 5}" text-anchor="middle" font-family="{FONT}" font-size="14">１８０ｍ²</text>'
        + _dim_bracket_h(x, x + w, y - 14, "１５ｍ")
        + _dim_bracket_v(x - 14, y, y + h, "１２ｍ")
        + _road(y + h, y + h + 24, 40, 200, "２４０Ｃ")
    )
    return _svg_wrap(260, 160, inner)


def render_202605_q009() -> str:
    x, y, w, h = 40, 30, 150, 75
    inner = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="{LINE}"/>'
        f'<text x="{x + w / 2}" y="{y + h / 2 + 5}" text-anchor="middle" font-family="{FONT}" font-size="14">３００ｍ²</text>'
        + _dim_bracket_h(x, x + w, y - 14, "３０ｍ")
        + _dim_bracket_v(x + w + 14, y, y + h, "１５ｍ")
        + _road(y + h, y + h + 22, 20, 220, "幅員　６ｍ　市道")
        + _info_box(
            260,
            28,
            200,
            78,
            [
                "・ 準工業地域",
                "・ 指定建蔽率　８０％",
                "・ 指定容積率　４００％",
                "・ 敷地面積　３００ｍ²",
            ],
        )
    )
    return _svg_wrap(480, 150, inner, title="資料")


RENDERERS = {
    "fp3-jitsugi-202405-q009": render_202405_q009,
    "fp3-jitsugi-202505-q009": render_202505_q009,
    "fp3-jitsugi-202505-q020": render_202505_q020,
    "fp3-jitsugi-202605-q009": render_202605_q009,
}


def land_diagram_section(diagram_id: str) -> dict | None:
    if diagram_id in RENDERERS:
        return {"type": "land_diagram", "layout": "svg", "diagram_id": diagram_id}
    return None


def render_land_diagram(data: dict) -> str:
    did = str(data.get("diagram_id") or "")
    fn = RENDERERS.get(did)
    if not fn:
        return ""
    return fn()
