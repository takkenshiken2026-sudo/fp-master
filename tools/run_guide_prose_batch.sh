#!/usr/bin/env bash
# 全試験サイト: ガイド prose 修復 → ビルド → 監査
set -euo pipefail
SHELL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECTS="${HOME}/Projects"
SITES=(
  chintaikanrishi-master
  eisei1shu-master
  eisei2shu-master
  kangyou-master
  kikenbutsu-master
  mankan-master
  mentalhealth-master
  takken-master
  unkan-master
  boiler-master.jp
)

sync_tools() {
  local site="$1"
  for f in build_article_pages.py fix_editorial_auto.py related_links.py guide_section_resolve.py \
    guide_topic_normalize.py guide_content_shared.py guide_prose_patterns.py \
    fix_guide_prose_quality.py patch_guide_prose_templates.py \
    audit_guide_prose_quality.py validate_publish_gate.py fix_guide_duplicate_bodies.py; do
    cp "${SHELL_ROOT}/tools/${f}" "${site}/tools/${f}"
  done
}

for name in "${SITES[@]}"; do
  site="${PROJECTS}/${name}"
  [ -d "${site}/data" ] || { echo "skip missing ${name}"; continue; }
  echo "======== ${name} ========"
  sync_tools "${site}"
  python3 "${SHELL_ROOT}/tools/repair_csv_for_validate.py" --root "${site}" || true
  python3 "${SHELL_ROOT}/tools/fix_guide_duplicate_bodies.py" --root "${site}" --all-published --max-pass 2 || true
  python3 "${SHELL_ROOT}/tools/fix_editorial_auto.py" --root "${site}"
  python3 "${SHELL_ROOT}/tools/fix_guide_prose_quality.py" --root "${site}" || true
  (cd "${site}" && python3 tools/build_article_pages.py)
  python3 "${SHELL_ROOT}/tools/audit_guide_prose_quality.py" --root "${site}" || true
done

echo "batch complete"
