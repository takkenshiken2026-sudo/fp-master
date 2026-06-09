#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第63〜70バッチ相当：実技35問（第616〜650問）を practice_questions.csv に追記する。"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.jitsugi_practice_row_builder import build_batch  # noqa: E402
from tools.seed_practice_batch1 import COLUMNS  # noqa: E402

OUT = ROOT / "data" / "practice_questions.csv"


def main() -> None:
    batch = build_batch(616)
    if not OUT.is_file():
        raise FileNotFoundError(f"{OUT} がありません。")
    with OUT.open(encoding="utf-8-sig", newline="") as f:
        existing = list(csv.DictReader(f))
    existing_nos = {int(r["question_no"]) for r in existing}
    for r in batch:
        n = int(r["question_no"])
        if n in existing_nos:
            raise ValueError(f"question_no={n} は既に存在します")
    merged = existing + batch
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(merged)
    print(f"Appended {len(batch)} rows (total {len(merged)}) to {OUT}")


if __name__ == "__main__":
    main()
