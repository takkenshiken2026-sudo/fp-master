# ロードマップ実行手順

`exam-site-shell` を正本として、全本番サイトへ順に適用する。

## 実行

```bash
bash tools/run_roadmap_batch.sh
```

または Python オーケストレータ（サイト単位）:

```bash
python3 tools/run_roadmap_completion.py --all-phases --push
```

## フェーズ

| フェーズ | 内容 | ツール |
|---------|------|--------|
| B | ハブ本文 enrich・タイトル一意化 | `hub_pro_enrich.py`, `fix_hub_titles.py` |
| C | 編集 WARN 自動修正 | `fix_editorial_auto.py` |
| A | `build_all` → commit/push → gh-pages | `build_all.py`, `sync_gh_pages_branch.sh` |
| 検証 | ハブ監査・編集品質 | `audit_hub_quality.py`, `audit_editorial_quality.py` |

## 注意

- `validate_csv` / `audit_*` は **サイト cwd** または `EXAM_SITE_ROOT` で実行
- gh-pages 配信 repo（boiler / kikenbutsu / kangyou）は push 後 `sync_gh_pages_branch.sh` 必須
- `--strict` PASS まで残る WARN（FAQ 類似・用語ハブ活用法導線等）は記事単位の手当てが必要な場合あり
