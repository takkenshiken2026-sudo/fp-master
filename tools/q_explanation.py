# -*- coding: utf-8 -*-
"""過去問・実践演習・一問一答の解説 HTML（要約・正解の理由・他肢/反対符号・学習のヒント）。"""

from __future__ import annotations

import html
import re


def norm(value: object) -> str:
    return (value or "").strip() if value is not None else ""


def _correct_choice_index(correct: object) -> int | None:
    """page['correct'] が int または multi の '1,3' 等のとき、先頭肢番号を返す。"""
    if correct is None:
        return None
    if isinstance(correct, int):
        return correct
    raw = norm(correct)
    if not raw:
        return None
    if raw.isdigit():
        return int(raw)
    if "," in raw:
        head = raw.split(",", 1)[0].strip()
        if head.isdigit():
            return int(head)
    return None


def text_to_html(text: str) -> str:
    if not text:
        return ""
    return html.escape(text).replace("\n", "<br>\n")


def parse_explanation_choices(raw: str) -> dict[int, str]:
    """選択肢別解説。形式: 「2:理由;3:理由」または改行区切り「（2）理由」。"""
    out: dict[int, str] = {}
    if not raw:
        return out
    for chunk in re.split(r"[\n;]+", raw):
        chunk = norm(chunk)
        if not chunk:
            continue
        m = re.match(r"^[（(]?(\d+)[）)]?\s*[:：]?\s*(.+)$", chunk)
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


def question_ask_mode(stem: str) -> str:
    """設問の求め方: most_correct / least_appropriate / unknown。"""
    s = norm(stem)
    if re.search(r"適切でない|誤っている|誤りである|正しくない|不適切なもの", s):
        return "least_appropriate"
    if re.search(r"正しい|妥当|適切である|適切なもの", s):
        return "most_correct"
    return "unknown"


def _choice_sounds_positive(text: str) -> bool:
    t = norm(text)
    if not t:
        return False
    positive = (
        r"確認する|整理する|復習|見直|用語|過去問|頻出|公式|記録|学習に役立|効率|押さえ|"
        r"組み合わせ|たどる|ブックマーク|振り返|比較表|一覧"
    )
    negative = r"しない方が|不要|優先する|削除|送信される|連携できない|役立たない|変わらない|固定"
    if re.search(negative, t):
        return False
    return bool(re.search(positive, t))


def _snippet(text: str, max_len: int = 36) -> str:
    t = norm(text)
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


_FW_DIGIT_TRANS = str.maketrans("０１２３４５６７８９", "0123456789")


def _normalize_for_compare(text: str) -> str:
    return re.sub(r"\s+", "", norm(text))


def _parse_kana_slots(text: str) -> dict[str, str]:
    slots: dict[str, str] = {}
    for m in re.finditer(r"（([ア-ウ])）\s*([^（]+?)(?=(?:（[ア-ウ]）)|$)", norm(text)):
        slots[m.group(1)] = norm(m.group(2))
    return slots


def _slot_values_equal(a: str, b: str) -> bool:
    return _normalize_for_compare(a) == _normalize_for_compare(b)


def _combo_diff_note(wrong: str, correct: str, explanation: str) -> str:
    """（ア）（イ）（ウ）形式の組合せ肢について、ずれている空欄だけを説明する。"""
    w_slots = _parse_kana_slots(wrong)
    c_slots = _parse_kana_slots(correct)
    if len(w_slots) < 2 or len(c_slots) < 2:
        return ""
    diffs: list[tuple[str, str, str]] = []
    for k in ("ア", "イ", "ウ", "エ", "オ"):
        if k not in w_slots and k not in c_slots:
            continue
        wv = w_slots.get(k, "")
        cv = c_slots.get(k, "")
        if wv and cv and not _slot_values_equal(wv, cv):
            diffs.append((k, wv, cv))
    if not diffs:
        return ""
    lines: list[str] = []
    for k, wv, cv in diffs:
        line = f"（{k}）が「{wv}」となっていますが、正しくは「{cv}」です"
        if k == "ア" and "再調達原価" in cv and "原価法" in explanation:
            line += "（原価法は再調達原価を基に試算します）"
        elif k == "イ" and "取引事例比較法" in cv and "取引事例" in explanation:
            line += "（取引事例の比較がこの行の評価手法です）"
        elif k == "ウ" and "現在価値" in cv and "現在価値" in explanation:
            line += "（収益還元法では純収益を現在価値に割り引きます）"
        lines.append(line)
    return "。".join(lines) + "。"


