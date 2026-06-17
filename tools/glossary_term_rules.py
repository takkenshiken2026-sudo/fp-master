#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用語詳細記事（glossary_terms.csv）の必須列・最低品質基準."""

from __future__ import annotations

import re
from dataclasses import dataclass

from tools.build_glossary_pages import lookup_key
from tools.editorial_quality import (
    GLOSSARY_PRO,
    concreteness_issues,
    duplicate_faq_answers,
    generic_issues,
    long_sentence_issues,
    placeholder_issues,
    readability_issues,
    split_paragraphs,
)

# 詳細記事として必須の CSV 列（全用語）
GLOSSARY_DETAIL_COLUMNS: tuple[str, ...] = (
    "article_title",
    "article_lead",
    "term_detail_body",
    "exam_points",
    "common_mistakes",
    "memory_tip",
    "example_question",
    "example_answer",
    "faq_1_question",
    "faq_1_answer",
    "faq_2_question",
    "faq_2_answer",
    "faq_3_question",
    "faq_3_answer",
    "faq_4_question",
    "faq_4_answer",
)

GLOSSARY_BASE_REQUIRED: frozenset[str] = frozenset(
    {
        "term",
        "category",
        "tags",
        "short_def",
        "definition",
        "related_terms",
        "legal_basis",
        "importance",
        "explanation",
    }
    | set(GLOSSARY_DETAIL_COLUMNS)
)

# 列ごとの最低文字数（空白除去後）— 専門家×プロライター水準を ERROR で強制
GLOSSARY_MIN_LENGTHS: dict[str, int] = {
    "short_def": 12,
    "definition": 50,
    "explanation": 80,
    "article_title": 10,
    "article_lead": 60,
    "term_detail_body": 180,
    "common_mistakes": 40,
    "memory_tip": 25,
    "example_question": 12,
    "example_answer": 3,
    "faq_1_question": 6,
    "faq_1_answer": 100,
    "faq_2_question": 6,
    "faq_2_answer": 100,
    "faq_3_question": 6,
    "faq_3_answer": 100,
    "faq_4_question": 6,
    "faq_4_answer": 100,
}

GLOSSARY_PRODUCTION_TARGET = 300
GLOSSARY_IMPORTANCE_VALUES = frozenset({"A", "B", "C", "S"})
GLOSSARY_MIN_RELATED_TERMS = 2
GLOSSARY_MIN_EXAM_POINT_ITEMS = 2
GLOSSARY_FAQ_COUNT = 4

# 相続税・基礎控除の人数→金額（万円）。docs/fp2-glossary-calculation-rules.md と同期。
# 式: 3,000 + 600 × 法定相続人の数
INHERITANCE_BASIC_DEDUCTION_BY_HEADCOUNT: dict[int, int] = {
    1: 3600,
    2: 4200,
    3: 4800,
    4: 5400,
    5: 6000,
}

_STATUTORY_HEIR_HEADCOUNT = re.compile(
    r"(?:"
    r"法定相続人(?:の数(?:は|が))?(\d+)人"
    r"|(?<=[＝=])(\d+)人"
    r"|(\d+)人[＝=]\s*[\d,]+\s*万"
    r"|(\d+)人(?:の場合|なら|です|。|\)|（)"
    r")",
    re.I,
)

# 法令・制度分野で importance A/S のときは根拠列を推奨（警告）
LAW_CATEGORY_KEYWORDS = ("法令", "制度", "法")

def split_semicolon(value: str) -> list[str]:
    return [x.strip() for x in value.split(";") if x.strip()]


def norm(value: object) -> str:
    return str(value or "").strip()


@dataclass(frozen=True)
class GlossaryRowIssue:
    level: str  # ERROR | WARN
    message: str


def _is_law_heavy(category: str, importance: str) -> bool:
    if importance not in {"A", "S"}:
        return False
    return any(k in category for k in LAW_CATEGORY_KEYWORDS)


def inheritance_basic_deduction_yen(headcount: int) -> int:
    """相続税法第15条の基礎控除額（万円）。"""
    return 3000 + 600 * headcount


def _parse_man_yen(value: str) -> int | None:
    digits = value.replace(",", "").replace("，", "").strip()
    if not digits.isdigit():
        return None
    return int(digits)


