#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
賃管マスター移行前の read-only チェック（本番ディレクトリは変更しない）。

  python3 sites/chintaikanrishi-master/check_ready.py --target /path/to/chintaikanrishi-master
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parents[2]
SITE_DIR = Path(__file__).resolve().parent
DRAFT_CONFIG = SITE_DIR / "site-config.json"

if str(TEMPLATE_ROOT) not in sys.path:
    sys.path.insert(0, str(TEMPLATE_ROOT))

from tools.template_sync import collect_drift  # noqa: E402


def load_genre_labels(config_path: Path) -> set[str]:
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    return {g["label"] for g in cfg.get("guideArticleGenres", []) if g.get("label")}


def main() -> int:
    ap = argparse.ArgumentParser(description="賃管マスター移行準備チェック（read-only）")
    ap.add_argument("--target", required=True, type=Path, help="本番サイトのルート")
    args = ap.parse_args()
    target = args.target.resolve()
    if not target.is_dir():
        print(f"error: not a directory: {target}", file=sys.stderr)
        return 1

    print(f"target: {target}")
    print(f"draft site-config: {DRAFT_CONFIG}")
    print()

    blockers: list[str] = []
    warnings: list[str] = []

    cfg_at_target = target / "site-config.json"
    if cfg_at_target.is_file():
        print("ok: site-config.json が本番にあります")
        labels = load_genre_labels(cfg_at_target)
    else:
        warnings.append(
            "site-config.json が本番にありません。同期の前に "
            f"cp {DRAFT_CONFIG} {target}/site-config.json を実行してください。"
        )
        labels = load_genre_labels(DRAFT_CONFIG)

    drift = collect_drift(TEMPLATE_ROOT, target)
    problems = [r for r in drift if r[1] not in ("ok",)]
    ok_n = sum(1 for _, s in drift if s == "ok")
    print(f"drift: ok={ok_n} drift={len(problems)} total={len(drift)}")
    if problems:
        for rel, status in problems[:8]:
            print(f"  {status}: {rel}")
        if len(problems) > 8:
            print(f"  ... 他 {len(problems) - 8} 件")
    print()

    ga_path = target / "data" / "guide_articles.csv"
    if ga_path.is_file():
        with ga_path.open(encoding="utf-8-sig", newline="") as f:
            genres = {row.get("genre", "").strip() for row in csv.DictReader(f) if row.get("genre")}
        unknown = sorted(g for g in genres if g and g not in labels)
        if unknown:
            blockers.append(f"guide_articles.csv の未登録 genre: {unknown}")
        else:
            print(f"ok: guide_articles genre は site-config と一致（{len(genres)} 種類）")
    else:
        blockers.append("data/guide_articles.csv がありません")

    gl_path = target / "data" / "glossary_terms.csv"
    template_header = (
        TEMPLATE_ROOT / "data" / "glossary_terms.csv"
    )
    if gl_path.is_file() and template_header.is_file():
        with gl_path.open(encoding="utf-8-sig", newline="") as f:
            prod_cols = set(csv.DictReader(f).fieldnames or [])
        with template_header.open(encoding="utf-8-sig", newline="") as f:
            tmpl_cols = set(csv.DictReader(f).fieldnames or [])
        missing = sorted(tmpl_cols - prod_cols)
        if missing:
            warnings.append(
                "glossary_terms.csv にテンプレ必須列が不足（同期後の validate_csv でエラーになり得る）: "
                + ", ".join(missing[:6])
                + (" ..." if len(missing) > 6 else "")
            )
        else:
            print("ok: glossary_terms.csv の列はテンプレと同等以上")

    for name in (
        "eisei1-master-data.js",
        "index.html",
        "tools/csv_to_chintaikan_eisei_master.py",
    ):
        p = target / name
        print(f"{'ok' if p.is_file() else 'missing'}: {name}（SPA 固有・同期対象外）")

    print()
    print("UI:")
    theme = target / "site-theme.css"
    if theme.is_file():
        print("ok: site-theme.css あり")
    else:
        warnings.append("site-theme.css なし（apply_site_config / build_all で生成）")
    sample = target / "articles" / "exam-overview" / "index.html"
    if sample.is_file():
        html = sample.read_text(encoding="utf-8", errors="replace")
        if 'class="topnav site-shell-header"' in html:
            print("ok: 記事ページは既に topnav（再 build 不要の可能性）")
        elif 'class="site-page-header"' in html:
            warnings.append(
                "記事 HTML は旧 site-page-header → 同期 + build_all で topnav に置き換わります"
            )
    spa = target / "index.html"
    if spa.is_file():
        body = spa.read_text(encoding="utf-8", errors="replace")
        if "site-theme.css" in body:
            print("ok: SPA に site-theme.css リンクあり")
        else:
            warnings.append(
                "SPA に site-theme.css 未リンク（apply_site_config で任意追加。UI_ALIGNMENT.md 参照）"
            )
        if 'id="tnav-orig"' in body and "実践演習" in body:
            print("ok: SPA は「実践演習」表記")
        elif 'id="tnav-orig"' in body and "オリジナル問題" in body:
            warnings.append("SPA が「オリジナル問題」のまま（apply_site_config を実行）")

    print()
    if warnings:
        print("warnings:")
        for w in warnings:
            print(f"  - {w}")
    if blockers:
        print("blockers:")
        for b in blockers:
            print(f"  - {b}")
        print("\n→ 上記を解消してから sync --dry-run → sync --build")
        return 1
    print("→ 同期前の主要ブロッカーはありません。次: SITE.md の手順 1〜3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
