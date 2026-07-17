#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""site-config.json の adsenseClientId からルート ads.txt を生成する。"""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.site_config import ROOT, adsense_client_id, clean_origin


GOOGLE_CERT_AUTHORITY_ID = "f08c47fec0942fa0"


def publisher_id(client_id: str) -> str:
    raw = client_id.strip()
    if raw.startswith("ca-pub-"):
        return "pub-" + raw[len("ca-pub-") :]
    if raw.startswith("pub-"):
        return raw
    return f"pub-{raw}"


def owner_domain() -> str:
    host = urlparse(clean_origin()).hostname or ""
    return host.strip().lower().lstrip(".")


def ads_txt_contents(client_id: str) -> str:
    """AdSense 公式スニペット形式 + OWNERDOMAIN（ルートドメイン明示）。"""
    pub = publisher_id(client_id)
    lines = [f"google.com, {pub}, DIRECT, {GOOGLE_CERT_AUTHORITY_ID}"]
    domain = owner_domain()
    if domain:
        lines.append(f"OWNERDOMAIN={domain}")
    return "\n".join(lines) + "\n"


def main() -> int:
    path = ROOT / "ads.txt"
    client = adsense_client_id()
    if not client:
        if path.is_file():
            path.unlink()
            print(f"Removed {path} (adsenseClientId 未設定)")
        else:
            print("ads.txt: skip (adsenseClientId 未設定)")
        return 0

    body = ads_txt_contents(client)
    path.write_text(body, encoding="utf-8", newline="\n")
    print(f"Wrote {path}")
    print(body, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