def _extract_digits(text: str) -> str:
    raw = re.sub(r"[^\d０-９]", "", norm(text)).translate(_FW_DIGIT_TRANS)
    return raw if raw.isdigit() else ""


def _numeric_diff_note(wrong: str, correct: str, explanation: str) -> str:
    """数値だけが違う選択肢向けの短い解説。"""
    w, c = _extract_digits(wrong), _extract_digits(correct)
    if not w or not c or w == c:
        return ""
    w_label, c_label = norm(wrong), norm(correct)
    if re.search(rf"最長\s*{re.escape(c)}年|{re.escape(c)}年間", explanation):
        return (
            f"任意継続被保険者の加入期間は最長{c_label}です。"
            f"「{w_label}」は設問の正答期間と一致しません。"
        )
    if re.search(rf"{re.escape(c_label)}", explanation) or re.search(
        rf"{re.escape(c)}", explanation
    ):
        return f"正答は「{c_label}」です。「{w_label}」は解説の数値と異なります。"
    return f"正答は「{c_label}」です。「{w_label}」との数値の違いを確認してください。"


def _text_overlap_diff_note(wrong: str, correct: str, explanation: str) -> str:
    """長文肢で正答肢との差分キーワードを拾う。"""
    if len(norm(wrong)) < 20 or len(norm(correct)) < 20:
        return ""
    w_set = set(re.findall(r"[\u4e00-\u9fff]{2,}", _normalize_for_compare(wrong)))
    c_set = set(re.findall(r"[\u4e00-\u9fff]{2,}", _normalize_for_compare(correct)))
    only_wrong = [t for t in sorted(w_set - c_set) if len(t) >= 2][:3]
    only_correct = [t for t in sorted(c_set - w_set) if len(t) >= 2][:3]
    if not only_wrong and not only_correct:
        return ""
    parts: list[str] = []
    if only_wrong:
        parts.append(f"この肢特有の論点は「{'・'.join(only_wrong)}」です")
    if only_correct:
        parts.append(f"正答側では「{'・'.join(only_correct)}」が要点です")
    if explanation and len(explanation) >= 24:
        hint = _snippet(explanation, 72)
        if hint not in "".join(parts):
            parts.append(hint)
    return "。".join(parts) + "。"


_MIN_CHOICE_NOTE_LEN = 72


def _is_thin_choice_note(note: str, mode: str) -> bool:
    """CSV の選択肢別解説が形式的・短すぎるか（読み手向けの価値が低い）。"""
    n = norm(note)
    if not n:
        return True
    if len(n) < _MIN_CHOICE_NOTE_LEN:
        return True
    if mode == "least_appropriate":
        if re.search(r"本肢.*妥当|正しい学習|推奨される学習", n) and len(n) < 140:
            if not re.search(
                r"最も適切でない|正答は[（(]?\d|学習効果.*損|有害|放棄|誤った記述",
                n,
            ):
                return True
        if re.search(r"設問形式の読み違えに注意", n) and len(n) < 100:
            return True
    if mode == "most_correct" and re.search(r"本肢を選ぶ場合は、設問が", n):
        return True
    return False


