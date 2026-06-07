# -*- coding: utf-8 -*-
"""試験対策 知識ハブ S44 追加分（各10件）."""

from tools.archive.write_exam_site_shell_hub_s30 import _OFFICIAL, cmp, mis, num

L = "法令・制度"
R = "契約・実務"
O = "設備・その他"

def _related(cat: str) -> str:
    if cat == L:
        return "公式情報;試験要項;合格基準"
    if cat == R:
        return "過去問;模擬試験;復習"
    return "比較表;用語解説;学習記録"

COMPARISON_TOPICS = [
    ("s44-gakushu-kiroku-cmp", "学習記録の比較", O),
    ("s44-sogo-shiage-diff", "総仕上げの違い", L),
    ("s44-gakushu-kiroku-matome", "学習記録の整理", O),
    ("s44-sogo-shiage-point", "総仕上げの要点", L),
    ("s44-gakushu-kiroku-taihi", "学習記録の対比", O),
    ("s44-sogo-shiage-kubun", "総仕上げの区分", L),
    ("s44-gakushu-kiroku-tejun", "学習記録の手順", O),
    ("s44-sogo-shiage-seido", "総仕上げの制度", L),
    ("s44-gakushu-kiroku-unyo", "学習記録の運用", O),
    ("s44-sogo-shiage-hantei", "総仕上げの判定", L),
]

NUMBER_TOPICS = [
    ("s44-gakushu-kiroku-num", "学習記録の数値", O),
    ("s44-sogo-shiage-cycle", "総仕上げの周期", L),
    ("s44-gakushu-kiroku-meyasu", "学習記録の目安", O),
    ("s44-sogo-shiage-freq", "総仕上げの頻度", L),
    ("s44-gakushu-kiroku-ratio", "学習記録の比率", O),
    ("s44-sogo-shiage-time", "総仕上げの時間", L),
    ("s44-gakushu-kiroku-count", "学習記録の回数", O),
    ("s44-sogo-shiage-kijun", "総仕上げの基準", L),
    ("s44-gakushu-kiroku-haibun", "学習記録の配分", O),
    ("s44-sogo-shiage-check", "総仕上げの確認", L),
]

MISTAKE_TOPICS = [
    ("s44-kon-gakushu-kiroku-kon", "学習記録の混同", O),
    ("s44-kon-sogo-shiage-gokai", "総仕上げの誤認", L),
    ("s44-kon-gakushu-kiroku-reverse", "学習記録の逆転", O),
    ("s44-kon-sogo-shiage-omit", "総仕上げの省略", L),
    ("s44-kon-gakushu-kiroku-blind", "学習記録の盲信", O),
    ("s44-kon-sogo-shiage-over", "総仕上げの過剰", L),
    ("s44-kon-gakushu-kiroku-noconf", "学習記録の未確認", O),
    ("s44-kon-sogo-shiage-nouse", "総仕上げの未使用", L),
    ("s44-kon-gakushu-kiroku-skip", "学習記録の放置", O),
    ("s44-kon-sogo-shiage-zero", "総仕上げのゼロ", L),
]

COMPARISONS_ADD = [
    cmp(
        slug, title, cat,
        "学習法;S44;比較",
        f"{title}について、試験で混同しやすい観点を5軸で整理します。",
        "観点A;観点B",
        [
            ("定義", ["主語・目的の確認", "手順・対象の確認"]),
            ("頻出", ["類似語の入替", "数値・条件付き出題"]),
            ("運用", ["点検・記録の順序", "異常時の対応"]),
            ("試験", ["名称だけで判断", "旧要項の流用"]),
            ("誤答", ["比較軸を先に固定", "条件文を最後まで読む"]),
        ],
        f"{title}｜試験対策 S44",
        "S44では学習記録・総仕上げを中心に整理します。比較表で軸を先に固定してください。" + _OFFICIAL,
        "学習記録;総仕上げ;条件文の主語確認",
        "名称だけ暗記;旧要項流用;主語の読み飛ばし",
        "「主語→手順→法令→誤答」。",
        _related(cat),
        [
            ("この比較の先に覚える点は？", "主語を一文で言えるようにしてください。その後に手順と法令を広げると正誤判定の再現性が上がります。"),
            ("本番での使い方は？", "問題文のキーワードから比較軸を1つ選び、表の該当行と照合してから選択肢を読みます。"),
            ("S43との違いは？", "S43は基礎整理、S44は学習記録・総仕上げの深掘りです。"),
            ("公式確認はどこですか？", "試験要項と関係法令で必ず最新確認してください。" + _OFFICIAL),
        ],
    )
    for slug, title, cat in COMPARISON_TOPICS
]

