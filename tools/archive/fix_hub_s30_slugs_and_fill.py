#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""テンプレート exam-site-shell: ハブCSVに slug を付与し 10/10/10 に揃える."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
DATA = ROOT / "data"

COMPARE_SLUGS = [
    "kako-mogi",
    "koushiki-youkou",
    "goukaku-shutsudai",
    "ichimon-jissen",
    "fukushu-kiroku",
    "sanketa-enso",
    "juken-goukaku",
    "yougo-hikaku",
    "hub-4tabs",
    "glossary-vs-numbers",
]

NUMBERS_SLUGS = [
    "keiyaku-kigen",
    "teate-hoshu",
    "teitiku-nensu",
    "seinin-nenrei",
    "touki-koukoku",
    "shiken-tensu",
    "goukaku-ritsu-yohaku",
    "moshi-jikan-yohaku",
    "shikenryo-yohaku",
    "shutsudai-su-yohaku",
]

MISTAKES_SLUGS = [
    "ju35-ju37",
    "baikai-dairi",
    "tochi-toji",
    "senpaku-junni",
    "kotei-toshi",
    "cooling-teiki",
    "goukaku-shutsudai-kon",
    "ichimon-jissen-kon",
    "yougo-hikaku-kon",
    "koushiki-youkou-kon",
]


def _load(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])
        return header, list(reader)