def _statutory_heir_headcount_from_match(match: re.Match[str]) -> int:
    for group in match.groups():
        if group is not None:
            return int(group)
    raise ValueError("no headcount group")


def _is_family_role_headcount(text: str, match: re.Match[str], headcount: int) -> bool:
    """配偶者1人・子2人など、法定相続人の総数ではない表記を除外。"""
    prefix = text[max(0, match.start() - 10) : match.start() + len(str(headcount))]
    return bool(
        re.search(
            rf"(?:配偶者|実子|養子|兄弟|父母|祖父母|子|孫){headcount}\s*$",
            prefix,
        )
    )


def inheritance_basic_deduction_calc_issues(text: str) -> list[str]:
    """600万×人数と基礎控除額の不整合を検出。戻り値は WARN メッセージ。"""
    if not text:
        return []
    if "600万" not in text and "基礎控除" not in text:
        return []
    issues: list[str] = []

    # 3,000万＋600万×N＝X万 / 600万×N＝X万
    amount_pattern = r"(?:3,?000|3000)万(?:円|)"
    patterns = (
        re.compile(
            rf"{amount_pattern}\s*[＋+]\s*600万(?:円|)\s*[×x]\s*(\d+)"
            r"[^0-9]{{0,24}}[=＝]\s*([\d,]+)\s*万",
            re.I,
        ),
        re.compile(
            r"600万(?:円|)\s*[×x]\s*(\d+)[^0-9]{0,24}[=＝]\s*([\d,]+)\s*万",
            re.I,
        ),
    )
    seen: set[tuple[int, int]] = set()
    for pattern in patterns:
        for match in pattern.finditer(text):
            headcount = int(match.group(1))
            stated = _parse_man_yen(match.group(2))
            if stated is None:
                continue
            key = (headcount, stated)
            if key in seen:
                continue
            seen.add(key)
            expected = inheritance_basic_deduction_yen(headcount)
            if stated != expected:
                issues.append(
                    f"相続税の基礎控除の算数不一致: {headcount}人なら"
                    f" {expected:,}万円（3,000万＋600万×{headcount}）ですが、"
                    f" {stated:,}万円 と記載されています"
                )

    # 法定相続人の人数表記と基礎控除額（配偶者1人などは除外）
    for hc_match in _STATUTORY_HEIR_HEADCOUNT.finditer(text):
        headcount = _statutory_heir_headcount_from_match(hc_match)
        if _is_family_role_headcount(text, hc_match, headcount):
            continue

        fragment = hc_match.group(0)
        inline = re.search(r"(\d+)人[＝=]\s*([\d,]+)\s*万", fragment, re.I)
        if inline:
            stated = _parse_man_yen(inline.group(2))
        else:
            start = max(0, hc_match.start() - 60)
            end = min(len(text), hc_match.end() + 100)
            window = text[start:end]
            if "基礎控除" not in window:
                near = re.search(r"([\d,]+)\s*万(?:円|)控除", window, re.I)
                if not near:
                    continue
                stated = _parse_man_yen(near.group(1))
            else:
                bi_idx = window.find("基礎控除")
                tail = window[bi_idx:]
                stated = None
                formula = re.search(
                    rf"{amount_pattern}\s*[＋+]\s*600万[^=＝]{{0,40}}[=＝]\s*([\d,]+)\s*万",
                    tail,
                    re.I,
                )
                if formula:
                    stated = _parse_man_yen(formula.group(1))
                else:
                    direct = re.search(
                        r"(?:額|の金額|)(?:は|が|)\s*([\d,]+)\s*万(?!円?\s*[＋+×])",
                        tail[len("基礎控除") :],
                        re.I,
                    )
                    if direct:
                        stated = _parse_man_yen(direct.group(1))
                    else:
                        near = re.search(r"([\d,]+)\s*万(?:円|)控除", window, re.I)
                        if near:
                            stated = _parse_man_yen(near.group(1))
                if stated is None:
                    continue

        key = (headcount, stated)
        if key in seen:
            continue
        seen.add(key)
        expected = inheritance_basic_deduction_yen(headcount)
        if stated != expected:
            issues.append(
                f"相続税の基礎控除の人数と金額が不一致: {headcount}人→"
                f"{expected:,}万円が正、記載は{stated:,}万円"
            )
    return issues


