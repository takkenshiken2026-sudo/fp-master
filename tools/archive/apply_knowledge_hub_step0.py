#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識ハブ Step 0: 全サイト向けの最小インフラ整備。

- build_glossary_pages: compare/numbers/mistakes サブディレクトリを削除しない
- build_all: build_compare_pages → build_numbers_mistakes_pages を glossary の直後に追加
- validate_csv: validate_knowledge_hub を追加
- data/*.csv: テンプレ汎用・宅建サンプル行を archive へ退避（title 一致のみ）

使い方:
  python3 tools/apply_knowledge_hub_step0.py --target /path/to/site [--dry-run]
"""

from __future__ import annotations

import argparse
import csv
import io
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TEMPLATE_COMPARE_TITLES = frozenset(
    {
        "過去問と模擬試験の違い",
        "公式情報と試験要項の違い",
        "合格基準と出題範囲の違い",
        "一問一答と実践演習の違い",
        "復習と学習記録の違い",
        "過去問・実践演習・一問一答の使い分け",
        "受験資格と合格基準の違い",
        "用語解説と比較表の使い分け",
    }
)
TEMPLATE_NUMBERS_TITLES = frozenset(
    {
        "契約前後の説明・交付期限",
        "手付金・報酬の上限",
        "借地借家の年数・期間",
        "成年・後見・保佐の年齢",
        "登記・公告の期間",
        "試験合格の得点・比率",
    }
)
TEMPLATE_MISTAKES_TITLES = frozenset(
    {
        "35条説明と37条書面の取り違え",
        "媒介と代理の混同",
        "地上権と土地賃借権",
        "先取特権の順位",
        "固定資産税と都市計画税",
        "クーリング・オフと手付解除",
    }
)

ARCHIVE_BY_CSV = {
    "comparisons.csv": TEMPLATE_COMPARE_TITLES,
    "numbers.csv": TEMPLATE_NUMBERS_TITLES,
    "mistakes.csv": TEMPLATE_MISTAKES_TITLES,
}

PRESERVED_BLOCK = '''PRESERVED_TERM_SUBDIRS = frozenset({"compare", "numbers", "mistakes", "priority", "samples", "diagram-samples"})
PRESERVED_TERM_HTML = frozenset({"index.html", "g-writing-sample.html", "g-diagram-sample.html"})
'''

OLD_GLOSSARY_CLEANUP = """    for stale in TERMS_DIR.glob("*.html"):
        if stale.name != "index.html":
            stale.unlink()
    for stale in TERMS_DIR.iterdir():
        if stale.is_dir():
            shutil.rmtree(stale)"""

NEW_GLOSSARY_CLEANUP = """    for stale in TERMS_DIR.glob("*.html"):
        if stale.name not in PRESERVED_TERM_HTML:
            stale.unlink()
    for stale in TERMS_DIR.iterdir():
        if stale.is_dir() and stale.name not in PRESERVED_TERM_SUBDIRS:
            shutil.rmtree(stale)"""

HUB_BUILD_SNIPPET = """    run([py, "tools/build_compare_pages.py"])
    run([py, "tools/build_numbers_mistakes_pages.py"])"""

VALIDATE_IMPORT = """from tools.knowledge_hub_rules import (
    HUB_CSV_NAMES,
    HUB_LABELS,
    check_compare_row,
    check_mistakes_row,
    check_numbers_row,
    production_count_message,
)
"""

VALIDATE_METHOD = '''
    def validate_knowledge_hub(self) -> None:
        entries: list[dict[str, str]] = []
        glossary_path = DATA_DIR / "glossary_terms.csv"
        if glossary_path.is_file():
            _, gloss_rows = self.read_csv(glossary_path, set())
            for row in gloss_rows:
                term = self.norm(row.get("term"))
                if term:
                    entries.append({"term": term, "slug_file": "g-dummy.html"})
        term_lookup = make_term_lookup(entries)

        validators = {
            "compare": (check_compare_row, {"title", "category", "col_labels", "compare_rows"}),
            "numbers": (check_numbers_row, {"title", "category", "highlight", "item_rows"}),
            "mistakes": (check_mistakes_row, {"title", "category", "confusion_point", "pattern_rows"}),
        }
        for hub_type, (checker, required) in validators.items():
            path = DATA_DIR / HUB_CSV_NAMES[hub_type]
            if not path.is_file():
                self.warn(
                    path,
                    None,
                    f"{HUB_LABELS[hub_type]} の CSV がありません: {HUB_CSV_NAMES[hub_type]}",
                )
                continue
            _, rows = self.read_csv(
                path, required | {"article_title", "article_lead", "exam_points", "related_terms"}
            )
            published = [row for row in rows if self.norm(row.get("title"))]
            msg = production_count_message(hub_type, len(published))
            if msg:
                self.warn(path, None, msg)
            seen_titles: set[str] = set()
            for idx, row in enumerate(rows, start=2):
                title = self.norm(row.get("title"))
                if not title:
                    continue
                if title in seen_titles:
                    self.error(path, idx, f"title が重複しています: {title}")
                seen_titles.add(title)
                if hasattr(self, "validate_category"):
                    self.validate_category(path, row, idx)
                for issue in checker(row, term_lookup=term_lookup, line=idx):
                    if issue.level == "ERROR":
                        self.error(path, idx, f"[{issue.column}] {issue.message}")
                    else:
                        self.warn(path, idx, f"[{issue.column}] {issue.message}")
'''


def patch_glossary(path: Path, dry_run: bool) -> list[str]:
    text = path.read_text(encoding="utf-8")
    changes: list[str] = []
    if "PRESERVED_TERM_SUBDIRS" in text:
        return changes
    if OLD_GLOSSARY_CLEANUP not in text:
        changes.append("glossary: cleanup block not found (manual merge)")
        return changes
    insert_at = text.find("GLOSSARY_CSV = ")
    if insert_at < 0:
        insert_at = text.find("TERMS_DIR = ")
    if insert_at < 0:
        changes.append("glossary: insert point not found")
        return changes
    text = text[:insert_at] + PRESERVED_BLOCK + "\n" + text[insert_at:]
    text = text.replace(OLD_GLOSSARY_CLEANUP, NEW_GLOSSARY_CLEANUP)
    changes.append("glossary: PRESERVED + safe cleanup")
    if not dry_run:
        path.write_text(text, encoding="utf-8")
    return changes


def patch_build_all(path: Path, dry_run: bool) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if "build_compare_pages" in text:
        return []
    marker = "tools/build_glossary_pages.py"
    needle = f'run([py, "{marker}"])'
    if needle not in text:
        return ["build_all: glossary step not found"]
    replacement = needle + "\n" + HUB_BUILD_SNIPPET
    text = text.replace(needle, replacement, 1)
    if not dry_run:
        path.write_text(text, encoding="utf-8")
    return ["build_all: hub builders after glossary"]


def patch_validate(path: Path, dry_run: bool) -> list[str]:
    text = path.read_text(encoding="utf-8")
    changes: list[str] = []
    if "validate_knowledge_hub" in text:
        return changes
    if "from tools.knowledge_hub_rules import" not in text:
        anchor = "from tools.site_config import"
        if anchor not in text:
            anchor = "from tools.build_glossary_pages import"
        if anchor not in text:
            return ["validate: import anchor not found"]
        text = text.replace(anchor, VALIDATE_IMPORT + "\n" + anchor, 1)
        changes.append("validate: hub imports")
    if "make_term_lookup" not in text:
        text = text.replace(
            "from tools.build_glossary_pages import lookup_key",
            "from tools.build_glossary_pages import lookup_key, make_term_lookup",
            1,
        )
        if "make_term_lookup" not in text:
            text = text.replace(
                "from tools.site_config import",
                "from tools.build_glossary_pages import make_term_lookup\nfrom tools.site_config import",
                1,
            )
        changes.append("validate: make_term_lookup import")
    run_marker = "        self.validate_guide_articles()"
    if run_marker not in text:
        return changes + ["validate: run() marker not found"]
    if "self.validate_knowledge_hub()" not in text:
        text = text.replace(
            run_marker,
            run_marker + "\n        self.validate_knowledge_hub()",
            1,
        )
        changes.append("validate: run() calls hub")
    if "def validate_knowledge_hub" not in text:
        insert_before = "    def run(self) -> int:"
        if insert_before not in text:
            return changes + ["validate: run() def not found"]
        text = text.replace(insert_before, VALIDATE_METHOD + "\n" + insert_before, 1)
        changes.append("validate: method body")
    if not dry_run:
        path.write_text(text, encoding="utf-8")
    return changes


def archive_template_hub_rows(data_dir: Path, dry_run: bool) -> list[str]:
    changes: list[str] = []
    archive_dir = data_dir / "archive" / "hub-template-placeholders"
    stamp = date.today().isoformat()
    for csv_name, titles in ARCHIVE_BY_CSV.items():
        path = data_dir / csv_name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))
        if not rows:
            continue
        fieldnames = rows[0].keys() if rows else []
        kept: list[dict] = []
        removed: list[dict] = []
        for row in rows:
            title = (row.get("title") or "").strip()
            if title in titles:
                removed.append(row)
            else:
                kept.append(row)
        if not removed:
            continue
        changes.append(f"{csv_name}: archived {len(removed)} template row(s)")
        if dry_run:
            continue
        archive_dir.mkdir(parents=True, exist_ok=True)
        arch_path = archive_dir / f"{stamp}-{csv_name}"
        with arch_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            w.writeheader()
            w.writerows(removed)
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            w.writeheader()
            w.writerows(kept)
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply knowledge hub Step 0 to a site repo")
    parser.add_argument("--target", type=Path, required=True, help="Site repository root")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-archive", action="store_true")
    args = parser.parse_args()
    target: Path = args.target.resolve()
    if not (target / "tools").is_dir():
        print(f"Not a site root: {target}", file=sys.stderr)
        return 1

    print(f"{'[dry-run] ' if args.dry_run else ''}Step 0 → {target}")
    all_changes: list[str] = []

    bg = target / "tools/build_glossary_pages.py"
    if bg.is_file():
        all_changes.extend(patch_glossary(bg, args.dry_run))

    ba = target / "tools/build_all.py"
    if ba.is_file():
        all_changes.extend(patch_build_all(ba, args.dry_run))

    vc = target / "tools/validate_csv.py"
    if vc.is_file():
        all_changes.extend(patch_validate(vc, args.dry_run))

    if not args.skip_archive and (target / "data").is_dir():
        all_changes.extend(archive_template_hub_rows(target / "data", args.dry_run))

    if not all_changes:
        print("  (no changes needed)")
    else:
        for c in all_changes:
            print(f"  • {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
