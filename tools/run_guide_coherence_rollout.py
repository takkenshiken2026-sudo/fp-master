#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""テンプレ同期 → CSV sanitize → ガイド再ビルド → A級 HTML 整合性チェック（複数サイト）。"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1]
PROJECTS = Path.home() / "Projects"

DEFAULT_SITES = (
    "eisei1shu-master",
    "eisei2shu-master",
    "boiler-master.jp",
    "unkan-master",
    "kikenbutsu-master",
    "mentalhealth-master",
    "mankan-master",
    "kangyou-master",
    "chintaikanrishi-master",
    "takken-master",
)


def run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    print(f"  $ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="ガイド整合性ロールアウト（テンプレ→本番）")
    parser.add_argument("--site", action="append", help="対象サイト dir 名（省略時は既定一覧）")
    parser.add_argument("--skip-sync", action="store_true")
    parser.add_argument("--skip-sanitize", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--eisei2shu-content-fix", action="store_true", help="eisei2shu のみ専用テンプレ修復")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sites = args.site or list(DEFAULT_SITES)
    failures: list[str] = []

    for name in sites:
        target = PROJECTS / name
        if not target.is_dir():
            print(f"skip (missing): {name}", file=sys.stderr)
            continue
        print(f"\n=== {name} ===")

        if not args.skip_sync:
            sync_cmd = [
                sys.executable,
                str(TEMPLATE / "tools" / "sync_from_template.py"),
                "--target",
                str(target),
            ]
            if args.dry_run:
                sync_cmd.append("--dry-run")
            proc = run(sync_cmd, cwd=TEMPLATE)
            if proc.returncode != 0:
                print(proc.stderr or proc.stdout, file=sys.stderr)
                failures.append(f"{name}: sync")
                continue
            if not args.dry_run:
                print(proc.stdout.strip())

        if args.dry_run:
            continue

        if not args.skip_sanitize:
            proc = run([sys.executable, "tools/fix_guide_sanitize_tier_a.py"], cwd=target)
            print(proc.stdout.strip() or proc.stderr.strip())

        if args.eisei2shu_content_fix and name == "eisei2shu-master":
            env = {**os.environ, "PYTHONPATH": f"{TEMPLATE}:{target}"}
            proc = subprocess.run(
                [sys.executable, "tools/fix_tier_a_guide_articles.py"],
                cwd=target,
                text=True,
                capture_output=True,
                env=env,
            )
            print(proc.stdout.strip() or proc.stderr.strip())
            if proc.returncode != 0:
                failures.append(f"{name}: tier_a_fix")

        if not args.skip_build:
            proc = run([sys.executable, "tools/build_article_pages.py"], cwd=target)
            if proc.returncode != 0:
                print(proc.stderr, file=sys.stderr)
                failures.append(f"{name}: build")
                continue
            print(proc.stdout.strip())

            proc = run([sys.executable, "tools/validate_guide_html_coherence.py"], cwd=target)
            out = (proc.stdout or "") + (proc.stderr or "")
            print(out.strip())
            if proc.returncode != 0:
                failures.append(f"{name}: validate")

    if failures:
        print("\nFailed:", ", ".join(failures), file=sys.stderr)
        return 1
    print("\nAll sites OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
