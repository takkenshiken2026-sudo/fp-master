#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 親族関係図（公表PDFレイアウトに近い HTML ジェノグラム）。"""

from __future__ import annotations

import html
from typing import Any


def _esc(s: str) -> str:
    return html.escape(s or "")


def _person_box(person: dict[str, Any]) -> str:
    role = str(person.get("role") or "")
    name = str(person.get("name") or "").strip()
    sub = str(person.get("sub") or "").strip()
    suffix = str(person.get("suffix") or "").strip()

    classes = ["q-ft-person"]
    if role == "decedent":
        classes.append("q-ft-person--decedent")
    if role == "deceased":
        classes.append("q-ft-person--deceased")

    if role == "deceased" and not name:
        inner = (
            '<span class="q-ft-deceased-x" aria-hidden="true">×</span>'
            f'<span class="q-ft-sub">{_esc(sub or "（すでに死亡）")}</span>'
        )
        return f'<div class="{" ".join(classes)} q-ft-person--marker">{inner}</div>'

    suffix_html = f'<span class="q-ft-suffix">{_esc(suffix)}</span>' if suffix else ""
    sub_html = f'<span class="q-ft-sub">{_esc(sub)}</span>' if sub else ""
    return (
        f'<div class="{" ".join(classes)}">'
        f'<span class="q-ft-name">{_esc(name)}{suffix_html}</span>'
        f"{sub_html}</div>"
    )


def _couple_block(left: dict, right: dict) -> str:
    return (
        '<div class="q-ft-couple">'
        f"{_person_box(left)}"
        '<div class="q-ft-marriage-bar" aria-hidden="true"></div>'
        f"{_person_box(right)}"
        "</div>"
    )


def _child_unit(unit: dict[str, Any]) -> str:
    person = unit.get("person")
    if isinstance(person, dict):
        return (
            '<div class="q-ft-branch q-ft-branch--solo">'
            '<div class="q-ft-branch-stem" aria-hidden="true"></div>'
            f"{_person_box(person)}"
            "</div>"
        )

    spouse = unit.get("spouse") or {}
    left = spouse.get("left") or {}
    right = spouse.get("right") or {}
    descendants = unit.get("descendants") or []
    desc_html = ""
    if descendants:
        cells = "".join(_person_box(p) for p in descendants if isinstance(p, dict))
        desc_html = (
            '<div class="q-ft-descendants">'
            '<div class="q-ft-descendants-stem" aria-hidden="true"></div>'
            f'<div class="q-ft-descendants-row">{cells}</div>'
            "</div>"
        )
    return (
        '<div class="q-ft-branch">'
        '<div class="q-ft-branch-stem" aria-hidden="true"></div>'
        f"{_couple_block(left, right)}"
        f"{desc_html}"
        "</div>"
    )


def render_genogram_family_tree(data: dict[str, Any]) -> str:
    title = _esc(str(data.get("title") or "親族関係図"))
    footnotes = data.get("footnotes") or []
    fn_html = ""
    if footnotes:
        items = "".join(f"<li>{_esc(str(x))}</li>" for x in footnotes if str(x).strip())
        fn_html = f'<ul class="q-ft-notes">{items}</ul>'

    above = data.get("above")
    above_html = ""
    if isinstance(above, dict):
        above_html = (
            '<div class="q-ft-genogram-above">'
            f"{_person_box(above)}"
            '<div class="q-ft-genogram-above-stem" aria-hidden="true"></div>'
            "</div>"
        )

    spouse = data.get("spouse") or {}
    top = _couple_block(spouse.get("left") or {}, spouse.get("right") or {})
    units = data.get("child_units") or data.get("children") or []
    branches = "".join(_child_unit(u) for u in units if isinstance(u, dict))

    return (
        '<figure class="q-family-tree q-family-tree--genogram" role="group">'
        f'<figcaption class="q-materials-title">{title}</figcaption>'
        '<div class="q-ft-genogram">'
        f"{above_html}"
        f'<div class="q-ft-genogram-top">{top}</div>'
        '<div class="q-ft-genogram-connector" aria-hidden="true"></div>'
        f'<div class="q-ft-genogram-children">{branches}</div>'
        "</div>"
        f"{fn_html}</figure>"
    )
