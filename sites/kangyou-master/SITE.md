# 管業マスター（kangyou-master）

## 本番

| 項目 | 値 |
|------|-----|
| サイトID | `kangyou-master` |
| ブランド名 | 管業マスター |
| 試験名 | 管理業務主任者試験 |
| 公開 URL | https://kangyou-master.jp |
| Git | https://github.com/takkenshiken2026-sudo/kangyou-master |
| ローカル | `/Users/otedaiki/Projects/kangyou-master` |

## デプロイ

| 項目 | 値 |
|------|-----|
| 方式 | GitHub Actions（[DEPLOY.md](../../docs/DEPLOY.md) 標準） |
| ワークフロー | `.github/workflows/deploy-pages.yml` |
| トリガー | `main` push / `workflow_dispatch` |
| GitHub 設定 | Settings → Pages → **Source: GitHub Actions** |
| ビルド | `python3 tools/build_all.py` → `public_site/` |

**gh-pages から Actions へ移行中。** Pages Source を GitHub Actions に切替後、`sync_gh_pages_branch.sh` は使わない。

## 同期（テンプレ → 本番）

```bash
cd ~/Projects/exam-site-shell
python3 tools/check_template_drift.py --target ~/Projects/kangyou-master
python3 tools/sync_from_template.py --target ~/Projects/kangyou-master --dry-run
python3 tools/sync_from_template.py --target ~/Projects/kangyou-master --build
cd ~/Projects/kangyou-master && python3 tools/build_all.py
```

フル同期不可のサイト（takken）は [sites/takken-master/SITE.md](sites/takken-master/SITE.md) のフェーズ手順に従う。

- 契約・検証: [docs/integration-checklist.md](../../docs/integration-checklist.md)
- 横断一覧: [docs/site-registry.md](../../docs/site-registry.md)

## 同期しないもの

[sites/kangyou-master/site-only.paths](./site-only.paths)（存在する場合）および `tools/template_site_only.paths`

---

## 展開手順

```bash
python3 tools/sync_from_template.py --target /path/to/kangyou-master
cd /path/to/kangyou-master && python3 tools/build_all.py
git add -A && git commit -m "..." && git push origin main
```

## 同期しないもの

[site-only.paths](./site-only.paths)

## 最終同期

- 日付: 2026-05-28
- 4タブ・compare/numbers・gh-pages 同期: OK
- 本番検証: OK
