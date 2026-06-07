# 二衛マスター（eisei2shu-master）

## 本番

| 項目 | 値 |
|------|-----|
| サイトID | `eisei2shu-master` |
| ブランド名 | 二衛マスター |
| 試験名 | 第二種衛生管理者試験 |
| 公開 URL | https://eisei2shu-master.jp |
| Git | https://github.com/takkenshiken2026-sudo/eisei2shu-master |
| ローカル | `/Users/otedaiki/Projects/eisei2shu-master` |

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
python3 tools/check_template_drift.py --target ~/Projects/eisei2shu-master
python3 tools/sync_from_template.py --target ~/Projects/eisei2shu-master --dry-run
python3 tools/sync_from_template.py --target ~/Projects/eisei2shu-master --build
cd ~/Projects/eisei2shu-master && python3 tools/build_all.py
```

フル同期不可のサイト（takken）は [sites/takken-master/SITE.md](sites/takken-master/SITE.md) のフェーズ手順に従う。

- 契約・検証: [docs/integration-checklist.md](../../docs/integration-checklist.md)
- 横断一覧: [docs/site-registry.md](../../docs/site-registry.md)

## 同期しないもの

[sites/eisei2shu-master/site-only.paths](./site-only.paths)（存在する場合）および `tools/template_site_only.paths`

---

## 移行手順（本番を壊さない順）

### 0. 準備確認（本番を変更しない）

テンプレ root で:

```bash
python3 sites/eisei2shu-master/check_ready.py --target /path/to/eisei2shu-master
python3 tools/check_template_drift.py --target /path/to/eisei2shu-master
```

### 1. `site-config.json` を本番に置く（同期の前に必須）

```bash
cp sites/eisei2shu-master/site-config.json /path/to/eisei2shu-master/site-config.json
```

### 2. 同期 dry-run

```bash
cat tools/template_site_only.paths sites/eisei2shu-master/site-only.paths > /tmp/eisei2-sync-site-only.paths
python3 tools/sync_from_template.py --target /path/to/eisei2shu-master --dry-run \
  --site-only /tmp/eisei2-sync-site-only.paths
```

`would copy:` に `index.html`・`data/`・`articles/`・`q/`・`about.html` が**出ない**こと。

### 3. 同期（CSS / generator のみ・**--build はまだ付けない**）

```bash
cat tools/template_site_only.paths sites/eisei2shu-master/site-only.paths > /tmp/eisei2-sync-site-only.paths
python3 tools/sync_from_template.py --target /path/to/eisei2shu-master \
  --site-only /tmp/eisei2-sync-site-only.paths
```

### 3b. UI 反映（本番 root）

```bash
cd /path/to/eisei2shu-master
python3 tools/apply_site_config.py
```

`about.html` / `related-sites.html` / `articles/index.html` / SPA フッターが topnav 化。  
**この時点では `build_all.py` を実行しない**（既存 `articles/*.html`・`terms/*.html`・`q/` の URL を壊さないため）。

詳細: [UI_ALIGNMENT.md](./UI_ALIGNMENT.md)

### 4. データ移行 + ビルド（本番 root）

```bash
python3 sites/eisei2shu-master/migrate_import_data.py --target /path/to/eisei2shu-master
cd /path/to/eisei2shu-master
python3 /path/to/exam-site-shell/sites/eisei2shu-master/build_all.py
```

`build_all.py` は **既存 `q/`（721 ページ）を維持**し、`articles/{slug}/` + `terms/{slug}.html` を生成したあと、旧フラット URL へリダイレクト HTML を置きます。

### 5. データ移行の残タスク（別タスク・順序固定）

| 優先 | 内容 | 注意 |
|------|------|------|
| 高 | `migrate_past_questions.py` → `data/past_questions.csv` | 既存 `q/` URL と突合してから `build_past_question_pages` |
| 高 | `docs/glossary-terms-checklist.csv` → `glossary_terms.csv` | 217→300件は別途拡充 |
| 高 | 既存 `articles/*.html` → `guide_articles.csv` | **URL**: `foo.html` vs `foo/index.html` を決めてから再生成 |
| 中 | `privacy.html` 分割 or リダイレクト | 現状は `privacy-terms.html` で運用継続可 |
| 低 | SPA を `exam-site-data-*.js` へ | 大規模・任意 |

### URL を変えない場合の原則

- テンプレ標準の `build_article_pages.py` は `articles/{slug}/index.html` を出力する。
- 本番の `articles/{slug}.html` を維持するには、**再生成前に**リダイレクト HTML を置くか、ビルド側にフラット URL オプションを足す。
- 同様に用語は `terms/{slug}.html`（本番）と `terms/g-*.html`（テンプレ）でスラッグ規則が異なる。

## 本番だけが持つファイル

[site-only.paths](./site-only.paths) と `tools/template_site_only.paths` の「二衛マスター」節を参照。

## 最終同期

- 日付: 2026-05-21
- テンプレ commit: （exam-site-shell main・`build_glossary_pages` レガシー slug 対応含む）
- 備考:
  - `migrate_import_data.py` + `build_all.py` 成功（リンク検証 OK）
  - 試験ガイド **100** 本（+ `glossary-how-to`, `past-question-strategy`）
  - 用語 **216** 本・過去問 SEO **721**（既存 `q/` 維持）
  - フラット URL → `write_flat_redirects.py` でリダイレクト維持
