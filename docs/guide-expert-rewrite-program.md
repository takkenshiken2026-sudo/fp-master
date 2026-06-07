# 試験ガイド「編集合格」全件リライト・プログラム

**目的:** `exam-schedule` お手本（`tools/mankan_rewrite_exemplar.py`）と同水準で、全サイトの公開ガイドを揃える。  
**旧 `hand_done` は v0（下書き）扱い。** 本プログラムの完了ラベルは **`expert_pass`** とする。

関連:
- 5本 batch のコマンド手順: [guide-hand-rewrite-batch-workflow.md](./guide-hand-rewrite-batch-workflow.md)
- SEO 共通方針: [seo-article-guidelines.md](./seo-article-guidelines.md)
- アフィリエイト: [affiliate/affiliate-article-rules.md](./affiliate/affiliate-article-rules.md)

---

## 1. 完了定義（3段階）

| 段階 | ラベル | 意味 | 公開 |
|------|--------|------|------|
| v0 | `hand_done`（廃止予定） | 禁止句除去・180字・手書き印 | 可だが再編集対象 |
| **v1** | **`expert_pass`** | 本ドキュメントのルーブリック＋機械ゲート＋目視1本 | **本番の正** |
| v2 | `expert_polished`（任意） | Tier A のみ：監査ゼロ・KPI追跡 | 将来 |

`revision_note` 例: `2026-06-04: 編集合格（手書きリライト）`  
`original_note` に執筆メモ（参照要項・確認日）を残してよい（読者非公開）。

---

## 2. お手本（参照必須）

| 項目 | 正本 |
|------|------|
| 記事 slug | `exam-schedule`（マン管） |
| batch | `tools/mankan_rewrite_exemplar.py`（サイト sync 後は各サイト `tools/*_rewrite_exemplar.py` または batch 内コメント参照） |
| 公開 HTML | `articles/exam-schedule/index.html` |
| 表 CSS | `seo-editorial.css` … `.seo-article-section table.seo-info-table` |

**お手本の特徴（全記事で再現する）**

1. **具体:** 年度・日付・金額・機関の正式名称・分野数（例: マン管7分野）
2. **正本:** 「要項で再確認」を必ず1回以上。非公式まとめ依存を書かない
3. **独自:** slug 固有の見出し・FAQ・混同注意（他記事のリードコピペ禁止）
4. **表:** 比較・一覧・日程は **パイプ表** を1つ以上（本文セクション内）
5. **導線:** `related_links` に内部 slug **3件**（`slug:表示ラベル`）。演習・用語・関連ガイドを具体名で
6. **禁止テンプレなし:** 「公式情報はどこで確認しますか」だけの FAQ、他資格の分野数、量産リード
7. **具体＋例示:** 各節に **場面が浮かぶ一文**（`例えば` / `たとえば` / `イメージすると` 等）。表の数字だけで済ませない（§3.1.1）

---

## 3. 品質ルーブリック（expert_pass 必須）

### 3.1 全記事共通

| # | 項目 | 合格基準 |
|---|------|----------|
| A | 検索意図 | `user_intent` が「読むと何が分かるか」1文で明確。title と lead が**同一文でない** |
| B | リード | 80字以上。試験名＋**この記事だけの角度**（年度・手続・分野など） |
| C | 節 | `section_1_heading`〜`section_5_heading` が本文と一致。**5節すべて別テーマ**（同型チェックリストの使い回し禁止） |
| D | 節本文 | 各180字以上（sanitize 後）。**箇条書きだけで字数を満たさない**（説明段落＋表 or リスト） |
| E | 表 | **最低1つ**のパイプ表（`| 列 | 列 |` ＋ `| --- |`）。比較・日程・手順のいずれか |
| F | FAQ | 質問3つ**重複なし**。slug 固有の疑問（サイト横断の「公式はどこ」だけは不可） |
| G | 内部リンク | `related_links` 内部 slug **2件以上**（推奨3件） |
| H | 禁止句 | `guide_rewrite_rules.REWRITE_FORBIDDEN_PHRASES` および `audit_guide_prose_quality` **0件** |
| I | サイト辞書 | `data/guide_site_lexicon.json`（要作成）の **禁止語・必須語** に適合 |
| J | 目視 | batch 5本をブラウザで確認（表・誤字・事実の違和感） |

