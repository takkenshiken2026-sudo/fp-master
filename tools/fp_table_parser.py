#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 資料テキスト → fp_table / fp_materials JSON。"""

from __future__ import annotations

import re
from typing import Any

FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")


def norm(s: str | None) -> str:
    return (s or "").strip()


def nfkc_line(s: str) -> str:
    return norm(s).translate(FULLWIDTH_DIGITS)


def split_material_sections(text: str) -> list[tuple[str, str]]:
    """＜見出し＞で区切った (title, body) のリスト。"""
    text = norm(text)
    if not text:
        return []
    parts = re.split(r"(＜[^＞]+＞)", text)
    sections: list[tuple[str, str]] = []
    current_title = ""
    buf: list[str] = []
    for part in parts:
        if part.startswith("＜") and part.endswith("＞"):
            if current_title or buf:
                sections.append((current_title, "\n".join(buf).strip()))
            current_title = part.strip("＜＞").strip()
            buf = []
        elif part.strip():
            buf.append(part.strip())
    if current_title or buf:
        sections.append((current_title, "\n".join(buf).strip()))
    return sections


def parse_tax_bracket_table(body: str) -> dict[str, Any]:
    lines = [nfkc_line(ln) for ln in body.splitlines() if norm(ln)]
    rows: list[list[str]] = []
    for ln in lines:
        if "法定相続分" in ln and "税率" in ln:
            continue
        s = ln.replace("％", "%")
        m = re.match(r"^(.+?)\s+(\d+%|－|-)\s+(.+)$", s)
        if m:
            rows.append([m.group(1).strip(), m.group(2).strip(), m.group(3).strip()])
            continue
        if re.search(r"\d", s) and ("%" in s or "万円" in s):
            cells = re.split(r"\s{2,}|\t", s)
            cells = [c.strip() for c in cells if c.strip()]
            if len(cells) >= 3:
                rows.append(cells[:3])
            elif len(cells) == 2:
                rows.append([cells[0], cells[1], ""])
    return {
        "type": "fp_table",
        "title": "相続税の速算表",
        "headers": ["法定相続分に応ずる取得金額", "税率", "控除額"],
        "rows": rows,
    }


def parse_insurance_table(body: str) -> dict[str, Any]:
    lines = [ln.strip() for ln in body.splitlines() if norm(ln)]
    headers: list[str] = []
    rows: list[list[str]] = []
    for ln in lines:
        if "保険契約者" in ln or "被保険者" in ln:
            headers = re.split(r"\s{2,}|\s(?=被保険者|死亡保険金)", nfkc_line(ln))
            headers = [h.strip() for h in headers if h.strip()]
            continue
        if "万円" in ln or re.search(r"\d", nfkc_line(ln)):
            cells = re.split(r"\s{2,}|\t", ln)
            cells = [c.strip() for c in cells if c.strip()]
            if cells:
                rows.append(cells)
    return {
        "type": "fp_table",
        "title": "遺族が受け取った生命保険の死亡保険金",
        "headers": headers or ["保険契約者（保険料負担者）", "被保険者", "死亡保険金受取人", "金額"],
        "rows": rows,
    }


def parse_cashflow_table(title: str, body: str, *, source_id: str = "") -> dict[str, Any]:
    if source_id:
        from tools.fp3_cashflow_tables import get_cashflow_table

        hand = get_cashflow_table(source_id)
        if hand:
            return hand
    lines = [ln.rstrip() for ln in body.splitlines()]
    rows: list[list[str]] = []
    for ln in lines:
        s = norm(ln)
        if not s:
            continue
        if s.startswith("※"):
            rows.append([{"text": s, "colspan": 99, "note": True}])
            continue
        # 空白区切りを粗くセル化（元PDFの列揃えを近似）
        cells = re.split(r"\s{2,}|\t", s)
        if len(cells) == 1:
            cells = s.split()
        cells = [c for c in cells if c]
        if cells:
            rows.append(cells)
    unit = ""
    m = re.search(r"（単位：[^）]+）", title)
    if m:
        unit = m.group(0)
    return {
        "type": "fp_table",
        "title": title,
        "unit": unit,
        "rows": rows,
        "dense": True,
    }


def parse_simple_amount_block(title: str, body: str) -> dict[str, Any]:
    amount = norm(body).replace("\n", " ")
    return {"type": "fp_text_block", "title": title, "body": amount}


def materials_text_to_diagram(source_id: str, text: str, *, kind: str) -> dict[str, Any]:
    """資料全文から fp_materials JSON を組み立てる。"""
    sections = split_material_sections(text)
    blocks: list[dict[str, Any]] = []

    if kind == "family_tree":
        from tools.fp3_family_trees import FP3_FAMILY_TREES, source_id_to_diagram_id

        fid = source_id_to_diagram_id(source_id)
        tree = FP3_FAMILY_TREES.get(fid)
        if tree:
            blocks.append(tree)

    for title, body in sections:
        if not body and not title:
            continue
        if "速算表" in title or ("税率" in body and "控除額" in body):
            blocks.append(parse_tax_bracket_table(body))
        elif "死亡保険金" in title or "保険契約者" in body:
            blocks.append(parse_insurance_table(body if body else title))
        elif "課税遺産総額" in title:
            amount = norm(body)
            if amount and "万円" in amount and len(amount) < 40:
                blocks.append(parse_simple_amount_block(title, amount))
        elif "キャッシュフロー" in title or "経過年数" in body or "収入合計" in body:
            blocks.append(parse_cashflow_table(title or "資料表", body, source_id=source_id))
        elif title and body and kind != "family_tree" and "正しいものはどれか" not in body:
            blocks.append({"type": "fp_text_block", "title": title, "body": body})

    if not blocks and text.strip():
        blocks.append({"type": "fp_text_block", "title": "", "body": text.strip()})

    return {"type": "fp_materials", "sections": blocks}
