#!/usr/bin/env bash
# 全サイトに run_roadmap_site.py を順次適用
set -uo pipefail

SHELL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
PUSH="${PUSH:-0}"

SITES=(
  unkan-master
  mankan-master
  kangyou-master
  kikenbutsu-master
  boiler-master.jp
  eisei2shu-master
  eisei1shu-master
  mentalhealth-master
  chintaikanrishi-master
  takken-master
)

for site in "${SITES[@]}"; do
  echo ""
  echo "========== $site =========="
  args=(--site "$site")
  [[ "$PUSH" == "1" ]] && args+=(--push)
  if ! "$PY" "$SHELL_ROOT/tools/run_roadmap_site.py" "${args[@]}"; then
    echo "FAILED: $site" >&2
  fi
done
echo ""
echo "========== all sites done =========="
