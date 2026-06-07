#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""過去問・実践演習向け HTML 図解（data/question_diagrams/*.json）。"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS_DIR = ROOT / "data" / "question_diagrams"
DIAGRAM_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def load_diagram(diagram_id: str) -> dict | None:
    if not diagram_id or not DIAGRAM_ID_RE.fullmatch(diagram_id):
        return None
    path = DIAGRAMS_DIR / f"{diagram_id}.json"
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else None


def diagram_id_exists(diagram_id: str) -> bool:
    return load_diagram(diagram_id) is not None


def _person_html(person: dict) -> str:
    name = html.escape(str(person.get("name") or ""))
    sub = html.escape(str(person.get("sub") or ""))
    suffix = html.escape(str(person.get("suffix") or ""))
    role = str(person.get("role") or "")
    classes = ["q-ft-person"]
    if role == "decedent":
        classes.append("q-ft-person--decedent")
    if role == "deceased":
        classes.append("q-ft-person--deceased")
    sub_html = f'<span class="q-ft-sub">{sub}</span>' if sub else ""
    suffix_html = f'<span class="q-ft-suffix">{suffix}</span>' if suffix else ""
    below = person.get("below") or []
    below_html = ""
    if below:
        below_html = (
            '<div class="q-ft-below">'
            + "".join(_person_html(p) for p in below if isinstance(p, dict))
            + "</div>"
        )
    return (
        f'<div class="{" ".join(classes)}">'
        f'<span class="q-ft-name">{name}{suffix_html}</span>'
        f"{sub_html}{below_html}</div>"
    )


def render_family_tree(data: dict) -> str:
    title = html.escape(str(data.get("title") or "親族関係図"))
    rows_html: list[str] = []
    for row in data.get("rows") or []:
        if not isinstance(row, list):
            continue
        cells: list[str] = []
        for person in row:
            if not isinstance(person, dict):
                continue
            join = person.get("join")
            person_html = _person_html(person)
            if join == "marriage":
                cells.append('<div class="q-ft-marriage">' + person_html + "</div>")
            else:
                cells.append(person_html)
        if cells:
            rows_html.append('<div class="q-ft-row">' + "".join(cells) + "</div>")
    footnotes = data.get("footnotes") or []
    fn_html = ""
    if footnotes:
        items = "".join(f"<li>{html.escape(str(x))}</li>" for x in footnotes if str(x).strip())
        fn_html = f'<ul class="q-ft-notes">{items}</ul>'
    return (
        '<figure class="q-family-tree" role="group">'
        f'<figcaption class="q-materials-title">{title}</figcaption>'
        f'<div class="q-family-tree-body">{"".join(rows_html)}</div>'
        f"{fn_html}</figure>"
    )


def _render_cf_cell(cell: Any) -> str:
    if isinstance(cell, dict):
        text = html.escape(str(cell.get("text") or "")).replace("\n", "<br>")
        cls = str(cell.get("class") or "").strip()
        attrs: list[str] = []
        if cls:
            attrs.append(f' class="{html.escape(cls)}"')
        colspan = cell.get("colspan")
        if colspan:
            attrs.append(f' colspan="{int(colspan)}"')
        rowspan = cell.get("rowspan")
        if rowspan:
            attrs.append(f' rowspan="{int(rowspan)}"')
        return f"<td{''.join(attrs)}>{text}</td>"
    text = html.escape(str(cell or ""))
    return f"<td>{text}</td>"


def render_fp_cashflow_table(data: dict) -> str:
    title = html.escape(str(data.get("title") or "資料"))
    unit = html.escape(str(data.get("unit") or ""))
    rows = data.get("rows") or []
    body_rows: list[str] = []
    for row in rows:
        if not row:
            continue
        cells = [_render_cf_cell(c) for c in row]
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    notes = data.get("notes") or []
    for note in notes:
        if str(note).strip():
            body_rows.append(
                f'<tr><td colspan="8" class="q-fp-table-note">'
                f"{html.escape(str(note))}</td></tr>"
            )
    unit_html = f'<p class="q-fp-table-unit">{unit}</p>' if unit else ""
    return (
        '<figure class="q-fp-table-wrap q-fp-cashflow-wrap" role="group">'
        f'<figcaption class="q-materials-title">{title}</figcaption>'
        f"{unit_html}"
        '<div class="q-fp-table-scroll"><table class="seo-info-table q-fp-table q-fp-cashflow">'
        f"<tbody>{''.join(body_rows)}</tbody></table></div></figure>"
    )


def render_fp_table(data: dict) -> str:
    if str(data.get("layout") or "") == "cashflow":
        return render_fp_cashflow_table(data)
    title = html.escape(str(data.get("title") or "資料"))
    unit = html.escape(str(data.get("unit") or ""))
    headers = data.get("headers") or []
    rows = data.get("rows") or []
    dense = bool(data.get("dense"))
    thead = ""
    if headers:
        ths = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)
        thead = f"<thead><tr>{ths}</tr></thead>"
    body_rows: list[str] = []
    for row in rows:
        if not row:
            continue
        if isinstance(row, list) and row and isinstance(row[0], dict) and row[0].get("note"):
            text = html.escape(str(row[0].get("text") or ""))
            body_rows.append(f'<tr><td colspan="12" class="q-fp-table-note">{text}</td></tr>')
            continue
        cells = [html.escape(str(c)) for c in row]
        if not headers and len(cells) == 1:
            body_rows.append(f'<tr><td colspan="12">{cells[0]}</td></tr>')
        else:
            tds = "".join(f"<td>{c}</td>" for c in cells)
            body_rows.append(f"<tr>{tds}</tr>")
    dense_cls = " q-fp-table--dense" if dense else ""
    unit_html = f'<p class="q-fp-table-unit">{unit}</p>' if unit else ""
    return (
        '<figure class="q-fp-table-wrap" role="group">'
        f'<figcaption class="q-materials-title">{title}</figcaption>'
        f"{unit_html}"
        f'<div class="q-fp-table-scroll"><table class="seo-info-table q-fp-table{dense_cls}">'
        f"{thead}<tbody>{''.join(body_rows)}</tbody></table></div></figure>"
    )


def render_text_block(data: dict) -> str:
    title = html.escape(str(data.get("title") or ""))
    body = html.escape(str(data.get("body") or "")).replace("\n", "<br>\n")
    title_html = f'<p class="q-materials-title">{title}</p>' if title else ""
    return f'<div class="q-fp-text-block">{title_html}<p>{body}</p></div>'


def render_section(section: dict) -> str:
    stype = str(section.get("type") or "").strip()
    if stype == "family_tree":
        return render_family_tree(section)
    if stype == "fp_table":
        return render_fp_table(section)
    if stype == "fp_text_block":
        return render_text_block(section)
    return ""


def render_fp_materials(data: dict) -> str:
    parts = [render_section(s) for s in (data.get("sections") or []) if isinstance(s, dict)]
    inner = "".join(p for p in parts if p)
    if not inner:
        return ""
    return f'<div class="q-materials">{inner}</div>'


def render_diagram(data: dict) -> str:
    dtype = str(data.get("type") or "").strip()
    if dtype == "fp_materials":
        return render_fp_materials(data)
    if dtype == "family_tree":
        return f'<div class="q-materials">{render_family_tree(data)}</div>'
    if dtype == "fp_table":
        return f'<div class="q-materials">{render_fp_table(data)}</div>'
    return ""


def diagram_body_html(diagram_id: str) -> str:
    data = load_diagram(diagram_id)
    if not data:
        return ""
    return render_diagram(data)
