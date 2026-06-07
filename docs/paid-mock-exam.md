# 有料模試（note）導線 — 共通ルール

サイト内の無料演習とは別に、note で販売する有料予想模試へ誘導する UI の設置ルール。**正本はこのドキュメント**。

## いつ使うか

- note に有料 PDF 模試（予想模試）を用意したサイトだけ `site-config.json` に `paidMockExam` を追加する
- 未設定・`url` 空のサイトでは UI は一切出さない（テンプレート側はコード込み・表示オフ）

## 設置位置（固定）

| 場所 | 内容 |
|------|------|
| **問題を解く**（`quiz-start`） | モード一覧 **05番**。04=弱点集中の直後 |
| **結果画面**（`page-score`） | スコア下ボタン群の**下**。区切り線 + CTA ストリップ |

番号・レイアウト・CSS クラス名はサイト間で揃える。文言だけ `site-config.json` で差し替え。

## カラー（固定）

有料模試バナーは **サイトの `theme.accent` を使わない**。販売導線として全サイト共通の赤系トークンを使う。

```css
--paid-mock-accent: #c0392b;
--paid-mock-accent-text: #ffffff;
--paid-mock-accent-soft: color-mix(in srgb, #c0392b 11%, #ffffff);
--paid-mock-accent-border: color-mix(in srgb, #c0392b 26%, #ffffff);
--paid-mock-accent-shadow: color-mix(in srgb, #c0392b 12%, transparent);
```

タグ・CTA 枠・「詳細 ↗」は `--paid-mock-accent*` のみ。乙4（`theme.accent` が赤）でも同じ変数を使う。

## `site-config.json` スキーマ

```json
"paidMockExam": {
  "url": "https://note.com/shikaku_master/n/xxxxxxxxxxxx",
  "modeTitle": "予想模試（PDF・3回分）",
  "modePurpose": "本番形式で実力確認したい",
  "priceLabel": "¥590",
  "scoreMeta": "PDF・3回",
  "scoreLead": "本番形式の予想模試",
  "footnote": "※ note で販売する有料コンテンツ（¥590）です。サイト内の無料演習とは別商品です。"
}
```

| キー | 必須 | 用途 |
|------|------|------|
| `url` | ○ | note 記事 URL。空なら非表示 |
| `modeTitle` | ○ | 05番カード見出し・結果 CTA タイトル |
| `modePurpose` | ○ | 05番カードの一行説明（目的） |
| `priceLabel` | ○ | 例: `¥590`（タグ・メタに表示） |
| `scoreMeta` | 推奨 | 結果 CTA のサブ行（例: `PDF・3回` / `35問×2`） |
| `scoreLead` | 推奨 | 結果 CTA リード文の `<strong>` 内（例: `本番同形式の35問`） |
| `footnote` | ○ | 05番下・CTA 下の注記（価格・別商品である旨） |

`site-config.js` は `python3 tools/site_config.py`（または `build_all` 内）で JSON から再生成する。

## 実装の所在

| ファイル | 内容 |
|----------|------|
| `index.html`（テンプレ） | CSS（`--paid-mock-*`）、`#score-paid-mock-wrap`、`getPaidMockExamConfig` / `injectPaidMockExamCard` / `renderScorePaidMockPromo`、`gotoPage`・`showScore` フック |
| `site-config.json` | サイト別文言・URL・回数 |

テンプレ修正後は対象サイトへ `sync_from_template.py --target ~/Projects/<site>` → `paidMockExam` を追記 → デプロイ。

## 新規サイトへの追加手順

1. テンプレから `index.html` を同期（未同期サイトは乙4 / メンタルを参照してマージ可）
2. `site-config.json` に `paidMockExam` を追加（上記スキーマ）
3. `python3 tools/site_config.py` で `site-config.js` を更新
4. ローカルで「問題を解く」05番・結果画面 CTA を確認
5. 本番反映
   - **管業・乙4**: `bash tools/sync_gh_pages_branch.sh`（対象 repo 内）
   - **その他**: `main` push → GitHub Actions

note URL だけ差し替える場合:

```bash
python3 tools/set_paid_mock_exam_url.py 'https://note.com/shikaku_master/n/xxxxxxxxxxxx'
```

（`site-config.json` の `paidMockExam` ブロックが前提）

## 文言の例

| サイト | modeTitle | scoreMeta | scoreLead |
|--------|-----------|-----------|-----------|
| 宅建 | 予想模試（PDF・2回分） | `50問×2` | 本番同形式の50問 |
| 乙4 | 予想模試（PDF・2回分） | `35問×2` | 本番同形式の35問 |
| メンタル二種 | 予想模試（PDF・3回分） | `PDF・3回` | 本番形式の予想模試 |

回数・問題数は **note 商品の実態**に合わせる。価格変更時は `priceLabel` と `footnote` をセットで更新。

## やってはいけないこと

- サイト `--accent`（グレー/黒テーマ）を有料模試バナーに流用する
- 05番以外の位置に置く・無料モードと同じ見た目にする
- `target="_blank"` / `rel="noopener noreferrer"` を省略する
- 他サイトの `paidMockExam` をコピペしたまま URL だけ変える（回数・文言の確認を怠る）

## 参照実装

- 宅建: `~/Projects/takken-master`（`paidMockExam.url` 設定後に 05番・結果 CTA が表示）
- 乙4: `~/Projects/kikenbutsu-master`
- メンタル二種: `~/Projects/mentalhealth-master`
