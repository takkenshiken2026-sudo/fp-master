#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP2級用語カタログを fp2/data/glossary_terms.csv に投入する（一覧公開用 draft 行）."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP2 = ROOT / "fp2"
FP2_DATA = FP2 / "data"
CATALOG_CSV = FP2_DATA / "fp2_terms_catalog.csv"
CATALOG_MASTER_CSV = FP2_DATA / "fp2_terms_catalog_master.csv"
GLOSSARY_CSV = FP2_DATA / "glossary_terms.csv"
FP3_CATALOG = ROOT / "data" / "fp3_terms_catalog.csv"
FP3_GLOSSARY = ROOT / "data" / "glossary_terms.csv"
ADD_CANDIDATES_CSV = FP2_DATA / "fp2_glossary_add_candidates.csv"

# fp3_terms_catalog.csv でカンマ入り数値が列分割された行の修復
CATALOG_TERM_FIXES: dict[str, str] = {
    "3": "3,000万円特別控除",
}

CATALOG_DEF_FIXES: dict[str, str] = {
    "ペイオフ": (
        "金融機関が破綻した際に預金保険機構が1金融機関につき元本1000万円まで"
        "（利子を含め1200万円まで）を保護する制度。"
    ),
    "新NISA": (
        "2024年から始まった恒久化されたNISA制度。"
        "年間360万円・生涯1800万円まで非課税枠がある。"
    ),
    "基礎控除": (
        "すべての納税者に認められる控除。"
        "合計所得金額2400万円以下なら48万円、以降段階的に減少する。"
    ),
    "3,000万円特別控除": (
        "居住用財産の譲渡所得について、3000万円まで特別控除できる制度。"
    ),
    "相続税の基礎控除": (
        "相続税の課税遺産総額から差し引ける控除。"
        "「3000万円＋600万円×法定相続人の数」が基本控除額となる。"
    ),
    "相続時精算課税制度": (
        "60歳以上の親・祖父母から18歳以上の子・孫への贈与に適用できる制度。"
        "2500万円まで非課税、超過分は20%の税率で精算課税される。"
    ),
    "教育資金の一括贈与の非課税特例": (
        "祖父母等から30歳未満の孫等への教育資金の一括贈与について"
        "1500万円まで非課税とする特例。"
    ),
    "結婚・子育て資金の一括贈与の非課税特例": (
        "祖父母等から18歳以上50歳未満の子・孫への結婚・子育て資金の贈与について"
        "1000万円まで非課税とする特例。"
    ),
    "配偶者への居住用不動産の贈与": (
        "婚姻期間20年以上の配偶者に居住用不動産または購入資金を贈与する場合、"
        "2000万円までの控除などの特例がある。"
    ),
}

DEFAULT_EXAM_POINTS = (
    "{term}は{category}分野でFP2級学科に出題されやすい;"
    "四択では定義の言い換え・数値・例外の区別が問われやすい"
)
DEFAULT_EXPLANATION = (
    "{term}が出る問題では、定義の言い換え・数値や期限の条件・"
    "似た用語との違いが問われやすいです。"
    "FP2級学科では{category}分野の計算・制度理解とセットで確認してください。"
)


@dataclass
class CatalogEntry:
    term: str
    category: str
    short_def: str
    tier: str = ""
    importance: str = ""


def norm(value: object) -> str:
    return str(value or "").strip()


def adapt_fp2_text(text: str) -> str:
    if not text:
        return text
    out = text.replace("（FP3級）", "（FP2級）")
    out = out.replace("FP3級", "FP2級")
    out = out.replace("FP3", "FP2")
    return out


def load_fieldnames() -> list[str]:
    if FP3_GLOSSARY.is_file():
        with FP3_GLOSSARY.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                fields = list(reader.fieldnames)
                if "content_status" not in fields:
                    fields.append("content_status")
                return fields
    return [
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
        "slug",
        "author_name",
        "reviewer_name",
        "fact_checked_at",
        "primary_sources",
        "content_status",
    ]


