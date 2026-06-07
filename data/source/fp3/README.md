# FP3級 過去問ソースデータ

| ファイル | 内容 |
|----------|------|
| `fp3_gakka_past_questions_all.json` | 学科（正誤式90 + 三答択90） |
| `fp3_jitsugi_past_questions_all.json` | 実技（三答択60） |
| `diagram_manifest.json` | 実技の図表メタデータ（HTML再現予定） |

取り込み:

```bash
python3 tools/import_fp3_past_questions.py
python3 tools/build_all.py
```

## サイト上の番号

| 種別 | CSV | 年度内の問番 |
|------|-----|----------------|
| 学科・正誤式 | `ichimon_questions.csv` | id `{年}-05-01` 〜 `{年}-05-30` |
| 学科・三答択 | `past_questions.csv` | 問1〜30 |
| 実技・三答択 | `past_questions.csv` | 問31〜50 |

実技の図表は `data/question_diagrams/` に JSON 化し、過去問 CSV の `diagram_id` から HTML 生成。

```bash
python3 tools/build_fp3_question_diagrams.py
python3 tools/import_fp3_past_questions.py
python3 tools/build_all.py
```
