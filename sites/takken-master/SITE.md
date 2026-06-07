# 宅建マスター（takken-master）

## 本番

| 項目 | 値 |
|------|-----|
| サイトID | `takken-master` |
| ブランド名 | 宅建マスター |
| 試験名 | 宅地建物取引士試験 |
| 公開 URL | https://takken-master.jp |
| Git | https://github.com/takkenshiken2026-sudo/takken-master |
| ローカル | `/Users/otedaiki/Projects/takken-master` |

## デプロイ

| 項目 | 値 |
|------|-----|
| 方式 | GitHub Actions（[DEPLOY.md](../../docs/DEPLOY.md) 標準） |
| ワークフロー | `.github/workflows/deploy-pages.yml` |
| トリガー | `main` push / `workflow_dispatch` |
| GitHub 設定 | Settings → Pages → **Source: GitHub Actions** |
| ビルド | `python3 tools/build_all.py` → `public_site/` |

標準 workflow。同期はフェーズ別（manifest-phase*.txt）。

## 同期（テンプレ → 本番）

**フェーズ同期サイト** — 一括 `sync_from_template` だけでは完結しません。

正本: [sites/takken-master/SITE.md](sites/takken-master/SITE.md) · `manifest-phase*.txt`

```bash
cd ~/Projects/exam-site-shell
python3 tools/check_template_drift.py --target ~/Projects/takken-master \
  --manifest sites/takken-master/manifest-phase1.txt
# フェーズごとに sync → 本番 build_all → 検証
```

## 同期しないもの

[sites/takken-master/site-only.paths](./site-only.paths)（存在する場合）および `tools/template_site_only.paths`

## 上書き禁止（フル同期しない）

| パス | 理由 |
|------|------|
| `tools/build_all.py` | `csv_to_takken_*`, `build_legacy_redirects` |
| `tools/build_past_question_pages.py` | `past_question_seo.py`、信頼表、用語リンク等 |
| `data/past_questions.csv` | 481問・enrich 済み |

`html_footer.py` は **上書きではなくマージ**（`static_q_*` 維持 + `q_hub_links_html` / `site_shell_footer` / `footer_href`）。

## フェーズ同期（テンプレ root で実行）

### 0. 本番をクリーンに

```bash
cd /Users/otedaiki/Projects/takken-master
git pull --ff-only
git status
```

### 1. フェーズ1 — CSS・新規モジュール

```bash
cd /Users/otedaiki/Projects/exam-site-shell

python3 tools/check_template_drift.py \
  --target /Users/otedaiki/Projects/takken-master \
  --manifest sites/takken-master/manifest-phase1.txt

python3 tools/sync_from_template.py \
  --target /Users/otedaiki/Projects/takken-master \
  --manifest sites/takken-master/manifest-phase1.txt
```

**同期しない:** `about.html`, `related-sites.html`（テンプレは `q/practice`・`q/ichimon` 前提）。誤同期したら `git checkout HEAD -- about.html related-sites.html`。

```bash
cd /Users/otedaiki/Projects/takken-master
python3 tools/apply_site_config.py
python3 tools/build_all.py
```

### 2. フェーズ2 — 本番 `build_past` へマージ

テンプレの `build_past_question_pages.py` から取り込む（本番ファイルを**置換しない**）:

- `from tools.q_explanation import build_explanation_html`
- `from tools.q_similar_questions import build_similar_questions_html, load_question_catalog`
- 解説: `build_explanation_html(page, row)`
- 類似: `build_similar_questions_html(..., mode="past")`（`publish_root` フィルタ）
- ハブ: `build_q_index()` に `q_hub_links_html(rel_path, current="past")`（`html_footer` から import）

### 3. フェーズ3 — 実践・一問一答・フッター・用語

**マニフェスト:** [manifest-phase3.txt](./manifest-phase3.txt)（テンプレ root で `--manifest` 指定）

本番へコピーまたはマージ:

| ファイル | 内容 |
|----------|------|
| `tools/build_practice_ichimon_pages.py` | `INDEX_CONFIG`（分野グループ・`categoryOrder`） |
| `tools/csv_to_exam_site_past_js.py` | 実践 SPA JS・`level` タグ |
| `tools/csv_to_exam_site_ichimondou_js.py` | 一問一答 `publicPath`（`q/ichimon/...`） |
| `tools/import_orig_questions_to_practice_csv.py` | ORIG → 実践 CSV |
| `tools/import_base_questions_to_ichimon_csv.py` | 4択 → 一問一答 CSV |
| `tools/enrich_past_explanation_choices.py` | 過去問 CSV 補完 |
| `tools/html_footer.py` | `q_hub_*`, `site_shell_footer`（`static_q_*` 維持） |
| `tools/build_glossary_pages.py` | `terms_index_item_dict` に `shortDef` |
| `tools/validate_site_integration.py` | 統合契約（件数・分野順・フッター） |
| `site-q-index.js` | `categoryOrder`・`data-group` ジャンプ |
| `site-terms-index.js` | `shortDef \|\| definition` |
| `site-config.json` | フッター「過去問一覧」→ `q/index.html` |
| `tools/apply_site_config.py` | 本番 `index.html` フッターを site-config から再生成 |

