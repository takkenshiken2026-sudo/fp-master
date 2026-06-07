# 賃管マスター（chintaikanrishi-master）

## 本番

| 項目 | 値 |
|------|-----|
| サイトID | `chintaikanrishi-master` |
| ブランド名 | 賃管マスター |
| 試験名 | 賃貸不動産経営管理士試験 |
| 公開 URL | https://chintaikanrishi-master.jp |
| Git | https://github.com/takkenshiken2026-sudo/chintaikanrishi-master |
| ローカル | `/Users/otedaiki/Projects/chintaikanrishi-master` |

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
python3 tools/check_template_drift.py --target ~/Projects/chintaikanrishi-master
python3 tools/sync_from_template.py --target ~/Projects/chintaikanrishi-master --dry-run
python3 tools/sync_from_template.py --target ~/Projects/chintaikanrishi-master --build
cd ~/Projects/chintaikanrishi-master && python3 tools/build_all.py
```

フル同期不可のサイト（takken）は [sites/takken-master/SITE.md](sites/takken-master/SITE.md) のフェーズ手順に従う。

- 契約・検証: [docs/integration-checklist.md](../../docs/integration-checklist.md)
- 横断一覧: [docs/site-registry.md](../../docs/site-registry.md)

## 同期しないもの

[sites/chintaikanrishi-master/site-only.paths](./site-only.paths)（存在する場合）および `tools/template_site_only.paths`

---

## 移行手順（本番を壊さない順）

### 0. 準備確認（本番を変更しない）

テンプレ root で:

```bash
python3 sites/chintaikanrishi-master/check_ready.py --target /path/to/chintaikanrishi-master
python3 tools/check_template_drift.py --target /path/to/chintaikanrishi-master
```

### 1. 本番に `site-config.json` を置く（同期の前に必須）

```bash
cp sites/chintaikanrishi-master/site-config.json /path/to/chintaikanrishi-master/site-config.json
```

※ この時点ではまだ `sync` しない。SPA（`index.html` / `eisei1-*.js`）は触らない。

### 2. 同期 dry-run

```bash
python3 tools/sync_from_template.py --target /path/to/chintaikanrishi-master --dry-run
```

`would copy:` に `index.html` や `data/` が**出ない**ことを確認（`template_site_only.paths` 効き）。

### 3. 同期（まず CSS / generator のみ）

```bash
python3 tools/sync_from_template.py --target /path/to/chintaikanrishi-master
```

### 3b. UI 用の設定反映（本番 root）

```bash
cd /path/to/chintaikanrishi-master
python3 tools/apply_site_config.py
python3 tools/build_all.py
```

詳細・目視 URL 一覧: [UI_ALIGNMENT.md](./UI_ALIGNMENT.md)

失敗したら `validate_csv` / `validate_generated_seo` のログに従い **本番 `data/*.csv` のみ**修正。  
`tools/write_guide_articles_csv.py` はテンプレ `build_all` には含まれない（上書きされても手動実行しなければ動かない）。

### 4. 同期後の作業（別タスク）

| 優先 | 内容 |
|------|------|
| 高 | `glossary_terms.csv` をテンプレ列へ拡張（または段階的スキャフォールド） |
| 中 | `genre` を 12 区分へ統合（レガシー 5 種は `site-config` に暫定登録済み） |
| 中 | 試験ガイド 28 → 100 本、過去問 SEO `q/` 整備 |
| 低 | SPA を `exam-site-data-*.js` へ寄せる（大規模・任意） |

### genre 移行マップ（既存 CSV → 12 区分）

| 現行 genre | 移行先（推奨） |
|------------|----------------|
| 試験概要 | 試験概要 |
| 試験対策 | 学習計画 / 独学対策 |
| 過去問活用 | 過去問活用 |
| 科目別対策 | 分野別対策 |
| 法令対策 | 分野別対策 |
| 重要論点 | 用語整理 / 分野別対策 |
| 学習法 | 独学対策 |

## 本番だけが持つファイル

`tools/template_site_only.paths` の「賃管マスター」節と [site-only.paths](./site-only.paths) を参照。

- SPA: `index.html`, `eisei1-*.js`
- CSV: `data/past_questions.csv`, `data/original_questions.csv`, `data/past_questions_marubatsu_all_explanations.csv` ほか
- 固有 tools: `csv_to_chintaikan_eisei_master.py`, `csv_to_eisei_ichimon_js.py`, `glossary_csv_to_eisei_embed_js.py`, `internal_links.py`

## 最終同期

- 日付: 2026-05-21
- テンプレ commit: （exam-site-shell main・learningNavLabelOverrides 含む）
- 備考:
  - `site-config.json` 配置・過去問 category aliases 拡張
  - `ichimon_questions.csv` / `practice_questions.csv` を既存 CSV から複製
  - `build_all` 成功（過去問 SEO 500件・用語 469・リンク検証 OK）
  - SPA は `eisei1-*.js` のまま（`index.html` 未同期）