### 3.1.1 具体性＋例示（手書き batch 必須）

表・数値表だけでは「読者の頭に場面が残らない」ため、**手書き batch は以下を満たす**（`revision_note` に `具体例` を含める。編集合格お手本 `exam-schedule` のみ例外）。

| # | 項目 | 合格基準 |
|---|------|----------|
| K | リードの逆算 | `lead` に **残り○週 / ○か月 / ○月○日** の逆算アンカー **と**、数値・日付入りの **例えば/たとえば** 1文 |
| L | 節ごとの例示 | **5節中4節以上**に、マーカー＋**具体アンカー**（％・問数・曜日・章・正答率など）を含む例示文 |
| M | 浅い例示禁止 | `例えば〜してください` だけで数値がない文は **ERROR**（浅い例示） |
| N | 例示なし節 | 例示がない節は表外 prose に **具体アンカー3つ以上** |
| O | FAQ | **3回答中2つ以上**が具体性あり。**1つ以上**は `例えば/たとえば` 入りの場面描写 |
| P | user_intent | リード冒頭の写し禁止。**読了後の得**＋数値 or 例示1つ |
| Q | 好比 | **好比** は資格固有の数値・分野とセットで可（比喩だけは不可） |
| R | auto-prose | `revision_note` が手書きでも **量産署名2件以上**なら ERROR |
| S | batch 見出し | 5 slug batch で **同一 section_N_heading が4回以上** → ERROR |
| T | 機械チェック | `validate_guide_hand_batch.py` → `guide_concrete_rewrite_rules.py` |

**例示の書き方（良い / 悪い）**

```text
悪い: 例えば演習量を調整してください。
良い: たとえば管理組合運営の正答率が40％なら、翌月の演習20問のうち12問をこの分野に寄せます。

悪い: 復習を続けましょう。
良い: 例えば日曜3時間のうち最初の45分は、前週のミス5問を解き直し専用にします。

悪い: 例えば計画を見直しましょう。（数値なし・浅い）
良い: 具体例として、Googleカレンダーに「8/3申込開始」「11/29試験日」を別色で入れると混同しにくいです。
```

### 3.2 ジャンル別（各 slug は該当ジャンルの行を満たす）

| ジャンル | 必ず入れる具体要素 | 推奨表 | 避ける構成 |
|----------|-------------------|--------|------------|
| 試験概要 | 合格基準・試験時間・科目/分野数・実施機関 | 数値・確認項目一覧 | 演習10問だけの5項目リスト |
| 受験・申込 | 年度・手数料・申込方法2種の締切差・正本URL名 | 日程早見・申込比較 | 資格確認と日程が逆順のテンプレ |
| 合格・難易度 | 合格率の読み方・公式発表数値の確認先 | 指標の見方（断定しすぎない） | 体験談のみ |
| 学習計画 / 独学 | 週時間・残週数・**当該試験の分野名** | 月次マイルストーン | 他資格の分野数 |
| 過去問活用 | 演習量の目安・当サイトの q/terms 導線 | 段階（テキスト→分野→通し） | 過去問だけで合格 |
| 分野別対策 | **分野名**・頻出論点 or 典型誤答1つ | 論点と参照章 | 全分野共通の独学話 |
| 用語ハブ活用法 | `terms/` の開き方・演習との往復 | 1周の手順 | 用語の定義の写し |
| 直前・当日 | 持ち物・時間配分・禁止物品 | 当日チェック表 | 一般論のみ |
| 注意点・更新 | 改正年・確認習慣 | 更新時に見る公式ページ | 古い年度の断定 |
| アフィリエイト | [affiliate-article-rules](./affiliate/affiliate-article-rules.md) | brief 比較表 | 一般ガイドの5節テンプレ |

---

## 4. 本文・表記法

### 4.1 パイプ表（CSV `section_*_body`）

```text
| 項目 | 内容 | 確認先 |
| --- | --- | --- |
| 試験日 | 2026年11月29日（日） | 要項「試験日程」 |
```

