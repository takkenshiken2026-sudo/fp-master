# マン管マスター（mankan-master）

## 本番

| 項目 | 値 |
|------|-----|
| サイトID | `mankan-master` |
| ブランド名 | マン管マスター |
| 試験名 | マンション管理士試験 |
| 公開 URL | https://mankan-master.jp |
| Git | https://github.com/takkenshiken2026-sudo/mankan-master |
| ローカル | `/Users/otedaiki/Projects/mankan-master` |

## デプロイ

| 項目 | 値 |
|------|-----|
| 方式 | GitHub Actions（[DEPLOY.md](../../docs/DEPLOY.md) 標準） |
| ワークフロー | `.github/workflows/deploy-pages.yml` |
| トリガー | `main` push / `workflow_dispatch` |
| GitHub 設定 | Settings → Pages → **Source: GitHub Actions** |
| ビルド | `python3 tools/build_all.py` → `public_site/` |

標準 workflow を追加（旧: main 直配信）。

## 同期（テンプレ → 本番）

```bash
cd ~/Projects/exam-site-shell
python3 tools/check_template_drift.py --target ~/Projects/mankan-master
python3 tools/sync_from_template.py --target ~/Projects/mankan-master --dry-run
python3 tools/sync_from_template.py --target ~/Projects/mankan-master --build
cd ~/Projects/mankan-master && python3 tools/build_all.py
```

フル同期不可のサイト（takken）は [sites/takken-master/SITE.md](sites/takken-master/SITE.md) のフェーズ手順に従う。

- 契約・検証: [docs/integration-checklist.md](../../docs/integration-checklist.md)
- 横断一覧: [docs/site-registry.md](../../docs/site-registry.md)

## 同期しないもの

[sites/mankan-master/site-only.paths](./site-only.paths)（存在する場合）および `tools/template_site_only.paths`

---

