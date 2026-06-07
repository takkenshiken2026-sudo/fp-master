# 乙4マスター（kikenbutsu-master）

## 本番

| 項目 | 値 |
|------|-----|
| サイトID | `kikenbutsu-master` |
| ブランド名 | 乙4マスター |
| 試験名 | 危険物取扱者試験（乙種第4類） |
| 公開 URL | https://kikenbutsu-master.jp |
| Git | https://github.com/takkenshiken2026-sudo/kikenbutsu-master |
| ローカル | `/Users/otedaiki/Projects/kikenbutsu-master` |

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
python3 tools/check_template_drift.py --target ~/Projects/kikenbutsu-master
python3 tools/sync_from_template.py --target ~/Projects/kikenbutsu-master --dry-run
python3 tools/sync_from_template.py --target ~/Projects/kikenbutsu-master --build
cd ~/Projects/kikenbutsu-master && python3 tools/build_all.py
```

フル同期不可のサイト（takken）は [sites/takken-master/SITE.md](sites/takken-master/SITE.md) のフェーズ手順に従う。

- 契約・検証: [docs/integration-checklist.md](../../docs/integration-checklist.md)
- 横断一覧: [docs/site-registry.md](../../docs/site-registry.md)

## 同期しないもの

[sites/kikenbutsu-master/site-only.paths](./site-only.paths)（存在する場合）および `tools/template_site_only.paths`

---

## 展開手順

```bash
python3 tools/sync_from_template.py --target /path/to/kikenbutsu-master --dry-run
python3 tools/sync_from_template.py --target /path/to/kikenbutsu-master
cd /path/to/kikenbutsu-master && python3 tools/build_all.py
git add -A && git commit -m "..." && git push origin main
# build_all 内で gh-pages 同期（push 権限が必要）
```

## 同期しないもの

[site-only.paths](./site-only.paths) — `build_all.py`, `validate_csv.py`, `build_glossary_pages.py` など

## 最終同期

- 日付: 2026-05-28
- 4タブ・compare/numbers・gh-pages 同期: OK
- 本番検証: OK
