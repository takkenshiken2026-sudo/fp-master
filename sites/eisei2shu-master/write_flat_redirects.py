#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旧フラット URL（articles/foo.html, terms/foo.html）→ ディレクトリ形式へのリダイレクト HTML を生成。

  python3 sites/eisei2shu-master/write_flat_redirects.py --target /path/to/eisei2shu-master
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent

# 移行時にリネームした試験ガイド（旧フラット URL → 新 slug）
LEGACY_ARTICLE_SLUGS: dict[str, str] = {
    "category-kankeihOrei": "category-kankeihorei",
    "category-rodoEisei": "category-rodoeisei",
    "category-rodoSeiri": "category-rodoseiri",
}


def redirect_html(origin: str, section: str, slug: str) -> str:
    dest = f"{origin.rstrip('/')}/{section}/{slug}/"
    rel = f"{slug}/"
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<link rel="canonical" href="{dest}">
<meta http-equiv="refresh" content="0; url={rel}">
<meta name="robots" content="noindex, follow">
<title>移動中…</title>
<script>location.replace("{rel}");</script>
</head>
<body>
<p>ページの場所が変わりました。<a href="{rel}">こちら</a>からお進みください。</p>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, type=Path)
    args = ap.parse_args()
    target = args.target.resolve()
    cfg_path = target / "site-config.json"
    if not cfg_path.is_file():
        print(f"error: missing {cfg_path}", file=sys.stderr)
        return 1
    origin = json.loads(cfg_path.read_text(encoding="utf-8")).get("siteOrigin", "").strip()
    if not origin:
        print("error: siteOrigin empty in site-config.json", file=sys.stderr)
        return 1

    n_art = n_term = n_legacy = 0
    for old, new in LEGACY_ARTICLE_SLUGS.items():
        out = target / "articles" / f"{old}.html"
        out.write_text(redirect_html(origin, "articles", new), encoding="utf-8")
        n_legacy += 1
    ga = target / "data" / "guide_articles.csv"
    if ga.is_file():
        with ga.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                slug = (row.get("slug") or "").strip()
                if not slug:
                    continue
                out = target / "articles" / f"{slug}.html"
                out.write_text(redirect_html(origin, "articles", slug), encoding="utf-8")
                n_art += 1

    gl = target / "data" / "glossary_terms.csv"
    if gl.is_file():
        with gl.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                slug = (row.get("slug") or "").strip()
                if not slug:
                    continue
                out = target / "terms" / f"{slug}.html"
                out.write_text(redirect_html(origin, "terms", slug), encoding="utf-8")
                n_term += 1

    print(f"wrote redirects: articles={n_art} terms={n_term} legacy_renames={n_legacy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