def infer_wrong_choice_note(
    page: dict,
    choice_num: int,
    choice_text: str,
    row: dict,
) -> str:
    """CSV に explanation_choices が無いとき、正答との差分を中心に短い解説を組み立てる。"""
    stem = norm(page.get("stem_plain") or page.get("stem") or "")
    mode = question_ask_mode(stem)
    opt = norm(choice_text)
    correct = page.get("correct")
    correct_text = ""
    cor_idx = _correct_choice_index(correct)
    opts = page.get("opts") or []
    if cor_idx is not None and 1 <= cor_idx <= len(opts):
        correct_text = opts[cor_idx - 1]
    correct_body = strip_choice_answer_prefix(
        norm(row.get("explanation_correct")) or norm(row.get("explanation")) or ""
    )
    category = norm(page.get("category") or "")

    if correct_text and opt:
        for builder in (
            lambda: _combo_diff_note(opt, correct_text, correct_body),
            lambda: _numeric_diff_note(opt, correct_text, correct_body),
            lambda: _text_overlap_diff_note(opt, correct_text, correct_body),
        ):
            note = builder()
            if note:
                return note

    if mode == "least_appropriate" and _choice_sounds_positive(opt):
        parts = [
            "単体では適切な学習法・対応に当たるため、"
            "「最も適切でないもの」の正答にはなりません。",
        ]
        if correct and correct_text:
            parts.append(
                f"本問の正答（{correct}）は「{_snippet(correct_text, 48)}」で、"
                "他の肢より明らかに不適切です。"
            )
        return " ".join(parts)

    if mode == "least_appropriate":
        return (
            "一見もっともらしい記述ですが、本問で「最も適切でない」とされるのは"
            f"正答（{correct}）です。四肢を比較して選び直してください。"
        )

    if mode == "most_correct":
        return (
            f"{category or '本分野'}の論点では正答（{correct}）と内容が一致しません。"
            "正解の理由と表・数値の対応を照らしてください。"
        )

    return (
        f"正答（{correct}）とは異なる内容です。"
        f"{category or '本分野'}の要点を正解の理由と照らして確認してください。"
    )


def resolve_wrong_choice_note(
    page: dict,
    choice_num: int,
    choice_text: str,
    row: dict,
    *,
    csv_note: str = "",
) -> str:
    """CSV 優先。薄い解説は推論で置き換え、未記入は推論で補完。"""
    stem = norm(page.get("stem_plain") or page.get("stem") or "")
    mode = question_ask_mode(stem)
    note = norm(csv_note)
    inferred = infer_wrong_choice_note(page, choice_num, choice_text, row)
    if not note:
        return inferred
    if _is_thin_choice_note(note, mode):
        return inferred
    return note


