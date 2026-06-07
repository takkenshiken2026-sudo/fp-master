# tools/ — スクリプト分類

`exam-site-shell/tools/` には約150本の Python があります。**普段使うのはごく一部**です。

---

## 日常（これだけでよい）

```bash
python3 tools/build_all.py
```

`build_all.py` から順に呼ばれるもの:

| スクリプト | 役割 |
|------------|------|
| `validate_csv.py` | CSV・リンク先の事前検証 |
| `generate_brand_assets.py` | favicon / og-image |
| `apply_site_config.py` | `index.html` INDEX_SEO_HEAD・静的ページ chrome |
| `csv_to_exam_site_past_js.py` | 過去問 JS |
| `csv_to_exam_site_ichimondou_js.py` | 一問一答 JS |
| `build_past_question_pages.py` | `q/past/` |
| `build_practice_ichimon_pages.py` | `q/practice/`, `q/ichimon/` |
| `build_article_pages.py` | `articles/` |
| `build_glossary_pages.py` | `terms/` |
| `build_hub_retire_redirects.py` | 旧ハブ URL リダイレクト |
| `build_sitemap.py` | `sitemap.xml` |
| `validate_generated_seo.py` | 生成 SEO 検証 |
| `validate_site_integration.py` | フッター・ヘッダー・SPA SEO 契約 |
| `validate_internal_links.py` | 内部リンク |
| `validate_public_content.py` | 運用者向け文言の混入検出 |
| `prepare_public_site.sh` | `public_site/` 配置 |

`tools/ci_deploy_build.sh`（GitHub Actions 用）も **`build_all.py` を実行**します。

---

## 本番同期

| スクリプト | 用途 |
|------------|------|
| `sync_from_template.py` | マニフェストに従い本番へコピー（`--target` 必須） |
| `check_template_drift.py` | テンプレとの差分確認 |
| `template_sync_manifest.txt` | コピー対象一覧 |
| `template_site_only.paths` | 本番だけが持つパス（上書き禁止） |

---

## バッチ・過去作業用 → `archive/`

約90本を `tools/archive/` に移動済み。`build_all` からは呼ばれません。

```bash
python3 tools/archive/run_hub_deploy_final.py   # 例: 全サイト一括（要注意）
```

一覧・注意: [archive/README.md](archive/README.md)

**モノレポ横断スクリプト**（10サイト同時）は `~/Projects/scripts/`（`_deploy_*.py`, `_hub_*.py` 等）。

---

## スキャフォールド（新規コンテンツ）

| スクリプト | 用途 |
|------------|------|
| `scaffold_guide_article.py` | 試験ガイド1本 |
| `scaffold_glossary_term.py` | 用語1件 |
| `scaffold_affiliate_article.py` | アフィリエイト記事 |

ルールは `docs/guide-article-template.md` 等を参照。
