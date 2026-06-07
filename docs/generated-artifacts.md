# 生成物と Git 管理方針

## 方針（exam-site-shell テンプレ）

| パス | Git | 理由 |
|------|-----|------|
| `data/*.csv` | **管理する** | コンテンツの正本 |
| `site-config.json` | **管理する** | 設定の正本 |
| `index.html`（SPA） | **管理する** | 手メンテの学習アプリ |
| `articles/`, `terms/`, `q/` | **管理する** | GitHub Pages が `main` ブランチの静的 HTML を配信するため |
| `public_site/` | **管理しない** | `build_all` のコピー先（`.gitignore`） |
| `*_report.txt` | **管理しない** | 一括運用ログ |

テンプレの `articles/` 等は **サンプル兼ビルド検証用** です。本番サイトと同様、「CSV を直す → `build_all` → 生成 HTML を commit」が基本です。

## 本番サイト（10リポジトリ）

各 `~/Projects/<サイトID>/` も同じです。

- 生成 HTML を Git に含めない運用は **GitHub Pages の設定変更が必要**なため、現状は従来どおり commit します。
- 手で `q/**/*.html` を編集しない（`build_all` 再生成で上書き）。

## ローカルだけで試す

```bash
python3 tools/build_all.py
python3 -m http.server 8765
```

`public_site/` で配布バンドルを確認したいときも、上記ビルドの末尾で自動生成されます（Git には載りません）。
