#!/usr/bin/env bash
# GitHub Pages 用:
#   /           … 級選択ポータル
#   /fp3/       … FP3級サイト（SPA + 静的ページ）
#   /fp2/       … FP2級準備中
#   /q/ 等      … 旧URLから /fp3/ へのリダイレクト（build_legacy_redirects.py）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/public_site"
rm -rf "$OUT"
mkdir -p "$OUT/fp3" "$OUT/fp2"
cd "$ROOT"

if [[ ! -f grade-portal.html ]]; then
  echo "prepare_public_site.sh: grade-portal.html がありません。" >&2
  exit 1
fi

# --- ドメインルート（級選択 + ポータル用共有CSS）---
cp grade-portal.html "$OUT/index.html"
for f in CNAME robots.txt .nojekyll favicon.ico; do
  if [[ -e "$f" ]]; then
    cp "$f" "$OUT/"
  fi
done
for f in site-pages.css site-theme.css; do
  if [[ -f "$f" ]]; then
    cp "$f" "$OUT/"
  fi
done

# --- FP3 本番サイト ---
FP3_FILES=(
  index.html
  about.html
  privacy.html
  related-sites.html
  site-config.json
  site-config.js
  site-pages.css
  site-theme.css
  seo-editorial.css
  site-q-index.js
  site-terms-index.js
  site-compare-index.js
  site-knowledge-hub-index.js
  site-priority-index.js
  site-analytics.js
  exam-site-data-past.js
  exam-site-data-practice.js
  exam-site-data-ichimondou.js
)
for f in "${FP3_FILES[@]}"; do
  if [[ ! -e "$f" ]]; then
    echo "prepare_public_site.sh: 必須ファイルがありません: $f" >&2
    echo "先に python3 tools/build_all.py を実行してください。" >&2
    exit 1
  fi
  cp "$f" "$OUT/fp3/"
done
if [[ -f privacy-terms.html ]]; then
  cp privacy-terms.html "$OUT/fp3/"
fi
for d in articles q terms; do
  if [[ -d "$ROOT/$d" ]]; then
    cp -R "$ROOT/$d" "$OUT/fp3/"
  fi
done
if [[ -d "$ROOT/assets/brand" ]]; then
  mkdir -p "$OUT/fp3/assets"
  cp -R "$ROOT/assets/brand" "$OUT/fp3/assets/"
fi
if [[ -f "$ROOT/favicon.ico" ]]; then
  cp "$ROOT/favicon.ico" "$OUT/fp3/favicon.ico"
fi
for f in site-spa.css site-spa-fields.js site-app.css; do
  if [[ -f "$ROOT/$f" ]]; then
    cp "$ROOT/$f" "$OUT/fp3/"
  fi
done
if [[ -f "$ROOT/docs/glossary-article-slugs.json" ]]; then
  mkdir -p "$OUT/fp3/docs"
  cp "$ROOT/docs/glossary-article-slugs.json" "$OUT/fp3/docs/"
fi

# --- FP2 準備中 ---
if [[ -d "$ROOT/fp2" ]]; then
  cp -R "$ROOT/fp2/." "$OUT/fp2/"
fi

# --- サイトマップ（ポータル + FP3 + FP2）---
if [[ -f sitemap.xml ]]; then
  cp sitemap.xml "$OUT/sitemap.xml"
fi

# --- 旧ルートURL → /fp3/ リダイレクト ---
python3 tools/build_legacy_redirects.py

if grep -q 'site-spa.css' "$OUT/fp3/index.html" 2>/dev/null && [[ ! -f "$OUT/fp3/site-spa.css" ]]; then
  echo "prepare_public_site.sh: fp3/index.html が site-spa.css を参照していますが fp3 にありません。" >&2
  exit 1
fi
n="$(find "$OUT"/. -type f 2>/dev/null | wc -l | tr -d ' ')"
echo "prepare_public_site.sh: $OUT に $n ファイルを配置しました（/ + /fp3/ + /fp2/ + リダイレクト）。"
