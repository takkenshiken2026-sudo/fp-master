# 実践演習バッチ作成チェックリスト

過去問をベースに数字・表現を変えた実践演習を **1バッチ（計算系10問）** 追加するときの確認用です。  
作業後は `python3 tools/validate_practice_questions.py` を必ず実行してください。

---

## A. バッチ着手前

- [ ] 対象は **図表なし（diagram_id なし）の計算系** か（初回バッチは Tier1 のみ）
- [ ] 種問題の `source_ref`（例: `2025-gakka-12`）を決め、同じ種の派生が既に何問あるか確認した
- [ ] 数値変更後の **正答を手計算または式で再計算** した（推測で選ばない）
- [ ] 過去問と **問題文がほぼ同一** になっていない（数値・主語・語順を変えている）

---

## B. CSV 1行あたり

- [ ] `question_no` が重複していない
- [ ] `category` が FP3級の6分野のいずれか
- [ ] `tags` に `FP3級;学科;実践演習;三答択` と `source:年度-問番号-vN` を含める
- [ ] `source_ref` 列に種を記録（例: `2025-gakka-12`）
- [ ] `stem` に資料本文を混ぜていない（表・図は `diagram_id` へ）
- [ ] 選択肢が3つ（三答択）で空欄がない
- [ ] `correct` が 1〜3 のいずれかで、選択肢の内容と一致
- [ ] `explanation` に「正解はNです」と計算過程がある
- [ ] `explanation_correct` に正答の理由（2〜4文）
- [ ] `explanation_choices` の誤答メモが **各72文字以上**（薄い解説の自動置換を避ける）
- [ ] `explanation_point` に学習ヒントがある

---

## C. バッチ全体（10問）

- [ ] `validate_practice_questions.py` が **エラー0** で通った
- [ ] 同じ `stem`・同じ正答パターンの重複がない
- [ ] 6分野に偏りすぎていない（可能なら2分野以上）
- [ ] サンプル **3問** を人が全文読んで計算・制度の整合を確認した
- [ ] サンプル **2問** を静的ページで表示確認（改行・選択肢・解説ブロック）

---

## D. ビルド・デプロイ前

```bash
python3 tools/validate_practice_questions.py
python3 tools/csv_to_exam_site_past_js.py
python3 tools/build_practice_ichimon_pages.py
# または
python3 tools/build_all.py
```

- [ ] `exam-site-data-practice.js` の問数が想定どおり
- [ ] `q/practice/p{no}/index.html` が新規問数分ある
- [ ] アプリ（`index.html#orig`）で1問実際に解いて表示を確認

---

## E. バッチ後の振り返り

- [ ] ミスが **0件** → 次バッチは同サイズ（計算系10問）で継続
- [ ] ミスが **1件** → 原因をメモし、次は5問に減らす
- [ ] ミスが **2件以上** → 同型の自動化ルールを見直してから再開

---

## 推奨バッチサイズ（再掲）

| 種類 | 1バッチ |
|------|---------|
| 数値計算（図なし） | **10問** |
| 条文・概念 | **5問** |
| 図表あり実技 | **1〜3問** |

---

## 関連ファイル

| ファイル | 役割 |
|----------|------|
| `data/practice_questions.csv` | 実践演習の正本 |
| `data/templates/practice_question_row.template.csv` | 行テンプレート |
| `tools/validate_practice_questions.py` | 自動検証 |
| `.cursor/rules/fp-past-question-authoring.mdc` | 過去問・資料の品質ルール |
