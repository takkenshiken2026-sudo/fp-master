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
        f'<line x1="{mid_x - 36}" y1="{mid_y}" x2="{mid_x + 36}" y2="{mid_y}" stroke="#111" stroke-width="1"/>'
        f'<line x1="{mid_x - 36}" y1="{mid_y - 3}" x2="{mid_x - 36}" y2="{mid_y + 3}" stroke="#111" stroke-width="1"/>'
        f'<line x1="{mid_x + 36}" y1="{mid_y - 3}" x2="{mid_x + 36}" y2="{mid_y + 3}" stroke="#111" stroke-width="1"/>'
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


def _note_box(x: float, y: float, w: float, lines: list[str], *, font_size: int = 10) -> str:
    line_h = font_size + 5
    h = line_h * len(lines) + 14
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="{LINE}"/>'
    ]
    ty = y + font_size + 8
    for line in lines:
        parts.append(
            f'<text x="{x + 8}" y="{ty}" font-family="{FONT}" font-size="{font_size}">{_esc(line)}</text>'
        )
        ty += line_h
    return "".join(parts)


def _material_frame(x: float, y: float, w: float, h: float, inner: str) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="1.5"/>'
        f'<g transform="translate({x},{y})">{inner}</g>'
    )


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
    fx, fy, fw, fh = 8, 8, 484, 132
    x, y, w, h = 32, 24, 150, 75
    plot = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="{LINE}"/>'
        f'<text x="{x + w / 2}" y="{y + h / 2 + 5}" text-anchor="middle" font-family="{FONT}" font-size="14">４５０ｍ²</text>'
        + _dim_bracket_h(x, x + w, y - 14, "３０ｍ")
        + _dim_bracket_v(x + w + 14, y, y + h, "１５ｍ")
        + _road(y + h, y + h + 22, 12, 200, "幅員　６ｍ　市道")
        + _info_box(
            252,
            22,
            210,
            96,
            [
                "・ 近隣商業地域",
                "・ 指定建蔽率　６０％",
                "・ 指定容積率　４００％",
                "・ 前面道路の幅員に対する法定乗数　６／１０",
            ],
        )
    )
    inner = _material_frame(fx, fy, fw, fh, plot)
    return _svg_wrap(500, 148, inner, title="資料")


def render_202505_q009() -> str:
    """公表PDF: 甲土地（上）— 市道 — 乙土地（下）、注記は右側の枠。"""
    fx, fy, fw, fh = 8, 8, 504, 200
    scale = 5.5
    pw, pd = 18 * scale, 10 * scale
    x0, y0 = 36, 20
    road_h = 3 * scale
    y_road = y0 + pd
    y_b = y_road + road_h

    plot = (
        f'<rect x="{x0}" y="{y0}" width="{pw}" height="{pd}" fill="none" stroke="#111" stroke-width="{LINE}"/>'
        f'<text x="{x0 + pw / 2}" y="{y0 + pd / 2 - 4}" text-anchor="middle" font-family="{FONT}" font-size="12">（甲土地）</text>'
        f'<text x="{x0 + pw / 2}" y="{y0 + pd / 2 + 12}" text-anchor="middle" font-family="{FONT}" font-size="11">１８０ｍ²</text>'
        + _dim_bracket_h(x0, x0 + pw, y0 - 12, "１８ｍ")
        + _dim_bracket_v(x0 + pw + 12, y0, y0 + pd, "１０ｍ")
        + _road(y_road, y_road + road_h, x0 - 8, x0 + pw + 8, "幅員　３ｍ　市道")
        + f'<rect x="{x0}" y="{y_b}" width="{pw}" height="{pd}" fill="none" stroke="#111" stroke-width="{LINE}"/>'
        + f'<text x="{x0 + pw / 2}" y="{y_b + pd / 2 + 4}" text-anchor="middle" font-family="{FONT}" font-size="12">（乙土地）</text>'
        + _note_box(
            248,
            16,
            248,
            [
                "※甲土地・乙土地が面する道路は建築基準法第４２条第",
                "２項に該当する道路で、甲土地・乙土地はともにセット",
                "バックを要する。また、道路の中心線は現況道路の中心",
                "に位置するものとする。なお、特定行政庁が指定する幅",
                "員６ｍ指定区域ではない。",
            ],
        )
    )
    inner = _material_frame(fx, fy, fw, fh, plot)
    return _svg_wrap(520, 216, inner, title="資料")


def render_202505_q020() -> str:
    x, y, w, h = 48, 28, 120, 96
    inner = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="{LINE}"/>'
        f'<text x="{x + w / 2}" y="{y + h / 2 + 5}" text-anchor="middle" font-family="{FONT}" font-size="14">１８０ｍ²</text>'
        + _dim_bracket_h(x, x + w, y - 14, "１５ｍ")
        + _dim_bracket_v(x - 14, y, y + h, "１２ｍ")
        + _road(y + h, y + h + 24, 28, 188, "２４０Ｃ")
    )
    return _svg_wrap(220, 168, inner)


def render_202605_q009() -> str:
    fx, fy, fw, fh = 8, 8, 464, 132
    x, y, w, h = 32, 24, 150, 75
    plot = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#111" stroke-width="{LINE}"/>'
        f'<text x="{x + w / 2}" y="{y + h / 2 + 5}" text-anchor="middle" font-family="{FONT}" font-size="14">３００ｍ²</text>'
        + _dim_bracket_h(x, x + w, y - 14, "３０ｍ")
        + _dim_bracket_v(x + w + 14, y, y + h, "１５ｍ")
        + _road(y + h, y + h + 22, 12, 200, "幅員　６ｍ　市道")
        + _info_box(
            252,
            22,
            190,
            78,
            [
                "・ 準工業地域",
                "・ 指定建蔽率　８０％",
                "・ 指定容積率　４００％",
                "・ 敷地面積　３００ｍ²",
            ],
        )
    )
    inner = _material_frame(fx, fy, fw, fh, plot)
    return _svg_wrap(480, 148, inner, title="資料")


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
