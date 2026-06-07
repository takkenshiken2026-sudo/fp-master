# サイト運用メモ（雛形）

`SITE_ID` を実際の ID に置き換えて `sites/<SITE_ID>/SITE.md` として保存してください。

## 本番

| 項目 | 値 |
|------|-----|
| サイトID | `SITE_ID` |
| ブランド名 | （site-config.json の brandName） |
| 試験名 | （site-config.json の examName） |
| 公開 URL | `https://example.com` |
| Git | https://github.com/takkenshiken2026-sudo/REPO |
| ローカル | `/Users/otedaiki/Projects/SITE_ID` |

## デプロイ

| 項目 | 値 |
|------|-----|
| 方式 | GitHub Actions（[DEPLOY.md](../../docs/DEPLOY.md) 標準） |
| ワークフロー | `.github/workflows/deploy-pages.yml` |
| トリガー | `main` push / `workflow_dispatch` |
| GitHub 設定 | Settings → Pages → **Source: GitHub Actions** |
| ビルド | `python3 tools/build_all.py` → `public_site/` |

CI テンプレ: [docs/templates/deploy-pages.workflow.template.yml](../../docs/templates/deploy-pages.workflow.template.yml)

## 新規サイト初回セットアップ

**宅建 fork ではなく、テンプレ正本 `exam-site-shell/index.html` を使うこと。**

```bash
cd /path/to/new-site-repo
# site-config.json / data/*.csv を配置したあと:
python3 tools/generate_brand_assets.py
python3 tools/apply_site_config.py    # INDEX_SEO_HEAD（SNS/OGP）・フッター
python3 tools/build_all.py
python3 tools/validate_site_integration.py
```

- SNS カード確認（トップ URL）: [X Card Validator](https://cards-dev.twitter.com/validator)
- 詳細: [integration-checklist.md §1.9](../../docs/integration-checklist.md)

## 同期（テンプレ root で実行）

`q/`・フッター・用語一覧を直すときは先に [docs/integration-checklist.md](../../docs/integration-checklist.md)。

```bash
cd ~/Projects/exam-site-shell
python3 tools/check_template_drift.py --target /path/to/your-production-site
python3 tools/sync_from_template.py --target /path/to/your-production-site --dry-run
python3 tools/sync_from_template.py --target /path/to/your-production-site --build
```

フル同期不可のサイト（例: takken）は `sites/takken-master/SITE.md` と `manifest-phase*.txt` を参考に段階同期する。

## 同期しないもの

`tools/template_site_only.paths` および `sites/<SITE_ID>/site-only.paths` を参照。

- `index.html`（SPA）— テンプレ正本から取り込み、`apply_site_config` で SEO head を生成
- `site-config.json`, `data/`

## サイト固有メモ

- （例: 過去問 SEO 拡張、CI の Site-specific prep ステップ）

## 最終同期

- 日付:
- テンプレ commit:
- 備考:
