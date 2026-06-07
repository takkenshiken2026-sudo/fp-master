#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
boiler-master 本番の同期前準備（read/write）。

  python3 sites/boiler-master/migrate_prepare.py --target /path/to/boiler-master.jp
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parents[2]
SITE_DIR = Path(__file__).resolve().parent
DRAFT_CONFIG = SITE_DIR / "site-config.json"

GENRE_MAP = {
    "学習法": "独学対策",
    "科目別対策": "分野別対策",
    "重要論点": "用語整理",
    "試験概要": "試験概要",
    "法令対策": "分野別対策",
    "試験対策": "復習・苦手克服",
    "学習計画": "学習計画",
    "過去問活用": "過去問活用",
    "キャリア": "注意点・更新",
    "受験準備": "受験・申込",
}


def symlink_or_copy(src: Path, dst: Path) -> None:
    if dst.exists() or dst.is_symlink():
        return
    try:
        dst.symlink_to(src.name)
        print(f"symlink: {dst.name} -> {src.name}")
    except OSError:
        shutil.copy2(src, dst)
        print(f"copy: {dst.name} <- {src.name}")


def merge_site_config(target: Path) -> None:
    cfg_path = target / "site-config.json"
    draft = json.loads(DRAFT_CONFIG.read_text(encoding="utf-8"))
    if cfg_path.is_file():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    else:
        cfg = {}
    cfg["guideArticleGenres"] = draft["guideArticleGenres"]
    for key in ("theme", "navigation", "fields", "externalLinks"):
        if key in draft and key not in cfg:
            cfg[key] = draft[key]
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated: {cfg_path} (guideArticleGenres)")


def remap_guide_genres(target: Path) -> None:
    path = target / "data" / "guide_articles.csv"
    if not path.is_file():
        print(f"skip: {path} not found")
        return
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    changed = 0
    for row in rows:
        old = (row.get("genre") or "").strip()
        new = GENRE_MAP.get(old, old)
        if new != old:
            row["genre"] = new
            changed += 1
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"updated: {path} (genre remap: {changed} rows)")


def link_csv_aliases(data_dir: Path) -> None:
    maru = data_dir / "past_questions_marubatsu_all_explanations.csv"
    orig = data_dir / "original_questions.csv"
    if maru.is_file():
        symlink_or_copy(maru, data_dir / "ichimon_questions.csv")
    if orig.is_file():
        symlink_or_copy(orig, data_dir / "practice_questions.csv")


def main() -> int:
    ap = argparse.ArgumentParser(description="boiler-master 同期前準備")
    ap.add_argument("--target", required=True, type=Path)
    args = ap.parse_args()
    target = args.target.resolve()
    if not target.is_dir():
        print(f"error: not a directory: {target}", file=sys.stderr)
        return 1
    merge_site_config(target)
    remap_guide_genres(target)
    link_csv_aliases(target / "data")
    print("done: migrate_prepare")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
