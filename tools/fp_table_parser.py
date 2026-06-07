#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級実技 資料テキスト → fp_table / fp_materials JSON。"""

from __future__ import annotations

import re
from typing import Any

FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")

_QUESTION_STEM_MARKERS = (
    "正しいものはどれか",
    "最も適切なものはどれか",
    "最も不適切なものはどれか",
    "誤っているものはどれか",
    "適切なものはどれか",
    "適切でないものはどれか",
    "対象とならないものはどれか",
    "対象となるものはどれか",
    "支払い対象とならないものはどれか",
    "いうものとする",
)


def norm(s: str | None) -> str:
    return (s or "").strip()


def preamble_is_materials(preamble: str) -> bool:
    """CSV preamble が資料ブロック（表・図）かどうか。設問文の続き（穴埋め等）は False。"""
    p = norm(preamble)
    if not p:
        return False
    if p.startswith("＜") or p.startswith("<"):
        return True
    markers = (
        "速算表",
        "親族関係図",
        "キャッシュフロー",
        "バランスシート",
        "借地権割合",
        "係数早見表",
    )
    return any(m in p for m in markers)


def nfkc_line(s: str) -> str:
    return norm(s).translate(FULLWIDTH_DIGITS)


def split_question_and_materials(text: str) -> tuple[str, str]:
    """設問文とそれ以降の資料ブロックを分離する。"""
    t = norm(text)
    if not t:
        return "", ""
    # 「なお、～こととする。」は設問の定義文として stem に含める（改行で分断されても可）
    na_m = re.search(
        r"なお、[^＜]*?(?:こととする|こと\s*\n\s*とする)\s*。",
        t,
        re.DOTALL,
    )
    if na_m:
        return t[: na_m.end()].strip(), t[na_m.end() :].strip()
    compact = re.sub(r"\s+", "", t)
    if "いうものとする" in compact:
        pos = compact.find("いうものとする")
        # 原文上の「。」位置を compact インデックスから復元
        seen = 0
        for i, ch in enumerate(t):
            if ch.isspace():
                continue
            if seen == pos + len("いうものとする"):
                end = t.find("。", i)
                if end >= 0:
                    return t[: end + 1].strip(), t[end + 1 :].strip()
                break
            seen += 1
    m = re.search(r"どれ\s*か\s*。", t, re.DOTALL)
    if m:
        return t[: m.end()].strip(), t[m.end() :].strip()
    return t, ""


_MATERIAL_TAIL_MARKERS = (
    "価格の種類",
    "公示価格",
    "運用スタイル",
    "保険証券",
    "無配当",
    "がん保険",
    "医療保険",
    "譲渡価額",
    "支給された退職",
    "終価係数",
    "経過年数",
    "収入合計",
    "◆",
    "■ご契約",
    "■お払い",
    "表面利率",
    "青色申告者",
    "贈与税の速算表",
    "親族関係図",
    "キャッシュフロー",
    "種類 ",
    "一般定期借地権",
)


def tail_looks_like_materials(tail: str) -> bool:
    """stem 末尾に混入した資料ブロックかどうか。"""
    t = norm(tail)
    if not t:
        return False
    if preamble_is_materials(t):
        return True
    compact = re.sub(r"\s+", "", t)
    if compact.startswith("＜資料＞") or compact.startswith("＜贈与"):
        return True
    if t.lstrip().startswith("・") and "万円" in t and "贈与" in t:
        return False
    return any(m in t for m in _MATERIAL_TAIL_MARKERS)


def _stem_keep_naoto_mata(tail: str) -> tuple[list[str], str]:
    """tail 先頭の「なお／また」定義文を stem 用に取り出す。"""
    kept: list[str] = []
    rem = tail.strip()
    while rem:
        rem = rem.lstrip()
        if rem.startswith("なお、") or rem.startswith("また、"):
            end = rem.find("。")
            if end >= 0:
                kept.append(rem[: end + 1].strip())
                rem = rem[end + 1 :].strip()
                continue
            m = re.match(r"なお、下記\s*", rem)
            if m and not tail_looks_like_materials(rem[m.end() :]):
                kept.append(m.group(0).strip())
                rem = rem[m.end() :].strip()
                continue
            break
        break
    return kept, rem


