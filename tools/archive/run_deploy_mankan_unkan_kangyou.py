#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mankan / unkan / kangyou のテンプレ同期・フッター修正・ハブ廃止・push。"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[2]

SITES: list[tuple[str, Path, Path]] = [
    (
        "mankan-master",
        Path("/Users/otedaiki/Projects/mankan-master"),
        TEMPLATE / "sites/mankan-master/site-only.paths",
    ),
    (
        "unkan-master",
        Path("/Users/otedaiki/Projects/unkan-master"),
        TEMPLATE / "sites/unkan-master/site-only.paths",
    ),
    (
        "kangyou-master",
        Path("/Users/otedaiki/Projects/kangyou-master"),
        TEMPLATE / "sites/kangyou-master/site-only.paths",
    ),
]

CLONE_URLS = {
    "mankan-master": "https://github.com/takkenshiken2026-sudo/mankan-master.git",
    "unkan-master": "https://github.com/takkenshiken2026-sudo/unkan-master.git",
    "kangyou-master": "https://github.com/takkenshiken2026-sudo/kangyou-master.git",
}

HUB_TOOL_FILES = (
    "knowledge_hub_tabs.py",
    "build_hub_retire_redirects.py",
    "internal_links.py",
    "knowledge_hub_seo.py",
    "build_sitemap.py",
)

FORBIDDEN = ("比較・整理表", "数値・期限早見表", "よくある誤答")
BAD_FOOTER = ("Sampleマスター", "YOUR-DOMAIN", "example.com/contact")
FOOTER_COMMIT = "fix: 静的ページのフッター・ヘッダーを site-config から再生成"
HUB_COMMIT = "廃止: 比較・数値早見・よくある誤答タブを削除し旧URLをリダイレクト"


def run(cmd: list[str], *, cwd: Path | None = None, check: bool = False) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    if check and p.returncode != 0:
        raise RuntimeError(f"failed: {' '.join(cmd)}\n{out}")
    return p.returncode, out


def ensure_clone(name: str, path: Path) -> bool:
    if path.is_dir() and (path / ".git").is_dir():
        return True
    url = CLONE_URLS.get(name)
    if not url:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    code, out = run(["git", "clone", url, str(path)])
    print(out)
    return code == 0


def sync_template(path: Path, site_only: Path) -> tuple[bool, str]:
    code, out = run(
        [
            sys.executable,
            str(TEMPLATE / "tools/sync_from_template.py"),
            "--target",
            str(path),
            "--site-only",
            str(site_only),
        ],
        cwd=TEMPLATE,
    )
    return code == 0, out[-2000:]


def copy_hub_tools(path: Path) -> None:
    for name in HUB_TOOL_FILES:
        src = TEMPLATE / "tools" / name
        dst = path / "tools" / name
        if src.is_file():
            shutil.copy2(src, dst)


def patch_glossary_lead(path: Path) -> bool:
    build_glossary = path / "tools/build_glossary_pages.py"
    if not build_glossary.is_file():
        return False
    text = build_glossary.read_text(encoding="utf-8")
    old = (
        'f"{exam_name()}の試験で押さえたい知識（用語・比較・数値・誤答）を、分野別にまとめています。"'
    )
    new = 'f"{exam_name()}の試験で押さえたい用語を、分野別にまとめています。"'
    if old not in text:
        return False
    build_glossary.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def patch_build_all(path: Path) -> bool:
    build_all = path / "tools/build_all.py"
    if not build_all.is_file():
        return False
    text = build_all.read_text(encoding="utf-8")
    if "build_hub_retire_redirects.py" in text:
        return False
    new_text, n = re.subn(
        r'\n\s*run\(\[py, "tools/build_compare_pages\.py"\]\)\n'
        r'\s*run\(\[py, "tools/build_numbers_mistakes_pages\.py"\]\)\n',
        '\n    run([py, "tools/build_hub_retire_redirects.py"])\n',
        text,
        count=1,
    )
    if n:
        build_all.write_text(new_text, encoding="utf-8")
        return True
    return False


def apply_site_config(path: Path) -> tuple[bool, str]:
    script = path / "tools/apply_site_config.py"
    if not script.is_file():
        return False, "missing apply_site_config.py"
    code, out = run([sys.executable, "tools/apply_site_config.py"], cwd=path)
    return code == 0, out[-1500:]


