#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP3級試験ガイド記事カタログを fp3_article_titles.csv から guide_articles.csv へ取り込む."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.scaffold_guide_article import load_fieldnames  # noqa: E402

CATALOG_BODY_STUB = (
    "本記事は現在執筆中です。公開時に、{topic}について公式情報を確認したうえで"
    "受験者が迷いやすい点を整理します。制度の数値や期限は、試験実施団体の最新の受験案内で必ず確認してください。"
    "それまでの間は、同じカテゴリの他記事やこのサイトの過去問・用語解説を活用してください。"
)
from tools.site_config import brand_name, guide_genre_labels, primary_external_link  # noqa: E402

ARTICLES_CSV = ROOT / "data" / "guide_articles.csv"

CATEGORY_PREFIX = {
    "属性別・状況別": "attr",
    "分野別対策（6科目別）": "field",
    "学科・実技の違いと対策": "exam-wp",
    "比較・選択系": "compare",
    "合格後・活用": "after-pass",
    "よくある質問": "faq",
    "学習ツール・サイト活用": "tools",
    "制度・法改正対応": "reform",
}

GENRE_SECTIONS: dict[str, list[str]] = {
    "属性別・状況別": [
        "対象者の特徴と受験の背景",
        "FP3級を受けるメリット",
        "学習時間の確保と進め方",
        "つまずきやすいポイント",
        "次に読む記事",
    ],
    "分野別対策（6科目別）": [
        "出題傾向の概要",
        "頻出論点と押さえるポイント",
        "計算・暗記のコツ",
        "このサイトでの演習の使い方",
        "直前期の確認事項",
    ],
    "学科・実技の違いと対策": [
        "学科試験と実技試験の違い",
        "選び方と受験の組み合わせ",
        "実技試験の対策の進め方",
        "落ちやすいパターン",
        "次に確認すること",
    ],
    "比較・選択系": [
        "比較のポイント",
        "それぞれの特徴",
        "FP3級受験者へのおすすめ",
        "学習への影響",
        "判断のまとめ",
    ],
    "合格後・活用": [
        "合格後にできること",
        "資格の活用シーン",
        "履歴書・職場での記載",
        "継続学習と上位資格",
        "よくある誤解",
    ],
    "よくある質問": [
        "質問の背景",
        "公式情報で確認すること",
        "受験者が知っておきたい答え",
        "学習・受験への影響",
        "関連する確認事項",
    ],
    "学習ツール・サイト活用": [
        "ツール・サイトの選び方",
        "効果的な使い方",
        "学習フェーズ別の活用法",
        "このサイトとの組み合わせ",
        "続けるためのコツ",
    ],
    "制度・法改正対応": [
        "制度変更の概要",
        "FP3級出題への影響",
        "学習で押さえるポイント",
        "公式情報の確認先",
        "直前までの見直し方",
    ],
}

GENRE_TAGS: dict[str, str] = {
    "属性別・状況別": "属性別;状況別;FP3級",
    "分野別対策（6科目別）": "分野別;6科目;FP3級",
    "学科・実技の違いと対策": "学科;実技;FP3級",
    "比較・選択系": "比較;選択;FP3級",
    "合格後・活用": "合格後;活用;FP3級",
    "よくある質問": "FAQ;よくある質問;FP3級",
    "学習ツール・サイト活用": "学習ツール;サイト活用;FP3級",
    "制度・法改正対応": "法改正;制度変更;FP3級",
}

GENRE_PRIORITY_BASE: dict[str, int] = {
    "属性別・状況別": 10,
    "分野別対策（6科目別）": 20,
    "学科・実技の違いと対策": 30,
    "比較・選択系": 40,
    "合格後・活用": 50,
    "よくある質問": 60,
    "学習ツール・サイト活用": 70,
    "制度・法改正対応": 80,
}