def strip_embedded_materials_from_stem(stem: str) -> str:
    """diagram 用 HTML がある設問で、stem 列に残った資料テキストを除去する。"""
    t = norm(stem)
    if not t:
        return t

    for pat in (
        r"(?:^|\n\n)＜資料＞\s*\n",
        r"\n＜資料＞\s*\n",
        r"＜資料＞(?:無配当|がん|医療|◆|■|譲渡|支給)",
    ):
        m = re.search(pat, t)
        if m:
            before = t[: m.start()].strip()
            tail_ctx = before[-40:]
            if "のとおり" in tail_ctx or "参照" in tail_ctx or tail_ctx.rstrip().endswith("下記"):
                continue
            return before

    dq = re.search(r"どれ\s*か\s*。", t, re.DOTALL)
    if dq:
        head = t[: dq.end()].strip()
        tail = t[dq.end() :].strip()
        if not tail:
            return head
        kept, rem = _stem_keep_naoto_mata(tail)
        if rem and tail_looks_like_materials(rem):
            out = head
            if kept:
                out += "\n\n" + "\n\n".join(kept)
            return out.strip()
        if not rem and tail_looks_like_materials(tail):
            out = head
            if kept:
                out += "\n\n" + "\n\n".join(kept)
            return out.strip()

    stem_only, tail = split_question_and_materials(t)
    if tail and tail_looks_like_materials(tail) and stem_only:
        kept, rem = _stem_keep_naoto_mata(tail)
        if rem and tail_looks_like_materials(rem):
            out = stem_only
            if kept:
                out += "\n\n" + "\n\n".join(kept)
            return out.strip()

    return t


def strip_leading_question_from_materials(text: str) -> str:
    """資料テキスト先頭に含まれる設問文を除去する。"""
    t = norm(text)
    if not t:
        return t
    m = re.search(r"＜[^＞]+＞", t)
    if m and m.start() > 0:
        before = t[: m.start()].strip()
        looks_like_stem = (
            is_question_stem_text(before)
            or "どれか" in before
            or before.endswith("下記")
            or "いうものとする" in before
        )
        if looks_like_stem and "経過年数" not in before and "収入合計" not in before:
            return t[m.start() :].strip()
    _, tail = split_question_and_materials(t)
    if tail and tail != t:
        return strip_leading_question_from_materials(tail)
    return t


def is_question_stem_text(text: str) -> bool:
    """資料ではなく設問文のみか（表・＜見出し＞を含まない）。"""
    t = norm(text).replace("\n", "")
    if not t:
        return False
    if "＜" in t or "経過年数" in t or "収入合計" in t:
        return False
    if any(m in t for m in _QUESTION_STEM_MARKERS):
        _, tail = split_question_and_materials(text)
        return not norm(tail)
    return False


def normalize_jp_linebreaks(text: str) -> str:
    """PDF由来の不自然な改行（例: の保\\n険）を結合する。"""
    if not text:
        return text
    lines = text.split("\n")
    merged: list[str] = []
    for line in lines:
        s = line.strip()
        if not s:
            if merged and merged[-1] != "":
                merged.append("")
            continue
        if not merged or merged[-1] == "":
            merged.append(s)
            continue
        prev = merged[-1]
        if prev and not re.search(r"[。．！？…」』）\)、]$", prev.rstrip()):
            if re.match(r"^[ぁ-んァ-ヶー・一-龠〝〟（(]", s):
                merged[-1] = prev.rstrip() + s
                continue
        merged.append(s)
    return "\n".join(merged)


