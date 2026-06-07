#!/usr/bin/env bash
# 9サイト（宅建除く）へガイドリライトツール同期＋CSV差し替え＋build_all
set -uo pipefail

TEMPLATE="${TEMPLATE:-$HOME/Projects/exam-site-shell}"
SITES=(
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

PY="${PYTHON:-python3}"

for site in "${SITES[@]}"; do
  target="$HOME/Projects/$site"
  echo "========== $site =========="
  if [[ ! -d "$target" ]]; then
    echo "skip: missing $target" >&2
    continue
  fi
  "$PY" "$TEMPLATE/tools/sync_from_template.py" --target "$target" 2>&1 | tail -3
  (cd "$target" && "$PY" tools/apply_site_config.py) 2>&1 | tail -2
  (cd "$target" && "$PY" tools/rewrite_guide_boilerplate.py --force)
  (cd "$target" && "$PY" tools/validate_guide_rewrite.py --strict)
  if (cd "$target" && "$PY" tools/build_all.py) 2>&1 | tail -5; then
    echo "build OK: $site"
  else
    echo "build FAILED: $site (continuing)" >&2
  fi
done

echo "done all sites"
