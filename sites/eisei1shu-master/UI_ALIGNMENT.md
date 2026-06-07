# 一衛マスター — UI 揃え方

賃管マスターと同様、静的 SEO ページを SPA の `topnav` に合わせます。

## 要点

- `learningNavLabelOverrides.tnav-orig` → **オリジナル問題**（本番 SPA の表記を維持）
- 用語 URL は CSV の `slug` 列で **既存ファイル名を維持**（例: `terms/stress-check.html`）
- `index.html` / `eisei1-master-data.js` は同期対象外

## 過去問 UI（本番 CI）

- `q/` は `.gitignore` のため **GitHub Actions の生成結果がそのまま本番 UI** になる。
- 旧 `build_question_pages.py` は `q-static-header` と年度ハブ埋め込み一覧（テンプレと不一致）。
- 本番は `data/past_questions.csv` があるとき **`build_question_pages.py` が `build_past_question_pages.py` に委譲**する（ワークフロー未更新でもテンプレ UI）。
- 推奨: `.github/workflows/deploy-pages.yml` で `python3 tools/build_all.py` を実行（`workflow` スコープ付き PAT で push）。

## 手順

```bash
cp sites/eisei1shu-master/site-config.json /path/to/eisei1shu-master/
python3 tools/sync_from_template.py --target /path/to/eisei1shu-master
cd /path/to/eisei1shu-master && python3 tools/apply_site_config.py && python3 tools/build_all.py
```

## 目視 URL

- `index.html`（SPA・オリジナル問題ラベル）
- `articles/index.html`
- `articles/shiken-guide/`
- `terms/stress-check.html`
- `q/index.html`
- `about.html`
