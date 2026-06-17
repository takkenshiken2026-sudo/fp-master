#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP2級用語カタログを過去問・シラバス観点で精査し Tier（A/B/C）を付与する."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.import_fp2_glossary_catalog import (  # noqa: E402
    CATALOG_DEF_FIXES,
    CATALOG_TERM_FIXES,
    CatalogEntry,
    read_catalog,
)

FP2_DATA = ROOT / "fp2" / "data"
CATALOG_MASTER_CSV = FP2_DATA / "fp2_terms_catalog_master.csv"
CATALOG_ACTIVE_CSV = FP2_DATA / "fp2_terms_catalog.csv"
CATALOG_EXCLUDED_CSV = FP2_DATA / "fp2_terms_catalog_excluded.csv"
AUDIT_REPORT_CSV = FP2_DATA / "fp2_glossary_audit_report.csv"
ADD_CANDIDATES_CSV = FP2_DATA / "fp2_glossary_add_candidates.csv"
FP2_PAST = FP2_DATA / "past_questions.csv"
FP3_PAST = ROOT / "data" / "past_questions.csv"

PAST_TEXT_COLUMNS = (
    "stem",
    "preamble",
    "statement_a",
    "statement_b",
    "statement_c",
    "statement_d",
    "choice_1",
    "choice_2",
    "choice_3",
    "choice_4",
    "explanation",
    "explanation_summary",
    "explanation_correct",
    "explanation_choices",
    "explanation_point",
)

# カタログ表記 ↔ 過去問表記
TERM_MATCH_ALIASES: dict[str, list[str]] = {
    "建ぺい率": ["建蔽率", "建ぺい率"],
    "iDeCo（個人型確定拠出年金）": ["iDeCo", "個人型確定拠出年金", "イデコ"],
    "NISA（少額投資非課税制度）": ["NISA", "少額投資非課税制度", "ニーサ"],
    "新NISA": ["新NISA", "新ニーサ"],
    "FP（ファイナンシャル・プランナー）": ["ファイナンシャル・プランナー", "ＦＰ", "FP"],
    "関連業法": ["関連法規", "関連業法"],
    "3,000万円特別控除": ["3,000万円特別控除", "3000万円特別控除", "3,000万円の特別控除"],
    "ペイオフ": ["ペイオフ"],
    "預金保険制度": ["預金保険制度", "ペイオフ"],
    "PER（株価収益率）": ["PER", "株価収益率"],
    "PBR（株価純資産倍率）": ["PBR", "株価純資産倍率"],
    "ROE（自己資本利益率）": ["ROE", "自己資本利益率"],
    "ETF（上場投資信託）": ["ETF", "上場投資信託"],
}

# 過去問に未出でも FP2 学科範囲として残す語（シラバス中核）
SYLLABUS_CORE: frozenset[str] = frozenset(
    {
        "6つの係数",
        "終価係数",
        "現価係数",
        "年金終価係数",
        "年金現価係数",
        "減債基金係数",
        "資本回収係数",
        "キャッシュフロー表",
        "個人バランスシート",
        "建ぺい率",
        "容積率",
        "重要事項説明",
        "インボイス制度",
        "相続税の基礎控除",
        "遺留分",
        "遺言",
        "贈与税の基礎控除",
        "相続時精算課税制度",
        "小規模宅地等の特例",
        "生命保険金の非課税枠",
        "退職手当金の非課税枠",
        "債券価格と金利の関係",
        "ポートフォリオ",
        "分散投資",
        "損益通算",
        "繰越控除",
        "住宅借入金等特別控除（住宅ローン控除）",
        "高額療養費制度",
        "繰上げ受給",
        "繰下げ受給",
        "iDeCo（個人型確定拠出年金）",
        "NISA（少額投資非課税制度）",
        "新NISA",
        "3,000万円特別控除",
        "教育資金の一括贈与の非課税特例",
        "結婚・子育て資金の一括贈与の非課税特例",
        "配偶者への居住用不動産の贈与",
    }
)

# 重複エントリ（主語彙があれば副次を C に下げる）
DUPLICATE_SECONDARY: dict[str, str] = {
    "成年後見制度（相続関連）": "成年後見制度",
}

