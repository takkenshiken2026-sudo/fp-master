# exam-site-shell を GitHub に push する手順

## 現在の状態（2026-05-29）

- リポジトリ: https://github.com/takkenshiken2026-sudo/exam-site-shell （private）
- `main` ブランチ push 済み（Phase 2 監査・レジストリ含む）
- **`.github/workflows/deploy-pages.yml` は未 push**（PAT に `workflow` スコープがないため）

## GitHub Pages を有効にする（workflow 追加）

1. GitHub → Settings → Developer settings → Personal access tokens  
   → **`workflow` スコープ付き**トークンを発行（または `gh auth login -s workflow`）
2. ローカルで workflow をコミット・push:

```bash
cd /Users/otedaiki/Projects/exam-site-shell
git add .github/workflows/deploy-pages.yml
git commit -m "Add GitHub Pages deploy workflow."
git push origin main
```

3. GitHub リポジトリ → **Settings → Pages → Build and deployment → Source: GitHub Actions**

## 一括デプロイ（推奨）

```bash
python3 /Users/otedaiki/Projects/_exam_shell_deploy.py
cat /Users/otedaiki/Projects/_exam_shell_deploy_result.txt
```

## 知識ハブの再生成

```bash
cd /Users/otedaiki/Projects/exam-site-shell
python3 tools/write_exam_site_shell_hub_data.py
python3 tools/validate_csv.py
python3 tools/audit_hub_quality.py
python3 tools/build_all.py
```

## Phase 2 numbers 照合（全8サイト横断）

正本レジストリ: `~/Projects/docs/hub_numbers_verified.json`（モノレポ側）

```bash
python3 ~/Projects/_numbers_apply_registry.py   # 各サイト audit CSV に反映
python3 ~/Projects/_numbers_verify_queue.py
```

## 全サイト Actions 確認

```bash
GH=/tmp/gh_install/gh_2.63.2_macOS_arm64/bin/gh   # または brew install gh
$GH auth login -s workflow
for site in chintaikanrishi-master takken-master eisei1shu-master eisei2shu-master kangyou-master kikenbutsu-master mentalhealth-master boiler-master.jp exam-site-shell; do
  echo "=== $site ==="
  $GH run list --repo "takkenshiken2026-sudo/${site%.jp}" --limit 1 2>/dev/null || \
  $GH run list --repo "takkenshiken2026-sudo/$site" --limit 1 2>/dev/null || echo skip
done
```
