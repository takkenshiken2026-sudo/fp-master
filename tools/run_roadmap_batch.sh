#!/usr/bin/env bash
# ロードマップ B→C→A: 全サイト品質修正・再ビルド・commit/push
set -uo pipefail

SHELL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECTS="$HOME/Projects"
PY="${PYTHON:-python3}"
COMMIT_MSG="build: ロードマップ（ハブ品質・編集WARN削減・全サイト再ビルド）"

SITES=(
  eisei1shu-master
  eisei2shu-master
  boiler-master.jp
  unkan-master
  kikenbutsu-master
  mentalhealth-master
  mankan-master
  kangyou-master
  chintaikanrishi-master
  takken-master
)

TOOLS=(
  fix_editorial_auto.py
  fix_hub_titles.py
  hub_pro_enrich.py
  audit_hub_quality.py
  validate_publish_gate.py
)

for site in "${SITES[@]}"; do
  ROOT="$PROJECTS/$site"
  [[ -d "$ROOT" ]] || continue
  echo ""
  echo "========== $site =========="
  for t in "${TOOLS[@]}"; do
    cp "$SHELL_ROOT/tools/$t" "$ROOT/tools/$t"
  done
  export EXAM_SITE_ROOT="$ROOT"
  export PYTHONPATH="$SHELL_ROOT:$ROOT"
  "$PY" "$SHELL_ROOT/tools/repair_csv_for_validate.py" --root "$ROOT" || true
  for repair in fix_tier_a_guide_articles.py fix_guide_duplicate_bodies.py; do
    [[ -f "$SHELL_ROOT/tools/$repair" ]] && "$PY" "$SHELL_ROOT/tools/$repair" --root "$ROOT" || true
  done
  "$PY" "$SHELL_ROOT/tools/hub_pro_enrich.py" --root "$ROOT"
  "$PY" "$SHELL_ROOT/tools/fix_hub_titles.py" --root "$ROOT"
  "$PY" "$SHELL_ROOT/tools/fix_editorial_auto.py" --root "$ROOT"
  "$PY" "$SHELL_ROOT/tools/repair_csv_for_validate.py" --root "$ROOT" || true
  (cd "$ROOT" && "$PY" tools/build_all.py) || { echo "build failed: $site"; continue; }
  (cd "$ROOT" && "$PY" "$SHELL_ROOT/tools/audit_hub_quality.py")
  (cd "$ROOT" && "$PY" tools/audit_editorial_quality.py 2>/dev/null | tail -1 || true)
  if git -C "$ROOT" status --porcelain | grep -q .; then
    git -C "$ROOT" add -A
    git -C "$ROOT" commit -m "$COMMIT_MSG" || true
    git -C "$ROOT" push origin HEAD || echo "push failed: $site"
    if [[ -f "$ROOT/tools/sync_gh_pages_branch.sh" ]]; then
      bash "$ROOT/tools/sync_gh_pages_branch.sh" || echo "gh-pages failed: $site"
    fi
  fi
done

echo ""
echo "========== batch done =========="
