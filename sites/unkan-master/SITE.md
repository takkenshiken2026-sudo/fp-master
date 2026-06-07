# 運管マスター（unkan-master）

## 本番

| 項目 | 値 |
|------|-----|
| サイトID | `unkan-master` |
| ブランド名 | 運管マスター |
| 試験名 | 運行管理者試験 |
| 公開 URL | https://unkan-master.jp |
| Git | https://github.com/takkenshiken2026-sudo/unkan-master |
| ローカル | `/Users/otedaiki/Projects/unkan-master` |

## デプロイ

| 項目 | 値 |
|------|-----|
| 方式 | GitHub Actions（[DEPLOY.md](../../docs/DEPLOY.md) 標準） |
| ワークフロー | `.github/workflows/deploy-pages.yml` |
| トリガー | `main` push / `workflow_dispatch` |
| GitHub 設定 | Settings → Pages → **Source: GitHub Actions** |
| ビルド | `python3 tools/build_all.py` → `public_site/` |

標準 workflow 済み。

## 同期（テンプレ → 本番）

```bash
cd ~/Projects/exam-site-shell
python3 tools/check_template_drift.py --target ~/Projects/unkan-master
python3 tools/sync_from_template.py --target ~/Projects/unkan-master --dry-run
python3 tools/sync_from_template.py --target ~/Projects/unkan-master --build
cd ~/Projects/unkan-master && python3 tools/build_all.py
```

フル同期不可のサイト（takken）は [sites/takken-master/SITE.md](sites/takken-master/SITE.md) のフェーズ手順に従う。

- 契約・検証: [docs/integration-checklist.md](../../docs/integration-checklist.md)
- 横断一覧: [docs/site-registry.md](../../docs/site-registry.md)

## 同期しないもの

[sites/unkan-master/site-only.paths](./site-only.paths)（存在する場合）および `tools/template_site_only.paths`

---