CATEGORY_STUDY_HINTS: dict[str, str] = {
    "法令・制度": (
        "試験制度・受験要件は年度ごとに見直されることがあります。"
        "受験要項・実施要領・合格発表の公式ページをブックマークし、改定年度は出題範囲表と学習計画を更新してください。"
        "用語解説で「受験資格」「試験要項」「公式情報」などの定義を押さえたうえで、"
        "同年・前後年度の過去問で出題パターンを確認すると、制度問題と実務問題のつながりが整理できます。"
        "模試・実践演習の前には、最新の公式情報を再確認する習慣を入れておくと安心です。"
    ),
    "契約・実務": (
        "実務・学習法の問題は、「誰が・何を・どこまで」が適切か、または「最も適切でないもの」かを"
        "設問文で切り替えて読むことが重要です。間違えた問題は復習リストに残し、"
        "正答・誤答それぞれについて「どの条件を満たさないか」を一文で書き出してください。"
        "関連ガイド（学習計画・過去問の進め方）と用語解説を往復すると、"
        "単発の暗記ではなく判断基準として定着しやすくなります。"
    ),
    "設備・その他": (
        "数値・期限・例外規定は、暗記だけでは混同しやすいです。"
        "自分用の比較表（単位・条件・責任者・手続の順序）を作り、週次で見直してください。"
        "分野別の用語一覧から関連語をたどり、過去問一覧で出題傾向を確認する流れが効率的です。"
        "実践演習で時間配分を測ったあと、間違えた設問だけ過去問の同分野に戻ると弱点がはっきりします。"
    ),
    "基礎・役割": (
        "管理監督者の役割・法令の趣旨・ストレスの基礎は、用語の定義と"
        "「誰が・何を・どこまで」がセットで出題されます。"
        "間違えた肢ごとに、正答との差分（根拠法令・対象範囲・責任の所在）をメモし、"
        "関連用語から同分野の過去問・実践演習を解き直してください。"
    ),
    "職場環境・配慮": (
        "職場の配慮・リスク要因は、具体策と「誰が担うか」を対にして覚えると得点しやすくなります。"
        "数値基準や手順は表に整理し、同年の過去問で実務イメージを補強してください。"
        "一問一答で用語の定義を確認してから、記述式に近い過去問に戻ると理解が深まります。"
    ),
    "相談・連携・復職": (
        "面談・医療連携・復職支援は、手順と禁止事項（やってはいけないこと）の区別が重要です。"
        "正答肢のキーワードを用語解説で確認し、同分野の過去問でケースのパターンを増やしてください。"
        "「最も不適切」形式では、一見正しそうな肢に惑わされないよう、設問文を先にマークする習慣をつけましょう。"
    ),
    "関係法令": (
        "法令・制度は条文の趣旨と数字・期限をセットで覚えると得点しやすくなります。"
        "関連用語を用語解説で押さえ、同年の過去問で「例外」「罰則」「手続」の組み合わせを確認してください。"
        "公式情報の更新時期は学習カレンダーに入れておくと、直前期の取りこぼしを防げます。"
    ),
    "労働衛生": (
        "衛生・安全は用語の定義と数値基準の組み合わせが多いです。"
        "間違えた問題は復習リストに残し、用語解説で意味を確認しながら解き直してください。"
        "図や表で「基準値・測定・記録義務」を一覧化すると、本番直前の確認が短くなります。"
    ),
    "労働生理": (
        "生理・人体は図解と用語の対応づけが有効です。"
        "分野別の用語一覧から関連語をたどり、過去問で「原因・対策・禁忌」のセットで復習してください。"
    ),
    "賃貸住宅管理業法": (
        "業法は「誰が・何を・どこまで」がセットで問われます。"
        "正答肢の義務主体と手続の流れをメモし、似た制度との違いを表に整理してから、"
        "同年・前後年度の過去問で定着を確認してください。"
    ),
    "民法・借地借家法": (
        "借地借家・民法改正は、権利関係の主体と効果の発生時期を一文で説明できるかが要点です。"
        "間違えた肢は正答と「誰に・いつ・どの効果が及ぶか」で対比してください。"
    ),
    "賃貸借契約": (
        "契約条項・個人情報・原状回復は、条文の趣旨と実務上の判断基準の両方が問われます。"
        "数字・期限・例外は一覧表にし、他の選択肢との差分を意識して復習してください。"
    ),
    "賃貸借契約実務": (
        "実務問題は「適切な対応か」「義務の範囲か」を区別する設問が多いです。"
        "誤答肢がどの要件を満たさないかを具体的に書き出すと定着します。"
    ),
    "賃貸不動産経営": (
        "経営・管理では、貸主・借主・管理者の視点の違いがポイントです。"
        "「最も不適切」形式では、一見正しそうな肢こそ見落としやすいので、設問文を再確認してください。"
    ),
    "管理実務": (
        "管理実務は手続の順序と義務の主体が問われやすいです。"
        "間違えた問題は復習リストに残し、同分野の用語とセットで解き直してください。"
    ),
    "建物・設備": (
        "設備・維持保全は数値基準・点検周期・責任の所在がセットで出題されます。"
        "他選択肢がどの要件（数値・主体・手続）とずれているかを確認してください。"
    ),
    "会計・税金・保険": (
        "税務・会計は計算の前提と課税関係者・時期の取り違えに注意です。"
        "誤答肢がどの前提を誤っているかを明示して復習してください。"
    ),
    "会計税務": (
        "税務・会計は計算の前提と課税関係者・時期の取り違えに注意です。"
        "誤答肢がどの前提を誤っているかを明示して復習してください。"
    ),
    "サブリース": (
        "サブリースは貸主・転貸人・借主の関係と契約上の効果の区別が要点です。"
        "誤答肢がどの関係を取り違えているかを確認してください。"
    ),
    "原状回復": (
        "原状回復は費用負担・範囲・特約の有無が問われやすいです。"
        "正答肢の要件を押さえ、他肢との差分を整理してください。"
    ),
    "賃料管理・督促": (
        "賃料・督促は手続の順序と法的効果の対応が重要です。"
        "誤答肢がどの段階・要件を誤っているかを確認してください。"
    ),
    "関連法令": (
        "関連法令は本試験の主たる論点と位置づけの違いが問われます。"
        "根拠法令名と趣旨をセットで覚えてください。"
    ),
    "政策課題・社会情勢": (
        "政策・社会情勢は制度の目的と論点の組み合わせが出題されます。"
        "公式の考え方・用語の定義を確認したうえで復習してください。"
    ),
}

