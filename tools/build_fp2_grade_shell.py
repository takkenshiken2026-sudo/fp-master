#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FP2級セクション（/fp2/）の準備中ページを生成する。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP2 = ROOT / "fp2"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_fp2_config() -> dict:
    path = FP2 / "site-config.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _write_theme_css(cfg: dict) -> None:
    t = cfg.get("theme") or {}
    accent = t.get("accent", "#1a4a7a")
    css = f""":root {{
  --sel: {accent};
  --accent: {accent};
  --accent-text: {t.get("accentText", "#ffffff")};
  --accent-soft: color-mix(in srgb, {accent} 11%, #ffffff);
  --accent-border: color-mix(in srgb, {accent} 26%, #ffffff);
  --accent-emphasis: color-mix(in srgb, {accent} 42%, #333333);
  --bg: {t.get("surface", "#ffffff")};
  --bg2: {t.get("surfaceAlt", "#f4f4f5")};
  --page-bg: {t.get("background", "#f0f0f1")};
  --text: {t.get("text", "#111111")};
  --text2: {t.get("textMuted", "#555555")};
  --border: {t.get("border", "rgba(0,0,0,.09)")};
  --r2: {t.get("radius", "10px")};
}}
body {{ background: var(--page-bg); }}
"""
    (FP2 / "site-theme.css").write_text(css, encoding="utf-8")


def _index_html(cfg: dict) -> str:
    exam = cfg.get("examName", "FP2級")
    brand = cfg.get("brandName", "FP2級マスター")
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{brand}｜{exam}（準備中）</title>
<meta name="description" content="{exam}向けの学習コンテンツを準備中です。FP3級の学習は /fp3/ からご利用ください。">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://fp-master.jp/fp2/">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="stylesheet" href="/site-pages.css">
<link rel="stylesheet" href="site-theme.css">
<style>
.fp2-shell-main {{
  width: min(720px, calc(100% - 32px));
  margin: 48px auto 80px;
  padding: 28px 24px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r2);
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}}
.fp2-shell-main h1 {{ margin: 0 0 12px; font-size: 1.5rem; }}
.fp2-shell-main p {{ margin: 0 0 14px; line-height: 1.7; color: var(--text2); }}
.fp2-shell-links {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }}
.fp2-shell-links a {{
  display: inline-block;
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid var(--accent-border);
  background: var(--accent-soft);
  color: var(--accent-emphasis);
  text-decoration: none;
  font-weight: 600;
  font-size: .95rem;
}}
</style>
</head>
<body class="site-shell-column-page">
<main class="fp2-shell-main">
  <h1>{exam}</h1>
  <p>FP2級向けの過去問・実践演習・一問一答・用語解説は現在作成中です。このページはコンテンツ追加に備えた準備用の公開枠です。</p>
  <p>学科・実技それぞれの問題データと試験画面は、順次 <code>/fp2/</code> 配下に追加していきます。</p>
  <div class="fp2-shell-links">
    <a href="/">級を選び直す</a>
    <a href="/">FP3級マスターで学習する</a>
  </div>
</main>
</body>
</html>
"""


def main() -> int:
    FP2.mkdir(parents=True, exist_ok=True)
    cfg = _load_fp2_config()
    _write_theme_css(cfg)
    (FP2 / "index.html").write_text(_index_html(cfg), encoding="utf-8")
    readme = FP2 / "README.md"
    if not readme.is_file():
        readme.write_text(
            "# FP2級セクション（/fp2/）\n\n"
            "FP2級向け CSV・静的ページ・SPA は今後ここに追加します。\n"
            "- `data/` … 過去問・実践・一問一答 CSV（未作成）\n"
            "- `site-config.json` … FP2級設定（四答択・basePath `/fp2`）\n",
            encoding="utf-8",
        )
    (FP2 / "data").mkdir(exist_ok=True)
    print(f"Wrote FP2 grade shell under {FP2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
