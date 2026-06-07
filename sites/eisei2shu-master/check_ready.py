#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二衛マスター移行前の read-only チェック（本番ディレクトリは変更しない）。

  python3 sites/eisei2shu-master/check_ready.py --target /path/to/eisei2shu-master
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
    ap = argparse.ArgumentParser(description="二衛マスター移行準備チェック（read-only）")
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

    arts = sorted(
        p.stem for p in (target / "articles").glob("*.html") if p.name != "index.html"
    )
    print(f"ok: 試験ガイド（フラット HTML / リダイレクト） {len(arts)} 本")
    gen_dirs = sum(1 for p in (target / "articles").iterdir() if p.is_dir() and (p / "index.html").is_file())
    if gen_dirs:
        print(f"ok: テンプレ生成記事 articles/{{slug}}/ … {gen_dirs} 本")
    else:
        warnings.append("articles/{{slug}}/index.html が未生成 → build_all.py を実行")

    ga_path = target / "data" / "guide_articles.csv"
    if ga_path.is_file():
        with ga_path.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
            genres = {row.get("genre", "").strip() for row in rows if row.get("genre")}
        unknown = sorted(g for g in genres if g and g not in labels)
        if unknown:
            blockers.append(f"guide_articles.csv の未登録 genre: {unknown}")
        else:
            print(f"ok: guide_articles.csv {len(rows)} 本（genre {len(genres)} 種類）")
    else:
        warnings.append(
            "data/guide_articles.csv なし → migrate_import_data.py を実行"
        )

    gl_path = target / "data" / "glossary_terms.csv"
    checklist = target / "docs" / "glossary-terms-checklist.csv"
    if gl_path.is_file():
        print("ok: data/glossary_terms.csv あり")
    elif checklist.is_file():
        with checklist.open(encoding="utf-8-sig", newline="") as f:
            n = sum(1 for _ in csv.DictReader(f))
        warnings.append(
            f"glossary_terms.csv なし（checklist {n} 行 → テンプレ列への変換が必要）"
        )
    else:
        blockers.append("用語データ（glossary_terms.csv または checklist）がありません")

    pq = target / "data" / "past_questions.csv"
    eisei2 = target / "data" / "eisei2_past_questions.csv"
    if pq.is_file():
        print("ok: data/past_questions.csv あり")
    elif eisei2.is_file():
        warnings.append(
            "past_questions.csv なし（migrate_past_questions.py で eisei2 CSV から生成可）"
        )
    else:
        blockers.append("過去問 CSV（past_questions または eisei2_past）がありません")

    q_pages = list((target / "q").rglob("index.html")) if (target / "q").is_dir() else []
    print(f"ok: 過去問 SEO ページ q/ … {len(q_pages)} 件（既存 generator 維持想定）")

    for name in ("eisei2-master-data.js", "index.html", "tools/csv_to_eisei2_master.py"):
        p = target / name
        print(f"{'ok' if p.is_file() else 'missing'}: {name}")

    print()
    print("UI:")
    if (target / "site-theme.css").is_file():
        print("ok: site-theme.css あり")
    else:
        warnings.append("site-theme.css なし（apply_site_config / sync 後に生成）")

    sample_art = target / "articles" / "benkyou-jikan.html"
    if sample_art.is_file():
        html = sample_art.read_text(encoding="utf-8", errors="replace")
        if 'class="topnav site-shell-header"' in html:
            print("ok: 個別記事は既に topnav")
        elif 'class="site-page-header"' in html:
            warnings.append("個別記事は旧 site-page-header（build_all または手動ヘッダー差し替え待ち）")

    if (target / "privacy-terms.html").is_file() and not (target / "privacy.html").is_file():
        print("ok: privacy-terms.html（テンプレ privacy.html とは別運用）")

    print()
    if warnings:
        print("warnings:")
        for w in warnings:
            print(f"  - {w}")
    if blockers:
        print("blockers:")
        for b in blockers:
            print(f"  - {b}")
        print("\n→ 上記を解消してから sync。UI のみなら SITE.md 手順 1〜3b（build_all なし）")
        return 1
    print("→ 移行ビルド可能な状態です。未 push の変更を確認してからデプロイしてください。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