# 公開一覧から除外する重複語（正本語彙を fp2_terms_catalog.csv に残す）
REMOVE_DUPLICATE_TERMS: frozenset[str] = frozenset(
    {
        *DUPLICATE_SECONDARY.keys(),
        "消費者契約法（金融適用）",  # → 消費者契約法（未出のため公開対象外だが重複防止）
        "ペイオフ",  # → 預金保険制度（同一制度の別称）
    }
)

# 過去問未出かつ単独ページ優先度を下げる語
LOW_PRIORITY_IF_NO_HIT: frozenset[str] = frozenset(
    {
        "ライフプランニング",
        "就業不能保険",
        "契約転換制度",
        "株主優待",
        "奨学金",
        "教育ローン",
        "個人賠償責任保険",
        "自動振替貸付",
        "延長（定期）保険",
        "生命保険契約者保護機構",
        "アクティブ型投資信託",
        "インデックス型投資信託",
        "円高・円安",
        "為替差益・為替差損",
        "リスクとリターン",
    }
)

# FP2 過去問に出るがカタログ未収録の追加候補
ADD_CANDIDATES: list[tuple[str, str, str, str]] = [
    (
        "課税標準",
        "タックスプランニング",
        "所得税・住民税などで税率を乗じる対象となる所得額・評価額。",
        "FP2学科120問に複数回出題。カタログ未収録。",
    ),
    (
        "区分所有法",
        "不動産",
        "マンション等の区分所有に関する法律。管理組合・規約・修繕等が試験論点。",
        "FP2学科過去問に「区分所有」関連の記述あり。",
    ),
    (
        "準防火地域",
        "不動産",
        "都市計画法上の防火・準防火地域の一種。建蔽率・容積率の緩和要件とセットで問われる。",
        "建蔽率問題の文脈で出題。",
    ),
    (
        "耐火建築物",
        "不動産",
        "建築基準法上の耐火性能を有する建築物。防火・準防火地域内の建蔽率制限と関連。",
        "建蔽率問題の文脈で出題。",
    ),
    (
        "公的年金の裁定請求",
        "ライフプランニングと資金計画",
        "老齢・障害・遺族年金等の支給開始手続。FPの関連法規問題で論点になる。",
        "関連法規・年金手続の不適切行為問題で出題。",
    ),
]


@dataclass
class TermAudit:
    term: str
    category: str
    short_def: str
    fp2_hits: int
    fp3_hits: int
    tier: str
    importance: str
    audit_note: str


def norm(value: object) -> str:
    return str(value or "").strip()


def load_past_blob(path: Path) -> str:
    if not path.is_file():
        return ""
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    parts: list[str] = []
    for row in rows:
        for col in PAST_TEXT_COLUMNS:
            parts.append(norm(row.get(col)))
    return "\n".join(parts)


def term_core(term: str) -> str:
    return re.sub(r"（[^）]*）|\([^)]*\)", "", term).strip()


def match_variants(term: str) -> list[str]:
    variants = [term, term_core(term)]
    variants.extend(TERM_MATCH_ALIASES.get(term, []))
    seen: set[str] = set()
    out: list[str] = []
    for v in variants:
        v = norm(v)
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def count_hits(blob: str, term: str) -> int:
    if not blob:
        return 0
    total = 0
    for variant in match_variants(term):
        total += len(re.findall(re.escape(variant), blob))
    return total


def assign_tier(
    term: str,
    *,
    fp2_hits: int,
    fp3_hits: int,
    primary_tier: str | None = None,
) -> tuple[str, str]:
    """tier と audit_note を返す。"""
    notes: list[str] = []

    if fp2_hits > 0:
        notes.append(f"FP2学科過去問に{fp2_hits}回出現")
        return "A", "; ".join(notes)

    if term in SYLLABUS_CORE:
        notes.append("FP2学科範囲の中核語（シラバス）")
        if fp3_hits > 0:
            notes.append(f"FP3過去問に{fp3_hits}回")
        return "A", "; ".join(notes)

    if fp3_hits >= 2:
        notes.append(f"FP3過去問に{fp3_hits}回（FP2未出）")
        return "A", "; ".join(notes)

    if fp3_hits == 1:
        notes.append("FP3過去問に1回（FP2未出）")
        return "B", "; ".join(notes)

    secondary_of = DUPLICATE_SECONDARY.get(term)
    if secondary_of and primary_tier in {"A", "B"}:
        notes.append(f"「{secondary_of}」の副次エントリ")
        return "C", "; ".join(notes)

    if term in LOW_PRIORITY_IF_NO_HIT:
        notes.append("過去問未出・優先度低")
        return "C", "; ".join(notes)

    if term in DUPLICATE_SECONDARY.values() or term in DUPLICATE_SECONDARY:
        pass

    notes.append("過去問未出（範囲内の基礎語として B 維持）")
    return "B", "; ".join(notes)


