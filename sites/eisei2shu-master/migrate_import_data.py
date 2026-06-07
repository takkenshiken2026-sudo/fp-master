#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二衛マスター（eisei2shu-master）の既存 HTML / CSV をテンプレ形式の data/*.csv に取り込む。

  python3 sites/eisei2shu-master/migrate_import_data.py --target /path/to/eisei2shu-master
  python3 sites/eisei2shu-master/migrate_import_data.py --target /path/to/eisei2shu-master --only glossary
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
from html import unescape
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
TEMPLATE_ROOT = SITE_DIR.parents[1]
DRAFT_CONFIG = SITE_DIR / "site-config.json"

GLOSSARY_HEADER = [
    "term",
    "category",
    "tags",
    "short_def",
    "definition",
    "related_terms",
    "legal_basis",
    "importance",
    "explanation",
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
    "slug",
]

GUIDE_HEADER = [
    "slug",
    "genre",
    "title",
    "meta_description",
    "lead",
    "priority",
    "tags",
    "author_name",
    "author_profile",
    "reviewer_name",
    "reviewer_profile",
    "fact_checked_at",
    "primary_sources",
    "original_note",
    "user_intent",
    "action_items",
    "update_policy",
    "last_reviewed_at",
    "next_review_at",
    "source_checked_at",
    "content_status",
    "revision_note",
    "section_1_heading",
    "section_1_body",
    "section_2_heading",
    "section_2_body",
    "section_3_heading",
    "section_3_body",
    "section_4_heading",
    "section_4_body",
    "section_5_heading",
    "section_5_body",
    "section_6_heading",
    "section_6_body",
    "section_7_heading",
    "section_7_body",
    "faq_1_question",
    "faq_1_answer",
    "faq_2_question",
    "faq_2_answer",
    "related_links",
]

PAST_HEADER = [
    "exam_year",
    "exam_wareki",
    "question_no",
    "type",
    "category",
    "tags",
    "stem",
    "preamble",
    "statement_a",
    "statement_b",
    "statement_c",
    "statement_d",
    "choice_1",
    "choice_2",
    "choice_3",
    "choice_4",
    "choice_5",
    "correct",
    "is_exempt",
    "is_invalidated",
    "note",
    "explanation",
    "explanation_summary",
    "explanation_correct",
    "explanation_choices",
    "explanation_point",
    "related_links",
]


def norm(s: str | None) -> str:
    return (s or "").strip()