def format_stem_display_text(text: str) -> str:
    """設問文の表示用整形: PDF途中改行の除去と、なお・また・箇条書き前の段落改行。"""
    t = normalize_jp_linebreaks(norm(text))
    if not t:
        return t
    t = t.replace("\n・", "\x00・")
    t = re.sub(r"(?<!\n)\n(?!\n)", "", t)
    t = t.replace("\x00・", "\n・")
    t = re.sub(r"(?<=[^・\n])・ (?=[\u4e00-\u9fff])", "\n・ ", t)
    t = re.sub(r"。[ \t　]*(?=なお、)", "。\n\n", t)
    t = re.sub(r"。[ \t　]*(?=また、)", "。\n\n", t)
    if "・" in t:
        t = re.sub(r"。[ \t　]*(?=・)", "。\n\n", t)
    paras: list[str] = []
    for block in re.split(r"\n\n+", t):
        block = block.strip()
        if not block:
            continue
        if "\n・" in block or block.startswith("・"):
            lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
            paras.append("\n".join(lines))
        else:
            paras.append(block)
    return "\n\n".join(paras)


def stem_display_to_html(text: str) -> str:
    """format_stem_display_text 済みテキストを設問 HTML に変換。"""
    import html as html_mod

    formatted = format_stem_display_text(text)
    if not formatted:
        return "<p>（問題文なし）</p>"
    br = "<br>\n"
    parts: list[str] = []
    for para in formatted.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        inner = html_mod.escape(para).replace("\n", br)
        parts.append(f"<p>{inner}</p>")
    return "\n".join(parts) if parts else "<p>（問題文なし）</p>"


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


def _tax_table_title(body: str, section_title: str = "") -> str:
    blob = f"{section_title}\n{body}"
    if "生命保険料控除" in blob or ("支払保険料" in body and "控除額" in body):
        return "所得税の生命保険料控除額の速算表"
    if "給与所得控除" in blob:
        return "給与所得控除額の速算表"
    if "公的年金" in blob:
        return "公的年金等控除額の速算表"
    if "課税される所得金額" in body or "所得税の速算表" in blob:
        return "所得税の速算表"
    return "相続税の速算表"


def _tax_table_headers(body: str, title: str) -> list[str]:
    if "生命保険料控除" in title:
        return ["年間の支払保険料の合計", "控除額"]
    if "給与所得控除" in title:
        return ["給与等の収入金額", "給与所得控除額"]
    if "公的年金" in title:
        return ["納税者区分", "公的年金等の収入金額（Ａ）", "公的年金等控除額"]
    if "所得税の速算表" in title:
        return ["課税される所得金額", "税率", "控除額"]
    return ["法定相続分に応ずる取得金額", "税率", "控除額"]


def parse_tax_bracket_table(body: str, *, section_title: str = "") -> dict[str, Any]:
    title = _tax_table_title(body, section_title)
    headers = _tax_table_headers(body, title)
    lines = [nfkc_line(ln) for ln in body.splitlines() if norm(ln)]
    rows: list[list[str]] = []
    for ln in lines:
        if ln.startswith("（注）") or ln.startswith("※"):
            rows.append([{"text": ln, "note": True}])
            continue
        if any(h in ln for h in headers if len(h) > 4) and "税率" in ln:
            continue
        s = ln.replace("％", "%")
        m = re.match(r"^(.+?)\s+(\d+%|－|-)\s+(.+)$", s)
        if m:
            rows.append([m.group(1).strip(), m.group(2).strip(), m.group(3).strip()])
            continue
        if re.search(r"\d", s) and ("%" in s or "万円" in s or "円" in s):
            cells = re.split(r"\s{2,}|\t", s)
            cells = [c.strip() for c in cells if c.strip()]
            if len(cells) >= 3:
                rows.append(cells[:3])
            elif len(cells) == 2:
                rows.append(cells[:2])
    return {"type": "fp_table", "title": title, "headers": headers, "rows": rows, "dense": True}


