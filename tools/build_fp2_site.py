#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP2級サイト（/fp2/）を fp2/ 配下にビルドする。"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP2 = ROOT / "fp2"
FP2_DATA = FP2 / "data"

SHELL_FILES = (
    "index.html",
    "about.html",
    "privacy.html",
    "related-sites.html",
    "site-pages.css",
    "site-analytics.js",
    "site-q-index.js",
    "site-terms-index.js",
    "site-compare-index.js",
    "site-knowledge-hub-index.js",
    "site-priority-index.js",
    "seo-editorial.css",
    "favicon.ico",
    "robots.txt",
    ".nojekyll",
)

STUB_CSVS: dict[str, list[str]] = {
    "glossary_terms.csv": [
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
        "faq_3_question",
        "faq_3_answer",
        "faq_4_question",
        "faq_4_answer",
        "diagram_id",
    ],
    "guide_articles.csv": [
        "slug",
        "genre",
        "title",
        "meta_description",
        "lead",
        "priority",
        "tags",
        "section_1_heading",
        "section_1_body",
    ],
}


def fp2_env() -> dict[str, str]:
    return {
        **os.environ,
        "EXAM_SITE_ROOT": str(FP2.resolve()),
        "PYTHONPATH": str(ROOT),
    }


def run(cmd: list[str], *, optional: bool = False) -> bool:
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=ROOT, env=fp2_env())
    if proc.returncode != 0:
        if optional:
            print(f"  (optional step failed: {' '.join(cmd)})", file=sys.stderr)
            return True
        return False
    return True


def ensure_stub_csvs() -> None:
    FP2_DATA.mkdir(parents=True, exist_ok=True)
    for name, columns in STUB_CSVS.items():
        path = FP2_DATA / name
        if path.is_file():
            continue
        path.write_text(",".join(columns) + "\n", encoding="utf-8")


def sync_shell_files() -> None:
    for name in SHELL_FILES:
        src = ROOT / name
        dst = FP2 / name
        if not src.is_file():
            continue
        shutil.copy2(src, dst)


def sync_brand_assets() -> None:
    src = ROOT / "assets" / "brand"
    if not src.is_dir():
        return
    dst = FP2 / "assets" / "brand"
    if dst.is_dir():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    FP2.mkdir(parents=True, exist_ok=True)
    ensure_stub_csvs()
    sync_shell_files()
    sync_brand_assets()

    py = sys.executable
    steps: list[tuple[list[str], bool]] = [
        ([py, "tools/import_fp2_past_questions.py"], False),
        ([py, "tools/audit_fp2_glossary_catalog.py", "--write-catalog"], False),
        ([py, "tools/import_fp2_glossary_catalog.py"], False),
        ([py, "tools/validate_csv.py", "--scope", "questions"], False),
        ([py, "tools/validate_practice_questions.py"], False),
        ([py, "tools/generate_brand_assets.py", "--target", str(FP2.resolve())], True),
        ([py, "tools/apply_site_config.py"], False),
        ([py, "tools/csv_to_exam_site_past_js.py"], False),
        ([py, "tools/csv_to_exam_site_ichimondou_js.py"], False),
        ([py, "tools/build_past_question_pages.py"], False),
        ([py, "tools/build_practice_ichimon_pages.py"], False),
        ([py, "tools/build_article_pages.py"], False),
        ([py, "tools/build_glossary_pages.py"], False),
        ([py, "tools/build_sitemap.py"], True),
        ([py, "tools/validate_site_integration.py"], False),
    ]
    for cmd, optional in steps:
        if not run(cmd, optional=optional):
            return 1

    print(f"FP2 site built under {FP2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