def strip_tags(html: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"</p>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return unescape(re.sub(r"\n{3,}", "\n\n", text)).strip()


def first_meta(html: str, name: str) -> str:
    m = re.search(
        rf'<meta\s+name="{re.escape(name)}"\s+content="([^"]*)"',
        html,
        re.I,
    )
    return unescape(m.group(1)).strip() if m else ""


def extract_block(html: str, pattern: str) -> str:
    m = re.search(pattern, html, re.I | re.S)
    return m.group(1).strip() if m else ""


def section_by_id(body: str, sec_id: str) -> str:
    m = re.search(
        rf'<h2[^>]*id="{re.escape(sec_id)}"[^>]*>.*?</h2>(.*?)(?=<h2\b|<div class="related-box"|</article>)',
        body,
        re.I | re.S,
    )
    return strip_tags(m.group(1)) if m else ""


def faq_pairs(body: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for m in re.finditer(
        r'<details\s+class="faq-item"[^>]*>\s*<summary>(.*?)</summary>\s*<div>(.*?)</div>',
        body,
        re.I | re.S,
    ):
        q = strip_tags(m.group(1))
        a = strip_tags(m.group(2))
        if q and a:
            out.append((q, a))
    if out:
        return out
    for m in re.finditer(
        r'"name":\s*"([^"]+)".*?"text":\s*"([^"]+)"',
        body,
        re.S,
    ):
        out.append((unescape(m.group(1)), unescape(m.group(2))))
    return out[:2]


GENRE_ALIASES = {
    "合格基準": "合格・難易度",
    "受験資格": "受験・申込",
    "日程・申込": "受験・申込",
    "試験情報": "試験概要",
}


def infer_genre(slug: str, title: str) -> str:
    s = slug.lower()
    t = title
    if any(k in s for k in ("matome", "まとめ")):
        return "分野別対策"
    if any(k in s for k in ("shiken", "juken", "goukaku", "gokaku", "ninte")):
        if "当日" in t or "会場" in t or "持ち物" in t:
            return "直前・当日"
        if "合格率" in t or "難易" in t:
            return "合格・難易度"
        return "試験概要"
    if any(k in s for k in ("benkyou", "gakushu", "keikaku", "schedule", "jikan")):
        return "学習計画"
    if any(k in s for k in ("kakomon", "saijuken", "mondai")):
        return "過去問活用"
    if any(k in s for k in ("ho-", "law", "horei")):
        return "分野別対策"
    if "独学" in t:
        return "独学対策"
    return "試験対策"


def load_checklist(target: Path) -> dict[str, dict[str, str]]:
    path = target / "docs" / "glossary-terms-checklist.csv"
    out: dict[str, dict[str, str]] = {}
    if not path.is_file():
        return out
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            term = norm(row.get("用語"))
            if term:
                out[term] = row
    return out


def load_slug_by_term(target: Path) -> dict[str, str]:
    path = target / "docs" / "glossary-article-slugs.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {norm(k): norm(v) for k, v in data.items() if norm(k) and norm(v)}


def term_from_title(title: str) -> str:
    t = re.sub(r"【[^】]+】\s*$", "", title).strip()
    t = re.sub(r"とは[？?].*$", "", t).strip()
    return t or title.strip()


def import_glossary(target: Path) -> int:
    checklist = load_checklist(target)
    slug_by_term = load_slug_by_term(target)
    terms_dir = target / "terms"
    rows_out: list[dict[str, str]] = []

    for path in sorted(terms_dir.glob("*.html")):
        if path.name == "index.html":
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        slug = path.stem
        title = extract_block(html, r'<h1\s+class="article-title"[^>]*>(.*?)</h1>')
        if not title:
            title = first_meta(html, "twitter:title") or first_meta(html, "og:title")
        term = next((t for t, s in slug_by_term.items() if s == slug), "")
        if not term:
            term = term_from_title(title)
        category = extract_block(html, r'<span\s+class="meta-category"[^>]*>(.*?)</span>')
        ck = checklist.get(term, {})
        if not category:
            category = norm(ck.get("カテゴリ"))
        if not category or category == "その他":
            category = norm(ck.get("カテゴリ")) or "関係法令"
        body_m = re.search(r'<article\s+class="article-body"[^>]*>(.*)</article>', html, re.I | re.S)
        body = body_m.group(1) if body_m else ""
        lead = strip_tags(
            extract_block(body, r'<p\s+class="article-lead"[^>]*>(.*?)</p>') if body else ""
        )
        overview = section_by_id(body, "overview") or section_by_id(body, "definition")
        exam = section_by_id(body, "exam")
        mistakes = section_by_id(body, "privacy") or section_by_id(body, "mistakes")
        ck = checklist.get(term, {})
        short = norm(ck.get("解説"))[:120] if ck.get("解説") else (lead[:120] if lead else term)
        definition = norm(ck.get("解説")) or overview or lead or term
        faqs = faq_pairs(body)

        rows_out.append(
            {
                "term": term,
                "category": category or "その他",
                "tags": "第二種衛生管理者",
                "short_def": short,
                "definition": definition,
                "related_terms": "",
                "legal_basis": "",
                "importance": "A",
                "explanation": exam or definition,
                "article_title": title or term,
                "article_lead": lead or definition[:200],
                "term_detail_body": overview or definition,
                "exam_points": exam,
                "common_mistakes": mistakes,
                "memory_tip": "",
                "example_question": "",
                "example_answer": "",
                "faq_1_question": faqs[0][0] if len(faqs) > 0 else "",
                "faq_1_answer": faqs[0][1] if len(faqs) > 0 else "",
                "faq_2_question": faqs[1][0] if len(faqs) > 1 else "",
                "faq_2_answer": faqs[1][1] if len(faqs) > 1 else "",
                "slug": slug,
            }
        )

    out_path = target / "data" / "glossary_terms.csv"
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=GLOSSARY_HEADER, lineterminator="\n")
        w.writeheader()
        w.writerows(rows_out)
    print(f"glossary_terms.csv: {len(rows_out)} rows -> {out_path}")
    return len(rows_out)


def import_guide(target: Path) -> int:
    articles_dir = target / "articles"
    rows_out: list[dict[str, str]] = []
    priority = 10

    for path in sorted(articles_dir.glob("*.html")):
        if path.name == "index.html":
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        slug = path.stem
        title = extract_block(html, r'<h1\s+class="article-title"[^>]*>(.*?)</h1>')
        if not title:
            title = re.sub(r"\s*｜.*$", "", first_meta(html, "twitter:title"))
        meta = first_meta(html, "description")
        category = extract_block(html, r'<span\s+class="meta-category"[^>]*>(.*?)</span>')
        genre = GENRE_ALIASES.get(category, category) if category else infer_genre(slug, title)
        updated = ""
        um = re.search(r"更新日[：:]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", html)
        if um:
            updated = um.group(1)
        body_m = re.search(r'<article\s+class="article-body"[^>]*>(.*)</article>', html, re.I | re.S)
        body = body_m.group(1) if body_m else ""
        sections: list[tuple[str, str]] = []
        for hm in re.finditer(r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2\b|</article>)", body, re.I | re.S):
            heading = strip_tags(hm.group(1))
            if heading in (
                "この記事の信頼性について",
                "公式情報の確認",
                "記事の基本情報",
                "この記事でできること",
            ):
                continue
            sec_body = strip_tags(hm.group(2))
            if sec_body:
                sections.append((heading, sec_body))
        lead = ""
        if body:
            pm = re.search(r"<p[^>]*>(.*?)</p>", body, re.I | re.S)
            if pm:
                lead = strip_tags(pm.group(1))
        if not lead and sections:
            lead = sections[0][1][:300]
        if not lead:
            lead = title

        row: dict[str, str] = {
            "slug": slug,
            "genre": genre,
            "title": title,
            "meta_description": meta,
            "lead": lead,
            "priority": str(priority),
            "tags": "第二種衛生管理者;試験ガイド",
            "author_name": "二衛マスター編集部",
            "author_profile": "第二種衛生管理者試験の学習コンテンツを整理する編集チーム",
            "reviewer_name": "二衛マスター確認担当",
            "reviewer_profile": "公開前に公式情報と内部リンクを確認",
            "fact_checked_at": updated or "2026-05-19",
            "primary_sources": "安全衛生技術試験協会（公式）|https://www.jissh.or.jp/",
            "original_note": "旧 articles/*.html から移行",
            "user_intent": f"{title}について試験前に整理したい",
            "action_items": "公式情報を確認する;関連用語と過去問で定着する",
            "update_policy": "試験要項・公式情報の改定時に見直す",
            "last_reviewed_at": updated or "2026-05-19",
            "next_review_at": "2026-08-19",
            "source_checked_at": updated or "2026-05-19",
            "content_status": "published",
            "revision_note": "migrate_import_data.py で移行",
            "faq_1_question": f"{title}の公式情報はどこで確認しますか？",
            "faq_1_answer": "安全衛生技術試験協会の公式サイトおよび厚生労働省の関連ページで最新情報を確認してください。",
            "faq_2_question": "この記事のあとに何を学習するとよいですか？",
            "faq_2_answer": "関連する用語解説と過去問演習で、出題形式に合わせた定着を進めてください。",
            "related_links": "",
        }
        for i in range(1, 8):
            row[f"section_{i}_heading"] = ""
            row[f"section_{i}_body"] = ""
        for i, (h, b) in enumerate(sections[:7], start=1):
            row[f"section_{i}_heading"] = h
            row[f"section_{i}_body"] = b
        if not row["section_1_body"]:
            row["section_1_heading"] = "概要"
            row["section_1_body"] = lead or title
        rows_out.append(row)
        priority += 10

    out_path = target / "data" / "guide_articles.csv"
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=GUIDE_HEADER, lineterminator="\n")
        w.writeheader()
        w.writerows(rows_out)
    print(f"guide_articles.csv: {len(rows_out)} rows -> {out_path}")
    return len(rows_out)


