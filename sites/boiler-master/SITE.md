# 2級ボイラー技士マスター（boiler-master）

## 本番

| 項目 | 値 |
|------|-----|
| サイトID | `boiler-master` |
| ブランド名 | 2級ボイラー技士マスター |
| 試験名 | 2級ボイラー技士試験 |
| 公開 URL | https://boiler-master.jp |
| Git | https://github.com/takkenshiken2026-sudo/boiler-master |
| ローカル | `/Users/otedaiki/Projects/boiler-master.jp` |

## デプロイ

| 項目 | 値 |
|------|-----|
| 方式 | GitHub Actions（[DEPLOY.md](../../docs/DEPLOY.md) 標準） |
| ワークフロー | `.github/workflows/deploy-pages.yml` |
| トリガー | `main` push / `workflow_dispatch` |
| GitHub 設定 | Settings → Pages → **Source: GitHub Actions** |
| ビルド | `python3 tools/build_all.py` → `public_site/` |

GitHub リポジトリ名は `boiler-master`。標準 workflow 済み。

## 同期（テンプレ → 本番）

```bash
cd ~/Projects/exam-site-shell
python3 tools/check_template_drift.py --target ~/Projects/boiler-master.jp
python3 tools/sync_from_template.py --target ~/Projects/boiler-master.jp --dry-run
python3 tools/sync_from_template.py --target ~/Projects/boiler-master.jp --build
cd ~/Projects/boiler-master.jp && python3 tools/build_all.py
```

フル同期不可のサイト（takken）は [sites/takken-master/SITE.md](sites/takken-master/SITE.md) のフェーズ手順に従う。

- 契約・検証: [docs/integration-checklist.md](../../docs/integration-checklist.md)
- 横断一覧: [docs/site-registry.md](../../docs/site-registry.md)

## 同期しないもの

[sites/boiler-master/site-only.paths](./site-only.paths)（存在する場合）および `tools/template_site_only.paths`

---

## 移行手順（テンプレ root で実行）

### 0. 同期前準備（本番）

```bash
python3 sites/boiler-master/migrate_prepare.py --target /path/to/boiler-master.jp
python3 sites/boiler-master/check_ready.py --target /path/to/boiler-master.jp
```

### 1. 同期

```bash
python3 tools/sync_from_template.py --target /path/to/boiler-master.jp --dry-run
python3 tools/sync_from_template.py --target /path/to/boiler-master.jp
```

### 2. 本番用 build_all を戻す（SPA 用 generator 維持）

```bash
cp sites/boiler-master/build_all.py /path/to/boiler-master.jp/tools/build_all.py
```

### 3. ビルド（本番 root）

```bash
cd /path/to/boiler-master.jp
python3 tools/apply_site_config.py
python3 tools/build_all.py
```

詳細: [UI_ALIGNMENT.md](./UI_ALIGNMENT.md)

### 4. 本番で commit / push（運用者）

## 同期しないもの

[site-only.paths](./site-only.paths) および `tools/template_site_only.paths` の boiler-master 節。

## 移行後の残タスク

| 優先 | 内容 |
|------|------|
| 中 | 試験ガイド 92 → 100 本以上 |
| 低 | 用語 CSV のテンプレ拡張列（build で enrich 可） |
| 低 | SPA を `exam-site-data-*.js` へ統一（任意） |