NUMBERS_ADD = [
    num(
        slug, title, cat,
        "学習法;S44;数値",
        f"{title}で押さえる代表数値と確認観点を整理します。",
        "代表値は要項・法令で確認",
        [
            ("代表数値", "要項・規則で確認", "年度更新に注意"),
            ("適用条件", "対象・手順を確認", "主語の取り違え防止"),
            ("記録", "運転・学習記録", "異常時は原因を併記"),
            ("試験対策", "数値+条件で暗記", "単独暗記を避ける"),
        ],
        f"{title}｜試験対策 数値S44",
        "S44の数値は学習記録・総仕上げと条件のセットで覚えると得点が安定します。" + _OFFICIAL,
        "数値と条件をセット;単位を確認;最新法令で照合",
        "数値のみ暗記;他設備の値を流用;旧要項の使用",
        "「数値・単位・条件・対象」を1行で書く。",
        _related(cat),
        [
            ("数値問題のコツは？", "単位と対象を先に確認し、次に条件文を読みます。"),
            ("復習の進め方は？", "誤答時は読み落とした条件を記録し、型別再演習してください。"),
            ("実務との接続は？", "日常の点検・学習記録と対応づけると定着しやすくなります。"),
            ("公式確認は？", "受験直前に必ず最新版を照合してください。" + _OFFICIAL),
        ],
    )
    for slug, title, cat in NUMBER_TOPICS
]

MISTAKES_ADD = [
    mis(
        slug, title, cat,
        "学習法;S44;誤答",
        f"{title}で発生しやすい誤答パターンを4ケースで整理します。",
        "学習記録・総仕上げは名称が似るため、主語と時点の読み飛ばしが起きやすい。",
        [
            ("用語", "名称だけで判断", "主語・手順をセット確認", "同義語の入替え"),
            ("手順", "順序の逆転", "確認→実施→記録の順", "類似工程の混同"),
            ("数値", "単位未確認", "数値・単位・条件を同時確認", "近似値の誤誘導"),
            ("情報", "旧規則の流用", "最新規則で照合", "非公式情報優先"),
        ],
        f"{title}｜試験対策 誤答S44",
        "S44の誤答は学習記録・総仕上げの読み落としが中心です。誤答型を記録し、比較表へ戻って根拠を再確認してください。" + _OFFICIAL,
        "誤答型を分類;主語を固定で読む;比較表と往復",
        "原因を残さない;同型を放置;法令未確認",
        "「誤答原因を1行で書く」を毎回実施。",
        _related(cat),
        [
            ("誤答パターンの使い方は？", "解いた直後に型を選び、同型問題をまとめて再演習します。"),
            ("最優先で直す点は？", "主語確認です。ここが改善すると数値・法令問題の取りこぼしも減ります。"),
            ("過去問との併用は？", "過去問の誤答に型タグを付け、S44比較表で整理し直してください。"),
            ("公式確認は？", "誤答修正後は要項・関係法令の更新有無を必ず確認してください。" + _OFFICIAL),
        ],
    )
    for slug, title, cat in MISTAKE_TOPICS
]
