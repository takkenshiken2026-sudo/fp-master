# メンタルヘルス二種マスター（mentalhealth-master）

## 本番

| 項目 | 値 |
|------|-----|
| サイトID | `mentalhealth-master` |
| ブランド名 | メンタルヘルス二種マスター |
| 試験名 | メンタルヘルス・マネジメント検定II種 |
| 公開 URL | https://mentalhealth-master.jp |
| Git | https://github.com/takkenshiken2026-sudo/mentalhealth-master |
| ローカル | `/Users/otedaiki/Projects/mentalhealth-master` |

## デプロイ

| 項目 | 値 |
|------|-----|
| 方式 | GitHub Actions（[DEPLOY.md](../../docs/DEPLOY.md) 標準） |
| ワークフロー | `.github/workflows/deploy-pages.yml` |
| トリガー | `main` push / `workflow_dispatch` |
| GitHub 設定 | Settings → Pages → **Source: GitHub Actions** |
| ビルド | `python3 tools/build_all.py` → `public_site/` |

標準 workflow 済み。

## 同期（テンプレ → 本番）

```bash
cd ~/Projects/exam-site-shell
python3 tools/check_template_drift.py --target ~/Projects/mentalhealth-master
python3 tools/sync_from_template.py --target ~/Projects/mentalhealth-master --dry-run
python3 tools/sync_from_template.py --target ~/Projects/mentalhealth-master --build
cd ~/Projects/mentalhealth-master && python3 tools/build_all.py
```

フル同期不可のサイト（takken）は [sites/takken-master/SITE.md](sites/takken-master/SITE.md) のフェーズ手順に従う。

- 契約・検証: [docs/integration-checklist.md](../../docs/integration-checklist.md)
- 横断一覧: [docs/site-registry.md](../../docs/site-registry.md)

## 同期しないもの

[sites/mentalhealth-master/site-only.paths](./site-only.paths)（存在する場合）および `tools/template_site_only.paths`

---

## 移行（2026-05-21）— ローカル完了

- 静的 SEO（試験ガイド・用語・`q/`・about 等）をテンプレ共通エンジンへ同期済み
- `python3 tools/build_all.py` 成功（検証・内部リンク・公開コンテンツ含む）
- SPA（`index.html` / `eisei1-*.js`）は維持（`exam-site-data-*.js` は生成されるが SPA 未接続）
- `genre` を 12 区分へ統合済み（18行を `migrate_mentalhealth_genres.py` で更新）
- 用語 URL は従来どおり `terms/<url_slug>/index.html`（`tools/build_glossary_pages.py` をサイト向けに調整）

### genre 移行マップ

| 現行 genre | 移行先 |
|------------|--------|
| 試験概要 | 試験概要 |
| 制度理解 | 試験概要 |
| 受験情報 / 受験要項 | 受験・申込 |
| 出題範囲 | 出題・形式 |
| 学習計画 | 学習計画 |
| 学習法 | 独学対策 |
| 直前対策 | 直前・当日 |
| 分野別対策 / 復職支援 | 分野別対策 |

## 反映手順

```bash
cp sites/mentalhealth-master/site-config.json /path/to/mentalhealth-master/
python3 tools/migrate_mentalhealth_genres.py --target /path/to/mentalhealth-master
python3 tools/sync_from_template.py --target /path/to/mentalhealth-master
cd /path/to/mentalhealth-master && python3 tools/apply_site_config.py && python3 tools/build_all.py
```
