#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公表過去問 PDF（j3_YYYY05_q.pdf）から実技問題の資料図を切り出す。

  python3 tools/extract_fp3_pdf_diagrams.py \\
    --pdf-2024 ~/Desktop/j3_202405_q.pdf \\
    --pdf-2025 ~/Desktop/j3_202505_q.pdf \\
    --pdf-2026 ~/Desktop/j3_202605_q.pdf
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyMuPDF が必要です: pip install pymupdf") from exc

OUT_DIR = ROOT / "assets" / "q-diagrams"
MANIFEST = ROOT / "data" / "source" / "fp3" / "pdf_diagram_manifest.json"

FW = str.maketrans("０１２３４５６７８９", "0123456789")
Q_RE = re.compile(r"問\s*([０-９0-9]+)")


def qnum_from_text(text: str) -> int | None:
    m = Q_RE.search(text.strip())
    if not m:
        return None
    return int(m.group(1).translate(FW))


def diagram_id(exam_year: int, qno: int) -> str:
    """fp3-jitsugi-202405-q002 形式（既存 diagram_id と一致）。"""
    return f"fp3-jitsugi-{exam_year}05-q{qno:03d}"


def find_question_anchors(page: fitz.Page) -> list[tuple[int, float]]:
    """ページ内の 問N の y 座標（上端）。"""
    anchors: list[tuple[int, float]] = []
    blocks = page.get_text("dict").get("blocks") or []
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines") or []:
            text = "".join(span.get("text", "") for span in line.get("spans") or [])
            qn = qnum_from_text(text)
            if qn is None:
                continue
            y0 = line["bbox"][1]
            if not anchors or anchors[-1][0] != qn:
                anchors.append((qn, y0))
    anchors.sort(key=lambda x: x[1])
    return anchors


def find_material_top(page: fitz.Page, after_y: float) -> float:
    """資料ブロック開始（＜見出し＞）を探す。"""
    best = None
    for token in ("＜", "<"):
        for rect in page.search_for(token):
            if rect.y0 >= after_y - 2:
                if best is None or rect.y0 < best:
                    best = rect.y0
    if best is not None:
        return max(best - 6, after_y + 24)
    return after_y + 72


def find_choice_top(page: fitz.Page, after_y: float) -> float | None:
    for token in ("１．", "1."):
        for rect in page.search_for(token):
            if rect.y0 > after_y + 40:
                return rect.y0 - 8
    return None


def crop_question_material(
    page: fitz.Page,
    *,
    qy: float,
    next_qy: float | None,
    page_bottom: float,
) -> fitz.Rect | None:
    y0 = find_material_top(page, qy)
    y1 = find_choice_top(page, qy)
    if y1 is None:
        y1 = next_qy - 10 if next_qy else page_bottom - 36
    if next_qy and y1 > next_qy - 12:
        y1 = next_qy - 12
    if y1 - y0 < 48:
        return None
    margin_x = 42
    return fitz.Rect(margin_x, y0, page.rect.width - margin_x, y1)


def extract_pdf(pdf_path: Path, exam_year: int) -> dict[str, str]:
    doc = fitz.open(pdf_path)
    written: dict[str, str] = {}
    for page_index in range(doc.page_count):
        page = doc[page_index]
        anchors = find_question_anchors(page)
        if not anchors:
            continue
        page_bottom = page.rect.height
        for i, (qno, qy) in enumerate(anchors):
            if qno < 2 or qno > 20:
                continue
            next_qy = anchors[i + 1][1] if i + 1 < len(anchors) else None
            rect = crop_question_material(page, qy=qy, next_qy=next_qy, page_bottom=page_bottom)
            if rect is None:
                continue
            did = diagram_id(exam_year, qno)
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            out_path = OUT_DIR / f"{did}.png"
            pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), clip=rect, alpha=False)
            pix.save(str(out_path))
            written[did] = f"assets/q-diagrams/{did}.png"
            print("wrote", out_path.name, f"{int(rect.width)}x{int(rect.height)}")
    return written


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-2024", type=Path, default=Path.home() / "Desktop" / "j3_202405_q.pdf")
    ap.add_argument("--pdf-2025", type=Path, default=Path.home() / "Desktop" / "j3_202505_q.pdf")
    ap.add_argument("--pdf-2026", type=Path, default=Path.home() / "Desktop" / "j3_202605_q.pdf")
    args = ap.parse_args()

    all_written: dict[str, str] = {}
    mapping = [
        (args.pdf_2024, 2024),
        (args.pdf_2025, 2025),
        (args.pdf_2026, 2026),
    ]
    for path, year in mapping:
        if not path.is_file():
            print(f"SKIP missing PDF: {path}", file=sys.stderr)
            continue
        print(f"=== {path.name} (exam_year={year}) ===")
        all_written.update(extract_pdf(path, year))

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(all_written, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"manifest: {len(all_written)} figures → {MANIFEST}")
    return 0 if all_written else 1


if __name__ == "__main__":
    raise SystemExit(main())