def tier_to_importance(tier: str, fp2_hits: int) -> str:
    if tier == "A" and fp2_hits >= 3:
        return "A"
    if tier == "A":
        return "B"
    if tier == "B":
        return "B"
    return "C"


def audit_catalog(
    catalog: list[CatalogEntry], fp2_blob: str, fp3_blob: str
) -> list[TermAudit]:
    primary_tiers: dict[str, str] = {}
    raw: list[tuple[str, str, str, int, int]] = []

    for entry in catalog:
        fp2_h = count_hits(fp2_blob, entry.term)
        fp3_h = count_hits(fp3_blob, entry.term)
        raw.append((entry.term, entry.category, entry.short_def, fp2_h, fp3_h))

    for term, category, short_def, fp2_h, fp3_h in raw:
        tier, _ = assign_tier(term, fp2_hits=fp2_h, fp3_hits=fp3_h)
        primary_tiers[term] = tier

    audits: list[TermAudit] = []
    for term, category, short_def, fp2_h, fp3_h in raw:
        primary = DUPLICATE_SECONDARY.get(term)
        primary_tier = primary_tiers.get(primary) if primary else None
        tier, note = assign_tier(
            term,
            fp2_hits=fp2_h,
            fp3_hits=fp3_h,
            primary_tier=primary_tier,
        )
        importance = tier_to_importance(tier, fp2_h)
        audits.append(
            TermAudit(
                term=term,
                category=category,
                short_def=short_def,
                fp2_hits=fp2_h,
                fp3_hits=fp3_h,
                tier=tier,
                importance=importance,
                audit_note=note,
            )
        )
    return audits


