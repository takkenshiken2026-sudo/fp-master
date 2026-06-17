# FP2級 過去問ソースデータ

| ファイル | 内容 |
|----------|------|
| `fp2_gakka_past_questions_all.json` | 学科（四答択60問×年度） |
| `fp2_jitsugi_past_questions_all.json` | 実技（40問×年度・四択・○×・記述） |

取り込み:

```bash
python3 tools/import_fp2_past_questions.py
python3 tools/build_fp2_site.py
```

過去問 CSV の番号: 問1〜60 学科 / 問61〜100 実技。

正解未収録の実技問は `tags` に「正解未収録」を付与し、静的ページで問題文のみ公開します。
