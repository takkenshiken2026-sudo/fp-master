# ブランドカラーレジストリ

各サイトの `site-config.json` → `theme.accent` を正とする。ファビコン・ロゴマーク・`theme-color`・UI アクセントに使用。

- 文字色: 全サイト `theme.accentText` = `#ffffff`
- 有料模試バナー: 全サイト固定 `#c0392b`（`docs/paid-mock-exam.md`）
- 記事本文の強調青: `#2563a8`（`seo-editorial.css`、accent とは独立）

## 方針

- 彩度: おおむね 35〜50%、明度 32〜40%（乙4除く）
- 同系統サイトは明度差、別系統は色相差で識別
- 赤 `#c0392b` は乙4専用（他サイトに使わない）

## 本番10サイト

| # | サイトID | accent | ファミリー |
|---|----------|--------|------------|
| 1 | `takken-master` | `#2c4a6e` | 不動産・青 |
| 2 | `mentalhealth-master` | `#4a6b5c` | 衛生・緑 |
| 3 | `kikenbutsu-master` | `#c0392b` | 危険・赤 |
| 4 | `eisei1shu-master` | `#2d5c45` | 衛生・深緑 |
| 5 | `chintaikanrishi-master` | `#5c4d7a` | 不動産・紫 |
| 6 | `eisei2shu-master` | `#4a8f6a` | 衛生・明緑 |
| 7 | `kangyou-master` | `#1a5f7a` | 管理・ティール |
| 8 | `mankan-master` | `#3f4f8a` | 不動産・インディゴ |
| 9 | `unkan-master` | `#8f5a24` | 運行・橙 |
| 10 | `boiler-master` | `#7a4a32` | 設備・茶 |

## 増設予約（5スロット）

試験・サイトID未定。新規 scaffold 時に空きスロットから1色を割り当てる。

| # | スロット | accent | ファミリー |
|---|----------|--------|------------|
| 11 | `reserved-11` | `#3d5a6b` | 設備・スレート青 |
| 12 | `reserved-12` | `#4a5568` | 建築・クールグレー |
| 13 | `reserved-13` | `#914530` | 危険・焦茶 |
| 14 | `reserved-14` | `#5a6640` | 土木・オリーブ |
| 15 | `reserved-15` | `#3a6f72` | ビル設備・シアン |

## 反映手順

```bash
# site-config.json の theme.accent を更新後
python3 tools/generate_brand_assets.py --force
python3 tools/apply_site_config.py
bash tools/prepare_public_site.sh   # ローカル確認時
```

GitHub Actions デプロイ時は `ci_deploy_build.sh` が brand 生成を含む。
