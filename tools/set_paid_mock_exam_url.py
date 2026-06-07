#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""site-config.json の paidMockExam.url を設定し site-config.js を再生成する。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    ap = argparse.ArgumentParser(description="paidMockExam.url を設定")
    ap.add_argument("url", help="note 記事 URL（例: https://note.com/shikaku_master/n/xxxxxxxxxxxx）")
    ap.add_argument(
        "--config",
        type=Path,
        default=ROOT / "site-config.json",
        help="site-config.json（既定: リポジトリ root）",
    )
    args = ap.parse_args()
    url = args.url.strip()
    if not url.startswith("https://note.com/"):
        print("error: note.com の URL を指定してください", file=sys.stderr)
        return 1

    config_path = args.config.resolve()
    if not config_path.is_file():
        print(f"error: {config_path} がありません", file=sys.stderr)
        return 1

    data = json.loads(config_path.read_text(encoding="utf-8"))
    pm = data.get("paidMockExam")
    if not isinstance(pm, dict):
        print("error: site-config.json に paidMockExam ブロックがありません", file=sys.stderr)
        return 1

    pm["url"] = url
    config_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if config_path.parent == ROOT:
        from tools.site_config import write_site_config_js  # noqa: E402

        write_site_config_js()
        print(f"updated {config_path.name} and site-config.js")
    else:
        import subprocess

        subprocess.run(
            [sys.executable, str(config_path.parent / "tools" / "site_config.py")],
            cwd=config_path.parent,
            check=True,
        )
        print(f"updated {config_path}")

    print("確認: index.html → 問題を解く 05番・結果画面 CTA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