def is_glossary_draft_stub(row: dict[str, str]) -> bool:
    """一覧用 draft 行（詳細記事未執筆）。published または article_title ありは詳細記事扱い。"""
    status = norm(row.get("content_status")).lower()
    if status == "published":
        return False
    if norm(row.get("article_title")):
        return False
    return status in {"", "draft"}


def check_glossary_draft_stub(row: dict[str, str]) -> list[GlossaryRowIssue]:
    """draft 一覧行の最小検証（詳細記事ルールは適用しない）。"""
    issues: list[GlossaryRowIssue] = []
    term = norm(row.get("term"))
    if not term:
        return issues

    def err(msg: str) -> None:
        issues.append(GlossaryRowIssue("ERROR", msg))

    def warn(msg: str) -> None:
        issues.append(GlossaryRowIssue("WARN", msg))

    if not norm(row.get("category")):
        err("category は必須です")
    short_def = norm(row.get("short_def"))
    if not short_def:
        err("short_def は必須です")
    elif len(short_def) < GLOSSARY_MIN_LENGTHS["short_def"]:
        err(
            f"short_def は {GLOSSARY_MIN_LENGTHS['short_def']} 文字以上にしてください"
            f"（現在 {len(short_def)} 文字）"
        )
    if not split_semicolon(norm(row.get("tags"))):
        err("tags は1件以上必須です（セミコロン区切り）")
    importance = norm(row.get("importance"))
    if importance and importance not in GLOSSARY_IMPORTANCE_VALUES:
        warn(f"importance は A / B / C / S のいずれかを推奨します: {importance!r}")
    return issues


