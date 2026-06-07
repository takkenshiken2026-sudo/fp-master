#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bootstrap full S31–S44 hub pipeline onto unkan-master / mankan-master."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path("/Users/otedaiki/Projects")
TEMPLATE = ROOT / "exam-site-shell/tools"

HUB_TOOL_FILES = [
    "knowledge_hub_rules.py",
    "hub_faq_expand.py",
    "hub_premium_faq_auto.py",
    "hub_merge_data.py",
    "hub_strip_batch_suffix.py",
    "hub_diversify_content.py",
    "hub_collapse_angles.py",
    "hub_collapse_series.py",
    "hub_quality_gate.py",
    "audit_hub_quality.py",
    "build_numbers_mistakes_pages.py",
    "hub_site_topics.py",
]

BATCHES = [
    ("s31", "S31"),
    ("s32", "S32"),
    ("s33", "S33"),
    ("s34", "S34"),
    ("s35", "S35"),
    ("s36", "S36"),
    ("s37", "S37"),
    ("s38", "S38"),
    ("s39", "S39"),
    ("s40", "S40"),
    ("s41", "S41"),
    ("s42", "S42"),
    ("s43", "S43"),
    ("s44", "S44"),
]


def _qa_fn() -> str:
    return textwrap.dedent(
        '''
        def _qa(topic: str) -> list[tuple[str, str]]:
            return [
                (
                    f"{topic}で落としやすい論点は？",
                    f"{topic}は義務主体、手続順序、記録保存の3点が崩れやすい領域です。"
                    "主語を固定してから条文・数値を照合してください。",
                ),
                (
                    "実務・試験での覚え方は？",
                    "比較表または早見表を作成し、過去問の逆転肢を型別に分類してください。",
                ),
                (
                    "直前期の復習は？",
                    "誤答したテーマだけを再演習し、同一テーマの引っかけを連続で確認してください。",
                ),
                (
                    "公式情報の確認先は？",
                    "試験要項・省令・用語集を参照し、本ページは学習整理用である点に留意してください。",
                ),
            ]
        '''
    ).strip()


def _make_axes(related: list[str], labels: str) -> str:
    parts = [x.strip() for x in labels.split(";")]
    terms = related + related
    axes = []
    axis_names = ["論点A", "論点B", "論点C", "論点D", "論点E"][: len(parts)]
    for i, name in enumerate(axis_names):
        cols = [terms[i % len(terms)], terms[(i + 1) % len(terms)]]
        while len(cols) < len(parts):
            cols.append(terms[(i + len(cols)) % len(terms)])
        cols = cols[: len(parts)]
        cols_str = ", ".join(f'"{c}"' for c in cols)
        axes.append(f'    ("{name}", [{cols_str}]),')
    return "[\n" + "\n".join(axes) + "\n]"


def _make_items(related: list[str]) -> str:
    rows = []
    for i, lbl in enumerate(["確認1", "確認2", "確認3", "確認4"]):
        t = related[i % len(related)]
        rows.append(f'    ("{lbl}", "{t}", "試験要点を確認"),')
    return "[\n" + "\n".join(rows) + "\n]"


def _make_patterns(related: list[str]) -> str:
    rows = []
    for i, tp in enumerate(["手順", "主体", "記録", "報告"]):
        t = related[i % len(related)]
        rows.append(f'    ("{tp}", "誤った対応", "{t}を確認", "典型誤答"),')
    return "[\n" + "\n".join(rows) + "\n]"


