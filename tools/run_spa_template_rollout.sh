#!/usr/bin/env bash
# テンプレ SPA/SEO/favicon 修正を全10サイトへ反映
set -euo pipefail
SHELL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
SITES=(
  takken-master
  mentalhealth-master
  kikenbutsu-master
  eisei1shu-master
  chintaikanrishi-master
  eisei2shu-master
  kangyou-master
  mankan-master
  unkan-master
  boiler-master.jp
)

for site in "${SITES[@]}"; do
  target="$HOME/Projects/$site"
  if [[ ! -f "$target/site-config.json" ]]; then
    echo "skip $site (no site-config.json)" >&2
    continue
  fi
  echo "=== $site ==="
  "$PY" "$SHELL_ROOT/tools/sync_from_template.py" --target "$target"
  cp "$SHELL_ROOT/index.html" "$target/index.html"
  (
    cd "$target"
    "$PY" tools/generate_brand_assets.py --force
    "$PY" tools/apply_site_config.py
    "$PY" tools/build_all.py
  ) || {
    echo "  WARN: build failed for $site (continuing)" >&2
  }
  echo "  done $site"
done
echo "=== rollout complete ==="
