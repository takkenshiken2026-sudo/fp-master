# -*- coding: utf-8 -*-
"""exam-site-shell 知識ハブ：S30比較スラッグ向けプレミアムFAQ."""

from tools.archive.hub_slug_maps import COMPARE_SLUGS
from tools.archive.write_exam_site_shell_hub_s30 import _OFFICIAL

SLUG_TITLES = {
    "kako-mogi": "過去問と模擬試験",
    "koushiki-youkou": "公式情報と試験要項",
    "goukaku-shutsudai": "合格基準と出題範囲",
    "ichimon-jissen": "一問一答と実践演習",
    "fukushu-kiroku": "復習と学習記録",
    "sanketa-enso": "3択演習と実践演習",
    "juken-goukaku": "受験資格と合格基準",
    "yougo-hikaku": "用語解説と比較表",
    "hub-4tabs": "知識ハブ4タブの使い分け",
    "glossary-vs-numbers": "用語集と数値早見表",
}


def _answers(title: str) -> list[tuple[str, str]]:
    return [
        (
            f"{title}は何から押さえるべきですか？",
            "まず『目的・使うタイミング・確認する情報源』の3点を固定してください。"
            "試験学習では似た用語を入れ替えた選択肢が多く、定義だけでなく学習段階との対応まで説明できると誤答が減ります。"
            "比較表を声に出して説明できる状態を目標にしてください。",
        ),
        (
            "本番に近い学習ではどう使い分けますか？",
            "中盤は論点把握（過去問・用語・比較表）、直前期は形式慣れ（模擬試験・実践演習）に寄せるのが一般的です。"
            "時間配分の練習が不足しないよう、演習形式ごとに週次目標を立て、模試後は必ず誤答理由を記録してください。",
        ),
        (
            "テンプレートサイトでの学習のコツは？",
            "知識ハブの比較・数値・誤答の3種CSVと用語集を往復し、演習モード（一問一答・実践・過去問）で理解を確認します。"
            "プレースホルダー数値は学習用であり、受験判断は必ず公式要項で行ってください。",
        ),
        (
            "公式情報はどのタイミングで確認しますか？",
            "学習開始時・申込前・直前期のほか、制度改正の案内が出た週は必ず試験実施団体のサイトで要項を再確認してください。"
            "非公式情報と食い違う場合は常に公式情報を優先します。"
            + _OFFICIAL,
        ),
    ]


PREMIUM_FAQS: dict[str, list[tuple[str, str]]] = {
    slug: _answers(SLUG_TITLES[slug]) for slug in COMPARE_SLUGS if slug in SLUG_TITLES
}


def apply_premium_faqs(row: dict[str, str]) -> dict[str, str]:
    slug = row.get("slug", "")
    if slug not in PREMIUM_FAQS:
        return row
    row = dict(row)
    for i, (q, a) in enumerate(PREMIUM_FAQS[slug], start=1):
        row[f"faq_{i}_question"] = q
        row[f"faq_{i}_answer"] = a
    return row


def apply_all(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [apply_premium_faqs(r) for r in rows]