# タイトル内のキーワード → slug 断片（長い語句を先にマッチさせる）
SLUG_FRAGMENTS: list[tuple[str, str]] = [
    ("ライフプランニングと資金計画", "life-plan"),
    ("キャッシュフロー表・個人バランスシート", "cashflow-balance"),
    ("医療保険・介護保険", "medical-nursing-insurance"),
    ("公的年金（老齢・障害・遺族）", "public-pension"),
    ("株式・債券・投資信託", "stocks-bonds-funds"),
    ("不動産の売買・賃貸借", "real-estate-trade-lease"),
    ("所得税の計算問題（給与所得・事業所得）", "income-tax-calc"),
    ("贈与税と相続税の違い", "gift-inheritance-tax"),
    ("相続税の基礎控除・計算", "inheritance-tax-basic"),
    ("生命保険・損害保険の種類", "life-nonlife-insurance"),
    ("社会保険（健康保険・年金）", "social-insurance"),
    ("NISAとiDeCo", "nisa-ideco"),
    ("6科目の得点配分", "six-subjects-scoring"),
    ("日本FP協会実技「資産設計提案業務」", "jafp-asset-design"),
    ("きんざい実技「保険顧客資産相談業務」", "kinyu-hoken-consult"),
    ("きんざい実技「個人資産相談業務」", "kinyu-personal-asset"),
    ("日本FP協会ときんざい", "jafp-vs-kinyu"),
    ("FP3級とAFP認定研修", "fp3-vs-afp"),
    ("FP3級と証券外務員", "fp3-vs-securities"),
    ("FP3級と簿記3級", "fp3-vs-boki"),
    ("紙試験（きんざい）とCBT", "paper-vs-cbt"),
    ("午前（学科）と午後（実技）", "am-pm-difficulty"),
    ("2026年度のFP3級試験", "fp3-2026-changes"),
    ("2025年・2026年税制改正", "tax-reform-2025-2026"),
    ("最新の出題範囲改定（シラバス変更）", "syllabus-update"),
    ("大学生がFP3級", "university-student"),
    ("高校生がFP3級", "highschool-student"),
    ("主婦・主夫がFP3級", "homemaker"),
    ("転職活動中にFP3級", "job-hunting"),
    ("銀行・保険・証券に就職", "financial-industry-job"),
    ("不動産業界への就職", "real-estate-career"),
    ("50代・60代がFP3級", "senior-50s-60s"),
    ("金融知識ゼロから", "zero-knowledge-start"),
    ("他資格（簿記・宅建・証券外務員）", "parallel-qualifications"),
    ("育休・産休中にFP3級", "parental-leave"),
    ("FP3級とFP2級を連続", "fp3-fp2-consecutive"),
    ("理系・文系出身者", "science-vs-liberal-arts"),
    ("経理・会計担当者", "accounting-staff"),
    ("副業・フリーランス", "side-business-freelance"),
    ("公務員がFP3級", "public-servant"),
    ("リスク管理（保険）", "risk-insurance"),
    ("金融資産運用", "asset-management"),
    ("タックスプランニング（税金）", "tax-planning"),
    ("不動産の頻出論点", "real-estate"),
    ("相続・事業承継", "inheritance-succession"),
    ("住宅ローン", "housing-loan"),
    ("為替・金利", "fx-interest"),
    ("学科試験と実技試験", "written-vs-practical"),
    ("実技試験（日本FP協会・きんざい）", "practical-exam-choice"),
    ("実技試験で落ちやすい", "practical-fail-patterns"),
    ("学科は合格・実技は不合格", "written-pass-practical-fail"),
    ("実技試験の過去問", "practical-past-questions"),
    ("独学と通信講座", "self-study-vs-correspondence"),
    ("テキストなしで過去問だけ", "past-questions-only"),
    ("紙のテキストとアプリ", "textbook-vs-app"),
    ("1回で合格するのと複数回", "one-shot-vs-retake"),
    ("FP3級合格後にFP2級", "fp2-roadmap"),
    ("履歴書・職務経歴書", "resume-cv"),
    ("名刺に記載", "business-card"),
    ("独立・開業", "independent-practice"),
    ("継続教育・更新制度", "continuing-education"),
    ("AFPとCFPへの道", "afp-cfp-route"),
    ("合格後に読むべき書籍", "books-after-pass"),
    ("家計・資産管理に活かす", "household-asset-mgmt"),
    ("就職・転職への活かし方（金融以外）", "career-non-finance"),
    ("意味がないと言われる", "worthless-debate"),
    ("有効期限・失効", "expiry-validity"),
    ("活かせる仕事・職種", "jobs-careers"),
    ("勉強時間は何時間", "study-hours"),
    ("意味ない」「簡単すぎる", "easy-meaningless-myth"),
    ("合格率が高い理由", "high-pass-rate"),
    ("独学で何ヶ月", "self-study-months"),
    ("落ちた人の共通パターン", "fail-patterns"),
    ("電卓は使えるか", "calculator-allowed"),
    ("試験会場は全国", "exam-venues"),
    ("結果はいつわかるか", "result-timing"),
    ("試験料はいくらか", "exam-fee"),
    ("CBT試験とは", "cbt-exam"),
    ("年齢制限はあるか", "age-limit"),
    ("合格証書はいつ届く", "certificate-delivery"),
    ("申込をキャンセル", "cancel-application"),
    ("当日に遅刻", "late-on-exam-day"),
    ("問題用紙・解答用紙は持ち帰れる", "take-home-papers"),
    ("無料過去問サイト", "free-past-question-sites"),
    ("スマホアプリ", "smartphone-app"),
    ("通勤・隙間時間", "commute-gap-time"),
    ("音声・動画", "audio-video"),
    ("模擬試験を無料", "free-mock-exam"),
    ("一問一答と過去問", "ichimon-vs-past"),
    ("用語を体系的に", "glossary-systematic"),
    ("計算問題を紙なし", "mental-math-practice"),
    ("間違えた問題だけ", "wrong-answer-review"),
    ("学習進捗を可視化", "progress-tracking"),
    ("新NISA", "new-nisa"),
    ("iDeCoの制度変更", "ideco-reform"),
    ("社会保険料・年金額の改定", "social-insurance-reform"),
    ("相続・贈与税制の改正", "inheritance-gift-reform"),
    ("医療費控除・セルフメディケーション", "medical-deduction"),
    ("住宅ローン控除の改正", "housing-loan-deduction"),
    ("介護保険制度の改正", "nursing-care-reform"),
]

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def slug_for_title(category: str, title: str, used: set[str]) -> str:
    prefix = CATEGORY_PREFIX[category]
    parts: list[str] = []
    remaining = title
    for jp, en in SLUG_FRAGMENTS:
        if jp in remaining:
            parts.append(en)
            remaining = remaining.replace(jp, "", 1)
    if not parts:
        parts = ["guide"]
    base = "-".join(parts)[:56]
    slug = f"{prefix}-{base}"
    if not SLUG_RE.fullmatch(slug):
        slug = re.sub(r"[^a-z0-9-]", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
    n = 2
    candidate = slug
    while candidate in used:
        candidate = f"{slug}-{n}"
        n += 1
    used.add(candidate)
    return candidate


def meta_for_title(title: str) -> str:
    return f"{title}について、FP3級受験者向けに公式情報の確認方法と学習の進め方を整理します。"


def lead_for_title(title: str) -> str:
    return f"{title}について、受験を検討・準備中の方が迷いやすい点を整理します。公式情報を優先し、このサイトの演習・用語解説と組み合わせて学習を進めてください。"


def build_row(slug: str, genre: str, title: str, priority: int, related: str) -> dict[str, str]:
    today = date.today().isoformat()
    next_month = (date.today() + timedelta(days=30)).isoformat()
    official = primary_external_link()
    source = f"{official['label']}|{official['url']}"
    sections = GENRE_SECTIONS.get(genre, GENRE_SECTIONS["よくある質問"])
    row = {k: "" for k in load_fieldnames()}
    row.update(
        {
            "slug": slug,
            "genre": genre,
            "title": title,
            "meta_description": meta_for_title(title),
            "lead": lead_for_title(title),
            "priority": str(priority),
            "tags": GENRE_TAGS.get(genre, "FP3級"),
            "author_name": f"{brand_name()}編集部",
            "author_profile": "資格学習サイトの編集チーム",
            "reviewer_name": "公式情報確認担当",
            "reviewer_profile": "公開前に一次情報との照合を行う担当者",
            "fact_checked_at": today,
            "primary_sources": source,
            "original_note": f"fp3_article_titles.csv から取り込み（{today}）。本文は執筆前のカタログ行。",
            "user_intent": f"本記事を読むと、{title}について公式情報で確認すべき点と学習の進め方が分かります。",
            "action_items": "公式サイトで最新情報を確認する;関連分野の演習に取り組む;用語解説で弱点を補強する",
            "update_policy": "試験要項・制度改正時に本文と参照元を見直します。",
            "last_reviewed_at": today,
            "next_review_at": next_month,
            "source_checked_at": today,
            "content_status": "draft",
            "revision_note": f"カタログ取り込み（{today}）。公開前に本文を全面リライトしてください。",
        }
    )
    for i, heading in enumerate(sections[:5], start=1):
        row[f"section_{i}_heading"] = heading
        row[f"section_{i}_body"] = CATALOG_BODY_STUB.format(topic=heading)
    row["faq_1_question"] = f"{title}について最初に確認することは？"
    row["faq_1_answer"] = "試験実施団体の公式サイトで最新の受験案内・出題範囲を確認してください。数値や期限は年度で変わることがあります。"
    row["faq_2_question"] = "このサイトではどう学習を進めればよいですか？"
    row["faq_2_answer"] = "過去問・実践演習で弱点を見つけ、用語解説で理解を深め、間違えた問題は復習リストに残して解き直してください。"
    row["related_links"] = related
    return row


def read_titles_csv(path: Path) -> list[tuple[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out: list[tuple[str, str]] = []
    for row in rows:
        genre = (row.get("カテゴリ") or row.get("genre") or "").strip()
        title = (row.get("タイトル") or row.get("title") or "").strip()
        if genre and title:
            out.append((genre, title))
    return out


def import_catalog(source: Path, *, dry_run: bool = False) -> int:
    items = read_titles_csv(source)
    if not items:
        raise ValueError(f"タイトルが読み取れません: {source}")

    unknown = {g for g, _ in items if g not in CATEGORY_PREFIX}
    if unknown:
        raise ValueError(f"未対応カテゴリ: {sorted(unknown)}")

    configured = set(guide_genre_labels())
    missing_genres = {g for g, _ in items if g not in configured}
    if missing_genres:
        raise ValueError(
            f"site-config.json の guideArticleGenres に未登録: {sorted(missing_genres)}"
        )

    used_slugs: set[str] = set()
    built: list[dict[str, str]] = []
    genre_seq: dict[str, int] = {}
    slug_by_title: dict[str, str] = {}

    for genre, title in items:
        slug = slug_for_title(genre, title, used_slugs)
        slug_by_title[title] = slug
        seq = genre_seq.get(genre, 0)
        genre_seq[genre] = seq + 1
        priority = GENRE_PRIORITY_BASE[genre] + seq
        built.append((slug, genre, title, priority))

    rows_out: list[dict[str, str]] = []
    for slug, genre, title, priority in built:
        same_genre = [(s, t) for s, g, t, _p in built if g == genre and s != slug]
        fallback = [(s, t) for s, _g, t, _p in built if s != slug]
        peers = (same_genre or fallback)[:2]
        related = ";".join(f"{s}:{t[:24]}" for s, t in peers)
        rows_out.append(build_row(slug, genre, title, priority, related))

    if dry_run:
        print(f"Would write {len(rows_out)} rows to {ARTICLES_CSV}")
        for row in rows_out[:5]:
            print(f"  {row['slug']}: {row['title']}")
        print("  ...")
        return 0

    with ARTICLES_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=load_fieldnames(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows_out)
    print(f"Wrote {len(rows_out)} guide articles to {ARTICLES_CSV}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="FP3級試験ガイドカタログを取り込む")
    parser.add_argument(
        "source",
        nargs="?",
        default=str(Path.home() / "Downloads" / "fp3_article_titles.csv"),
        help="カテゴリ・タイトル CSV（既定: ~/Downloads/fp3_article_titles.csv）",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return import_catalog(Path(args.source).expanduser(), dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
