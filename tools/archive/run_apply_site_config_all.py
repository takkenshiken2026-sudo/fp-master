#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全サイトで apply_site_config.py を実行し、静的ページのプレースホルダを除去する。"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[2]

PROJECTS = Path("/Users/otedaiki/Projects")

SITES: list[tuple[str, Path]] = [
    ("exam-site-shell", TEMPLATE),
    ("takken-master", PROJECTS / "takken-master"),
    ("chintaikanrishi-master", PROJECTS / "chintaikanrishi-master"),
    ("eisei1shu-master", PROJECTS / "eisei1shu-master"),
    ("eisei2shu-master", PROJECTS / "eisei2shu-master"),
    ("kangyou-master", PROJECTS / "kangyou-master"),
    ("kikenbutsu-master", PROJECTS / "kikenbutsu-master"),
    ("mankan-master", PROJECTS / "mankan-master"),
    ("unkan-master", PROJECTS / "unkan-master"),
    ("mentalhealth-master", PROJECTS / "mentalhealth-master"),
    ("boiler-master", PROJECTS / "boiler-master.jp"),
]

BAD = ("Sampleマスター", "YOUR-DOMAIN", "example.com/contact")
CHECK_FILES = ("about.html", "privacy.html", "related-sites.html", "articles/index.html")
COMMIT_MSG = "fix: 静的ページのフッター・ヘッダーを site-config から再生成"


def run(cmd: list[str], *, cwd: Path | None = None) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def verify_site(path: Path) -> tuple[bool, list[str]]:
    issues: list[str] = []
    for rel in CHECK_FILES:
        fp = path / rel
        if not fp.is_file():
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        hits = [b for b in BAD if b in text]
        if hits:
            issues.append(f"{rel}: {hits}")
    return not issues, issues


def git_commit_push(path: Path) -> tuple[str | None, bool, bool]:
    if not (path / ".git").is_dir():
        return None, False, False
    run(["git", "add", "-A"], cwd=path)
    code, _ = run(["git", "diff", "--cached", "--quiet"], cwd=path)
    if code == 0:
        _, h = run(["git", "rev-parse", "HEAD"], cwd=path)
        return h.strip().splitlines()[-1][:12] if h.strip() else None, False, False
    run(["git", "commit", "-m", COMMIT_MSG], cwd=path)
    _, h = run(["git", "rev-parse", "HEAD"], cwd=path)
    commit = h.strip().splitlines()[-1][:12]
    push_code, _ = run(["git", "push", "origin", "HEAD"], cwd=path)
    push_ok = push_code == 0
    gh_ok = False
    sync_sh = path / "tools/sync_gh_pages_branch.sh"
    _, branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path)
    branch = branch.strip()
    if push_ok and branch in ("main", "master") and sync_sh.is_file():
        gcode, _ = run(["bash", str(sync_sh)], cwd=path)
        gh_ok = gcode == 0
    return commit, push_ok, gh_ok


def main() -> int:
    report = TEMPLATE / "apply_site_config_report.txt"
    lines = [
        f"=== Apply Site Config Report ===",
        f"Started: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "| site | apply | verify | commit | push | gh-pages |",
        "|------|-------|--------|--------|------|----------|",
    ]
    seen: set[Path] = set()
    failed = False

    for name, path in SITES:
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)
        if not path.is_dir():
            lines.append(f"| {name} | missing | — | — | — | — |")
            failed = True
            continue
        script = path / "tools" / "apply_site_config.py"
        if not script.is_file():
            lines.append(f"| {name} | no script | — | — | — | — |")
            failed = True
            continue
        code, out = run([sys.executable, str(script.relative_to(path))], cwd=path)
        apply_ok = code == 0
        verify_ok, issues = verify_site(path)
        commit, push_ok, gh_ok = git_commit_push(path) if apply_ok and verify_ok else (None, False, False)
        if not verify_ok:
            failed = True
        vmsg = "ok" if verify_ok else "; ".join(issues)
        lines.append(
            f"| {name} | {apply_ok} ({out.strip()[-120:]}) | {verify_ok} ({vmsg}) | {commit or '—'} | {push_ok} | {gh_ok} |"
        )
        print(f"Done {name}: apply={apply_ok} verify={verify_ok} push={push_ok}")

    lines.append("")
    lines.append(f"Finished: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report.read_text(encoding="utf-8"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