def write_audit_report(audits: list[TermAudit], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "term",
        "category",
        "tier",
        "importance",
        "fp2_past_hits",
        "fp3_past_hits",
        "short_def",
        "audit_note",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for a in sorted(audits, key=lambda x: (x.tier, x.category, x.term)):
            w.writerow(
                {
                    "term": a.term,
                    "category": a.category,
                    "tier": a.tier,
                    "importance": a.importance,
                    "fp2_past_hits": a.fp2_hits,
                    "fp3_past_hits": a.fp3_hits,
                    "short_def": a.short_def,
                    "audit_note": a.audit_note,
                }
            )


def write_add_candidates(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["term", "category", "short_def", "audit_note", "suggested_tier"]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for term, category, short_def, note in ADD_CANDIDATES:
            w.writerow(
                {
                    "term": term,
                    "category": category,
                    "short_def": short_def,
                    "audit_note": note,
                    "suggested_tier": "A",
                }
            )


def write_catalog(audits: list[TermAudit], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for a in audits:
            w.writerow(
                {
                    "term": a.term,
                    "category": a.category,
                    "short_def": a.short_def,
                    "tier": a.tier,
                    "importance": a.importance,
                    "fp2_past_hits": a.fp2_hits,
                    "fp3_past_hits": a.fp3_hits,
                    "audit_note": a.audit_note,
                }
            )


def publish_decision(audit: TermAudit) -> tuple[bool, str]:
    """FP2 公開用語かどうか。重複・低重要度・根拠なしを除外。"""
    if audit.term in REMOVE_DUPLICATE_TERMS:
        return False, "重複（副次・別称）"
    if audit.tier == "C" or audit.term in LOW_PRIORITY_IF_NO_HIT:
        return False, "低重要度"
    if audit.fp2_hits > 0:
        return True, "FP2過去問に出現"
    if audit.term in SYLLABUS_CORE:
        return True, "FP2学科中核（シラバス）"
    return False, "FP2未出・中核外"


def ensure_master_catalog() -> None:
    """監査マスター CSV がなければ現行カタログから生成。"""
    if CATALOG_MASTER_CSV.is_file():
        return
    if CATALOG_ACTIVE_CSV.is_file():
        CATALOG_MASTER_CSV.write_text(
            CATALOG_ACTIVE_CSV.read_text(encoding="utf-8-sig"),
            encoding="utf-8-sig",
        )
        print(f"Created master from active: {CATALOG_MASTER_CSV}")
        return
    raise SystemExit(
        f"{CATALOG_MASTER_CSV} がありません。"
        "import_fp2_glossary_catalog.py --init-catalog を先に実行してください。"
    )


def print_summary(audits: list[TermAudit]) -> None:
    tier_counts = Counter(a.tier for a in audits)
    fp2_hit_terms = sum(1 for a in audits if a.fp2_hits > 0)
    pub = [a for a in audits if publish_decision(a)[0]]
    excl = [a for a in audits if not publish_decision(a)[0]]
    print(f"監査対象（マスター）: {len(audits)} 語")
    print(f"Tier A: {tier_counts.get('A', 0)} / B: {tier_counts.get('B', 0)} / C: {tier_counts.get('C', 0)}")
    print(f"FP2過去問ヒット: {fp2_hit_terms} 語")
    print(f"公開対象: {len(pub)} 語 / 除外: {len(excl)} 語")
    excl_reasons = Counter(publish_decision(a)[1] for a in excl)
    print("除外内訳:", dict(excl_reasons))


def prune_audits(audits: list[TermAudit]) -> tuple[list[TermAudit], list[tuple[TermAudit, str]]]:
    active: list[TermAudit] = []
    excluded: list[tuple[TermAudit, str]] = []
    for a in audits:
        ok, reason = publish_decision(a)
        if ok:
            active.append(a)
        else:
            excluded.append((a, reason))
    return active, excluded


def write_excluded_catalog(excluded: list[tuple[TermAudit, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "term",
        "category",
        "tier",
        "fp2_past_hits",
        "fp3_past_hits",
        "short_def",
        "exclude_reason",
        "audit_note",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for a, reason in sorted(excluded, key=lambda x: (x[1], x[0].term)):
            w.writerow(
                {
                    "term": a.term,
                    "category": a.category,
                    "tier": a.tier,
                    "fp2_past_hits": a.fp2_hits,
                    "fp3_past_hits": a.fp3_hits,
                    "short_def": a.short_def,
                    "exclude_reason": reason,
                    "audit_note": a.audit_note,
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-master",
        action="store_true",
        help="fp2_terms_catalog_master.csv を Tier 付きで更新",
    )
    parser.add_argument(
        "--prune-active",
        action="store_true",
        help="公開用 fp2_terms_catalog.csv を精査結果で上書き（除外語は excluded CSV へ）",
    )
    parser.add_argument(
        "--write-catalog",
        action="store_true",
        help="--write-master と --prune-active の両方（ビルド用）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="サマリのみ（CSV 書き込みなし）",
    )
    args = parser.parse_args()

    write_master = args.write_master or args.write_catalog
    prune_active = args.prune_active or args.write_catalog

    ensure_master_catalog()
    catalog = read_catalog(CATALOG_MASTER_CSV)
    fp2_blob = load_past_blob(FP2_PAST)
    fp3_blob = load_past_blob(FP3_PAST)
    audits = audit_catalog(catalog, fp2_blob, fp3_blob)

    print_summary(audits)

    if args.dry_run:
        return 0

    write_audit_report(audits, AUDIT_REPORT_CSV)
    write_add_candidates(ADD_CANDIDATES_CSV)

    if write_master:
        write_catalog(audits, CATALOG_MASTER_CSV)
        print(f"Updated master: {CATALOG_MASTER_CSV}")

    if prune_active:
        active, excluded = prune_audits(audits)
        write_catalog(active, CATALOG_ACTIVE_CSV)
        write_excluded_catalog(excluded, CATALOG_EXCLUDED_CSV)
        print(f"Active catalog: {len(active)} 語 → {CATALOG_ACTIVE_CSV}")
        print(f"Excluded: {len(excluded)} 語 → {CATALOG_EXCLUDED_CSV}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
