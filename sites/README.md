# sites/ — 本番サイトごとのメモ（テンプレ内）

本番リポジトリそのものはここには置きません。資格サイトごとに「固有拡張・同期メモ」だけをテンプレ側で管理します。

**横断一覧:** [docs/site-registry.md](../docs/site-registry.md) · **デプロイ:** [docs/DEPLOY.md](../docs/DEPLOY.md)

## ディレクトリの意味

```
sites/
  README.md           … このファイル
  _example/           … 新規サイト用の雛形
  <サイトID>/         … 例: takken-master
    SITE.md           … 本番パス・デプロイ・固有ファイル・運用メモ
    site-only.paths   … 同期しないパス（任意）
    manifest-*.txt    … フェーズ同期（takken 等）
```

## 使い方

1. 新しい本番サイトを作るときは `sites/_example/SITE.md` をコピーして `sites/<サイトID>/SITE.md` を作る
2. テンプレを直したら [docs/multi-site-workflow.md](../docs/multi-site-workflow.md) の手順で同期（`--target` に本番のローカルパスを指定）
   - `q/`・フッター・用語一覧を触るときは先に [docs/integration-checklist.md](../docs/integration-checklist.md)
   - **UI がスマホで崩れる**ときは [docs/responsive-layout.md](../docs/responsive-layout.md)
3. **本番 GitHub リポジトリは運用者が push** — テンプレ作業だけではリモートは更新しない

## 本番10サイト

| サイトID | 本番 URL | SITE.md |
|----------|----------|---------|
| `takken-master` | https://takken-master.jp | [SITE.md](./takken-master/SITE.md) |
| `mentalhealth-master` | https://mentalhealth-master.jp | [SITE.md](./mentalhealth-master/SITE.md) |
| `kikenbutsu-master` | https://kikenbutsu-master.jp | [SITE.md](./kikenbutsu-master/SITE.md) |
| `eisei1shu-master` | https://eisei1shu-master.jp | [SITE.md](./eisei1shu-master/SITE.md) |
| `chintaikanrishi-master` | https://chintaikanrishi-master.jp | [SITE.md](./chintaikanrishi-master/SITE.md) |
| `eisei2shu-master` | https://eisei2shu-master.jp | [SITE.md](./eisei2shu-master/SITE.md) |
| `kangyou-master` | https://kangyou-master.jp | [SITE.md](./kangyou-master/SITE.md) |
| `mankan-master` | https://mankan-master.jp | [SITE.md](./mankan-master/SITE.md) |
| `unkan-master` | https://unkan-master.jp | [SITE.md](./unkan-master/SITE.md) |
| `boiler-master` | https://boiler-master.jp | [SITE.md](./boiler-master/SITE.md) |

※ テンプレの CI / スクリプトから特定の本番 URL やリポジトリへは**自動アクセスしません**。