def parse_death_insurance_table(body: str) -> dict[str, Any]:
    lines = [ln.strip() for ln in body.splitlines() if norm(ln)]
    headers: list[str] = []
    rows: list[list[str]] = []
    for ln in lines:
        if "保険契約者" in ln and "被保険者" in ln:
            headers = re.split(r"\s{2,}|\s(?=被保険者|死亡保険金)", nfkc_line(ln))
            headers = [h.strip() for h in headers if h.strip()]
            continue
        if "万円" in ln:
            cells = re.split(r"\s{2,}|\t", ln)
            cells = [c.strip() for c in cells if c.strip()]
            if len(cells) >= 4:
                rows.append(cells[:4])
            elif len(cells) == 1 and "万円" in cells[0]:
                parts = cells[0].split()
                if len(parts) >= 4:
                    rows.append(parts[:4])
    return {
        "type": "fp_table",
        "title": "遺族が受け取った生命保険の死亡保険金",
        "headers": headers
        or ["保険契約者（保険料負担者）", "被保険者", "死亡保険金受取人", "金額"],
        "rows": rows,
        "dense": True,
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
    from tools.fp3_family_trees import FP3_FAMILY_TREES, source_id_to_diagram_id
    from tools.fp3_hand_tables import hand_material_sections

    hand = hand_material_sections(source_id)
    if hand is not None:
        sections = list(hand)
        if kind == "family_tree":
            fid = source_id_to_diagram_id(source_id)
            tree = FP3_FAMILY_TREES.get(fid)
            if tree and not any(s.get("type") == "family_tree" for s in sections):
                sections.insert(0, tree)
        return {"type": "fp_materials", "sections": sections}

    text = strip_leading_question_from_materials(text)
    sections = split_material_sections(text)
    blocks: list[dict[str, Any]] = []

    if kind == "family_tree":
        fid = source_id_to_diagram_id(source_id)
        tree = FP3_FAMILY_TREES.get(fid)
        if tree:
            blocks.append(tree)

    for title, body in sections:
        if not body and not title:
            continue
        if "遺族が受け取った生命保険" in title:
            blocks.append(parse_death_insurance_table(body if body else title))
        elif "速算表" in title or ("税率" in body and "控除額" in body):
            blocks.append(parse_tax_bracket_table(body, section_title=title))
        elif "死亡保険金" in title and "遺族" in title:
            blocks.append(parse_death_insurance_table(body if body else title))
        elif "課税遺産総額" in title:
            amount = norm(body)
            if amount and "万円" in amount and len(amount) < 40:
                blocks.append(parse_simple_amount_block(title, amount))
        elif "キャッシュフロー" in title or "経過年数" in body or "収入合計" in body:
            blocks.append(parse_cashflow_table(title or "資料表", body, source_id=source_id))
        elif title and body and kind != "family_tree" and not is_question_stem_text(body):
            blocks.append(
                {
                    "type": "fp_text_block",
                    "title": title,
                    "body": normalize_jp_linebreaks(body),
                }
            )
        elif not title and body and kind != "family_tree":
            mat = normalize_jp_linebreaks(strip_leading_question_from_materials(body))
            if mat and not is_question_stem_text(mat):
                if "速算表" in mat or ("税率" in mat and "控除額" in mat):
                    blocks.append(parse_tax_bracket_table(mat, section_title=""))
                elif "キャッシュフロー" in mat or "経過年数" in mat or "収入合計" in mat:
                    blocks.append(parse_cashflow_table("資料表", mat, source_id=source_id))
                else:
                    blocks.append({"type": "fp_text_block", "title": "", "body": mat})

    blocks = [
        b
        for b in blocks
        if not (
            b.get("type") == "fp_text_block"
            and is_question_stem_text(str(b.get("body") or ""))
        )
    ]

    return {"type": "fp_materials", "sections": blocks}