DEFAULT_STUDY_HINT = (
    "この問題で間違えた場合は、設問文の求め方（「正しいもの」「誤っているもの」「最も適切でないもの」）を"
    "最初に線引きしてください。正答・誤答それぞれについて、用語の定義と制度の前提を用語解説で確認し、"
    "復習リストや実践演習・一問一答と組み合わせて、同分野の過去問を解き直すと定着しやすくなります。"
)


def build_study_hint(page: dict, row: dict) -> str:
    point = norm(row.get("explanation_point"))
    if point:
        return point
    category = norm(page.get("category") or "")
    hint = CATEGORY_STUDY_HINTS.get(category) or DEFAULT_STUDY_HINT
    tags = page.get("tags") or []
    if tags and "復習" in tags and "復習" not in hint:
        hint += " 復習機能・学習日記と連携し、週次で振り返ると弱点の再発を防げます。"
    return hint


_CHOICE_ANSWER_PREFIX_RE = re.compile(r"^正解は\s*\d+\s*です[。.]?\s*", re.IGNORECASE)
_ANSWER_ONLY_SUMMARY_RE = re.compile(
    r"^正(?:答|解)は\s*[（(]?\d+[）)]?\s*です[。.]?\s*$"
)


def strip_choice_answer_prefix(text: str) -> str:
    """CSV 解説先頭の「正解は1です。」等を除去（正答欄と重複しないように）。"""
    return _CHOICE_ANSWER_PREFIX_RE.sub("", norm(text) or "").strip()


def is_answer_only_summary(text: str) -> bool:
    t = norm(text)
    if not t:
        return True
    return bool(_ANSWER_ONLY_SUMMARY_RE.match(t))


def split_legacy_explanation(exp: str) -> tuple[str, str]:
    body = strip_choice_answer_prefix(exp) or norm(exp) or "（解説は未入力です。）"
    return "", body


_WRONG_CHOICE_OPENING_RE = re.compile(
    r"^この肢「[^」]*」は、設問の求め方（正しいもの／誤っているもの／最も適切でないもの）と照らすと正答になりません。[。\s]*",
)
_WRONG_CHOICE_KEY_POINT_RE = re.compile(r"^正解の要点:\s*")
_WRONG_CHOICE_FOOTER_RE = re.compile(
    r"\s*この観点と両立しない部分がこの肢にないか、用語解説で定義を確認しながら見直してください。[。\s]*$"
)
_FP_WRONG_NOTE_BOILER_RE = re.compile(
    r"この肢は「[^」]*」と述べていますが、[^。]+。?"
    r"|正答（\d+）「[^」]*」は、制度・手続・学習法[^。]+。?"
    r"|正答の論点と照らすと、この肢は[^。]+。?"
    r"|主語・客体・数字・期限[^。]+。?"
    r"|制度・数値・手続の観点で[^。]+正答肢としては成立しません[^。]*。?"
    r"|用語解説で関連制度を確認し、同分野の過去問・実践演習で解き直すと定着しやすくなります[。.]?"
)


def polish_wrong_choice_note(note: str, *, choice_text: str, category: str) -> str:
    """他の選択肢の解説から正答欄・正解の理由と重複する定型文を除去する。"""
    n = norm(note)
    if not n:
        return n
    n = _WRONG_CHOICE_OPENING_RE.sub("", n)
    n = _WRONG_CHOICE_KEY_POINT_RE.sub("", n)
    n = strip_choice_answer_prefix(n)
    n = _WRONG_CHOICE_FOOTER_RE.sub("", n)
    n = _FP_WRONG_NOTE_BOILER_RE.sub("", n)
    n = re.sub(r"\s{2,}", " ", n).strip()
    if not n:
        opt = norm(choice_text)
        cat = category or "本分野"
        return f"{cat}の論点では本問の正答肢ではありません（「{_snippet(opt, 32)}」）。"
    return n


