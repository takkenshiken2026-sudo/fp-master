#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 親族関係図 — 公表PDFと同一レイアウトの SVG。"""

from __future__ import annotations

import html
from typing import Any

LINE = 1.5
STEM = 22
FONT = "YuMincho, 'Hiragino Mincho ProN', 'Noto Serif JP', serif"


def _esc(s: str) -> str:
    return html.escape(s or "")


def _nodes_by_id(nodes: list[dict]) -> dict[str, dict]:
    return {str(n["id"]): n for n in nodes if n.get("id")}


def _text_width(name: str, suffix: str = "") -> float:
    base = len(name) + len(suffix)
    return max(base * 15.0 + 8.0, 44.0)


def _node_geom(node: dict) -> dict[str, float]:
    if node.get("deceased"):
        name = str(node.get("name") or "")
        w = max(len(name) * 15.0 + 20.0, 44.0) if name else 40.0
        h = 40.0 if name else 40.0
        return {"x": float(node["x"]), "y": float(node["y"]), "w": w, "h": h, "kind": "deceased"}
    if node.get("role") == "decedent":
        return {"x": float(node["x"]), "y": float(node["y"]), "w": 92.0, "h": 42.0, "kind": "decedent"}
    w = _text_width(str(node.get("name") or ""), str(node.get("suffix") or ""))
    return {"x": float(node["x"]), "y": float(node["y"]), "w": w, "h": 22.0, "kind": "person"}


def _top_center(node: dict) -> tuple[float, float]:
    g = _node_geom(node)
    return g["x"] + g["w"] / 2, g["y"]


def _bottom_center(node: dict) -> tuple[float, float]:
    g = _node_geom(node)
    return g["x"] + g["w"] / 2, g["y"] + g["h"]


def _marriage_span(
    a: dict, b: dict
) -> tuple[float, float, float, float]:
    """結婚線の左右端 x と縦位置 y。"""
    ga, gb = _node_geom(a), _node_geom(b)
    left = ga["x"] + ga["w"]
    right = gb["x"]
    if left > right:
        left, right = gb["x"] + gb["w"], ga["x"]
    y = (ga["y"] + ga["h"] / 2 + gb["y"] + gb["h"] / 2) / 2
    return left, right, y, (left + right) / 2


def _find_marriage(node_id: str, edges: list[dict]) -> tuple[str, str] | None:
    for e in edges:
        if e.get("type") != "marriage":
            continue
        if node_id in (e.get("a"), e.get("b")):
            return str(e["a"]), str(e["b"])
    return None


def _branch_anchor(node_id: str, by_id: dict[str, dict], edges: list[dict]) -> tuple[float, float]:
    n = by_id[node_id]
    if n.get("deceased") or n.get("role") == "decedent":
        return _top_center(n)
    pair = _find_marriage(node_id, edges)
    if pair:
        a, b = by_id[pair[0]], by_id[pair[1]]
        if abs(float(a.get("y") or 0) - float(b.get("y") or 0)) < 18:
            _, _, _, cx = _marriage_span(a, b)
            return cx, _top_center(a)[1]
    return _top_center(n)


def _render_person_svg(node: dict) -> str:
    g = _node_geom(node)
    x, y, w, h = g["x"], g["y"], g["w"], g["h"]
    parts: list[str] = []

    if g["kind"] == "deceased":
        name = str(node.get("name") or "")
        cx, cy = x + w / 2, y + h / 2
        if name:
            parts.append(
                f'<text x="{cx:.1f}" y="{y + 18:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="15" fill="#111">{_esc(name)}</text>'
            )
            parts.append(
                f'<line x1="{x + 4:.1f}" y1="{y + 6:.1f}" x2="{x + w - 4:.1f}" y2="{y + h - 6:.1f}" '
                f'stroke="#111" stroke-width="2"/>'
            )
            parts.append(
                f'<line x1="{x + w - 4:.1f}" y1="{y + 6:.1f}" x2="{x + 4:.1f}" y2="{y + h - 6:.1f}" '
                f'stroke="#111" stroke-width="2"/>'
            )
        else:
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                f'fill="#fff" stroke="#111" stroke-width="{LINE}"/>'
            )
            parts.append(
                f'<text x="{cx:.1f}" y="{y + 24:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="20" font-weight="700" fill="#111">×</text>'
            )
        parts.append(
            f'<text x="{cx:.1f}" y="{y + h + 14:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="11" fill="#111">（すでに死亡）</text>'
        )
        return "".join(parts)

    name = str(node.get("name") or "")
    suffix = str(node.get("suffix") or "")
    sub = str(node.get("sub") or "")

    if g["kind"] == "decedent":
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h - 14:.1f}" '
            f'fill="#fff" stroke="#111" stroke-width="{LINE}"/>'
        )
        parts.append(
            f'<text x="{x + w/2:.1f}" y="{y + 20:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="15" font-weight="600" fill="#111">{_esc(name)}</text>'
        )
        if sub:
            parts.append(
                f'<text x="{x + w/2:.1f}" y="{y + h + 2:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="11" fill="#111">{_esc(sub)}</text>'
            )
        return "".join(parts)

    tx = x + w / 2
    ty = y + 16
    suffix_xml = f'<tspan>{_esc(suffix)}</tspan>' if suffix else ""
    parts.append(
        f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="15" fill="#111">'
        f"{_esc(name)}{suffix_xml}</text>"
    )
    if sub:
        parts.append(
            f'<text x="{tx:.1f}" y="{ty + 16:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="11" fill="#111">{_esc(sub)}</text>'
        )
    return "".join(parts)