def generate_batch_file(
    *,
    site_key: str,
    prefix: str,
    batch: str,
    batch_label: str,
    topics: list,
    cats: tuple[str, ...],
    cat_map: dict[str, str],
    out_path: Path,
) -> None:
    s30 = f"write_{prefix}_hub_s30_helpers"
    lines = [
        "# -*- coding: utf-8 -*-",
        f'"""{site_key} 知識ハブ {batch_label} 追加分（各10件）."""',
        "",
        f"from tools.{s30} import cmp, mis, num",
        "",
        f'CAT = {cat_map!r}',
        "",
        _qa_fn(),
        "",
        "COMPARISONS_ADD = [",
    ]
    for idx, (slug_base, title_base, tags, related) in enumerate(topics):
        cat_key = cats[idx % len(cats)]
        cat = f'CAT["{cat_key}"]'
        slug = f"{batch}-kon-{slug_base}-cmp"
        labels = "論点A;論点B" if idx % 3 else "対象;手順;記録"
        if idx % 3 == 1:
            labels = "法令;実施;保存"
        axes = _make_axes(related, labels)
        rel = ";".join(related)
        lines.append(
            f'    cmp("{slug}", "{title_base}の比較整理", {cat}, "{tags}", '
            f'"{title_base}の比較整理で試験頻出論点を軸ごとに整理します。", '
            f'"{labels}", {axes}, '
            f'"{title_base}の比較整理｜試験要点", '
            f'"{title_base}は主体・手順・記録の順で整理すると得点が安定します。条文と手続をセットで確認してください。", '
            f'"{related[0]};{related[1]};記録確認", '
            f'"主体と手順の混同;記録省略;条件文の読み飛ばし", '
            f'"{title_base}は手順順序を固定して覚える。", '
            f'"{rel}", _qa("{title_base[:8]}")),'
        )
    lines.extend(["]", "", "NUMBERS_ADD = ["])
    for idx, (slug_base, title_base, tags, related) in enumerate(topics):
        cat_key = cats[idx % len(cats)]
        cat = f'CAT["{cat_key}"]'
        slug = f"{batch}-kon-{slug_base}-num"
        items = _make_items(related)
        rel = ";".join(related)
        lines.append(
            f'    num("{slug}", "{title_base}の数値整理", {cat}, "{tags}", '
            f'"{title_base}の数値・手続で確認すべき代表項目を整理します。", '
            f'"{title_base}の代表数値・手続", {items}, '
            f'"{title_base}の数値整理｜試験要点", '
            f'"{title_base}で押さえる数値・期限・手続を整理します。試験では数値と主体を対で確認してください。", '
            f'"{related[0]};{related[1]};手続確認", '
            f'"数値だけ暗記;手順省略;主体混同", '
            f'"{title_base}は数値と手順を対で覚える。", '
            f'"{rel}", _qa("{title_base[:8]}数値")),'
        )
    lines.extend(["]", "", "MISTAKES_ADD = ["])
    for idx, (slug_base, title_base, tags, related) in enumerate(topics):
        cat_key = cats[idx % len(cats)]
        cat = f'CAT["{cat_key}"]'
        slug = f"{batch}-kon-{slug_base}-mis"
        patterns = _make_patterns(related)
        rel = ";".join(related)
        lines.append(
            f'    mis("{slug}", "{title_base}の典型誤答", {cat}, "{tags}", '
            f'"{title_base}で頻出する誤答パターンを整理します。", '
            f'"{title_base}と類似制度の境界が曖昧になり、総合問題で誤答しやすい。", {patterns}, '
            f'"{title_base}の典型誤答｜試験要点", '
            f'"{title_base}は義務主体を先に確定し、条件文を最後まで読んでください。引っかけ肢を型別に整理します。", '
            f'"{related[0]};手順混同;記録漏れ;数値混同", '
            f'"主体不明;手順省略;記録なし;数値逆転", '
            f'"{title_base}は主体→手順→記録の順で確認する。", '
            f'"{rel}", _qa("{title_base[:8]}誤答")),'
        )
    lines.append("]")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_s30_helpers(site_dir: Path, prefix: str, s30_data_module: str) -> None:
    path = site_dir / "tools" / f"write_{prefix}_hub_s30_helpers.py"
    path.write_text(
        textwrap.dedent(
            f'''
            # -*- coding: utf-8 -*-
            """cmp/num/mis helpers and S30 row exports for {prefix}."""
            from tools.{s30_data_module} import COMPARISONS, MISTAKES, NUMBERS, cmp, mis, num
            '''
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def write_mankan_s30_helpers(site_dir: Path) -> None:
    path = site_dir / "tools/archive/write_mankan_hub_s30_helpers.py"
    path.write_text(
        textwrap.dedent(
            '''
            # -*- coding: utf-8 -*-
            """cmp/num/mis helpers for mankan S31+ batches."""
            import json
            from tools.write_mankan_hub_s30 import HEADER_COMPARE, HEADER_MISTAKES, HEADER_NUMBERS, DATA
            from tools.write_mankan_hub_s30_data import COMPARISONS, MISTAKES, NUMBERS

            def _faq(qa: list[tuple[str, str]]) -> dict[str, str]:
                out: dict[str, str] = {}
                for i, (q, a) in enumerate(qa, start=1):
                    out[f"faq_{i}_question"] = q
                    out[f"faq_{i}_answer"] = a
                return out

            def _rows(*items: dict) -> str:
                return json.dumps(list(items), ensure_ascii=False)

            def cmp(slug, title, cat, tags, summary, labels, axes, article_title, lead, points, mistakes, tip, related, qa):
                return {
                    "slug": slug, "title": title, "category": cat, "tags": tags, "summary": summary,
                    "col_labels": labels,
                    "compare_rows": _rows(*[{"axis": a, "cols": c} for a, c in axes]),
                    "article_title": article_title, "article_lead": lead, "exam_points": points,
                    "common_mistakes": mistakes, "memory_tip": tip, "related_terms": related, **_faq(qa),
                }

            def num(slug, title, cat, tags, summary, highlight, items, article_title, lead, points, mistakes, tip, related, qa):
                return {
                    "slug": slug, "title": title, "category": cat, "tags": tags, "summary": summary,
                    "highlight": highlight,
                    "item_rows": _rows(*[{"item": i, "value": v, "note": n} for i, v, n in items]),
                    "article_title": article_title, "article_lead": lead, "exam_points": points,
                    "common_mistakes": mistakes, "memory_tip": tip, "related_terms": related, **_faq(qa),
                }

            def mis(slug, title, cat, tags, summary, confusion, patterns, article_title, lead, points, mistakes, tip, related, qa):
                return {
                    "slug": slug, "title": title, "category": cat, "tags": tags, "summary": summary,
                    "confusion_point": confusion,
                    "pattern_rows": _rows(*[{"topic": t, "wrong": w, "correct": c, "trap": p} for t, w, c, p in patterns]),
                    "article_title": article_title, "article_lead": lead, "exam_points": points,
                    "common_mistakes": mistakes, "memory_tip": tip, "related_terms": related, **_faq(qa),
                }
            '''
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def write_hub_data(site_dir: Path, prefix: str) -> None:
    import_lines = []
    merge_c = ["C30"]
    merge_n = ["N30"]
    merge_m = ["M30"]
    for batch, _ in BATCHES:
        mod = f"write_{prefix}_hub_{batch}_content"
        var = batch.upper()
        import_lines.append(
            f"from tools.{mod} import COMPARISONS_ADD as COMPARISONS_{var}, "
            f"MISTAKES_ADD as MISTAKES_{var}, NUMBERS_ADD as NUMBERS_{var}"
        )
        merge_c.append(f"COMPARISONS_{var}")
        merge_n.append(f"NUMBERS_{var}")
        merge_m.append(f"MISTAKES_{var}")

    lines = [
        "#!/usr/bin/env python3",
        "# -*- coding: utf-8 -*-",
        f'"""{prefix} 知識ハブ CSV 統合出力（S30 + S31–S44）."""',
        "",
        "from __future__ import annotations",
        "",
        "import csv",
        "import sys",
        "from pathlib import Path",
        "",
        "ROOT = Path(__file__).resolve().parents[2]",
        "sys.path.insert(0, str(ROOT))",
        "",
        "from tools.archive.hub_merge_data import apply_hub_collapse, finalize_hub_rows, merge",
        f"from tools.write_{prefix}_hub_s30 import DATA, HEADER_COMPARE, HEADER_MISTAKES, HEADER_NUMBERS",
        f"from tools.write_{prefix}_hub_s30_helpers import COMPARISONS as C30, MISTAKES as M30, NUMBERS as N30",
        *import_lines,
        "",
        "def write_csv(path: Path, header: list[str], rows: list[dict]) -> None:",
        '    with path.open("w", encoding="utf-8", newline="") as f:',
        "        w = csv.DictWriter(f, fieldnames=header, lineterminator=\"\\n\")",
        "        w.writeheader()",
        "        w.writerows(rows)",
        "",
        "def main() -> None:",
        f"    comparisons = finalize_hub_rows(merge({', '.join(merge_c)}))",
        f"    numbers = finalize_hub_rows(merge({', '.join(merge_n)}))",
        f"    mistakes = finalize_hub_rows(merge({', '.join(merge_m)}))",
        "    comparisons, numbers, mistakes = apply_hub_collapse(DATA, comparisons, numbers, mistakes)",
        '    write_csv(DATA / "comparisons.csv", HEADER_COMPARE, comparisons)',
        '    write_csv(DATA / "numbers.csv", HEADER_NUMBERS, numbers)',
        '    write_csv(DATA / "mistakes.csv", HEADER_MISTAKES, mistakes)',
        '    print(f"wrote compare={len(comparisons)} numbers={len(numbers)} mistakes={len(mistakes)}")',
        "",
        'if __name__ == "__main__":',
        "    main()",
        "",
    ]
    (site_dir / f"tools/archive/write_{prefix}_hub_data.py").write_text("\n".join(lines), encoding="utf-8")


def copy_hub_tools(site_dir: Path) -> None:
    for name in HUB_TOOL_FILES:
        src = TEMPLATE / name
        dst = site_dir / "tools" / name
        if src.is_file():
            shutil.copy2(src, dst)


def run(cmd: list[str], cwd: Path, *, optional: bool = False) -> None:
    print("+", " ".join(cmd), flush=True)
    result = subprocess.run(cmd, cwd=cwd, check=False)
    if result.returncode != 0 and not optional:
        raise subprocess.CalledProcessError(result.returncode, cmd)


def bootstrap_site(site_key: str, cfg: dict) -> None:
    site_dir = ROOT / site_key
    prefix = cfg["prefix"]
    tools = site_dir / "tools"
    copy_hub_tools(site_dir)

    if prefix == "mankan":
        write_mankan_s30_helpers(site_dir)
        # ensure mankan s30 has DATA/headers
        if not (tools / "write_mankan_hub_s30.py").is_file():
            raise FileNotFoundError("write_mankan_hub_s30.py missing")
        # patch write_mankan_hub_s30 to export DATA if needed
        s30_text = (tools / "write_mankan_hub_s30.py").read_text(encoding="utf-8")
        if "DATA = " not in s30_text:
            s30_text = s30_text.replace(
                "ROOT = Path(__file__).resolve().parents[2]",
                "ROOT = Path(__file__).resolve().parents[2]\nDATA = ROOT / \"data\"",
            )
            if "HEADER_COMPARE" not in s30_text:
                s30_text += textwrap.dedent(
                    '''

                    HEADER_COMPARE = [
                        "slug", "title", "category", "tags", "summary", "col_labels", "compare_rows",
                        "article_title", "article_lead", "exam_points", "common_mistakes", "memory_tip",
                        "related_terms", "faq_1_question", "faq_1_answer", "faq_2_question", "faq_2_answer",
                        "faq_3_question", "faq_3_answer", "faq_4_question", "faq_4_answer",
                    ]
                    HEADER_NUMBERS = [
                        "slug", "title", "category", "tags", "summary", "highlight", "item_rows",
                        "article_title", "article_lead", "exam_points", "common_mistakes", "memory_tip",
                        "related_terms", "faq_1_question", "faq_1_answer", "faq_2_question", "faq_2_answer",
                        "faq_3_question", "faq_3_answer", "faq_4_question", "faq_4_answer",
                    ]
                    HEADER_MISTAKES = [
                        "slug", "title", "category", "tags", "summary", "confusion_point", "pattern_rows",
                        "article_title", "article_lead", "exam_points", "common_mistakes", "memory_tip",
                        "related_terms", "faq_1_question", "faq_1_answer", "faq_2_question", "faq_2_answer",
                        "faq_3_question", "faq_3_answer", "faq_4_question", "faq_4_answer",
                    ]
                    '''
                )
            (tools / "write_mankan_hub_s30.py").write_text(s30_text, encoding="utf-8")
    else:
        write_s30_helpers(site_dir, prefix, cfg["s30_module"])

    for batch, label in BATCHES:
        generate_batch_file(
            site_key=site_key,
            prefix=prefix,
            batch=batch,
            batch_label=label,
            topics=cfg["topics"],
            cats=cfg["cats"],
            cat_map=cfg["cat_map"],
            out_path=tools / f"write_{prefix}_hub_{batch}_content.py",
        )

    write_hub_data(site_dir, prefix)

    py = sys.executable
    run([py, f"tools/archive/write_{prefix}_hub_data.py"], site_dir)
    if (tools / "validate_csv.py").is_file():
        run([py, "tools/validate_csv.py"], site_dir, optional=True)
    run([py, "tools/build_compare_pages.py"], site_dir)
    run([py, "tools/build_numbers_mistakes_pages.py"], site_dir)
    if (tools / "build_sitemap.py").is_file():
        run([py, "tools/build_sitemap.py"], site_dir)
    if (tools / "hub_quality_gate.py").is_file():
        run([py, "tools/hub_quality_gate.py"], site_dir, optional=True)


def main() -> int:
    sys.path.insert(0, str(TEMPLATE.parent))
    from tools.archive.hub_site_topics import SITE_TOPIC_CONFIG

    parser = argparse.ArgumentParser()
    parser.add_argument("sites", nargs="*", default=["unkan-master", "mankan-master"])
    args = parser.parse_args()
    for site in args.sites:
        if site not in SITE_TOPIC_CONFIG:
            raise SystemExit(f"unknown site: {site}")
        print(f"=== bootstrap {site} ===", flush=True)
        bootstrap_site(site, SITE_TOPIC_CONFIG[site])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
