#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二衛マスター用ビルド（既存 q/ の URL を維持するため build_past_question_pages をスキップ）。

  cd /path/to/eisei2shu-master
  python3 /path/to/exam-site-shell/sites/eisei2shu-master/build_all.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TARGET = Path.cwd()


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=TARGET, check=True)


def main() -> int:
    py = sys.executable
    site_dir = Path(__file__).resolve().parent
    run([py, "tools/validate_csv.py"])
    run([py, "tools/apply_site_config.py"])
    run([py, "tools/csv_to_exam_site_past_js.py"])
    run([py, "tools/csv_to_exam_site_ichimondou_js.py"])
    print("+ (skip) tools/build_past_question_pages.py — 既存 q/ を維持")
    run([py, "tools/build_article_pages.py"])
    run([py, "tools/build_glossary_pages.py"])
    run([py, "tools/build_sitemap.py"])
    run([py, "tools/validate_generated_seo.py"])
    run([py, "tools/validate_internal_links.py"])
    run([py, "tools/validate_public_content.py"])
    run(["bash", "tools/prepare_public_site.sh"])
    run([py, str(site_dir / "write_flat_redirects.py"), "--target", str(TARGET)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