- ビルド: `seo_body_markup.py` → `table.seo-info-table`
- 見出し行: `--seo-table-head-bg`（薄灰）、データ行: 白、枠線グリッド

### 4.2 使ってよいマークアップ

- 段落（空行区切り）
- `- ` 箇条書き
- `### ` 小見出し（混同注意など）
- `;` 区切りは action_items のみ推奨（本文は表 or リスト優先）

### 4.3 禁止運用

- `enrich_short_guide_sections.py`（水増し）
- `rewrite_guide_boilerplate.py` の一括適用（手書き済み行への再上書き）
- 他サイト batch の `section_*_body` のコピペ（類似度監査で ERROR 化予定）

---

## 5. batch 運用（変更なし＋ expert 追加）

### 5.1 単位

- **1 batch = 5 slug**、**同一ジャンル**（例: 受験・申込 5本）
- 正本: `tools/{site}_rewrite_batchN.py` の `REWRITES`

### 5.2 1 batch の手順

```bash
cd ~/Projects/<site>

# 0) 次の5 slug 雛形（任意）
python3 tools/scaffold_guide_rewrite_batch.py \
  --batch-num 21 --priority A --limit 5 \
  -o tools/<site>_rewrite_batch21.py

# 1) REWRITES をお手本水準で手書き（または AI 下書き→人が修正）

# 2) 機械チェック（apply 前）
python3 tools/validate_guide_hand_batch.py --batch tools/<site>_rewrite_batch21.py

# 3) 適用・検証（enrich なし）
python3 tools/run_guide_hand_batch.py --batch tools/<site>_rewrite_batch21.py

# 4) 目視5本（articles/*/index.html）

# 5) サイト全体ビルド・リンク検証
python3 tools/build_all.py
```

### 5.3 batch 必須列（v0 ＋ expert）

v0 列は [guide-hand-rewrite-batch-workflow.md](./guide-hand-rewrite-batch-workflow.md) 参照。  
expert 追加:

| 列 | 追加要件 |
|----|----------|
| `lead` | title と**異なる**文 |
| `key_points` | 5項目、`;` 区切り、**数字 or 固有名詞を2つ以上** |
| `related_links` | 内部 slug **3件** |
| `section_*_body` | **表を含む節が1つ以上** |
| `revision_note` | `編集合格` を含む |

---

## 6. 機械ゲート（公開前に全部通す）

| 順 | ツール | 条件 |
|----|--------|------|
| 1 | `validate_guide_hand_batch.py` | batch 単体 ERROR 0 |
| 2 | `run_guide_hand_batch.py` | `--only-slugs` で当該5本の CSV + `audit_guide_prose_quality --strict` PASS |
| 3 | `validate_csv.py` | サイト全体（batch 後） |
| 4 | `build_all.py` | 生成・統合・内部リンク |
| 5 | `audit_editorial_quality.py --strict` | 任意・週1回 |

**今後追加（Phase 0 ツール）**

- `validate_guide_expert_batch.py` … 表の有無・title≠lead・FAQ 横断禁止句・サイト辞書
- `audit_guide_cross_similarity.py` … リード/節の類似度上限
- `data/guide_site_lexicon.json` … 分野数・機関名・禁止フレーズ（サイトごと sync）

---

## 7. 運用方針：**サイトごとに完走**（既定）

**原則:** 次のサイトに着手するのは、前サイトの **全 published ガイドが `expert_pass`** になってから。  
週の作業は常に **「今のサイトの次の5本」** だけ（§5 の batch ループ）。

### 7.1 サイト完了の定義

| 条件 | 内容 |
|------|------|
| 対象 | `content_status=published` の試験ガイド（アフィリは ASP リンク済みのみ別枠） |
| 本文 | 各 slug が §3 ルーブリックを満たす |
| 印 | `revision_note` に `編集合格` |
| 機械 | `audit_guide_prose_quality --root . --strict` が **サイト全体** で PASS |
| 目視 | 全 batch 通過後、Tier A をスポット再読（10本程度） |

### 7.2 推奨サイト順