def _save(path: Path, header: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def _assign_slugs(rows: list[dict], slugs: list[str]) -> list[dict]:
    out = []
    for i, row in enumerate(rows):
        row = dict(row)
        if i < len(slugs):
            row["slug"] = slugs[i]
        elif not row.get("slug"):
            raise ValueError(f"slug missing at row {i}")
        out.append(row)
    while len(out) < len(slugs):
        raise ValueError(f"need {len(slugs)} rows, have {len(out)}")
    return out[: len(slugs)]


def _cmp_extra() -> list[dict]:
    return [
        {
            "slug": "hub-4tabs",
            "title": "知識ハブ4タブの違い",
            "category": "設備・その他",
            "tags": "知識ハブ;整理",
            "summary": "用語解説・比較・数値・誤答の4タブの役割と学習での使い分けを整理します。",
            "col_labels": "用語解説;比較・整理表;数値・期限;よくある誤答",
            "compare_rows": json.dumps(
                [
                    {"axis": "目的", "cols": ["1語の意味と試験ポイント", "似た概念の差分", "数字・期限の早見", "誤答パターンの整理"]},
                    {"axis": "形式", "cols": ["1語1ページ", "2〜3列の表", "項目と数値の一覧", "誤りと正解の対比"]},
                    {"axis": "向く場面", "cols": ["初見の語・根拠確認", "混同語の整理", "暗記・直前確認", "引っかけ対策"]},
                    {"axis": "入口", "cols": ["用語解説タブ", "比較・整理表タブ", "数値・期限タブ", "よくある誤答タブ"]},
                ],
                ensure_ascii=False,
            ),
            "article_title": "知識ハブ4タブの違い｜テンプレートサイトの使い方",
            "article_lead": "このテンプレートでは知識ハブを4種類に分けています。目的に応じてタブを切り替えると、学習コンテンツの配置例として活用できます。",
            "exam_points": "意味は用語解説;差分は比較表;数字は数値タブ;引っかけは誤答タブ",
            "common_mistakes": "1タブだけで全学習を完結させようとすると、数字や誤答対策が弱くなりがちです。",
            "memory_tip": "「意味→差分→数字→誤答」の順で巡回すると整理しやすいです。",
            "related_terms": "用語解説;比較表;公式情報",
            "faq_1_question": "4タブの違いは何ですか？",
            "faq_1_answer": "用語解説は定義、比較は差分、数値は期限・割合、誤答は典型ミスの整理です。テンプレートのナビゲーション例として設計されています。",
            "faq_2_question": "どのタブから始めますか？",
            "faq_2_answer": "未知の語は用語解説、混同しやすい組み合わせは比較表から入ると効率的です。その後、数値・誤答で仕上げます。",
            "faq_3_question": "本番サイトでも同じですか？",
            "faq_3_answer": "各試験サイトでも同じ4タブ構成を基本としています。件数や内容は試験ごとに拡充します。",
            "faq_4_question": "一覧はどこですか？",
            "faq_4_answer": "用語解説ページ上部のタブから、比較・数値・誤答の各一覧へ移動できます。",
        },
        {
            "slug": "glossary-vs-numbers",
            "title": "比較表と数値早見の違い",
            "category": "設備・その他",
            "tags": "比較表;数値",
            "summary": "概念の差分を並べる比較表と、数字・期限を並べる数値早見の使い分けを整理します。",
            "col_labels": "比較・整理表;数値・期限早見",
            "compare_rows": json.dumps(
                [
                    {"axis": "主な内容", "cols": ["2〜3項目の違い", "割合・年数・期限"]},
                    {"axis": "学習効果", "cols": ["混同防止", "暗記・直前確認"]},
                    {"axis": "例", "cols": ["媒介と代理", "35条8日・37条5日"]},
                    {"axis": "関連", "cols": ["用語解説へリンク", "試験要項で裏取り"]},
                ],
                ensure_ascii=False,
            ),
            "article_title": "比較表と数値早見の違い｜テンプレート早見表",
            "article_lead": "比較表は「違い」、数値早見は「数字」に特化したページです。両方を往復すると理解が定着しやすくなります。",
            "exam_points": "混同は比較;暗記は数値;公式で裏取り;用語とセット",
            "common_mistakes": "数値だけ暗記し比較で意味を確認しないと、類似数字の入れ替えに弱くなります。",
            "memory_tip": "「違い＝比較」「数字＝数値」と役割で分けてください。",
            "related_terms": "比較表;試験要項;合格基準",
            "faq_1_question": "比較表と数値早見の違いは？",
            "faq_1_answer": "比較表は概念の差分、数値早見は期限・割合・年数などの数字を一覧化したページです。",
            "faq_2_question": "どちらを先に見ますか？",
            "faq_2_answer": "意味を用語解説で押さえたあと、混同しやすい組は比較表、数字は数値早見の順がおすすめです。",
            "faq_3_question": "テンプレートの例は？",
            "faq_3_answer": "契約前後の期限や合格点の例が数値早見に、学習モードの違いが比較表に載っています。",
            "faq_4_question": "関連リンクは？",
            "faq_4_answer": "各ページの関連用語から用語解説へ移動できます。",
        },
    ]


def _num_extra() -> list[dict]:
    rows = []
    specs = [
        (
            "goukaku-ritsu-yohaku",
            "合格率・受験者数（記入例）",
            "法令・制度",
            "合格率;統計",
            "合格率や受験者数の欄をテンプレート用に示します。実値は公式統計で確認してください。",
            "要項・統計で確認",
            [
                (            "合格率（例）", "要記入", "年度・試験により変動"),
                ("受験者数（例）", "要記入", "公式発表を参照"),
                ("合格者数（例）", "要記入", "同上"),
                ("確認先", "試験要項", "一次情報"),
            ],
            "合格率・受験者数（記入例）｜数値早見テンプレ",
            "テンプレートでは数値欄の記入例として「要記入」を示しています。本番サイトでは年度ごとの統計を反映してください。",
            "合格率は年度で変動;受験者数も公式発表;学習計画は難易度の参考程度",
            "他試験の数字を流用すると誤解を招きます。",
            "「要記入」は未設定の印。本番は要項で置換。",
            "合格基準;試験要項;公式情報",
        ),
        (
            "moshi-jikan-yohaku",
            "模擬試験・演習時間（記入例）",
            "契約・実務",
            "模擬試験;時間",
            "制限時間の欄のテンプレート例です。本番試験時間は要項で必ず確認してください。",
            "要項で確認",
            [
                (            "本試験時間（例）", "要記入", "試験により異なる"),
                ("模擬試験（例）", "同左", "本番形式に合わせる"),
                ("1問あたり（例）", "要記入", "出題数で割算"),
                ("確認", "受験票", "当日情報"),
            ],
            "模擬試験・演習時間（記入例）｜数値早見テンプレ",
            "時間配分の練習用に、数値早見表の項目例を示しています。サイト内の実践演習とも対応づけてください。",
            "本番時間は要項確認;模試は本番に合わせる;1問あたり目安を計算",
            "テンプレ数字をそのまま暗記すると本番で齟齬が出ます。",
            "「要記入」は未設定。要項で置換。",
            "模擬試験;過去問;試験要項",
        ),
        (
            "shikenryo-yohaku",
            "受験手数料（記入例）",
            "法令・制度",
            "受験手数料",
            "受験料の欄テンプレート。申込前に試験要項の最新額を確認してください。",
            "要項で確認",
            [
                (            "受験手数料（例）", "要記入", "税込表示に注意"),
                ("申込期間（例）", "要記入", "年度で変動"),
                ("返還", "原則不可", "要項確認"),
                ("確認先", "公式情報", "一次情報"),
            ],
            "受験手数料（記入例）｜数値早見テンプレ",
            "受験料・申込期限は試験ごとに改定されます。テンプレートでは項目名だけを共通化し、値は本番データに差し替えます。",
            "金額は要項;申込期限も要項;返還条件を確認",
            "過去の受験料を最新とみなす誤りに注意。",
            "「要記入」は未設定。申込前に要項確認。",
            "受験資格;試験要項;公式情報",
        ),
        (
            "shutsudai-su-yohaku",
            "出題数・配点（記入例）",
            "設備・その他",
            "出題数;配点",
            "出題数と配点の欄テンプレート。合格戦略の前提となる数字です。",
            "要項で確認",
            [
                ("出題数（例）", "要記入", "形式により異なる"),
                ("配点（例）", "1問1点等", "要項確認"),
                ("合格点（例）", "要記入", "合格基準と連動"),
                ("科目別基準", "要項参照", "足切り注意"),
            ],
            "出題数・配点（記入例）｜数値早見テンプレ",
            "出題数・配点・合格点はセットで要項確認します。テンプレートでは学習計画の枠組み例として載せています。",
            "出題数は要項;配点方式も要項;科目別基準点に注意",
            "他資格の出題数を当てはめると計画が狂います。",
            "「要記入」は未設定。要項で置換。",
            "出題範囲;合格基準;試験要項",
        ),
    ]
    for spec in specs:
        slug, title, cat, tags, summary, highlight, items, at, lead, pts, mis, tip, rel = spec
        rows.append(
            {
                "slug": slug,
                "title": title,
                "category": cat,
                "tags": tags,
                "summary": summary,
                "highlight": highlight,
                "item_rows": json.dumps(
                    [{"item": i, "value": v, "note": n} for i, v, n in items],
                    ensure_ascii=False,
                ),
                "article_title": at,
                "article_lead": lead,
                "exam_points": pts,
                "common_mistakes": mis,
                "memory_tip": tip,
                "related_terms": rel,
                "faq_1_question": f"{title}の使い方は？",
                "faq_1_answer": "テンプレートでは項目名と確認先の例を示しています。本番サイトでは試験要項の数値に差し替えてください。",
                "faq_2_question": "「要記入」の欄はどう使いますか？",
                "faq_2_answer": "未設定・要記入を意味します。クローン後に各試験の公式データで置き換えます。",
                "faq_3_question": "どこで正式な数値を確認しますか？",
                "faq_3_answer": "試験要項・公式情報の一次データを参照してください。",
                "faq_4_question": "関連する比較表はありますか？",
                "faq_4_answer": "合格基準と出題範囲の比較表、受験資格と合格基準の比較表などとあわせて読むと整理しやすくなります。",
            }
        )
    return rows


def _mis_extra() -> list[dict]:
    pat = json.dumps(
        [
            {
                "topic": "混同",
                "wrong": "テンプレの例示数字をそのまま本番の正として暗記",
                "correct": "試験要項・公式情報で年度ごとに確認",
                "trap": "プレースホルダー",
            },
            {
                "topic": "情報源",
                "wrong": "非公式ブログだけで申込判断",
                "correct": "試験実施団体の公式情報を優先",
                "trap": "一次情報",
            },
            {
                "topic": "学習",
                "wrong": "一問一答だけで総合演習を省略",
                "correct": "過去問・実践演習で時間配分も練習",
                "trap": "演習バランス",
            },
        ],
        ensure_ascii=False,
    )
    specs = [
        (
            "goukaku-shutsudai-kon",
            "合格基準と出題範囲の取り違え",
            "法令・制度",
            "合格基準;出題範囲",
            "「何を学ぶか」と「何点取ればよいか」を混同する典型パターンです。",
            "両方とも要項に載るため、片方だけ確認して計画が偏る。",
            "【テンプレ】合格基準と出題範囲の誤答パターン",
            "合格基準だけ見て範囲外学習をしたり、範囲だけ見て目標点設定を忘れたりするミスを整理します。",
            "範囲＝学習対象;基準＝目標点;要項で同時確認",
            "合格点だけ暗記し範囲を無視;範囲だけ広げ基準点無視",
            "「何を／何点」をセットで確認。",
            "合格基準;出題範囲;試験要項",
        ),
        (
            "ichimon-jissen-kon",
            "一問一答と実践演習の取り違え",
            "契約・実務",
            "一問一答;模擬試験",
            "短時間点検と本番形式演習の目的を同一視する誤りです。",
            "どちらも「演習」に見えるため、時間配分練習が不足しがち。",
            "【テンプレ】一問一答と実践演習の誤答パターン",
            "一問一答は知識の点検、実践演習は総合力・時間配分の訓練です。テンプレートの3モード構成の理解用です。",
            "点検＝一問一答;総合＝実践;過去問は論点把握",
            "一問一答のみで足りる;実践演習を初期から偏重",
            "「点検→論点→総合」の順。",
            "一問一答;過去問;模擬試験",
        ),
        (
            "yougo-hikaku-kon",
            "用語解説だけで比較表を読まない",
            "設備・その他",
            "用語解説;比較表",
            "定義は分かったが差分表を見ず、類似語の引っかけに弱くなるパターンです。",
            "用語ページだけ巡回し、比較表タブを使わない。",
            "【テンプレ】用語と比較表の使い分けミス",
            "用語解説で意味を押さえたあと、比較表で差分を確認する流れがテンプレートの想定学習経路です。",
            "意味＝用語;差分＝比較;往復で定着",
            "用語だけで完結;比較表を見ない",
            "用語のあと比較表へ。",
            "用語解説;比較表;復習",
        ),
        (
            "koushiki-youkou-kon",
            "試験要項以外だけで申込判断",
            "法令・制度",
            "試験要項;公式情報",
            "SNSや古い記事だけで受験資格・日程を判断する誤りです。",
            "要項の年度更新を見落とす。",
            "【テンプレ】公式情報優先の誤答パターン",
            "非公式情報と食い違う場合は試験実施団体の公式情報を優先してください。テンプレートのフッター注意書きと同じ原則です。",
            "要項は年度更新;公式優先;申込前再確認",
            "古い要項;非公式のみ;更新見落とし",
            "申込前に要項の最新版。",
            "公式情報;試験要項;受験資格",
        ),
    ]
    out = []
    for slug, title, cat, tags, summary, conf, at, lead, pts, mis, tip, rel in specs:
        out.append(
            {
                "slug": slug,
                "title": title,
                "category": cat,
                "tags": tags,
                "summary": summary,
                "confusion_point": conf,
                "pattern_rows": pat,
                "article_title": at,
                "article_lead": lead,
                "exam_points": pts,
                "common_mistakes": mis,
                "memory_tip": tip,
                "related_terms": rel,
                "faq_1_question": f"{title}とは何ですか？",
                "faq_1_answer": summary + " テンプレートの学習導線例として掲載しています。",
                "faq_2_question": "テンプレートでの対策は？",
                "faq_2_answer": "比較表・数値早見・誤答タブを組み合わせ、公式情報で裏取りする流れを想定しています。",
                "faq_3_question": "本番サイトではどうなりますか？",
                "faq_3_answer": "各試験サイトで同型のハブを拡充し、試験固有の内容に差し替えます。",
                "faq_4_question": "関連ページは？",
                "faq_4_answer": "関連用語リンクから用語解説・比較表へ移動できます。",
            }
        )
    return out


def main() -> None:
    # comparisons: 8 existing + 2 new
    h, rows = _load(DATA / "comparisons.csv")
    rows = _assign_slugs(rows[:8], COMPARE_SLUGS[:8])
    rows.extend(_cmp_extra())
    assert len(rows) == 10
    _save(DATA / "comparisons.csv", h, rows)

    h, rows = _load(DATA / "numbers.csv")
    rows = _assign_slugs(rows[:6], NUMBERS_SLUGS[:6])
    rows.extend(_num_extra())
    assert len(rows) == 10
    _save(DATA / "numbers.csv", h, rows)

    h, rows = _load(DATA / "mistakes.csv")
    rows = _assign_slugs(rows[:6], MISTAKES_SLUGS[:6])
    rows.extend(_mis_extra())
    assert len(rows) == 10
    _save(DATA / "mistakes.csv", h, rows)

    print("updated comparisons=10 numbers=10 mistakes=10 with slugs")


if __name__ == "__main__":
    main()
