# 知識ハブ 品質パイプライン（全10サイト）

正本: `/Users/otedaiki/Projects/exam-site-shell`

## 読取専用の最終確認（CSV を再生成しない）

```bash
python3 /Users/otedaiki/Projects/scripts/_hub_final_verify.py
cat /Users/otedaiki/Projects/_hub_final_verify.txt
```

全10本番: compare/numbers/mistakes **150件/種**（衛1 compare のみ **153**）、`validate_csv` **ERROR 0**。

`_hub_sync_and_verify.py` は `write_*_hub_data.py` を実行するため、本番 CSV が安定している間は **使わない**（使う場合は直後に `repair_csv_for_validate.py` 必須）。

## 横断監査（2026-05-31・Phase B 完了後）

```bash
cd /Users/otedaiki/Projects/<site>
python3 tools/audit_hub_quality.py
cat reports/hub_audit/summary.json
```

| サイト | numbers pending | title 類似 | 薄い本文 | FAQ |
|--------|-----------------|------------|----------|-----|
| chintai | 0 | 155 | 118 | 0 |
| takken | 0 | 10 | 318 | 0 |
| eisei1shu | 0 | 13 | 310 | 0 |
| eisei2shu | 0 | 5 | 282 | 0 |
| kangyou | 0 | 73 | 127 | 0 |
| kikenbutsu | 0 | 112 | 115 | 0 |
| mentalhealth | 0 | 239 | 496 | 0 |
| mankan | 0 | 225 | 206 | 0 |
| unkan | 0 | 169 | 256 | 0 |
| boiler | 0 | 156 | 520 | 0 |

**numbers 公式照合**: `verify_official` **pending 0**（registry `/Users/otedaiki/Projects/docs/hub_numbers_verified.json`、テンプレ正本 `exam-site-shell/docs/` にもコピー済み）。

```bash
python3 /Users/otedaiki/Projects/scripts/_hub_numbers_bulk_verify_pending.py
python3 /Users/otedaiki/Projects/scripts/_numbers_apply_registry.py
```

## 一括ツール同期（注意）

```bash
python3 /Users/otedaiki/Projects/scripts/_hub_copy_run.py
cat /Users/otedaiki/Projects/scripts/_hub_copy_run_report.txt
```

`hub_merge_data.py` 等を上書きする。**CSV 再生成後は必ず** `repair_csv_for_validate.py` → `validate_csv.py`。

## 追加ツール（正本 exam-site-shell/tools/）

| ファイル | 役割 |
|---------|------|
| `tools/knowledge_hub_rules.py` | 目標件数 150/153 |
| `tools/hub_premium_faq_auto.py` | PREMIUM 未登録 slug の FAQ 自動生成 |
| `tools/audit_hub_quality.py` | numbers / FAQ / title 類似 / 薄い本文 |
| `tools/hub_merge_data.py` | premium → auto → expand |
| `tools/enrich_past_explanation_choices.py` | 正答本文から矛盾語句除去 |

## デプロイ手順（本番サイト）

```bash
cd /Users/otedaiki/Projects/<site>
python3 tools/build_compare_pages.py
python3 tools/build_numbers_mistakes_pages.py
bash tools/prepare_public_site.sh   # または CI の build_all.py
git add terms/compare terms/numbers terms/mistakes
git commit -m "Knowledge hub: 150件/種 HTML再ビルド"
git push origin main
```

## デプロイ状況（2026-05-31・Phase B 完了）

- **10本番**: CSV 150件/種、`validate ERROR 0`、**terms HTML push 済み**（kiken / eisei1 / takken / chintai / eisei2 / unkan / kangyou / mankan / mentalhealth / boiler）。
- **角度折りたたみ**: `MIN_ANGLE_COLLAPSE_BATCH=99`
- **テンプレ**: `hub_strip_batch_suffix`、`hub_diversify_content`、`repair_csv_for_validate`、`ROOT=parents[1]`（build/audit）
- **exam-site-shell**: GitHub push 済み（`hub_numbers_verified.json`、docs 150件目標、enrich 矛盾語句除去）

## Phase 3 以降（任意・段階的）

**進め方**: title 類似が少ないサイトから着手 → 監査 0 確認 → 次サイトへ。

| サイト | title 類似 | 状態 |
|--------|------------|------|
| **eisei2shu** | **0** | **2026-05-31 パイロット完了**（5件→0、content 正本修正） |
| **takken** | **0** | **2026-05-31 完了**（10件→0、CSV title 直接修正＋content 正本） |
| eisei1shu | 13 | 未着手 |
| 他7サイト | 5〜239 | 未着手 |

1. `reports/hub_audit/audit_title_similar.csv` … `write_*_hub_sXX_content.py` の title を差別化
2. `audit_thin_body.csv` … common_mistakes / memory_tip / article_lead を20字以上に
3. 長文ドキュメント統合（`knowledge-hub-article-templates.md` 正本一本化）

```bash
# 衛2パイロット手順（再現用）
cd ~/Projects/eisei2shu-master
# 1. write_*_hub_sXX_content.py で title / 薄いフィールド修正
python3 tools/write_eisei2shu_hub_data.py
python3 ~/Projects/exam-site-shell/tools/repair_csv_for_validate.py --root .
python3 tools/validate_csv.py
python3 tools/build_compare_pages.py && python3 tools/build_numbers_mistakes_pages.py
python3 tools/audit_hub_quality.py   # title_dup_similar: 0 を確認
```

## サイト順（横断作業時）

chintai → takken → eisei1shu → eisei2shu → kangyou → kikenbutsu → mentalhealth → mankan → unkan → boiler → exam-site-shell
