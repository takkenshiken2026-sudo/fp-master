# 一衛マスター（eisei1shu-master）

## 本番

| 項目 | 値 |
|------|-----|
| サイトID | `eisei1shu-master` |
| ブランド名 | 一衛マスター |
| 試験名 | 第一種衛生管理者試験 |
| 公開 URL | https://eisei1shu-master.jp |
| Git | https://github.com/takkenshiken2026-sudo/eisei1shu-master |
| ローカル | `/Users/otedaiki/Projects/eisei1shu-master` |

## デプロイ

| 項目 | 値 |
|------|-----|
| 方式 | GitHub Actions（[DEPLOY.md](../../docs/DEPLOY.md) 標準） |
| ワークフロー | `.github/workflows/deploy-pages.yml` |
| トリガー | `main` push / `workflow_dispatch` |
| GitHub 設定 | Settings → Pages → **Source: GitHub Actions** |
| ビルド | `python3 tools/build_all.py` → `public_site/` |

独自 workflow（Supabase 注入・旧 generator）。標準テンプレ workflow は上書きしない。

## 同期（テンプレ → 本番）

```bash
cd ~/Projects/exam-site-shell
python3 tools/check_template_drift.py --target ~/Projects/eisei1shu-master
python3 tools/sync_from_template.py --target ~/Projects/eisei1shu-master --dry-run
python3 tools/sync_from_template.py --target ~/Projects/eisei1shu-master --build
cd ~/Projects/eisei1shu-master && python3 tools/build_all.py
```

フル同期不可のサイト（takken）は [sites/takken-master/SITE.md](sites/takken-master/SITE.md) のフェーズ手順に従う。

- 契約・検証: [docs/integration-checklist.md](../../docs/integration-checklist.md)
- 横断一覧: [docs/site-registry.md](../../docs/site-registry.md)

## 同期しないもの

[sites/eisei1shu-master/site-only.paths](./site-only.paths)（存在する場合）および `tools/template_site_only.paths`

---

## 移行手順（テンプレ root で実行）

### 0. CSV 取り込み（本番ルート）

```bash
python3 sites/eisei1shu-master/migrate_import_data.py --target /path/to/eisei1shu-master
python3 sites/eisei1shu-master/check_ready.py --target /path/to/eisei1shu-master
```

### 1. 同期

```bash
python3 tools/sync_from_template.py --target /path/to/eisei1shu-master --dry-run
python3 tools/sync_from_template.py --target /path/to/eisei1shu-master
```

### 2. ビルド（本番 root）

```bash
cd /path/to/eisei1shu-master
python3 tools/apply_site_config.py
python3 tools/build_all.py
```

詳細: [UI_ALIGNMENT.md](./UI_ALIGNMENT.md)

### 3. 本番で commit / push（運用者）

## 同期しないもの

[site-only.paths](./site-only.paths) および `tools/template_site_only.paths` の一衛節を参照。

- SPA: `index.html`, `eisei1-*.js`
- 旧 CSV: `data/eisei1_past_questions.csv` 等
- `privacy-terms.html`（テンプレは `privacy.html`）

## 移行後の残タスク

| 優先 | 内容 |
|------|------|
| 中 | 試験ガイド 40 → 100 本（警告のみ・ビルドは通る） |
| 低 | 用語 CSV の表記・関連語の整備 |
| 低 | SPA を `exam-site-data-*.js` へ統一（任意） |