def load_fp3_lookup() -> dict[str, dict[str, str]]:
    if not FP3_GLOSSARY.is_file():
        return {}
    with FP3_GLOSSARY.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return {norm(r.get("term")): r for r in rows if norm(r.get("term"))}


def read_catalog(path: Path) -> list[CatalogEntry]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out: list[CatalogEntry] = []
    for row in rows:
        term = norm(row.get("term"))
        category = norm(row.get("category"))
        short_def = norm(row.get("short_def"))
        if term in CATALOG_TERM_FIXES:
            term = CATALOG_TERM_FIXES[term]
        if term in CATALOG_DEF_FIXES:
            short_def = CATALOG_DEF_FIXES[term]
        if not term or not category or not short_def:
            raise ValueError(f"用語・分野・定義のいずれかが空です: {row!r}")
        out.append(
            CatalogEntry(
                term=term,
                category=category,
                short_def=short_def,
                tier=norm(row.get("tier")),
                importance=norm(row.get("importance")),
            )
        )
    return out


def load_add_candidates() -> list[CatalogEntry]:
    if not ADD_CANDIDATES_CSV.is_file():
        return []
    with ADD_CANDIDATES_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out: list[CatalogEntry] = []
    for row in rows:
        term = norm(row.get("term"))
        category = norm(row.get("category"))
        short_def = norm(row.get("short_def"))
        if not term or not category or not short_def:
            continue
        out.append(
            CatalogEntry(
                term=term,
                category=category,
                short_def=short_def,
                tier=norm(row.get("suggested_tier")) or "A",
                importance="A",
            )
        )
    return out


def ensure_catalog(*, force: bool = False) -> None:
    FP2_DATA.mkdir(parents=True, exist_ok=True)
    if CATALOG_CSV.is_file() and not force:
        return
    if not FP3_CATALOG.is_file():
        raise FileNotFoundError(FP3_CATALOG)
    shutil.copy2(FP3_CATALOG, CATALOG_CSV)
    print(f"Created {CATALOG_CSV} from {FP3_CATALOG}")


def build_row(
    entry: CatalogEntry,
    *,
    fieldnames: list[str],
    fp3: dict[str, str] | None,
) -> dict[str, str]:
    term = entry.term
    category = entry.category
    short_def = entry.short_def
    row = {col: "" for col in fieldnames}
    definition = short_def
    if fp3:
        fp3_def = norm(fp3.get("definition"))
        if fp3_def and len(fp3_def) >= len(definition):
            definition = adapt_fp2_text(fp3_def)

    exam_points = ""
    explanation = ""
    if fp3:
        exam_points = adapt_fp2_text(norm(fp3.get("exam_points")))
        explanation = adapt_fp2_text(norm(fp3.get("explanation")))
    if not exam_points:
        exam_points = DEFAULT_EXAM_POINTS.format(term=term, category=category)
    if not explanation:
        explanation = DEFAULT_EXPLANATION.format(term=term, category=category)

    catalog_importance = entry.importance
    fp3_importance = norm(fp3.get("importance")) if fp3 else ""
    importance = catalog_importance or fp3_importance or "B"

    row.update(
        {
            "term": term,
            "category": category,
            "tags": "FP2級;用語",
            "short_def": short_def,
            "definition": definition,
            "importance": importance,
            "explanation": explanation,
            "exam_points": exam_points,
            "content_status": "draft",
        }
    )
    return row


def load_preserved_glossary_rows() -> dict[str, dict[str, str]]:
    """執筆済み行（published または article_title あり）を term → row で返す。"""
    if not GLOSSARY_CSV.is_file():
        return {}
    with GLOSSARY_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    preserved: dict[str, dict[str, str]] = {}
    for row in rows:
        term = norm(row.get("term"))
        if not term:
            continue
        status = norm(row.get("content_status")).lower()
        if status == "published" or norm(row.get("article_title")):
            preserved[term] = row
    return preserved


