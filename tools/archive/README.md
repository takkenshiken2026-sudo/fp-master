# archive/ — 一括作業・過去移行用スクリプト

**`build_all.py` からは呼ばれません。** 過去のハブ一括生成・全サイトデプロイ・移行作業用です。

実行するときはリポジトリ root から:

```bash
cd ~/Projects/exam-site-shell
python3 tools/archive/run_hub_deploy_final.py
```

`parents[1]` は `archive/` 配下用に `parents[2]`（リポジトリ root）へ補正済みです。

日常運用: [../README.md](../README.md) と [../../docs/ORGANIZATION.md](../../docs/ORGANIZATION.md)
