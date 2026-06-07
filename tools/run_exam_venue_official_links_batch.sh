#!/usr/bin/env bash
# 全会場記事へ公式リンクを展開: テンプレ同期 → lib パッチ → CSV 修復 → 記事 HTML 生成
set -euo pipefail

SHELL="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
SITES=(
  chintaikanrishi-master
  eisei1shu-master
  eisei2shu-master
  kangyou-master
  kikenbutsu-master
  mankan-master
  mentalhealth-master
  unkan-master
)

cd "$SHELL"
"$PY" tools/patch_guide_venue_official_links.py

for site in "${SITES[@]}"; do
  target="$HOME/Projects/$site"
  if [[ ! -d "$target/data" ]]; then
    echo "skip $site (no data/)"
    continue
  fi
  echo "=== $site ==="
  "$PY" tools/sync_from_template.py --target "$target" || true
  "$PY" tools/fix_exam_venue_guide_articles.py --target "$target" || echo "  (no *-center rows)"
  "$PY" tools/fix_exam_venue_hub_articles.py --target "$target" || echo "  (no hub rows)"
  (cd "$target" && "$PY" tools/build_article_pages.py)
  (cd "$target" && bash tools/prepare_public_site.sh 2>/dev/null || true)
done

echo "done."
