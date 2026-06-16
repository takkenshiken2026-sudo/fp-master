# FP2級 過去問ソースデータ

| ファイル | 内容 |
|----------|------|
| `fp2_gakka_past_questions_all.json` | 学科（四答択60問×年度） |

取り込み:

```bash
python3 tools/import_fp2_past_questions.py
python3 tools/build_fp2_site.py
```

実技 JSON（記述・○×混在）は正解未収録のため、学科から順次公開します。