```bash
cd /Users/otedaiki/Projects/exam-site-shell
python3 tools/sync_from_template.py \
  --target /Users/otedaiki/Projects/takken-master \
  --manifest sites/takken-master/manifest-phase3.txt

cd /Users/otedaiki/Projects/takken-master
# 初回または ORIG 更新時のみ:
python3 tools/import_orig_questions_to_practice_csv.py
python3 tools/import_base_questions_to_ichimon_csv.py --keep-manual
python3 tools/enrich_past_explanation_choices.py --csv data/past_questions.csv
python3 tools/build_all.py
python3 tools/validate_site_integration.py
python3 tools/validate_internal_links.py
```

### 4. フェーズ4 — ナレッジハブ SEO・検証器（2026-05-28）

**マニフェスト:** [manifest-phase4.txt](./manifest-phase4.txt)

```bash
cd /Users/otedaiki/Projects/exam-site-shell
python3 tools/sync_from_template.py \
  --target /Users/otedaiki/Projects/takken-master \
  --manifest sites/takken-master/manifest-phase4.txt \
  --site-only sites/takken-master/site-only.paths

cd /Users/otedaiki/Projects/takken-master
python3 tools/build_all.py
```

`build_glossary_pages.py` は **reading 込み slug** のため site-only 保護。ハブ lookup は `slug_file_for_glossary_row()` で本番と一致させる。

### 5. フェーズ5 — SEO 記事デザイン（2026-05-30）

**マニフェスト:** [manifest-phase5-seo-editorial.txt](./manifest-phase5-seo-editorial.txt)  
**手順正本:** [docs/seo-editorial-rollout-checklist.md](../../docs/seo-editorial-rollout-checklist.md)

```bash
cd /Users/otedaiki/Projects/exam-site-shell
python3 tools/check_template_drift.py \
  --target /Users/otedaiki/Projects/takken-master \
  --manifest sites/takken-master/manifest-phase5-seo-editorial.txt

python3 tools/sync_from_template.py \
  --target /Users/otedaiki/Projects/takken-master \
  --manifest sites/takken-master/manifest-phase5-seo-editorial.txt \
  --site-only sites/takken-master/site-only.paths

# build_glossary_pages.py は site-only → seo_editorial パッチを手動適用（reading slug 維持）

cd /Users/otedaiki/Projects/takken-master
python3 tools/build_article_pages.py
python3 tools/build_glossary_pages.py
python3 tools/build_compare_pages.py
python3 tools/build_numbers_mistakes_pages.py
python3 tools/build_seo_editorial_preview.py
python3 tools/verify_seo_editorial_rollout.py --target . --template /path/to/exam-site-shell
python3 tools/validate_generated_seo.py
```

### 6. 検証（統合チェックリスト §3.3 と同じ）

- `/q/index.html` — タブ3つ
- `/q/practice/index.html` — タブ・表
- `/terms/index.html` — 定義列（JS 後も非空）
- `/` — フッター過去問 → ハブ

### 7. commit / push

運用者が本番リポジトリで実施。

## 同期しないもの

[site-only.paths](./site-only.paths) + `tools/template_site_only.paths`

## 移行ログ

| 日付 | フェーズ | build_all | 備考 |
|------|----------|-----------|------|
| 2026-05-23 | 1 | OK | CSS/JS/q_explanation |
| 2026-05-23 | 2 | OK | 解説4段・類似・ハブタブ |
| 2026-05-23 | 3 | OK | enrich 481・practice/ichimon・リンク 0 broken |
| 2026-05-23 | 追補 | OK | フッター `q/index.html`、用語 `shortDef`、index フッター絶対パス |
| 2026-05-23 | 4 | f845ab98 | OK | 実践・一問一答一覧フィルタ、ichimon publicPath、validate_site_integration |
| 2026-05-23 | 5 | 9a1a6687 / cbaeab19 | OK | 実践1000・一問一答1437 静的化、一問一答分野順、取り込みスクリプト |
| 2026-05-28 | 4 | — | OK | ナレッジハブ SEO・compare JS・validate_public_content、slug lookup 統一、リンク 5191 OK |
| 2026-05-30 | 5 | — | OK | seo-editorial.css・要点ボックス・リンクカード・内部リンク強化。verify + validate_generated_seo ERROR 0 |

## 10サイト展開

| 順 | サイト | 備考 |
|----|--------|------|
| 1 | **takken-master** | フェーズ同期（本ファイル） |
| 2 | mentalhealth-master | OK |
| 3 | kikenbutsu-master | OK |
| 4 | eisei1shu-master | OK |
| 5 | chintaikanrishi-master | OK |
| 6 | eisei2shu-master | OK |
| 7 | kangyou-master | OK |
| 8 | mankan-master | OK |
| 9 | unkan-master | OK |
| 10 | boiler-master.jp | OK |
