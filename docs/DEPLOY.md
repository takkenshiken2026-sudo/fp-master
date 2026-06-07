# デプロイ標準（全10本番サイト）

本番公開は **GitHub Pages + GitHub Actions** に統一します。  
`main` への push（または手動実行）→ CI で `build_all.py` → `public_site/` を Pages に公開。

---

## 標準フロー

```
site-config.json / data/*.csv を編集
  → python3 tools/build_all.py（ローカル確認）
  → git commit && git push origin main
  → Deploy GitHub Pages ワークフロー
  → https://<ドメイン>/
```

| 項目 | 標準 |
|------|------|
| ワークフロー | `.github/workflows/deploy-pages.yml`（テンプレ: [deploy-pages.workflow.template.yml](../docs/templates/deploy-pages.workflow.template.yml)） |
| GitHub 設定 | Settings → Pages → **Build and deployment → Source: GitHub Actions** |
| ビルド | `python3 tools/build_all.py` |
| 公開物 | `public_site/`（artifact） |
| カスタムドメイン | リポジトリ直下 `CNAME` |

---

## 初回セットアップ（リポジトリごと）

1. `.github/workflows/deploy-pages.yml` を配置（テンプレ: [deploy-pages.workflow.template.yml](../.github/workflows/deploy-pages.workflow.template.yml)）
2. GitHub → **Settings → Pages → Source: GitHub Actions**
3. `main` に push して Actions が成功することを確認
4. カスタムドメイン DNS が `*.github.io` を向いていることを確認

PAT で workflow を push する場合は **`workflow` スコープ**が必要です（[GITHUB_REMOTE_SETUP.md](./GITHUB_REMOTE_SETUP.md) 参照）。

---

## レガシー: `gh-pages` ブランチ配信（移行中）

**kangyou-master** / **kikenbutsu-master** は以前 `gh-pages` ブランチから配信していました。

| 旧方式 | 問題 |
|--------|------|
| `main` push + `sync_gh_pages_branch.sh` | push だけでは本番が更新されない。手順忘れが起きやすい |

**移行手順:**

1. `.github/workflows/deploy-pages.yml` を `main` に merge
2. GitHub → Settings → Pages → Source を **GitHub Actions** に変更
3. Actions が成功したら本番 URL を確認
4. （任意）`gh-pages` ブランチを削除

`tools/sync_gh_pages_branch.sh` は **非推奨**。Actions 移行後は使わない。

---

## サイト別の例外

| サイト | 備考 |
|--------|------|
| **eisei1shu-master** | 独自 workflow（Supabase 注入・旧 generator 混在）。標準テンプレと差分あり |
| **eisei2shu-master** | 標準 workflow。ビルドパイプラインはサイト固有スクリプトを確認 |
| **takken-master** | 標準 workflow。`build_past` / `build_all` は部分同期（[sites/takken-master/SITE.md](../sites/takken-master/SITE.md)） |
| **boiler-master** | GitHub リポジトリ名は `boiler-master`、ローカルは `boiler-master.jp` |

一覧: [site-registry.md](./site-registry.md)

---

## トラブルシュート

| 症状 | 対処 |
|------|------|
| deploy ジョブが即 fail | Pages Source が **GitHub Actions** か確認 |
| build は通るが本番が古い | キャッシュ（10分）または別ブランチ配信の残存 |
| workflow push が拒否される | PAT に `workflow` スコープを付与 |
| `public_site/` が空 | `prepare_public_site.sh` が `build_all` 末尾で実行されているか |

---

## 横断確認

```bash
# gh インストール後
bash ~/Projects/scripts/check_deploy_status.sh
```

詳細: [~/Projects/scripts/README.md](../../scripts/README.md)