| 順 | サイト | 公開本数 | 備考 | batch 目安（÷5） |
|----|--------|----------|------|----------------|
| 1 | **mankan-master** | 129 | お手本 `exam-schedule` あり | **~26** |
| 2 | takken-master | 49 | **expert_pass 49/49 完走**（2026-06-04） | ~10 ✓ |
| 3 | chintaikanrishi-master | 152 | **expert_pass 149/149 完走**（buildable・2026-06-04） | ~31 ✓ |
| 4 | kikenbutsu-master | 133 | **expert_pass 130/130 完走**（2026-06-04） | ~27 ✓ |
| 5 | kangyou-master | 161 | **expert_pass 56/161 着手中**（2026-06-04） | ~33 |
| 6 | eisei1shu-master | 173 | auto_pending | ~35 |
| 7 | eisei2shu-master | 224 | auto_pending | ~45 |
| 8 | unkan-master | 139 | needs_rewrite 多 | ~28 |
| 9 | mentalhealth-master | 161 | needs_rewrite 多 | ~33 |
| 10 | boiler-master.jp | 221 | 最大 | ~45 |

全サイト合計 **約310 batch**（週5 batch ≈ **62週**）。**マン管だけ** なら約 **5週**（25本/週）。

### 7.3 横断の事前準備（Phase 0・1回）

テンプレ `exam-site-shell` で表記法・`validate_guide_expert_batch`・サイト辞書を整え、各サイトへ `sync_from_template.py`。

進捗確認:

```bash
cd ~/Projects/<site>
python3 tools/guide_rewrite_campaign.py --root .
grep -c '編集合格' data/guide_articles.csv   # 暫定: expert_pass 件数
python3 tools/audit_guide_prose_quality.py --root . --strict
```

---

## 8. 週次スプリント（現実的ペース）

| 指標 | 控えめ | 標準 | 攻め |
|------|--------|------|------|
| batch / 週 | 3（15本） | 5（25本） | 8（40本） |
| 1サイト完走（例129本） | ~9週 | ~5週 | ~3週 |
| 全10サイト | ~100週 | ~62週 | ~39週 |

**1本あたり工数目安:** 事実確認込み 30〜60分（Tier A は上限寄り）。

---

## 9. 人手と AI の分担

| 作業 | 人 | AI（Cursor） |
|------|-----|----------------|
| 要項・年度の事実確認 | **必須** | 下書き案・表のたたき |
| `REWRITES` への確定反映 | **必須** | 雛形・禁止句チェック |
| 目視5本 / batch | **必須** | HTML 差分の指摘 |
| apply / build | 人 or CI | コマンド実行 |

**禁止:** AI が5 slug を「テンプレ差し替えのみ」で一括完成 → そのまま apply。

---

## 10. 既存 `hand_done` の扱い

- **再編集必須。** `revision_note` に手書きがあっても expert ルーブリック対象。
- 優先: リード＝title、禁止句残存、`3分野` 等のサイト辞書違反、FAQ 横断定型。
- chintai / takken は「完了」表示でも **Tier A から spot 監査** → 問題あれば batch で上書き。

---

## 11. テンプレ同期

ルール・ツール・CSS を変えたら:

```bash
python3 ~/Projects/exam-site-shell/tools/sync_from_template.py --target ~/Projects/<site>
cd ~/Projects/<site> && python3 tools/build_all.py
```

正本: `exam-site-shell`（`seo_body_markup.py`・`seo-editorial.css`・本 doc・監査スクリプト）。

---

## 12. チェックリスト（目視・1記事）

- [ ] 表が読みやすい（枠・見出し色）
- [ ] 数字に「要項で再確認」がある
- [ ] 他記事とリードが似ていない
- [ ] FAQ がこの slug だけの内容
- [ ] 関連リンク先が存在し、ラベルが自然
- [ ] 当該試験の分野数・機関名が正しい
- [ ] 演習・用語への導線が具体的（「演習10問」だけで終わらない）

---

## 13. 次の実装タスク（開発）

1. `validate_guide_expert_batch.py`（お手本ルールの機械化）
2. `data/guide_site_lexicon.json` + `validate_csv` 連携
3. `guide_rewrite_campaign.py` に `expert_pass` 集計
4. `rewrite_exempt` 廃止（手書き印でも禁止句 ERROR）
5. `docs/README.md` に本 doc へのリンク