def write_glossary(fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    FP2_DATA.mkdir(parents=True, exist_ok=True)
    with GLOSSARY_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def merge_with_preserved_rows(
    catalog_rows: list[dict[str, str]],
    preserved: dict[str, dict[str, str]],
    *,
    fieldnames: list[str],
) -> list[dict[str, str]]:
    """カタログ由来 draft 行と、既存の執筆済み行をマージする。"""
    merged: list[dict[str, str]] = []
    catalog_terms: set[str] = set()
    for row in catalog_rows:
        term = norm(row.get("term"))
        catalog_terms.add(term)
        if term in preserved:
            merged.append({col: preserved[term].get(col, "") for col in fieldnames})
        else:
            merged.append(row)
    for term, row in preserved.items():
        if term not in catalog_terms:
            merged.append({col: row.get(col, "") for col in fieldnames})
    return merged


def append_additions_to_catalog(candidates: list[CatalogEntry], path: Path) -> int:
    """追加候補を fp2_terms_catalog.csv に永続化する。"""
    catalog = read_catalog(path)
    existing = {e.term for e in catalog}
    added = 0
    for c in candidates:
        if c.term in existing:
            continue
        catalog.append(c)
        existing.add(c.term)
        added += 1
    if not added:
        return 0
    fields = [
        "term",
        "category",
        "short_def",
        "tier",
        "importance",
        "fp2_past_hits",
        "fp3_past_hits",
        "audit_note",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for e in catalog:
            w.writerow(
                {
                    "term": e.term,
                    "category": e.category,
                    "short_def": e.short_def,
                    "tier": e.tier,
                    "importance": e.importance,
                }
            )
    return added


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--init-catalog",
        action="store_true",
        help="fp3_terms_catalog.csv から fp2_terms_catalog.csv を生成（既存は上書きしない）",
    )
    parser.add_argument(
        "--force-catalog",
        action="store_true",
        help="--init-catalog と併用。既存カタログも上書き",
    )
    parser.add_argument(
        "--merge-additions",
        action="store_true",
        help="fp2_glossary_add_candidates.csv の語をカタログ末尾に追加",
    )
    parser.add_argument(
        "--exclude-tier-c",
        action="store_true",
        help="監査 Tier C の語を glossary_terms.csv に含めない",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="件数のみ表示",
    )
    args = parser.parse_args()

    if args.init_catalog:
        ensure_catalog(force=args.force_catalog)

    ensure_catalog()
    fieldnames = load_fieldnames()
    catalog = read_catalog(CATALOG_CSV)
    existing_terms = {e.term for e in catalog}

    if args.merge_additions:
        target = CATALOG_MASTER_CSV if CATALOG_MASTER_CSV.is_file() else CATALOG_CSV
        added = append_additions_to_catalog(load_add_candidates(), target)
        if added:
            print(f"マスターカタログに追加候補 {added} 語を追記")
            subprocess.run(
                [sys.executable, "tools/audit_fp2_glossary_catalog.py", "--write-catalog"],
                cwd=ROOT,
                check=True,
            )
            catalog = read_catalog(CATALOG_CSV)
            existing_terms = {e.term for e in catalog}

    fp3_lookup = load_fp3_lookup()
    preserved = load_preserved_glossary_rows()

    rows: list[dict[str, str]] = []
    skipped_c = 0
    from_fp3_exam = 0
    for entry in catalog:
        if args.exclude_tier_c and entry.tier == "C":
            skipped_c += 1
            continue
        fp3 = fp3_lookup.get(entry.term)
        if fp3 and norm(fp3.get("exam_points")):
            from_fp3_exam += 1
        rows.append(build_row(entry, fieldnames=fieldnames, fp3=fp3))

    rows = merge_with_preserved_rows(rows, preserved, fieldnames=fieldnames)

    print(f"カタログ: {len(catalog)} 語")
    if skipped_c:
        print(f"Tier C 除外: {skipped_c} 語")
    print(f"出力行数: {len(rows)} 語")
    if preserved:
        print(f"執筆済み行を保持: {len(preserved)} 語")
    print(f"FP3 exam_points 流用: {from_fp3_exam} 語")
    print(f"出力先: {GLOSSARY_CSV}")

    if args.dry_run:
        return 0

    write_glossary(fieldnames, rows)
    print(f"Wrote {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
