#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パンくず（表示 HTML と BreadcrumbList JSON-LD）の共通組み立て。

多級サイト（/ + /fp3/）では次の階層を推奨:
  FPマスター（級選択） > FP3級マスター（級トップ） > セクション > 現ページ

単一サイト（basePath なし）では:
  ブランド名（トップ） > セクション > 現ページ
"""

from __future__ import annotations

import html

from tools.site_config import (
    CONFIG,
    base_path,
    brand_name,
    clean_origin,
    grade_portal_href,
    public_url,
    site_href,
)


def portal_brand_name() -> str:
    return str(CONFIG.get("portalBrandName") or "").strip() or "FPマスター"


def normalized_portal_href() -> str:
    """級選択ポータルへのパス（ルートは `/` のみ）。"""
    raw = (grade_portal_href() or "/").strip()
    if not raw.startswith("/"):
        raw = f"/{raw}"
    if raw == "/":
        return "/"
    return raw.rstrip("/") + "/"


def uses_portal_tier() -> bool:
    """級選択ポータル（/）と級サイト（/fp3/ 等）が分かれているか。"""
    bp = base_path().rstrip("/")
    if not bp:
        return False
    portal = normalized_portal_href().rstrip("/") or "/"
    return portal != bp


def static_crumb_items(
    *tail: tuple[str, str | None],
) -> list[tuple[str, str | None]]:
    """静的ページ用パンくず（表示・JSON-LD 共通）。"""
    items: list[tuple[str, str | None]] = []
    if uses_portal_tier():
        items.append((portal_brand_name(), normalized_portal_href()))
    items.append((brand_name(), "index.html"))
    items.extend(tail)
    return items


def crumb_href_to_absolute(href: str) -> str:
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/"):
        origin = clean_origin().rstrip("/")
        return origin + href
    return public_url(href)


def crumb_json_ld(
    items: list[tuple[str, str | None]],
    *,
    last_item_url: str | None = None,
) -> list[dict]:
    """BreadcrumbList の itemListElement を生成（表示パンくずと同じラベル順）。"""
    out: list[dict] = []
    for pos, (name, href) in enumerate(items, start=1):
        if href is None and pos == len(items) and last_item_url:
            href = last_item_url
        el: dict = {"@type": "ListItem", "position": pos, "name": name}
        if href:
            el["item"] = crumb_href_to_absolute(href)
        out.append(el)
    return out


def index_home_breadcrumb_json_ld() -> dict:
    """SPA トップ（/fp3/）用 BreadcrumbList。"""
    items = static_crumb_items()
    elements = crumb_json_ld(items, last_item_url=public_url("index.html"))
    return {"@type": "BreadcrumbList", "itemListElement": elements}


def spa_breadcrumb_prefix_li() -> str:
    """index.html SPA 内パンくずの先頭 <li> 群。"""
    lines: list[str] = []
    if uses_portal_tier():
        portal_href = normalized_portal_href()
        pn = html.escape(portal_brand_name())
        lines.append(
            f'<li class="breadcrumb-item"><a href="{html.escape(portal_href)}" title="{pn}">{pn}</a></li>'
        )
    bn = html.escape(brand_name())
    home = html.escape(site_href("index.html"))
    lines.append(
        f'<li class="breadcrumb-item"><a href="{home}" '
        f'onclick="event.preventDefault();gotoPage(\'quiz-start\')" title="{bn}">{bn}</a></li>'
    )
    return "\n          ".join(lines)
