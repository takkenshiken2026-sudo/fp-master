#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""旧ルートURL（/q/ 等）から /fp3/ 配下へのリダイレクトHTMLを public_site に生成する。"""

from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.site_config import base_path, clean_origin  # noqa: E402

PUBLIC_SITE = ROOT / "public_site"
FP3_PREFIX = base_path() or "/fp3"


def redirect_html(target_path: str) -> str:
    """target_path: /fp3/q/.../index.html"""
    url = html.escape(target_path)
    canon = html.escape(f"{clean_origin()}{target_path}")
    label = html.escape("新しいURLへ移動")
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={url}">
<link rel="canonical" href="{canon}">
<script>location.replace("{url}");</script>
<title>移動中…</title>
</head>
<body>
<p><a href="{url}">{label}</a></p>
</body>
</html>
"""


def legacy_rel_paths() -> list[str]:
    out: list[str] = []
    static = ["about.html", "privacy.html", "related-sites.html", "privacy-terms.html"]
    for name in static:
        if (ROOT / name).is_file():
            out.append(name)
    for d in ("articles", "q", "terms"):
        root_d = ROOT / d
        if not root_d.is_dir():
            continue
        for path in sorted(root_d.rglob("*.html")):
            out.append(path.relative_to(ROOT).as_posix())
    return out


def main() -> int:
    if not PUBLIC_SITE.is_dir():
        print("build_legacy_redirects: public_site がありません。prepare_public_site.sh の後に実行してください。", file=sys.stderr)
        return 1
    count = 0
    for rel in legacy_rel_paths():
        dest_url = f"{FP3_PREFIX}/{rel}"
        out_path = PUBLIC_SITE / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(redirect_html(dest_url), encoding="utf-8")
        count += 1
    print(f"Wrote {count} legacy redirect pages under {PUBLIC_SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