def build_site(path: Path) -> tuple[bool, str]:
    lines: list[str] = []
    ok = True
    for script in ("build_glossary_pages.py", "build_hub_retire_redirects.py", "build_sitemap.py"):
        sp = path / "tools" / script
        if not sp.is_file():
            lines.append(f"missing {script}")
            ok = False
            continue
        code, out = run([sys.executable, str(sp.relative_to(path))], cwd=path)
        lines.append(out[-1200:])
        if code != 0:
            ok = False
    return ok, "\n".join(lines)


def verify(path: Path) -> tuple[bool, str]:
    issues: list[str] = []
    for rel in ("about.html", "privacy.html", "related-sites.html"):
        fp = path / rel
        if fp.is_file():
            text = fp.read_text(encoding="utf-8", errors="replace")
            hits = [b for b in BAD_FOOTER if b in text]
            if hits:
                issues.append(f"footer:{rel}:{hits}")
    ti = path / "terms/index.html"
    if ti.is_file():
        text = ti.read_text(encoding="utf-8", errors="replace")
        for s in FORBIDDEN:
            if s in text:
                issues.append(f"hub:{s}")
    else:
        issues.append("terms/index.html missing")
    ci = path / "terms/compare/index.html"
    if not ci.is_file():
        issues.append("compare redirect missing")
    return not issues, "; ".join(issues) or "ok"


def git_commit_push(path: Path, msg: str) -> tuple[str | None, bool, bool]:
    if not (path / ".git").is_dir():
        return None, False, False
    run(["git", "add", "-A"], cwd=path)
    code, _ = run(["git", "diff", "--cached", "--quiet"], cwd=path)
    if code == 0:
        _, h = run(["git", "rev-parse", "HEAD"], cwd=path)
        return h.strip().splitlines()[-1][:12] if h.strip() else None, False, False
    run(["git", "commit", "-m", msg], cwd=path)
    _, h = run(["git", "rev-parse", "HEAD"], cwd=path)
    commit = h.strip().splitlines()[-1][:12]
    push_code, _ = run(["git", "push", "origin", "HEAD"], cwd=path)
    push_ok = push_code == 0
    gh_ok = False
    sync_sh = path / "tools/sync_gh_pages_branch.sh"
    _, branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path)
    if push_ok and branch.strip() in ("main", "master") and sync_sh.is_file():
        gcode, _ = run(["bash", str(sync_sh)], cwd=path)
        gh_ok = gcode == 0
    return commit, push_ok, gh_ok


def main() -> int:
    report = TEMPLATE / "mankan_unkan_kangyou_deploy_report.txt"
    lines = [
        "=== mankan / unkan / kangyou Deploy ===",
        f"Started: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "| site | sync | hub patch | apply | build | verify | commit | push | gh |",
        "|------|------|-----------|-------|-------|--------|--------|------|-----|",
    ]
    failed = False

    for name, path, site_only in SITES:
        path = path.resolve()
        ensure_clone(name, path)
        if not path.is_dir():
            lines.append(f"| {name} | missing | — | — | — | — | — | — | — |")
            failed = True
            continue

        sync_ok, _ = sync_template(path, site_only)
        copy_hub_tools(path)
        patch_glossary_lead(path)
        patched = patch_build_all(path)
        apply_ok, _ = apply_site_config(path)
        build_ok, _ = build_site(path) if apply_ok else (False, "")
        verify_ok, vmsg = verify(path) if build_ok else (False, "build failed")
        msg = HUB_COMMIT if patched or sync_ok else FOOTER_COMMIT
        commit, push_ok, gh_ok = git_commit_push(path, msg) if verify_ok else (None, False, False)
        if not verify_ok:
            failed = True
        lines.append(
            f"| {name} | {sync_ok} | {patched} | {apply_ok} | {build_ok} | {verify_ok} ({vmsg}) | {commit or '—'} | {push_ok} | {gh_ok} |"
        )
        print(f"Done {name}: verify={verify_ok} push={push_ok}")

    lines.append("")
    lines.append(f"Finished: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report.read_text(encoding="utf-8"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