def _wrong_note_dedupe_key(note: str) -> str:
    n = re.sub(r"「[^」]{20,}」", "「…」", norm(note))
    n = re.sub(r"（\d+）", "", n)
    return _normalize_for_compare(n)


def _is_generic_wrong_note(note: str) -> bool:
    n = norm(note)
    if not n or len(n) < 40:
        return True
    generic_markers = (
        r"この肢は「",
        r"正しい記述ではありません",
        r"制度・手続・学習法のいずれか",
        r"正答の論点と照らすと",
        r"正答肢としては成立しません",
        r"制度・数値・手続の観点で",
        r"用語解説で関連制度を確認し",
        r"論点では正答（\d+）と内容が一致しません",
        r"正解の理由と表・数値の対応を照らしてください",
    )
    return any(re.search(p, n) for p in generic_markers)


def _consolidated_wrong_choices_note(
    page: dict,
    row: dict,
    wrong_nums: list[int],
    wrong_opts: list[str] | None = None,
) -> str:
    correct = page.get("correct")
    label = "、".join(str(n) for n in wrong_nums)
    correct_body = strip_choice_answer_prefix(
        norm(row.get("explanation_correct")) or norm(row.get("explanation")) or ""
    )
    cor_idx = _correct_choice_index(correct)
    opts = page.get("opts") or []
    correct_text = opts[cor_idx - 1] if cor_idx and 1 <= cor_idx <= len(opts) else ""
    if wrong_opts and correct_text and all(_extract_digits(o) for o in wrong_opts):
        wrong_labels = "・".join(f"「{norm(o)}」" for o in wrong_opts)
        numeric = _numeric_diff_note(wrong_opts[0], correct_text, correct_body)
        if numeric:
            return numeric.replace(
                f"「{norm(wrong_opts[0])}」",
                wrong_labels,
                1,
            )
    hint = _snippet(correct_body, 80)
    if hint:
        return f"（{label}）はいずれも正答（{correct}）とは異なります。{hint}"
    return (
        f"（{label}）はいずれも正答（{correct}）とは異なります。"
        "正解の理由と各肢の差分を照らして確認してください。"
    )


def collapse_wrong_choice_items(
    page: dict, row: dict, items: list[tuple[int, str, str]]
) -> list[tuple[str, str, str]]:
    """同一の汎用解説をまとめ、テンプレの連打を防ぐ。"""
    if not items:
        return []
    groups: list[dict] = []
    index: dict[str, int] = {}
    for num, opt, note in items:
        key = _wrong_note_dedupe_key(note)
        if key not in index:
            index[key] = len(groups)
            groups.append({"nums": [num], "opts": [opt], "note": note})
        else:
            g = groups[index[key]]
            g["nums"].append(num)
            g["opts"].append(opt)
    collapsed: list[tuple[str, str, str]] = []
    for group in groups:
        nums = sorted(group["nums"])
        label = "、".join(str(n) for n in nums)
        note = group["note"]
        if len(nums) > 1 and _is_generic_wrong_note(note):
            note = _consolidated_wrong_choices_note(
                page, row, nums, wrong_opts=group["opts"]
            )
            opt_head = ""
        elif len(nums) == 1:
            opt_head = group["opts"][0]
        else:
            opt_head = "／".join(_snippet(o, 28) for o in group["opts"])
        collapsed.append((label, note, opt_head))
    return collapsed


def build_choice_commentary(page: dict, row: dict) -> list[tuple[int, str, str]]:
    parsed = parse_explanation_choices(norm(row.get("explanation_choices")))
    correct = page.get("correct")
    items: list[tuple[int, str, str]] = []
    for i, opt in enumerate(page["opts"], start=1):
        if page.get("is_invalidated") or correct is None:
            continue
        if i == correct:
            continue
        note = resolve_wrong_choice_note(
            page, i, opt, row, csv_note=parsed.get(i) or ""
        )
        note = polish_wrong_choice_note(
            note,
            choice_text=opt,
            category=norm(page.get("category") or ""),
        )
        items.append((i, opt, note))
    return items


