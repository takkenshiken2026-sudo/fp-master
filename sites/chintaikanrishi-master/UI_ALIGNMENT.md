# 賃管マスター — UI 揃え方

静的 SEO ページ（試験ガイド・用語・about 等）を、**学習 SPA（`index.html`）の topnav と同じ見た目**に寄せる手順です。本番を触る前の設計メモ兼チェックリストです。

## 現状のギャップ

| 項目 | 本番（いま） | 同期 + ビルド後（テンプレ） |
|------|--------------|---------------------------|
| ヘッダー | `site-page-header`（テキストリンクのみ） | `topnav site-shell-header`（**SPA と同型**・SVG アイコン） |
| CSS | `site-pages.css` 約 1.6k 行（旧版） | テンプレ `site-pages.css` 約 5.8k 行（**レスポンシブ節あり**） |
| テーマ | `site-theme.css` **なし** | `site-config.json` から **自動生成** |
| フッター | 旧 `site-page-footer` 系 | 固定 `site-footer`（SPA と同型） |
| 試験ガイド一覧 | カード + ジャンルチップ（概ねテンプレ互換） | カード中立・**ジャンル色はチップのみ** |
| 信頼性テーブル | あり | 見出し `#2b2b2b`・本文 `#121212` / `#333333` で統一 |
| SPA ラベル | 「実践演習」（旧「オリジナル問題」） | `learningNavLabelOverrides` **なし** + `apply_site_config` で表記統一 |

色は SPA の `:root`（`#333333` アクセント・`#f0f0f1` 背景・`#111111` 本文）に合わせた草案を `site-config.json` に入れています。

## 同期で UI が揃う理由

1. **`site-pages.css`** … テンプレ正本に差し替え（`topnav` / `article-index-*` / 表スタイル一式）
2. **`site-theme.css`** … `site-config.json` の `theme` から生成（チップ・マークの accent）
3. **`tools/html_footer.py`** … 生成 HTML のヘッダー・フッターを SPA ナビに統一
4. **`tools/apply_site_config.py`** … `about.html` 等の手書きページも `topnav` に差し替え + `site-theme.css` を link 注入
5. **`site-q-index.js` / `site-terms-index.js`** … 過去問・用語索引の UI 補助（新規追加）

`index.html`（SPA）は同期対象外ですが、移行時に `apply_site_config` で次を行えます（任意）:

- フッターを `site-config` の navigation.footer に合わせる
- `site-theme.css` を head に追加（アクセント変数の共有）
- 「オリジナル問題」→「実践演習」は `apply_site_config` の置換で統一（override は使わない）

## 本番反映手順（UI 重点）

```bash
# 1. 設定（テンプレ root）
cp sites/chintaikanrishi-master/site-config.json /path/to/chintaikanrishi-master/

# 2. 同期（CSS / generator / html_footer）
python3 tools/sync_from_template.py --target /path/to/chintaikanrishi-master --dry-run
python3 tools/sync_from_template.py --target /path/to/chintaikanrishi-master

# 3. 本番 root でテーマ生成 + 手書き HTML のヘッダー差し替え
cd /path/to/chintaikanrishi-master
python3 tools/apply_site_config.py

# 4. 記事・用語の再生成（ヘッダー付き HTML）
python3 tools/build_all.py
```

## ビルド後の目視チェック（5 URL + モバイル）

**デスクトップ**

- [ ] `index.html` … topnav・フッターが他ページと矛盾しない
- [ ] `articles/index.html` … カード中立・ジャンルチップにのみ色・検索/チップ動作
- [ ] `articles/exam-overview/` … パンくず・信頼性テーブル・目次
- [ ] `terms/index.html` … 分野チップ・用語一覧（`site-terms-index.js`）
- [ ] `about.html` … `topnav`・フッター固定・「試験ガイド」リンク

**モバイル（DevTools 375px）** — [responsive-layout.md §6.2](../../docs/responsive-layout.md)

- [ ] 上記 URL で **ページ全体の横スクロールなし**
- [ ] topnav 6 項目が横スクロールで使える
- [ ] 信頼性テーブル（試験ガイド記事）が **カード表示**
- [ ] 固定フッターが本文末尾を隠さない

## SPA まで完全に揃える場合（任意・別作業）

- `index.html` のインライン CSS を `site-pages.css` のトークンに段階的に寄せる
- `exam-site-data-*.js` へデータ生成を統一（現状は `eisei1-*.js` のまま）

## 関連ファイル

- 色・ナビ草案: [site-config.json](./site-config.json)
- テーマプレビュー: [site-theme.preview.css](./site-theme.preview.css)
- 移行全体: [SITE.md](./SITE.md)
