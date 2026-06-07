# 二衛マスター — UI 揃え方

静的 SEO ページを **SPA（`index.html`）の topnav** と同型に寄せる手順です。

## 現状のギャップ

| 項目 | 本番（いま） | 同期 + apply_site_config 後 |
|------|--------------|------------------------------|
| SPA | 既に `topnav` | フッターを `site-config` に統一・`site-theme.css` 追加 |
| 静的 about / related | `site-page-header` | `topnav site-shell-header` |
| 試験ガイド一覧 | 独自インライン CSS + 旧ヘッダー | `apply_site_config` でヘッダー差し替え（本文 CSS は残る） |
| 個別記事 98 本 | 旧ヘッダー・`articles/{slug}.html` | **build_all 前は手付き**（一括再生成で URL が変わる） |
| 用語 217 件 | `terms/{slug}.html` | build_all 前は手付き |
| `site-pages.css` | 約 8.8k 行（旧） | テンプレ正本（約 4.3k + topnav 一式） |
| `site-theme.css` | なし | `site-config.json` から生成 |

## 安全な UI 同期（記事・用語・q を壊さない）

```bash
# テンプレ root
cp sites/eisei2shu-master/site-config.json /path/to/eisei2shu-master/
python3 tools/sync_from_template.py --target /path/to/eisei2shu-master
cd /path/to/eisei2shu-master
python3 tools/apply_site_config.py
```

**実行しない:** `python3 tools/build_all.py`（`articles/`・`terms/`・`q/` を上書きするため）

## ビルド後の目視チェック（apply のみ）

- [ ] `index.html` … フッターリンクが `privacy-terms.html`・試験ガイド・用語集と一致
- [ ] `about.html` … `topnav`・お問い合わせ URL
- [ ] `articles/index.html` … ヘッダーが SPA と同型（カード色は既存のまま可）
- [ ] `articles/benkyou-jikan.html` … **まだ旧ヘッダーのまま**なら正常（個別記事は Phase 4）
- [ ] `terms/index.html` … 索引ページのヘッダー

## SPA 表記

`site-config.json` の `learningNavLabelOverrides.tnav-orig` で **「オリジナル問題」** を維持（テンプレの「実践演習」置換をスキップ）。

## 関連

- [SITE.md](./SITE.md) — 全体移行順序
- [site-config.json](./site-config.json) — 色・ナビ草案