def _line(x1: float, y1: float, x2: float, y2: float) -> str:
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="#111" stroke-width="{LINE}" stroke-linecap="square"/>'
    )


def _marriage_lines(left: float, right: float, y: float) -> str:
    gap = 4.0
    return (
        _line(left, y - gap, right, y - gap)
        + _line(left, y + gap, right, y + gap)
    )


def _render_edges(edges: list[dict], by_id: dict[str, dict]) -> str:
    out: list[str] = []
    for e in edges:
        et = e.get("type")
        if et == "marriage":
            a, b = by_id[str(e["a"])], by_id[str(e["b"])]
            left, right, y, _ = _marriage_span(a, b)
            out.append(_marriage_lines(left, right, y))
        elif et == "parent_bus":
            fa, fb = by_id[str(e["from"][0])], by_id[str(e["from"][1])]
            _, _, py, pcx = _marriage_span(fa, fb)
            _, pby = _bottom_center(fa)
            pby = max(pby, _bottom_center(fb)[1])
            targets = [str(t) for t in e.get("to") or []]
            anchors = [_branch_anchor(t, by_id, edges) for t in targets]
            bus_y = min(ay for _, ay in anchors) - STEM
            out.append(_line(pcx, pby, pcx, bus_y))
            xs = [ax for ax, _ in anchors]
            out.append(_line(min(xs), bus_y, max(xs), bus_y))
            for ax, ay in anchors:
                out.append(_line(ax, bus_y, ax, ay))
        elif et == "child":
            fa, fb = by_id[str(e["from"][0])], by_id[str(e["from"][1])]
            child = by_id[str(e["to"])]
            _, _, my, mcx = _marriage_span(fa, fb)
            my = max(_bottom_center(fa)[1], _bottom_center(fb)[1])
            cx, cy = _top_center(child)
            out.append(_line(mcx, my, mcx, cy))
    return "".join(out)


def render_svg_family_tree(data: dict[str, Any]) -> str:
    title = _esc(str(data.get("title") or "親族関係図"))
    footnotes = data.get("footnotes") or []
    nodes = data.get("nodes") or []
    edges = data.get("edges") or []
    vw = float(data.get("view_w") or 480)
    vh = float(data.get("view_h") or 200)
    by_id = _nodes_by_id(nodes)

    shapes = _render_edges(edges, by_id)
    labels = "".join(_render_person_svg(n) for n in nodes)

    fn_html = ""
    if footnotes:
        items = "".join(f"<li>{_esc(str(x))}</li>" for x in footnotes if str(x).strip())
        fn_html = f'<ul class="q-ft-notes">{items}</ul>'

    return (
        '<figure class="q-family-tree q-family-tree--svg" role="group">'
        f'<figcaption class="q-materials-title">{title}</figcaption>'
        f'<div class="q-ft-svg-wrap">'
        f'<svg class="q-ft-svg-genogram" viewBox="0 0 {vw:.0f} {vh:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}">'
        f'<rect width="100%" height="100%" fill="#fff"/>'
        f'<rect x="1" y="1" width="{vw - 2:.0f}" height="{vh - 2:.0f}" '
        f'fill="none" stroke="#111" stroke-width="2"/>'
        f'<g class="q-ft-svg-lines">{shapes}</g>'
        f'<g class="q-ft-svg-labels">{labels}</g>'
        f"</svg></div>{fn_html}</figure>"
    )


def render_genogram_family_tree(data: dict[str, Any]) -> str:
    if str(data.get("layout") or "") == "svg" or data.get("nodes"):
        return render_svg_family_tree(data)
    raise ValueError("unsupported genogram layout")
