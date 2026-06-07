#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
boiler-master 移行前チェック（本番は --target のみ変更、migrate_prepare 未実行時は警告）。

  python3 sites/boiler-master/check_ready.py --target /path/to/boiler-master.jp
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
    ap = argparse.ArgumentParser(description="boiler-master 移行準備チェック")
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
    labels = load_genre_labels(cfg_at_target if cfg_at_target.is_file() else DRAFT_CONFIG)
    if not cfg_at_target.is_file() or "guideArticleGenres" not in json.loads(
        cfg_at_target.read_text(encoding="utf-8")
    ):
        warnings.append("site-config.json に guideArticleGenres なし → migrate_prepare を先に実行")

    drift = collect_drift(TEMPLATE_ROOT, target)
    problems = [r for r in drift if r[1] != "ok"]
    print(f"drift: ok={len(drift) - len(problems)} drift={len(problems)} total={len(drift)}")

    ga_path = target / "data" / "guide_articles.csv"
    if ga_path.is_file():
        with ga_path.open(encoding="utf-8-sig", newline="") as f:
            genres = {row.get("genre", "").strip() for row in csv.DictReader(f) if row.get("genre")}
        unknown = sorted(g for g in genres if g and g not in labels)
        if unknown:
            blockers.append(f"guide_articles.csv の未登録 genre: {unknown}")
        else:
            print(f"ok: guide genres（{len(genres)} 種類）")

    for alias, src in (
        ("ichimon_questions.csv", "past_questions_marubatsu_all_explanations.csv"),
        ("practice_questions.csv", "original_questions.csv"),
    ):
        p = target / "data" / alias
        if not p.exists():
            warnings.append(f"data/{alias} なし（migrate_prepare で {src} からリンク）")

    if blockers:
        print("blockers:")
        for b in blockers:
            print(f"  - {b}")
        return 1
    if warnings:
        print("warnings:")
        for w in warnings:
            print(f"  - {w}")
    print("→ migrate_prepare → sync → cp build_all → build_all")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