def check_glossary_row(
    row: dict[str, str],
    *,
    term_lookup: dict[str, str],
    line: int | None = None,
) -> list[GlossaryRowIssue]:
    """1行分の用語詳細記事ルール。validate_csv と scaffold の双方から利用。"""
    if is_glossary_draft_stub(row):
        return check_glossary_draft_stub(row)

    issues: list[GlossaryRowIssue] = []
    term = norm(row.get("term"))
    if not term:
        return issues

    def err(msg: str) -> None:
        issues.append(GlossaryRowIssue("ERROR", msg))

    def warn(msg: str) -> None:
        issues.append(GlossaryRowIssue("WARN", msg))

    for col in GLOSSARY_BASE_REQUIRED:
        if col not in row:
            err(f"必須列がありません: {col}")

    answer_symbols = frozenset({"○", "〇", "×", "✕", "╳"})
    for col, min_len in GLOSSARY_MIN_LENGTHS.items():
        text = norm(row.get(col))
        if not text:
            err(f"{col} は必須です（全用語を詳細記事として公開）")
            continue
        if col == "example_answer" and text in answer_symbols:
            continue
        if len(text) < min_len:
            err(f"{col} は {min_len} 文字以上にしてください（現在 {len(text)} 文字）")

    importance = norm(row.get("importance"))
    if not importance:
        err("importance は必須です（A / B / C / S）")
    elif importance not in GLOSSARY_IMPORTANCE_VALUES:
        warn(f"importance は A / B / C / S のいずれかを推奨します: {importance!r}")

    tags = split_semicolon(norm(row.get("tags")))
    if not tags:
        err("tags は1件以上必須です（セミコロン区切り）")

    exam_points = split_semicolon(norm(row.get("exam_points")))
    if len(exam_points) < GLOSSARY_MIN_EXAM_POINT_ITEMS:
        err(
            f"exam_points はセミコロン区切りで {GLOSSARY_MIN_EXAM_POINT_ITEMS} 項目以上必須です"
        )
    else:
        for item in exam_points:
            if len(item) < 8:
                err(f"exam_points の各項目は8文字以上にしてください: {item!r}")

    related_labels = split_semicolon(norm(row.get("related_terms")))
    if len(related_labels) < GLOSSARY_MIN_RELATED_TERMS:
        err(
            f"related_terms は登録済み用語を {GLOSSARY_MIN_RELATED_TERMS} 件以上指定してください"
        )
    for label in related_labels:
        if label == term:
            warn(f"related_terms に自分自身 {term!r} が含まれています")
            continue
        if not (term_lookup.get(label) or term_lookup.get(lookup_key(label))):
            err(
                f"related_terms の {label!r} は用語ページにリンク化されません"
                "（登録済み用語名に直してください）"
            )

    category = norm(row.get("category"))
    legal = norm(row.get("legal_basis"))
    if _is_law_heavy(category, importance) and not legal:
        warn(
            f"{category} かつ importance={importance} の用語は legal_basis の記載を推奨します"
        )

    title = norm(row.get("article_title"))
    if title and term not in title and "とは" not in title:
        warn(f"article_title に用語名 {term!r} または「とは」を含めると SEO 上わかりやすくなります")

    for q_col in tuple(f"faq_{n}_question" for n in range(1, GLOSSARY_FAQ_COUNT + 1)):
        q = norm(row.get(q_col))
        if q and not q.endswith(("？", "?")):
            warn(f"{q_col} は疑問形（？）で終えることを推奨します")

    prose_cols = (
        "short_def",
        "definition",
        "explanation",
        "article_lead",
        "term_detail_body",
        "common_mistakes",
        "memory_tip",
        *(f"faq_{n}_answer" for n in range(1, GLOSSARY_FAQ_COUNT + 1)),
    )
    faq_answers: list[str] = []
    for col in prose_cols:
        text = norm(row.get(col))
        if not text:
            continue
        for issue in placeholder_issues(text, col):
            if issue.level == "ERROR":
                err(issue.message)
            else:
                warn(issue.message)
        for issue in readability_issues(text, col):
            warn(issue.message)
        for issue in generic_issues(text, col):
            warn(issue.message)
        if col.endswith("_answer") and col.startswith("faq_"):
            faq_answers.append(text)

    for issue in duplicate_faq_answers(faq_answers):
        warn(issue.message)

    body = norm(row.get("term_detail_body"))
    if body:
        if len(split_paragraphs(body)) < GLOSSARY_PRO["paragraphs_in_body"]:
            err(
                f"term_detail_body は段落を {GLOSSARY_PRO['paragraphs_in_body']} つ以上"
                "（空行区切り \\n\\n）に分けてください"
            )
        for issue in long_sentence_issues(
            body, "term_detail_body", max_chars=GLOSSARY_PRO["max_sentence_chars"]
        ):
            warn(issue.message)
        for issue in concreteness_issues(body, "term_detail_body"):
            warn(issue.message)

    expl = norm(row.get("explanation"))
    if expl:
        for issue in concreteness_issues(expl, "explanation"):
            warn(issue.message)

    if importance in {"A", "S"}:
        if len(exam_points) < GLOSSARY_PRO["exam_points_as"]:
            warn(
                f"importance={importance} の用語は exam_points を {GLOSSARY_PRO['exam_points_as']} 項目以上推奨"
            )
        if len(related_labels) < GLOSSARY_PRO["related_terms_as"]:
            warn(
                f"importance={importance} の用語は related_terms を {GLOSSARY_PRO['related_terms_as']} 件以上推奨"
            )

    if expl and term not in expl and "選択肢" not in expl and "試験" not in expl:
        warn("explanation に試験での出題・選択肢の論点を明示すると専門性が上がります")

    answer = norm(row.get("example_answer"))
    if answer and answer not in {"○", "〇", "×", "✕", "╳"} and len(answer) < 5:
        err("example_answer は ○/× または5文字以上の解説にしてください")

    calc_text = "\n".join(
        norm(row.get(col))
        for col in (
            "short_def",
            "definition",
            "explanation",
            "article_lead",
            "term_detail_body",
            "exam_points",
            "common_mistakes",
            "memory_tip",
            "example_question",
            "example_answer",
            *(f"faq_{n}_answer" for n in range(1, GLOSSARY_FAQ_COUNT + 1)),
        )
    )
    if "基礎控除" in calc_text or "600万" in calc_text:
        seen_calc: set[str] = set()
        for msg in inheritance_basic_deduction_calc_issues(calc_text):
            if msg in seen_calc:
                continue
            seen_calc.add(msg)
            warn(msg)

    _ = line
    return issues
