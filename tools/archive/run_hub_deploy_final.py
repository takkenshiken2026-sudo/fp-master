#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全サイトへ hub タブ廃止を同期・ビルド・commit/push する。"""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[2]
COMMIT_MSG = "廃止: 比較・数値早見・よくある誤答タブを削除し旧URLをリダイレクト"

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

CLONE_URLS = {
    "boiler-master": "https://github.com/takkenshiken2026-sudo/boiler-master.git",
    "chintaikanrishi-master": "https://github.com/takkenshiken2026-sudo/chintaikanrishi-master.git",
    "eisei1shu-master": "https://github.com/takkenshiken2026-sudo/eisei1shu-master.git",
    "eisei2shu-master": "https://github.com/takkenshiken2026-sudo/eisei2shu-master.git",
    "mankan-master": "https://github.com/takkenshiken2026-sudo/mankan-master.git",
    "unkan-master": "https://github.com/takkenshiken2026-sudo/unkan-master.git",
    "kangyou-master": "https://github.com/takkenshiken2026-sudo/kangyou-master.git",
}

SITE_CONFIG_SRC = {
    "boiler-master": TEMPLATE / "sites/boiler-master/site-config.json",
    "chintaikanrishi-master": TEMPLATE / "sites/chintaikanrishi-master/site-config.json",
    "eisei1shu-master": TEMPLATE / "sites/eisei1shu-master/site-config.json",
    "eisei2shu-master": TEMPLATE / "sites/eisei2shu-master/site-config.json",
}

FORBIDDEN = ("比較・整理表", "数値・期限早見表", "よくある誤答")
LEAD_BAD = "比較・数値・誤答"


def run(cmd: list[str], *, cwd: Path | None = None, check: bool = False) -> tuple[int, str]:
    p = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    out = (p.stdout or "") + (p.stderr or "")
    if check and p.returncode != 0:
        raise RuntimeError(f"failed: {' '.join(cmd)}\n{out}")
    return p.returncode, out


def ensure_clone(name: str, path: Path) -> bool:
    if path.is_dir() and (path / ".git").is_dir():
        return True
    url = CLONE_URLS.get(name)
    if not url:
        return path.is_dir()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not (path / ".git").is_dir():
        shutil.rmtree(path)
    code, out = run(["git", "clone", url, str(path)])
    print(out)
    return code == 0 and path.is_dir()


def ensure_site_config(name: str, path: Path) -> None:
    dst = path / "site-config.json"
    if dst.is_file():
        return
    src = SITE_CONFIG_SRC.get(name)
    if src and src.is_file():
        shutil.copy2(src, dst)
        print(f"  copied site-config.json from {src}")


def sync_template(path: Path) -> tuple[bool, str]:
    if path.resolve() == TEMPLATE.resolve():
        return True, "skip (template)"
    script = TEMPLATE / "tools/sync_from_template.py"
    if not script.is_file():
        return False, "sync_from_template.py missing"
    code, out = run([sys.executable, str(script), "--target", str(path)])
    return code == 0, out[-2000:]


def apply_site_config(path: Path) -> tuple[bool, str]:
    script = path / "tools" / "apply_site_config.py"
    if not script.is_file():
        return False, "apply_site_config.py missing"
    code, out = run([sys.executable, str(script.relative_to(path))], cwd=path)
    return code == 0, out[-1500:]


def build_site(path: Path) -> tuple[bool, str]:
    lines: list[str] = []
    ok = True
    for script in ("build_glossary_pages.py", "build_sitemap.py"):
        sp = path / "tools" / script
        if not sp.is_file():
            lines.append(f"missing {script}")
            ok = False
            continue
        code, out = run([sys.executable, str(sp)], cwd=path)
        lines.append(out[-1500:])
        if code != 0:
            ok = False
    return ok, "\n".join(lines)


def verify_site(path: Path) -> tuple[bool, str]:
    issues: list[str] = []
    ti = path / "terms/index.html"
    if not ti.is_file():
        return False, "terms/index.html missing"
    text = ti.read_text(encoding="utf-8", errors="replace")
    for s in FORBIDDEN:
        if s in text:
            issues.append(f"forbidden:{s}")
    if LEAD_BAD in text:
        issues.append("lead_has_compare_numbers_mistakes")
    ci = path / "terms/compare/index.html"
    if not ci.is_file():
        issues.append("compare/index missing")
    elif "noindex" not in ci.read_text(encoding="utf-8", errors="replace").lower():
        issues.append("compare/index no noindex")
    n = sum(1 for _ in (path / "terms/compare").rglob("*.html")) if (path / "terms/compare").is_dir() else 0
    if n == 0:
        issues.append("no compare redirects")
    return not issues, "; ".join(issues) or f"ok redirects~{n}"


def git_commit_push(path: Path) -> tuple[str | None, bool, bool]:
    if not (path / ".git").is_dir():
        return None, False, False
    run(["git", "add", "-A"], cwd=path)
    code, diff = run(["git", "diff", "--cached", "--quiet"], cwd=path)
    if code == 0:
        _, h = run(["git", "rev-parse", "HEAD"], cwd=path)
        return h.strip().splitlines()[-1][:12] if h.strip() else None, False, False
    run(
        ["git", "commit", "-m", COMMIT_MSG],
        cwd=path,
    )
    _, h = run(["git", "rev-parse", "HEAD"], cwd=path)
    commit = h.strip().splitlines()[-1][:12]
    push_code, push_out = run(["git", "push", "origin", "HEAD"], cwd=path)
    push_ok = push_code == 0
    gh_ok = False
    sync_sh = path / "tools/sync_gh_pages_branch.sh"
    _, branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path)
    branch = branch.strip()
    if push_ok and branch in ("main", "master") and sync_sh.is_file():
        gcode, gout = run(["bash", str(sync_sh)], cwd=path)
        gh_ok = gcode == 0
        if not gh_ok:
            print(gout[-500:])
    return commit, push_ok, gh_ok


def main() -> int:
    report_path = TEMPLATE / "hub_deploy_final_report.txt"
    lines: list[str] = [
        f"=== Hub Deploy Final Report ===",
        f"Started: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "| site | exists | sync | build | verify | commit | push | gh-pages |",
        "|------|--------|------|-------|--------|--------|------|----------|",
    ]
    seen_paths: set[Path] = set()

    for name, path in SITES:
        path = path.resolve()
        if path in seen_paths:
            continue
        seen_paths.add(path)

        if name in CLONE_URLS:
            ensure_clone(name, path)
        if not path.is_dir():
            lines.append(f"| {name} | no | — | — | — | — | — | — |")
            continue

        ensure_site_config(name, path)
        sync_ok, _ = sync_template(path) if name != "exam-site-shell" else (True, "")
        apply_ok, _ = apply_site_config(path) if (path / "site-config.json").is_file() else (False, "")
        if (path / "site-config.json").is_file() or path.resolve() == TEMPLATE.resolve():
            build_ok, bout = build_site(path)
            if not build_ok:
                print(f"BUILD FAIL {name}:\n{bout[-800:]}")
        else:
            build_ok = False
        verify_ok, vmsg = verify_site(path) if build_ok else (False, "build failed")
        commit, push_ok, gh_ok = git_commit_push(path) if verify_ok or build_ok else (None, False, False)

        lines.append(
            f"| {name} | yes | {sync_ok} | {build_ok} | {verify_ok} ({vmsg}) | {commit or '—'} | {push_ok} | {gh_ok} |"
        )
        print(f"Done {name}: sync={sync_ok} build={build_ok} verify={verify_ok} push={push_ok}")

    lines.append("")
    lines.append(f"Finished: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