def build_explanation_html(page: dict, row: dict) -> str:
    base = norm(row.get("explanation")) or "（解説は未入力です。）"
    if page.get("is_invalidated") or page.get("correct") is None:
        return f'<div class="q-exp"><p>{text_to_html(base)}</p></div>'

    summary = norm(row.get("explanation_summary"))
    correct_body = norm(row.get("explanation_correct"))

    if not summary and not correct_body:
        leg_summary, leg_body = split_legacy_explanation(base)
        summary = summary or leg_summary
        correct_body = correct_body or leg_body

    summary = strip_choice_answer_prefix(summary) if summary else ""
    correct_body = strip_choice_answer_prefix(correct_body) if correct_body else ""

    parts: list[str] = ['<div class="q-exp">']
    if summary and not is_answer_only_summary(summary):
        parts.append(f'<p class="q-exp-lead">{text_to_html(summary)}</p>')

    correct = page.get("correct")
    if correct and not page.get("is_invalidated"):
        cor_idx = _correct_choice_index(correct)
        opts = page.get("opts") or []
        opt_text = opts[cor_idx - 1] if cor_idx and 1 <= cor_idx <= len(opts) else ""
        parts.append(
            '<section class="q-exp-section" aria-labelledby="q-exp-correct-h">'
            '<h3 id="q-exp-correct-h" class="q-exp-h3">正解の理由</h3>'
        )
        if correct_body:
            parts.append(f"<p>{text_to_html(correct_body)}</p>")
        if opt_text:
            parts.append(
                f'<p class="q-exp-correct-opt"><strong>（{correct}）</strong> '
                f"{html.escape(opt_text)}</p>"
            )
        parts.append("</section>")

        wrong_items = collapse_wrong_choice_items(
            page, row, build_choice_commentary(page, row)
        )
        if wrong_items:
            lis = "".join(
                f'<li class="q-exp-choice-item">'
                f'<p class="q-exp-choice-head">'
                f'<span class="q-exp-choice-num">（{nums}）</span>'
                + (
                    f' <span class="q-exp-choice-text">{html.escape(opt_head)}</span>'
                    if opt_head
                    else ""
                )
                + "</p>"
                f'<p class="q-exp-choice-note">{text_to_html(note)}</p></li>'
                for nums, note, opt_head in wrong_items
            )
            parts.append(
                '<section class="q-exp-section" aria-labelledby="q-exp-wrong-h">'
                '<h3 id="q-exp-wrong-h" class="q-exp-h3">他の選択肢</h3>'
                f'<ul class="q-exp-choice-list">{lis}</ul></section>'
            )

    parts.append("</div>")
    return "\n    ".join(parts)


def _ichimon_answer_is_true(page: dict) -> bool:
    return bool(page.get("correct_answer"))


_ICHIMON_ANSWER_PREFIX_RE = re.compile(
    r"^正解は\s*[○×]\s*です[。.]?\s*",
    re.IGNORECASE,
)


def strip_ichimon_answer_prefix(text: str) -> str:
    """CSV 解説先頭の「正解は○です。」等を除去（正答欄と重複しないように）。"""
    return _ICHIMON_ANSWER_PREFIX_RE.sub("", norm(text) or "").strip()


def split_legacy_ichimon_explanation(
    exp: str, *, is_true: bool, statement: str
) -> tuple[str, str]:
    """1 段落の explanation から正解理由本文を取り出す（要約は正答欄に任せる）。"""
    _ = is_true
    _ = statement
    body = strip_ichimon_answer_prefix(exp) or norm(exp) or "（解説は未入力です。）"
    return "", body


