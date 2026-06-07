#!/usr/bin/env python3
"""Copy collapse tools to all sites, regenerate hub CSVs and HTML."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/otedaiki/Projects")
TEMPLATE = ROOT / "exam-site-shell/tools"
FILES = [
    "hub_collapse_angles.py",
    "hub_merge_data.py",
    "hub_diversify_content.py",
    "hub_quality_gate.py",
    "build_numbers_mistakes_pages.py",
]
SITES = [
    "chintaikanrishi-master",
    "takken-master",
    "eisei1shu-master",
    "eisei2shu-master",
    "kangyou-master",
    "kikenbutsu-master",
    "mentalhealth-master",
    "boiler-master.jp",
]

py = sys.executable
lines: list[str] = []


def patch_takken_style_write(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "apply_hub_collapse" in text:
        return False
    if "write_hub_csvs" in text:
        return False
    if "finalize_hub_rows" not in text or "write_csv(DATA" not in text:
        return False
    text = text.replace(
        "from tools.archive.hub_merge_data import finalize_hub_rows",
        "from tools.archive.hub_merge_data import apply_hub_collapse, finalize_hub_rows",
    )
    needle = "    write_csv(DATA / \"comparisons.csv\""
    if needle not in text:
        return False
    text = text.replace(
        needle,
        "    comparisons, numbers, mistakes = apply_hub_collapse(DATA, comparisons, numbers, mistakes)\n    write_csv(DATA / \"comparisons.csv\"",
        1,
    )
    path.write_text(text, encoding="utf-8")
    return True


for site in SITES:
    site_root = ROOT / site
    for name in FILES:
        src = TEMPLATE / name
        dst = site_root / "tools" / name
        if src.resolve() != dst.resolve():
            shutil.copy2(src, dst)
    hub_scripts = sorted(site_root.glob("tools/archive/write_*_hub_data.py"))
    if not hub_scripts:
        lines.append(f"{site}: NO write_*_hub_data.py")
        continue
    hub = hub_scripts[0]
    patched = patch_takken_style_write(hub)
    before = 0
    mistakes_csv = site_root / "data/mistakes.csv"
    if mistakes_csv.is_file():
        before = sum(1 for _ in mistakes_csv.open(encoding="utf-8")) - 1
    r = subprocess.run([py, str(hub)], cwd=site_root, capture_output=True, text=True)
    after = 0
    if mistakes_csv.is_file():
        after = sum(1 for _ in mistakes_csv.open(encoding="utf-8")) - 1
    b = subprocess.run([py, "tools/build_numbers_mistakes_pages.py"], cwd=site_root, capture_output=True, text=True)
    g = subprocess.run([py, "tools/hub_quality_gate.py"], cwd=site_root, capture_output=True, text=True)
    gate_ok = "QUALITY GATE OK" in (g.stdout or "")
    lines.append(
        f"{site}: patched={patched} hub={r.returncode} build={b.returncode} gate={'OK' if gate_ok else 'FAIL'} "
        f"mistakes {before}->{after}"
    )
    if r.returncode != 0:
        lines.append((r.stderr or r.stdout or "")[:400])
    if b.returncode != 0:
        lines.append((b.stderr or b.stdout or "")[:400])
    if not gate_ok:
        lines.append((g.stdout or g.stderr or "")[:400])

out = ROOT / "_hub_collapse_batch_report.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out.read_text())