def import_past(target: Path) -> int:
    script = SITE_DIR / "migrate_past_questions.py"
    if not script.is_file():
        print(f"error: missing {script}", file=sys.stderr)
        return 1
    import subprocess

    r = subprocess.run(
        [sys.executable, str(script), "--root", str(target)],
        check=False,
    )
    if r.returncode != 0:
        return 0
    with (target / "data" / "past_questions.csv").open(encoding="utf-8", newline="") as f:
        n = sum(1 for _ in csv.DictReader(f))
    print(f"past_questions.csv: {n} rows (via migrate_past_questions.py)")
    return n


def copy_stubs(target: Path) -> None:
    for name in ("practice_questions.stub.csv", "ichimon_questions.stub.csv"):
        stub = SITE_DIR / name
        dst_name = name.replace(".stub.csv", ".csv")
        dst = target / "data" / dst_name
        if stub.is_file() and not dst.is_file():
            shutil.copy2(stub, dst)
            print(f"{dst_name}: stub -> {dst}")


def main() -> int:
    ap = argparse.ArgumentParser(description="二衛マスター data CSV 移行")
    ap.add_argument("--target", required=True, type=Path)
    ap.add_argument(
        "--only",
        choices=("all", "glossary", "guide", "past", "config", "stubs"),
        default="all",
    )
    args = ap.parse_args()
    target = args.target.resolve()
    if not target.is_dir():
        print(f"error: not a directory: {target}", file=sys.stderr)
        return 1

    only = args.only
    if only in ("all", "config"):
        shutil.copy2(DRAFT_CONFIG, target / "site-config.json")
        print(f"site-config.json -> {target / 'site-config.json'}")
    if only in ("all", "stubs"):
        copy_stubs(target)
    if only in ("all", "glossary"):
        import_glossary(target)
    if only in ("all", "guide"):
        import_guide(target)
    if only in ("all", "past"):
        import_past(target)
    if only == "all":
        copy_stubs(target)

    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
