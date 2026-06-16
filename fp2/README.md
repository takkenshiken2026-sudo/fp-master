# FP2級セクション（/fp2/）

FP2級向け学習サイト。デスクトップの学科過去問 JSON から CSV を生成し、`python3 tools/build_fp2_site.py` で SPA・静的過去問ページを出力します。

## データ

| パス | 内容 |
|------|------|
| `data/past_questions.csv` | 学科・四答択（ビルドで生成） |
| `data/source/fp2/` | 取り込み元 JSON（リポジトリ正本: `data/source/fp2/`） |
| `site-config.json` | FP2級設定（`basePath` `/fp2`、6分野・四答択） |

## 取り込み

```bash
python3 tools/import_fp2_past_questions.py
python3 tools/build_fp2_site.py
```

デスクトップの JSON パスを変える場合:

```bash
python3 tools/import_fp2_past_questions.py \
  --gakka ~/Desktop/FP2級学科過去問データ/merged/fp2_gakka_past_questions_all.json
```

## 公開範囲（2026-06）

- **学科過去問** … 2025・2026年公表分（各60問・計120問）
- **実技過去問** … JSON はデスクトップにありますが、正解未収録のため未公開（順次追加予定）
- **用語・試験ガイド** … 未整備（空の index のみ）

ルートの FP3級サイトは `/`、FP2級は `/fp2/` です。
