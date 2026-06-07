# 本番サイトレジストリ（10サイト）

テンプレ `exam-site-shell` から派生する資格対策サイトの一覧。**運用の入口**は各 `sites/<サイトID>/SITE.md`。

| # | サイトID | ブランド | 試験 | 本番 URL | GitHub リポジトリ | ローカル |
|---|----------|----------|------|----------|-------------------|----------|
| 1 | `takken-master` | 宅建マスター | 宅地建物取引士 | https://takken-master.jp | [takken-master](https://github.com/takkenshiken2026-sudo/takken-master) | `~/Projects/takken-master` |
| 2 | `mentalhealth-master` | メンタルヘルス二種マスター | MHM検定II種 | https://mentalhealth-master.jp | [mentalhealth-master](https://github.com/takkenshiken2026-sudo/mentalhealth-master) | `~/Projects/mentalhealth-master` |
| 3 | `kikenbutsu-master` | 乙4マスター | 危険物取扱者（乙4） | https://kikenbutsu-master.jp | [kikenbutsu-master](https://github.com/takkenshiken2026-sudo/kikenbutsu-master) | `~/Projects/kikenbutsu-master` |
| 4 | `eisei1shu-master` | 一衛マスター | 第一種衛生管理者 | https://eisei1shu-master.jp | [eisei1shu-master](https://github.com/takkenshiken2026-sudo/eisei1shu-master) | `~/Projects/eisei1shu-master` |
| 5 | `chintaikanrishi-master` | 賃管マスター | 賃貸不動産経営管理士 | https://chintaikanrishi-master.jp | [chintaikanrishi-master](https://github.com/takkenshiken2026-sudo/chintaikanrishi-master) | `~/Projects/chintaikanrishi-master` |
| 6 | `eisei2shu-master` | 二衛マスター | 第二種衛生管理者 | https://eisei2shu-master.jp | [eisei2shu-master](https://github.com/takkenshiken2026-sudo/eisei2shu-master) | `~/Projects/eisei2shu-master` |
| 7 | `kangyou-master` | 管業マスター | 管理業務主任者 | https://kangyou-master.jp | [kangyou-master](https://github.com/takkenshiken2026-sudo/kangyou-master) | `~/Projects/kangyou-master` |
| 8 | `mankan-master` | マン管マスター | マンション管理士 | https://mankan-master.jp | [mankan-master](https://github.com/takkenshiken2026-sudo/mankan-master) | `~/Projects/mankan-master` |
| 9 | `unkan-master` | 運管マスター | 運行管理者 | https://unkan-master.jp | [unkan-master](https://github.com/takkenshiken2026-sudo/unkan-master) | `~/Projects/unkan-master` |
| 10 | `boiler-master` | 2級ボイラー技士マスター | 2級ボイラー技士 | https://boiler-master.jp | [boiler-master](https://github.com/takkenshiken2026-sudo/boiler-master) | `~/Projects/boiler-master.jp` |

## デプロイ方式（2026-06-02 標準化）

| 方式 | サイト |
|------|--------|
| **GitHub Actions**（標準） | 全10サイト — [DEPLOY.md](./DEPLOY.md) |
| レガシー `gh-pages` 同期 | kangyou, kikenbutsu（Actions 移行後は廃止） |
| 独自 workflow | eisei1shu（Supabase 等） |

## 同期難易度

| 区分 | サイト | メモ |
|------|--------|------|
| フル同期可 | mentalhealth, kikenbutsu, eisei1/2shu, chintai, kangyou, mankan, unkan, boiler | `sync_from_template.py --target ...` |
| フェーズ同期 | **takken-master** | `sites/takken-master/manifest-phase*.txt` |

## 関連

- テンプレ: [exam-site-shell](https://github.com/takkenshiken2026-sudo/exam-site-shell)
- 横断スクリプト: [~/Projects/scripts/README.md](../../scripts/README.md)
- 数値照合レジストリ: `~/Projects/docs/hub_numbers_verified.json`
