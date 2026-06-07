#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一衛マスター移行前の read-only チェック。"""

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
    ap = argparse.ArgumentParser(description="一衛マスター移行準備チェック（read-only）")
    ap.add_argument("--target", required=True, type=Path)
    args = ap.parse_args()
    target = args.target.resolve()
    if not target.is_dir():
        print(f"error: not a directory: {target}", file=sys.stderr)
        return 1

    print(f"target: {target}")
    blockers: list[str] = []
    warnings: list[str] = []

    cfg_at_target = target / "site-config.json"
    if cfg_at_target.is_file():
        print("ok: site-config.json")
        labels = load_genre_labels(cfg_at_target)
    else:
        warnings.append(f"site-config.json なし → cp {DRAFT_CONFIG} {target}/")
        labels = load_genre_labels(DRAFT_CONFIG)

    drift = collect_drift(TEMPLATE_ROOT, target)
    problems = [r for r in drift if r[1] != "ok"]
    print(f"drift: ok={sum(1 for _, s in drift if s == 'ok')} drift={len(problems)} total={len(drift)}")

    for name, path in (
        ("guide_articles.csv", target / "data" / "guide_articles.csv"),
        ("glossary_terms.csv", target / "data" / "glossary_terms.csv"),
        ("past_questions.csv", target / "data" / "past_questions.csv"),
    ):
        if path.is_file():
            with path.open(encoding="utf-8-sig", newline="") as f:
                n = sum(1 for _ in csv.DictReader(f))
            print(f"ok: {name} ({n} rows)")
        else:
            blockers.append(f"{name} がありません（migrate_import_data.py を実行）")

    ga = target / "data" / "guide_articles.csv"
    if ga.is_file():
        with ga.open(encoding="utf-8-sig", newline="") as f:
            genres = {row.get("genre", "").strip() for row in csv.DictReader(f) if row.get("genre")}
        unknown = sorted(g for g in genres if g and g not in labels)
        if unknown:
            blockers.append(f"未登録 genre: {unknown}")

    if blockers:
        print("blockers:")
        for b in blockers:
            print(f"  - {b}")
        return 1
    if warnings:
        print("warnings:")
        for w in warnings:
            print(f"  - {w}")
    print("→ sync --dry-run の準備 OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
