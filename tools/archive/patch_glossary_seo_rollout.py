#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""site-only 保護された build_glossary_pages.py に SEO editorial + prose 展開パッチを当てる。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def patch(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    changes: list[str] = []

    if "from tools.seo_editorial_chrome import" not in text:
        text = text.replace(
            "from tools.knowledge_hub_tabs import knowledge_hub_tab_hrefs, knowledge_hub_tabs_html\n",
            "from tools.knowledge_hub_tabs import knowledge_hub_tab_hrefs, knowledge_hub_tabs_html\n"
            "from tools.seo_editorial_chrome import (  # noqa: E402\n"
            "    seo_editorial_head_fonts,\n"
            "    seo_editorial_stylesheet_links,\n"
            ")\n",
        )
        changes.append("seo_editorial_chrome import")

    if "def rel_editorial_css" not in text:
        text = text.replace(
            "def rel_theme_css(rel_file: Path) -> str:\n"
            "    depth = len(rel_file.parent.parts)\n"
            '    return "/".join([".."] * depth) + "/site-theme.css"\n\n\n',
            "def rel_theme_css(rel_file: Path) -> str:\n"
            "    depth = len(rel_file.parent.parts)\n"
            '    return "/".join([".."] * depth) + "/site-theme.css"\n\n\n'
            "def rel_editorial_css(rel_file: Path) -> str:\n"
            "    return seo_editorial_stylesheet_links(rel_file, site_pages_ver=TERMS_INDEX_CSS_VER)\n\n\n"
            "HEAD_FONTS = seo_editorial_head_fonts()\n\n\n",
        )
        changes.append("rel_editorial_css")

    new_points = """    points = study_points(explanation)
    from tools.knowledge_hub_seo import (  # noqa: E402
        glossary_exam_points_body_html,
        glossary_memory_body_html,
        glossary_mistakes_body_html,
        hub_prose_html,
    )

    points_html = glossary_exam_points_body_html(entry)
    if not points_html and points:
        points_html = hub_prose_html([p for p in points])
"""
    old_points_variants = [
        """    points = study_points(explanation)
    points_html = ""
    if exam_points:
        points_html = semicolon_list_html(exam_points)
    elif points:
        points_html = '<ol class="term-point-list">' + "".join(f"<li>{html.escape(p)}</li>" for p in points) + "</ol>"
""",
        """    points = study_points(explanation)
    points_html = ""
    if exam_points:
        points_html = semicolon_list_html(exam_points)
    elif points:
        points_html = '<ol class="term-point-list">' + "".join(f"<li>{html.escape(p)}</li>" for p in points) + "</ol>"
    detail_html = text_paragraphs(term_detail_body or definition)
""",
    ]
    if "glossary_exam_points_body_html" not in text:
        for old_points in old_points_variants:
            if old_points in text:
                replacement = new_points
                if "detail_html = text_paragraphs" in old_points:
                    replacement += "    detail_html = text_paragraphs(term_detail_body or definition)\n"
                text = text.replace(old_points, replacement)
                changes.append("glossary prose points")
                break

    new_mistakes = """    mistakes_html = glossary_mistakes_body_html(entry)
    if not mistakes_html and common_mistakes:
        mistakes_html = text_paragraphs(common_mistakes)
    memory_html = glossary_memory_body_html(entry)
"""
    mistake_variants = [
        """    mistakes_html = semicolon_field_html(common_mistakes) or text_paragraphs(common_mistakes)
    if memory_tip:
        listed = semicolon_field_html(memory_tip)
        memory_html = listed if listed else text_paragraphs(memory_tip)
    else:
        memory_html = ""
""",
        """    mistakes_html = text_paragraphs(common_mistakes)
    if memory_tip:
        mem_paras = [p.strip() for p in re.split(r"\\n{2,}|\\n", memory_tip.strip()) if p.strip()]
        memory_html = "".join(
            f"<p>{html.escape(p)}</p>" for p in mem_paras
        )
    else:
        memory_html = ""
""",
        """    mistakes_html = (
        semicolon_list_html(common_mistakes)
        if common_mistakes and ("；" in common_mistakes or ";" in common_mistakes)
        else text_paragraphs(common_mistakes)
    )
    exam_angle_html = (
        semicolon_list_html(explanation)
        if explanation and ("；" in explanation or ";" in explanation)
        else text_paragraphs(explanation)
    )
    memory_html = memory_tip_html(memory_tip)
""",
    ]
    for old_mistakes in mistake_variants:
        if old_mistakes in text and "glossary_mistakes_body_html" not in text:
            if "exam_angle_html" in old_mistakes:
                text = text.replace(
                    old_mistakes,
                    new_mistakes.replace(
                        "    memory_html = glossary_memory_body_html(entry)\n",
                        "    memory_html = glossary_memory_body_html(entry)\n"
                        "    if not memory_html and memory_tip:\n"
                        "        memory_html = memory_tip_html(memory_tip)\n"
                        "    exam_angle_html = hub_prose_html(split_semicolon(explanation)) if explanation else \"\"\n"
                        "    if not exam_angle_html and explanation:\n"
                        "        exam_angle_html = text_paragraphs(explanation)\n",
                    ),
                )
            else:
                text = text.replace(old_mistakes, new_mistakes)
            changes.append("glossary prose mistakes/memory")
            break

    key_points_block = """    key_points_source = split_semicolon(exam_points)[:5]
    if not key_points_source:
        key_points_source = points[:3]
    if not key_points_source:
        key_points_source = [
            f"{term}の定義と位置づけを確認する",
            "試験で問われやすい条件や表現を整理する",
            "頻出の誤り選択肢や混同しやすい点を復習する",
        ]
    if not any("過去問" in item for item in key_points_source):
        key_points_source = [*key_points_source, "関連する用語解説や過去問へ進む"]
    from tools.knowledge_hub_seo import seo_key_points_box_html

    key_points_intro = f"この記事では、{term}の意味と試験での見方を、問題の解説に沿って整理します。"
    key_points_html = seo_key_points_box_html(
        key_points_source[:5],
        intro=key_points_intro,
    )

    content_sections: list[str] = []"""
    if "key_points_html =" not in text:
        old_can_do = re.search(
            r"    (?:action_points = split_semicolon\(exam_points\)\[:3\].*?"
            r"    )?can_do_html = \(.*?\)\n\n"
            r"    content_sections: list\[str\] = \[\]",
            text,
            re.S,
        )
        if old_can_do:
            text = text[: old_can_do.start()] + key_points_block + text[old_can_do.end() :]
            changes.append("key_points box")

    if '("action-box-title", "この記事でできること")' in text:
        text = text.replace(
            '("action-box-title", "この記事でできること"),',
            "",
        )
        changes.append("toc action-box removed")
    if '("key-points-title", "この記事の要点")' not in text:
        text = text.replace(
            '    toc_items: list[tuple[str, str]] = [\n'
            '        ("quality-panel-title", "この記事の信頼性について"),',
            '    toc_items: list[tuple[str, str]] = [\n'
            '        ("key-points-title", "この記事の要点"),\n'
            '        ("quality-panel-title", "この記事の信頼性について"),',
        )
        changes.append("toc key_points")

    if "{can_do_html}" in text:
        text = text.replace(
            "    {toc_html}\n    {quality_html}\n    {can_do_html}\n",
            "    {toc_html}\n    {key_points_html}\n    {quality_html}\n",
        )
        changes.append("template key_points")
    elif "{key_points_html}" in text and "can_do_html" in text:
        # 部分適用済み: can_do ブロックだけ残っている
        pass

    if "css_href = rel_css(rel_path)" in text:
        text = text.replace(
            "    css_href = rel_css(rel_path)",
            "    css_links = rel_editorial_css(rel_path)",
        )
        text = text.replace(
            "{HEAD_FONTS}\n<link rel=\"stylesheet\" href=\"{html.escape(css_href)}\">\n"
            "<link rel=\"stylesheet\" href=\"{html.escape(theme_href)}\">",
            "{HEAD_FONTS}\n{css_links}\n<link rel=\"stylesheet\" href=\"{html.escape(theme_href)}\">",
        )
        changes.append("editorial css links")

    if "def load_glossary_entries" not in text:
        entry_loop = re.search(
            r"    rows = load_glossary_rows\(\)\n"
            r"    used_slugs: dict\[str, str\] = \{\}\n"
            r"    entries: list\[dict\] = \[\]\n"
            r"    for i, row in enumerate\(rows, start=2\):.*?^\        \)\n\n"
            r"    term_lookup = make_term_lookup\(entries\)",
            text,
            re.S | re.M,
        )
        if entry_loop:
            load_fn = '''def load_glossary_entries(*, strict: bool = True) -> list[dict]:
    """CSV から slug_file 付き用語エントリ一覧を返す。"""
    rows = load_glossary_rows()
    used_slugs: dict[str, str] = {}
    entries: list[dict] = []
    for i, row in enumerate(rows, start=2):
        term = norm(row.get("term"))
        if not term:
            if strict:
                raise ValueError(f"line {i}: term が空です")
            continue
        legacy_slug = norm(row.get("slug")) or norm(row.get("url_slug"))
        if legacy_slug:
            if strict and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", legacy_slug):
                raise ValueError(f"line {i}: slug は半角英数字とハイフンのみ: {legacy_slug!r}")
            slug_file = f"{legacy_slug}.html"
            if strict and slug_file in used_slugs:
                raise ValueError(f"line {i}: slug が重複しています: {legacy_slug}")
            used_slugs[slug_file] = term
        else:
            slug_file = term_slug(term, used_slugs) + ".html"
        entries.append(
            {
                "term": term,
                "category": norm(row.get("category")),
                "tags": norm(row.get("tags")),
                "short_def": norm(row.get("short_def")),
                "definition": norm(row.get("definition")),
                "related_terms": norm(row.get("related_terms")),
                "legal_basis": norm(row.get("legal_basis")),
                "importance": norm(row.get("importance")),
                "explanation": norm(row.get("explanation")),
                "article_title": norm(row.get("article_title")),
                "article_lead": norm(row.get("article_lead")),
                "term_detail_body": norm(row.get("term_detail_body")),
                "exam_points": norm(row.get("exam_points")),
                "common_mistakes": norm(row.get("common_mistakes")),
                "memory_tip": norm(row.get("memory_tip")),
                "example_question": norm(row.get("example_question")),
                "example_answer": norm(row.get("example_answer")),
                "faq_1_question": norm(row.get("faq_1_question")),
                "faq_1_answer": norm(row.get("faq_1_answer")),
                "faq_2_question": norm(row.get("faq_2_question")),
                "faq_2_answer": norm(row.get("faq_2_answer")),
                "faq_3_question": norm(row.get("faq_3_question")),
                "faq_3_answer": norm(row.get("faq_3_answer")),
                "faq_4_question": norm(row.get("faq_4_question")),
                "faq_4_answer": norm(row.get("faq_4_answer")),
                "slug_file": slug_file,
                "field_hub": field_hub_slug(norm(row.get("category"))),
                "fact_checked_at": norm(row.get("fact_checked_at")),
                "last_reviewed_at": norm(row.get("last_reviewed_at")),
            }
        )
    return entries


'''
            text = text.replace(entry_loop.group(0), "    entries = load_glossary_entries()\n    term_lookup = make_term_lookup(entries)")
            text = text.replace("def main() -> int:", load_fn + "def main() -> int:", 1)
            changes.append("load_glossary_entries")

    old_field_hub = (
        '    hub_tabs = knowledge_hub_tabs_html(\n'
        '        current="terms",\n'
        '        **knowledge_hub_tab_hrefs(here="field"),\n'
        "    )"
    )
    new_field_hub = (
        '    hub_tabs = knowledge_hub_tabs_html(\n'
        '        current="field",\n'
        '        **knowledge_hub_tab_hrefs(here="field"),\n'
        "    )"
    )
    if old_field_hub in text:
        text = text.replace(old_field_hub, new_field_hub)
        changes.append("field hub tab current=field")

    if changes:
        path.write_text(text, encoding="utf-8")
    return changes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=Path, required=True)
    args = ap.parse_args()
    path = args.target / "tools/build_glossary_pages.py"
    if not path.is_file():
        print(f"missing: {path}", file=sys.stderr)
        return 1
    changes = patch(path)
    if changes:
        print(f"patched {path}: {', '.join(changes)}")
    else:
        print(f"no changes: {path} (already patched?)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
