#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""guide_articles.csv の量産テンプレをサイト別ライブラリで差し替える。"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

TEMPLATE_ROOT = Path(__file__).resolve().parents[2]


def _import_from_template(module_name: str) -> ModuleType:
    path = TEMPLATE_ROOT / "tools" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(f"exam_site_shell.{module_name}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load template module: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_lib(target: Path) -> ModuleType:
    target = target.resolve()
    ctx_mod = _import_from_template("guide_content_context")
    ctx_mod.init_guide_content(target)
    ctx = ctx_mod.get_context()

    if "ボイラー" in ctx.exam or "ボイラー" in ctx.brand:
        return _import_from_template("boiler_guide_content_lib")
    if "危険物" in ctx.exam or "乙種" in ctx.exam or "乙4" in ctx.brand:
        return _import_from_template("kikenbutsu_guide_content_lib")
    if "第二種衛生" in ctx.exam or "二衛" in ctx.brand:
        return _import_from_template("eisei2shu_guide_content_lib")
    if "第一種衛生" in ctx.exam or "一衛" in ctx.brand:
        return _import_from_template("eisei1shu_guide_content_lib")
    if "賃貸不動産経営" in ctx.exam or "賃管" in ctx.brand:
        return _import_from_template("chintaikanrishi_guide_content_lib")
    if "マンション管理士" in ctx.exam or "マ管" in ctx.brand:
        return _import_from_template("mankan_guide_content_lib")
    if "運行管理者" in ctx.exam or "運管" in ctx.brand:
        return _import_from_template("unkan_guide_content_lib")
    if "管理業務主任者" in ctx.exam or "管業" in ctx.brand:
        return _import_from_template("kangyou_guide_content_lib")
    if "メンタル" in ctx.exam or "メンタル" in ctx.brand:
        return _import_from_template("mentalhealth_guide_content_lib")
    if "宅建" in ctx.exam or "宅地建物" in ctx.exam or "宅建" in ctx.brand:
        return _import_from_template("takken_guide_content_lib")
    raise RuntimeError(
        f"no guide content library for exam={ctx.exam!r} brand={ctx.brand!r}; "
        "add a site profile or dedicated lib module"
    )


def hub_extra_sections(lib: ModuleType, row: dict[str, str], topic: str, slug: str, ctx: dict) -> int:
    if row.get("genre") != "用語ハブ活用法":
        return 0
    changes = 0
    if not (row.get("section_4_heading") or "").strip():
        row["section_4_heading"] = "比較表・よくある誤答タブ"
        row["section_4_body"] = lib.section_body_for(
            "比較表・よくある誤答タブ", topic, slug, row.get("genre") or "", ctx
        )
        changes += 1
    if not (row.get("section_5_heading") or "").strip():
        row["section_5_heading"] = "関連ガイドと演習への導線"
        row["section_5_body"] = lib.section_body_for(
            "関連ガイドと演習への導線", topic, slug, row.get("genre") or "", ctx
        )
        changes += 1
    return changes


def upgrade_row(lib: ModuleType, row: dict[str, str], glossary: dict[str, dict[str, str]]) -> int:
    changes = 0
    topic = lib.topic_from_row(row)
    slug = (row.get("slug") or "").strip()
    genre = (row.get("genre") or "").strip()

    ctx: dict = {}
    if genre == "用語ハブ活用法":
        term_name, term_short = lib.term_for_hub_slug(slug, row.get("title") or "", glossary)
        ctx["term_name"] = term_name
        ctx["term_short"] = term_short

    md = (row.get("meta_description") or "").strip()
    if len(md) < 70 or lib.META_STUB in md or lib.is_stub(md):
        row["meta_description"] = lib.meta_description_for(row, topic)
        changes += 1

    ui = (row.get("user_intent") or "").strip()
    if lib.is_stub(ui) or "読了後は行動チェックリストに沿って演習・用語確認まで進められる状態を目指します" in ui:
        if ui.count("読了後は行動チェックリスト") > 0 or len(ui) < 50 or lib.is_stub(ui):
            row["user_intent"] = lib.user_intent_for(topic, genre)
            changes += 1

    if not (row.get("key_points") or "").strip():
        row["key_points"] = lib.key_points_for(row, topic)
        changes += 1

    new_lead = lib.lead_for(row, topic)
    if new_lead != (row.get("lead") or "").strip():
        row["lead"] = new_lead
        changes += 1

    generic_action = "間違えた用語を用語解説で確認して解き直す"
    if generic_action in (row.get("action_items") or "") or len((row.get("action_items") or "").split(";")) < 3:
        row["action_items"] = lib.action_items_for(topic, slug, genre)
        changes += 1

    for n in range(1, 8):
        hcol, bcol = f"section_{n}_heading", f"section_{n}_body"
        heading = (row.get(hcol) or "").strip()
        body = (row.get(bcol) or "").strip()
        if not heading:
            continue
        needs = (
            lib.is_stub(body)
            or len(body) < 180
            or "<a href" in body
            or f"(記事:{slug})" not in body
        )
        if needs:
            row[bcol] = lib.section_body_for(heading, topic, slug, genre, ctx)
            changes += 1

    for n in range(1, 5):
        qcol, acol = f"faq_{n}_question", f"faq_{n}_answer"
        q = (row.get(qcol) or "").strip()
        if q:
            row[acol] = lib.faq_answer_for(q, topic, slug, row, faq_index=n)
            changes += 1

    changes += hub_extra_sections(lib, row, topic, slug, ctx)
    return changes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    target = args.target.resolve()
    guide_path = target / "data" / "guide_articles.csv"
    glossary_path = target / "data" / "glossary_terms.csv"
    if not guide_path.is_file():
        print(f"missing: {guide_path}", file=sys.stderr)
        return 1

    lib = _load_lib(target)
    glossary = lib.load_glossary_index(glossary_path)
    rows = list(csv.DictReader(guide_path.open(encoding="utf-8-sig")))
    total_changes = 0
    for row in rows:
        total_changes += upgrade_row(lib, row, glossary)

    if args.dry_run:
        print(f"dry-run: would update {total_changes} cell(s) across {len(rows)} rows")
        return 0

    with guide_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys(), lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"upgraded {guide_path}: {total_changes} cell(s) across {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