def infer_ichimon_opposite_note(page: dict, row: dict) -> str:
    """○/× のもう一方を選びそうになる理由（CSV 未記入時）。"""
    statement = norm(page.get("statement") or row.get("question"))
    is_true = _ichimon_answer_is_true(page)
    category = norm(page.get("category") or "")
    wrong = "×" if is_true else "○"
    parts: list[str] = []

    if is_true:
        parts.append(
            f"設問文は正しい記述ですが、{wrong} を選ぶ場合は"
            "「受験情報は一度調べれば足りる」「一般論として正しそうだから○/×はどちらでもよい」"
            "と読み替えている可能性があります。"
            "一問一答では、**必要・不要・毎年・常に・しなくてもよい** などの限定語が"
            "試験制度・学習法の正誤を決めるキーワードになります。"
        )
    else:
        parts.append(
            f"設問文は誤った記述ですが、{wrong} を選ぶ場合は"
            "「学習の一般論として正しそう」「自分の経験では合っている」"
            "と、設問の一文だけを見ずに判断している可能性があります。"
            "「最も適切でない」「誤っている」系の過去問と同様、"
            "一見もっともらしい記述こそ × の対象になりやすい点に注意してください。"
        )

    if "復習" in statement or "見直" in statement or "定着" in statement:
        parts.append(
            "誤答の記録・復習リスト・間隔を空けた解き直しは、弱点を可視化する基本です。"
            "「しなくても定着する」「二度と見ない」は学習科学の観点でも不適切です。"
        )
    elif re.search(r"公式|受験案内|出題範囲|毎年", statement):
        parts.append(
            "制度・日程・範囲の正誤は実施団体の公式発表が基準です。"
            "SNS や前年の記憶だけで ×/○ を決めないよう、公式ページを開く習慣をつけてください。"
        )
    elif re.search(r"数字|期限|表|整理", statement):
        parts.append(
            "数値・期限は暗記だけでは混同しやすいです。"
            "比較表で整理したうえで一問一答するほうが、本番の選択肢問題でも役立ちます。"
        )

    if category:
        parts.append(
            f"分野「{category}」では、用語の定義と制度の前提を用語解説で確認し、"
            "同分野の過去問・実践演習へつなげて解き直すと定着しやすくなります。"
        )

    return "\n\n".join(parts)


def build_ichimon_explanation_html(page: dict, row: dict) -> str:
    """一問一答 — 過去問と同型（要約・正解の理由・もう一方の記号・学習のヒント）。"""
    statement = norm(page.get("statement") or row.get("question"))
    is_true = _ichimon_answer_is_true(page)
    wrong = "×" if is_true else "○"

    summary = norm(row.get("explanation_summary"))
    correct_body = norm(row.get("explanation_correct"))
    opposite = norm(row.get("explanation_opposite"))
    base = norm(row.get("explanation")) or "（解説は未入力です。）"

    if not summary and not correct_body:
        leg_summary, leg_body = split_legacy_ichimon_explanation(
            base, is_true=is_true, statement=statement
        )
        summary = summary or leg_summary
        correct_body = correct_body or leg_body

    summary = strip_ichimon_answer_prefix(summary) if summary else ""
    correct_body = strip_ichimon_answer_prefix(correct_body) if correct_body else ""

    if not opposite:
        opposite = infer_ichimon_opposite_note(page, row)

    parts: list[str] = ['<div class="q-exp">']
    if summary and not is_answer_only_summary(summary):
        parts.append(f'<p class="q-exp-lead">{text_to_html(summary)}</p>')

    parts.append(
        '<section class="q-exp-section" aria-labelledby="q-exp-correct-h">'
        '<h3 id="q-exp-correct-h" class="q-exp-h3">正解の理由</h3>'
    )
    if correct_body:
        parts.append(f"<p>{text_to_html(correct_body)}</p>")
    if statement:
        parts.append(
            f'<blockquote class="q-exp-quote">{text_to_html(statement)}</blockquote>'
        )
    parts.append("</section>")

    parts.append(
        '<section class="q-exp-section" aria-labelledby="q-exp-opposite-h">'
        '<h3 id="q-exp-opposite-h" class="q-exp-h3">'
        f"{html.escape(wrong)} を選びやすい考え方</h3>"
        f"<p>{text_to_html(opposite)}</p></section>"
    )

    parts.append("</div>")
    return "\n    ".join(parts)
