# 2級ボイラーマスター — UI 揃え方

静的 SEO ページを SPA（`index.html` の `topnav`）と同型にする手順です。

## 同期で揃うもの

- `site-pages.css`（topnav / 記事一覧カード / 表スタイル）
- `site-theme.css`（`site-config.json` の `theme` から生成）
- `tools/html_footer.py`（生成 HTML のヘッダー・フッター）
- `site-q-index.js` / `site-terms-index.js`（過去問・用語索引）

## 本番反映（要約）

```bash
# テンプレ root
python3 sites/boiler-master/migrate_prepare.py --target /path/to/boiler-master.jp
python3 tools/sync_from_template.py --target /path/to/boiler-master.jp
cp sites/boiler-master/build_all.py /path/to/boiler-master.jp/tools/build_all.py

cd /path/to/boiler-master.jp
python3 tools/apply_site_config.py
python3 tools/build_all.py
```

## 目視チェック

- [ ] `articles/index.html` — カード中立・ジャンル色はチップのみ
- [ ] 記事1本 — 信頼性テーブル（執筆・確認・事実確認日・主な参照元）、`topnav`
- [ ] `terms/index.html` — 用語索引が動作
- [ ] `index.html`（SPA）— 学習タブ・過去問が従来どおり動作
