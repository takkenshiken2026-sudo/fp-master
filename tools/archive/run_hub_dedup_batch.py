#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全サイトで知識ハブ重複監査・修正・ビルドを実行する。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ROOT.parent

SITES = [
    "exam-site-shell",
    "takken-master",
    "boiler-master.jp",
    "mentalhealth-master",
    "chintaikanrishi-master",
    "eisei1shu-master",
    "eisei2shu-master",
    "kangyou-master",
    "kikenbutsu-master",
    "unkan-master",
    "mankan-master",
]

SYNC_TOOLS = (
    "hub_dedup.py",
    "hub_collapse_angles.py",
    "hub_collapse_series.py",
    "audit_hub_duplicates.py",
    "fix_hub_duplicates.py",
    "build_compare_pages.py",
)


def sync_tools(site_dir: Path) -> None:
    tools = site_dir / "tools"
    tools.mkdir(exist_ok=True)
    for name in SYNC_TOOLS:
        src = ROOT / "tools" / name
        if src.is_file():
            (tools / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def run(cmd: list[str], cwd: Path) -> int:
    print(f"\n>>> {' '.join(cmd)}  (cwd={cwd.name})")
    return subprocess.call(cmd, cwd=cwd)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "audit"
    audit_csv = ROOT / "docs" / "hub-duplicate-audit.csv"

    if mode == "audit":
        rows: list[str] = []
        for site in SITES:
            site_dir = PROJECTS / site
            if not (site_dir / "data").is_dir():
                continue
            sync_tools(site_dir)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "audit_hub_duplicates.py"),
                    "--target",
                    str(site_dir),
                    "--out",
                    str(ROOT / "docs" / f"hub-duplicate-audit-{site}.csv"),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            print(proc.stdout, end="")
            if proc.returncode != 0:
                print(proc.stderr, file=sys.stderr)
                return proc.returncode
            site_out = ROOT / "docs" / f"hub-duplicate-audit-{site}.csv"
            if site_out.is_file():
                lines = site_out.read_text(encoding="utf-8").splitlines()
                if len(lines) > 1:
                    header = lines[0]
                    if not rows:
                        rows.append(f"site\t{header}")
                    for line in lines[1:]:
                        rows.append(f"{site}\t{line}")
        if rows:
            audit_csv.write_text("\n".join(rows) + "\n", encoding="utf-8")
        print(f"Wrote combined audit -> {audit_csv}")
        return 0

    if mode == "fix-all":
        for site in SITES:
            site_dir = PROJECTS / site
            if not (site_dir / "data").is_dir():
                continue
            sync_tools(site_dir)
            code = run(
                [sys.executable, "tools/fix_hub_duplicates.py", "--apply", "--rebuild"],
                site_dir,
            )
            if code != 0:
                return code
        return 0

    if mode == "validate-build":
        for site in SITES:
            site_dir = PROJECTS / site
            if not (site_dir / "tools" / "build_all.py").is_file():
                continue
            code = run([sys.executable, "tools/build_all.py"], site_dir)
            if code != 0:
                return code
        return 0

    print(f"Unknown mode: {mode!r} (audit | fix-all | validate-build)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
