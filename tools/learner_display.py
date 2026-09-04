#!/usr/bin/env python3
"""Learner-facing exam display overlay (TTwin pack time).

Chemistry already ships this shape (extract + exam.v1): source question
numbers are not in the stem, A–D live once in `options` (and as a table when
the paper printed a matrix), PDF `(cid:N)` ticks are ✓/✗.

Physics / biology CMS stems still carry page furniture. This module derives
display text. It does not rewrite frozen exam.v1 or CMS JSON.

Evidence for the q-number gate: awm `stage1_cleanup.py` — only strip a
leading number when it matches the authoritative printed number (`:qN` in
the uid). `10 g of ammonium nitrate` stays.
"""
from __future__ import annotations

import re
from typing import Any

ELEMENTS = {
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si",
    "P", "S", "Cl", "Ar", "K", "Ca", "Fe", "Cu", "Zn", "Br", "Ag", "I", "Ba", "U",
    "Pb", "Au", "Sn", "Ni", "Co", "Mn", "Cr", "Ti", "Sr", "Cs", "Ra", "Th", "Pu",
}
UID_Q = re.compile(r":q(\d+)$", re.I)
UID_QP = re.compile(r"_qp_(\d+)", re.I)
LEAD_NUM = re.compile(r"^\s*(\d{1,2})(?:[.)])?(?:\s+|\s*$)", re.M)
LEAD_NUM_LINE = re.compile(r"^\s*(\d{1,2})\s*\n")
LETTER = re.compile(r"^([A-D])(?:[.)]|\s)\s*(.*)$")
INLINE_ABCD = re.compile(
    r"(?:^|\n)\s*A\s+.+\s+B\s+.+\s+C\s+.+\s+D\s+\S[\s\S]*$",
    re.I,
)
CID = re.compile(r"\(cid:(\d+)\)", re.I)
LEGEND_PAIR = re.compile(r"\(cid:(\d+)\)\s*=\s*([^\n]+)", re.I)
TURN_OVER = re.compile(r"(?im)^\s*\[?\s*Turn over\s*\]?\s*$")
UCLES = re.compile(r"(?im)^\s*©\s*UCLES[^\n]*$")
PAPER_CODE = re.compile(r"(?im)^\s*\d{4}/\d{2}/[A-Z]/[A-Z]/\d{2}\s*$")
BLANK_PAGE = re.compile(r"(?im)^\s*BLANK\s*PAGE\s*$")
KEY_WORD = re.compile(r"\bkey\b", re.I)
DENOM_LINE = re.compile(r"^[\d\s]{1,12}$")
DEGREE_CID = re.compile(r"(?<=\d)\s*\(cid:1\)")
FRAC = {"1/2": "½", "1/3": "⅓", "2/3": "⅔", "1/4": "¼", "3/4": "¾"}

TICK_CIDS = {"1", "22"}
CROSS_CIDS = {"2", "26"}
YESISH = re.compile(
    r"\b(tick|yes|true|affected|suitable|present|continues|has this|can be)\b",
    re.I,
)
NOISH = re.compile(
    r"\b(cross|no|false|not affected|not suitable|absent|stops|does not|cannot)\b",
    re.I,
)


def qnum_from_uid(uid: str) -> int | None:
    m = UID_Q.search(uid or "")
    return int(m.group(1)) if m else None


def paper_from_uid(uid: str) -> int | None:
    m = UID_QP.search(uid or "")
    return int(m.group(1)) if m else None


def _looks_like_nuclide(after: str) -> bool:
    t = (after or "").lstrip()
    if not t:
        return False
    tok = t.split()[0]
    if tok in ELEMENTS:
        return True
    # smashed "C l" / "A l" from ³⁷Cl / ²⁷Al
    if re.match(r"^[A-Z]\s+[a-z]\b", t):
        return True
    return False


def strip_leading_question_number(stem: str, uid: str) -> str:
    n = qnum_from_uid(uid)
    if n is None or not stem:
        return stem
    m = LEAD_NUM.match(stem)
    if m and int(m.group(1)) == n:
        after = stem[m.end() :]
        if not _looks_like_nuclide(after):
            return after
    m = LEAD_NUM_LINE.match(stem)
    if m and int(m.group(1)) == n:
        after = stem[m.end() :]
        if not _looks_like_nuclide(after):
            return after
    return stem


def strip_page_furniture(stem: str) -> str:
    t = TURN_OVER.sub("", stem or "")
    t = UCLES.sub("", t)
    t = PAPER_CODE.sub("", t)
    t = BLANK_PAGE.sub("", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def parse_legend(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in LEGEND_PAIR.finditer(text or ""):
        out[m.group(1)] = m.group(2).strip()
    return out


def cid_to_mark(cid: str, legend: dict[str, str]) -> str:
    meaning = legend.get(cid, "")
    # "not affected" contains "affected" — deny-list first.
    if meaning and NOISH.search(meaning):
        return "✗"
    if meaning and YESISH.search(meaning):
        return "✓"
    if cid in TICK_CIDS:
        return "✓"
    if cid in CROSS_CIDS:
        return "✗"
    return f"(cid:{cid})"


def peel_legend_suffix(rest: str) -> tuple[str, dict[str, str]]:
    legend = parse_legend(rest)
    cleaned = LEGEND_PAIR.sub("", rest)
    cleaned = KEY_WORD.sub("", cleaned)
    cleaned = re.sub(r"\s+=\s+[^\n]*$", "", cleaned).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned, legend


def option_cells(rest: str, legend: dict[str, str]) -> list[str] | None:
    body, extra = peel_legend_suffix(rest)
    legend = {**legend, **extra}
    cids = CID.findall(body)
    if cids:
        return [cid_to_mark(c, legend) for c in cids]
    body = CID.sub("", body)
    body = re.sub(r"\s{2,}", " ", body).strip()
    if not body:
        return None
    return None


def is_prose_option_line(rest: str) -> bool:
    words = rest.split()
    if len(words) >= 14:
        return True
    if rest.endswith(".") and re.search(r"\b(is|are|has|have|was|were|shows|shown)\b", rest, re.I):
        return True
    if len(words) >= 8 and rest.endswith("."):
        return True
    return False


def rest_matches_option(rest: str, opt: str) -> bool:
    r, _ = peel_legend_suffix(rest or "")
    o, _ = peel_legend_suffix(opt or "")
    if CID.search(r) and (CID.search(o) or "✓" in o or "✗" in o or not o):
        return True
    if not o:
        return not is_prose_option_line(r)
    if o in r or r in o:
        return True
    r0, o0 = r.split()[:3], o.split()[:3]
    return bool(r0 and r0 == o0)


def find_letter_lines(lines: list[str], options: dict[str, str] | None = None) -> dict[str, int] | None:
    found: dict[str, int] = {}
    options = options or {}
    for i, raw in enumerate(lines):
        m = LETTER.match(raw.strip())
        if not m:
            continue
        let, rest = m.group(1), m.group(2).strip()
        if let in found:
            continue
        if is_prose_option_line(rest):
            continue
        # A line that already contains B C D is the inline form, not a matrix row.
        if let == "A" and re.search(r"\sB\s.+\sC\s.+\sD\s", rest):
            continue
        opt = str(options.get(let) or "")
        if opt and not rest_matches_option(rest, opt):
            continue
        found[let] = i
        if len(found) == 4:
            break
    if set(found) != set("ABCD"):
        return None
    if not (found["A"] < found["B"] < found["C"] < found["D"]):
        return None
    return found


def header_start(lines: list[str], a_idx: int) -> int:
    start = a_idx
    i = a_idx - 1
    taken = 0
    while i >= 0 and taken < 4:
        s = lines[i].strip()
        if not s:
            i -= 1
            continue
        if s.endswith("?"):
            break
        if len(s) > 70:
            break
        words = s.split()
        if len(words) >= 12:
            break
        start = i
        taken += 1
        i -= 1
    return start


def extend_block_end(lines: list[str], d_idx: int, uid: str) -> int:
    end = d_idx
    paper = paper_from_uid(uid)
    j = d_idx + 1
    while j < len(lines):
        s = lines[j].strip()
        if not s:
            end = j
            j += 1
            continue
        if LEGEND_PAIR.search(s) or s.lower() in {"key"}:
            end = j
            j += 1
            continue
        if DENOM_LINE.match(s):
            n = int(re.sub(r"\s+", "", s) or "0")
            if paper is not None and n == paper:
                end = j
                j += 1
                continue
            if len(s) <= 2:
                end = j
                j += 1
                continue
        break
    return end


def merge_denominator_line(option_rest: str, denom: str) -> str:
    dens = denom.split()
    if not dens:
        return option_rest
    toks = option_rest.split()
    di = 0
    out: list[str] = []
    i = 0
    while i < len(toks):
        tok = toks[i]
        nxt = toks[i + 1] if i + 1 < len(toks) else ""
        if tok == "1" and di < len(dens) and nxt and nxt.isalpha() and len(nxt) <= 2:
            frac = f"1/{dens[di]}"
            out.append(FRAC.get(frac, f"1/{dens[di]}") + " " + nxt)
            di += 1
            i += 2
            continue
        out.append(tok)
        i += 1
    return " ".join(out)


def repair_stacked_fractions(lines: list[str], found: dict[str, int], options: dict[str, str]) -> dict[str, str]:
    out = dict(options)
    order = ["A", "B", "C", "D"]
    for n, let in enumerate(order):
        i = found[let]
        m = LETTER.match(lines[i].strip())
        if not m:
            continue
        rest = m.group(2).strip()
        next_i = found[order[n + 1]] if n < 3 else len(lines)
        j = i + 1
        while j < next_i and not lines[j].strip():
            j += 1
        if j < next_i and DENOM_LINE.match(lines[j].strip()):
            dens = lines[j].strip()
            if not (len(dens) <= 3 or " " in dens):
                j = next_i
            else:
                rest = merge_denominator_line(rest, dens)
        rest, _ = peel_legend_suffix(rest)
        if rest:
            out[let] = rest
    return out


def format_cells(headers: list[str], cells: list[str]) -> str:
    named = [h for h in headers if h]
    if named and len(headers) == len(cells) and all(headers):
        return "; ".join(f"{h} {c}" for h, c in zip(headers, cells))
    return " / ".join(cells)


def split_numeric_cells(text: str) -> list[str] | None:
    parts = text.split()
    if len(parts) >= 2 and all(re.fullmatch(r"-?\d+(?:\.\d+)?", p) for p in parts[:4]):
        return parts
    return None


def split_qty_cells(text: str) -> list[str] | None:
    toks = (text or "").split()
    cells: list[str] = []
    i = 0
    while i < len(toks):
        head = toks[i][:1]
        if (
            i + 1 < len(toks)
            and (head.isdigit() or head in "½⅓⅔¼¾")
            and len(toks[i + 1]) <= 2
            and toks[i + 1].isalpha()
        ):
            cells.append(toks[i] + " " + toks[i + 1])
            i += 2
            continue
        return None
    return cells if len(cells) >= 2 else None


def tidy_option_text(text: str, legend: dict[str, str]) -> str:
    t, extra = peel_legend_suffix(text or "")
    legend = {**legend, **extra}
    t = DEGREE_CID.sub("°", t)

    def one(m: re.Match) -> str:
        return cid_to_mark(m.group(1), legend)

    t = CID.sub(one, t)
    t = re.sub(r"\s{2,}", " ", t).strip()
    return t


def strip_trailing_page_token(options: dict[str, str], uid: str) -> dict[str, str]:
    paper = paper_from_uid(uid)
    out = dict(options)
    lengths = []
    for k in "ABC":
        lengths.append(len((out.get(k) or "").split()))
    d = (out.get("D") or "").split()
    if not d:
        return out
    last = d[-1]
    modal = max(set(lengths), key=lengths.count) if lengths else 0
    if last.isdigit() and len(last) <= 2 and len(d) == modal + 1:
        if paper is None or int(last) == paper or int(last) != int(d[0]) if d[0].isdigit() else True:
            out["D"] = " ".join(d[:-1])
    return out


def options_are_parse_debris(options: dict[str, str]) -> bool:
    vals = [str(options.get(k) or "").strip() for k in "ABCD"]
    if any(len(v) < 2 for v in vals):
        return True
    if any(v in {",", "and", "&", "A", "B", "C", "D"} for v in vals):
        return True
    return False


_SUP = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")
SCI_TIMES = re.compile(r"(×\s*10)\s+([–−-]?)(\d{1,2})\b")
SCI_NEG10 = re.compile(r"\b(10)\s+([–−-])(\d{1,2})\b")
UNIT_EXP = re.compile(
    r"\b(m s|mol dm|ms|cm|mm|µm|μm|nm|kg|Hz|Ω|Ω)\s+([–−-])(\d)\b"
)
DUMP_LINE = re.compile(
    r"^(displacement|distance|time|velocity|speed|extension|force|voltage|"
    r"current|temperature|pressure|volume|field|graph|energy|"
    r"wave [A-ZXYRS]|0(?:\s+time)?)$",
    re.I,
)
UNIT_HEADER = re.compile(
    r"([A-Za-z][A-Za-z0-9 ]*?)\s*/\s*([A-Za-zµμ°0-9²³⁻]+(?:\s*[A-Za-zµμ°⁻0-9]+)*?)"
    r"(?=(?:\s+[A-Za-z][A-Za-z0-9 ]*\s*/)|$)"
)


def _super_exp(sign: str, digits: str) -> str:
    pref = "⁻" if sign and sign in "-–−" else ""
    return pref + digits.translate(_SUP)


def repair_scientific_notation(text: str) -> str:
    """Chemistry already ships 7.00 × 10⁻³; physics CMS still has '× 10 7' and 'm s –1'."""
    if not text:
        return text

    def times(m: re.Match) -> str:
        return m.group(1) + _super_exp(m.group(2), m.group(3))

    t = SCI_TIMES.sub(times, text)
    t = SCI_NEG10.sub(lambda m: m.group(1) + _super_exp(m.group(2), m.group(3)), t)
    t = UNIT_EXP.sub(lambda m: m.group(1) + _super_exp(m.group(2), m.group(3)), t)
    return t


def strip_figure_dump_runs(stem: str) -> str:
    """Drop axis/wave labels that extraction dumped as their own lines between sentences."""
    lines = (stem or "").split("\n")
    dump = [bool(ln.strip()) and bool(DUMP_LINE.match(ln.strip())) for ln in lines]
    drop = [False] * len(lines)
    i = 0
    while i < len(lines):
        if dump[i]:
            j = i
            while j < len(lines) and dump[j]:
                j += 1
            if j - i >= 2:
                for k in range(i, j):
                    drop[k] = True
            i = j
        else:
            i += 1
    kept = [ln for ln, gone in zip(lines, drop) if not gone]
    return "\n".join(kept)


def join_wrapped_prose(stem: str) -> str:
    """Join PDF column-wraps: 'It emits light of\\nfrequency 4.57…'."""
    out: list[str] = []
    for raw in (stem or "").split("\n"):
        s = raw.strip()
        if not out:
            out.append(s)
            continue
        prev = out[-1]
        if (
            prev
            and not re.search(r"[.?!:]$", prev)
            and s
            and s[0].islower()
            and len(prev) >= 28
            and not DUMP_LINE.match(s)
        ):
            out[-1] = prev + " " + s
        else:
            out.append(s)
    # collapse extra blanks
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def parse_column_headers(header_lines: list[str], ncell: int) -> list[str]:
    last = header_lines[-1] if header_lines else ""
    parts = UNIT_HEADER.findall(last)
    if len(parts) == ncell:
        return [f"{a.strip()} / {b.strip()}" for a, b in parts]
    toks = [t for t in last.split() if t != "/"]
    if len(toks) == ncell and all(len(t) <= 24 for t in toks):
        return toks
    return [""] * ncell


def find_inline_span(stem: str, options: dict[str, str]) -> tuple[int, int] | None:
    if options_are_parse_debris(options):
        return None
    vals = [str(options[k]).strip() for k in "ABCD"]
    pat = (
        r"(?:^|\n)[ \t]*A\s+"
        + re.escape(vals[0])
        + r"\s+B\s+"
        + re.escape(vals[1])
        + r"\s+C\s+"
        + re.escape(vals[2])
        + r"\s+D\s+"
        + re.escape(vals[3])
        + r"[ \t]*$"
    )
    m = re.search(pat, stem, re.M)
    if not m:
        return None
    return m.start(), m.end()


def sanitize_item(uid: str, rec: dict[str, Any]) -> dict[str, Any]:
    """Return a new record with learner-facing stem/options/tables."""
    out = dict(rec)
    stem = str(out.get("stem") or out.get("stem_lead") or "")
    options = dict(out.get("options") or {})
    tables = list(out.get("tables") or [])

    original = stem
    stem = strip_leading_question_number(stem, uid)
    stem = strip_page_furniture(stem)
    stem = DEGREE_CID.sub("°", stem)
    stem = strip_figure_dump_runs(stem)
    stem = join_wrapped_prose(stem)
    after_qnum = stem

    if out.get("options_are_figure") or options_are_parse_debris(options):
        stem = repair_scientific_notation(stem)
        out["stem"] = stem
        out["stem_lead"] = stem
        out["options"] = {k: repair_scientific_notation(str(v)) for k, v in options.items()}
        return out

    legend = parse_legend(stem + "\n" + "\n".join(str(v) for v in options.values()))
    for k, v in list(options.items()):
        options[k] = tidy_option_text(str(v), legend)
    options = strip_trailing_page_token(options, uid)

    lines = stem.splitlines()
    found = find_letter_lines(lines, options)
    if found:
        options = repair_stacked_fractions(lines, found, options)
        for k, v in list(options.items()):
            options[k] = tidy_option_text(str(v), legend)

        a, d = found["A"], found["D"]
        hs = header_start(lines, a)
        end = extend_block_end(lines, d, uid)
        header_lines = [ln.strip() for ln in lines[hs:a] if ln.strip()]
        headers: list[str] = []

        row_cells: list[list[str]] = []
        for let in "ABCD":
            raw = lines[found[let]].strip()
            m = LETTER.match(raw)
            rest = m.group(2) if m else ""
            cells = option_cells(rest, legend)
            if cells is None:
                repaired = options.get(let) or rest
                cells = split_numeric_cells(repaired) or split_qty_cells(repaired)
            if cells is None:
                row_cells = []
                break
            row_cells.append(cells)

        if row_cells and len({len(r) for r in row_cells}) == 1:
            ncell = len(row_cells[0])
            if ncell >= 2:
                headers = parse_column_headers(header_lines, ncell)
                already = any(
                    (t.get("row_labels") or [])[:4] == list("ABCD") for t in tables if isinstance(t, dict)
                )
                if not already:
                    tables.append(
                        {
                            "headers": headers,
                            "rows": row_cells,
                            "row_labels": list("ABCD"),
                            "caption": "",
                            "is_option_table": True,
                        }
                    )
                for i, let in enumerate("ABCD"):
                    options[let] = format_cells(headers, row_cells[i])

        used_headers = bool(row_cells and headers and all(headers))
        keep = lines[:hs] if used_headers else lines[:a]
        stem = "\n".join(keep).strip()
        stem = strip_page_furniture(stem)
    else:
        span = find_inline_span(stem, options)
        if span:
            stem = (stem[: span[0]] + stem[span[1] :]).strip()

    # leftover lone page number
    paper = paper_from_uid(uid)
    ls = stem.splitlines()
    if ls and re.fullmatch(r"\d{1,2}", ls[-1].strip()):
        n = int(ls[-1].strip())
        if paper is not None and n == paper:
            stem = "\n".join(ls[:-1]).strip()

    if not (stem or "").strip() and (after_qnum or original).strip():
        stem = after_qnum or original

    stem = repair_scientific_notation(stem)
    for k, v in list(options.items()):
        options[k] = repair_scientific_notation(str(v))

    out["stem"] = stem
    out["stem_lead"] = stem
    out["options"] = options
    if tables:
        out["tables"] = tables
    elif "tables" in out and not tables:
        out.pop("tables", None)
    return out


def _selftest() -> None:
    q22 = {
        "stem": (
            "22 The graph shows the variation with time of the displacement of two separate waves X and Y.\n"
            "Wave X has frequency f and amplitude A .\n"
            "What is the frequency and what is the amplitude of wave Y?\n"
            "frequency amplitude\n"
            "A 1 f 1 A\n"
            "2 2\n"
            "B 1 f 2 A\n"
            "2\n"
            "C 2 f 1 A\n"
            "2\n"
            "D 2 f 2 A\n"
            "12"
        ),
        "options": {"A": "1 f 1 A", "B": "1 f 2 A", "C": "2 f 1 A", "D": "2 f 2 A"},
    }
    r = sanitize_item("9702_m16_qp_12:q22", q22)
    assert not r["stem"].startswith("22 "), r["stem"][:40]
    assert "A 1 f" not in r["stem"], r["stem"]
    assert "½" in r["options"]["A"], r["options"]
    assert r["options"]["B"].count("½") >= 1, r["options"]

    q22_dump = {
        "stem": (
            "22 The graph shows the variation with time of the displacement of two separate waves X and Y.\n"
            "displacement\nwave Y\n0\n0 time\nwave X\n"
            "Wave X has frequency f and amplitude A .\n"
            "What is the frequency and what is the amplitude of wave Y?\n"
            "frequency amplitude\n"
            "A 1 f 1 A\n2 2\nB 1 f 2 A\n2\nC 2 f 1 A\n2\nD 2 f 2 A\n12"
        ),
        "options": {"A": "1 f 1 A", "B": "1 f 2 A", "C": "2 f 1 A", "D": "2 f 2 A"},
    }
    r = sanitize_item("9702_m16_qp_12:q22", q22_dump)
    assert "\nwave Y\n" not in "\n" + r["stem"] + "\n"
    assert "0 time" not in r["stem"]
    assert "Wave X has frequency" in r["stem"]
    assert r["stem"].count("\n") <= 3, r["stem"]

    q21 = {
        "stem": (
            "21 A distant star is receding from the Earth with a speed of 1.40 × 10 7 m s –1 . It emits light of\n"
            "frequency 4.57 × 10 14 Hz. The speed of light is 3.00 × 10 8 m s –1 .\n"
            "What will be the frequency of this light when detected on Earth?\n"
            "A 2.04 × 10 13 Hz\nB 4.37 × 10 14 Hz\nC 4.57 × 10 14 Hz\nD 4.79 × 10 14 Hz"
        ),
        "options": {
            "A": "2.04 × 10 13 Hz",
            "B": "4.37 × 10 14 Hz",
            "C": "4.57 × 10 14 Hz",
            "D": "4.79 × 10 14 Hz",
        },
    }
    r = sanitize_item("9702_m16_qp_12:q21", q21)
    assert "× 10⁷" in r["stem"], r["stem"]
    assert "m s⁻¹" in r["stem"], r["stem"]
    assert "× 10¹⁴" in r["stem"], r["stem"]
    assert "of\nfrequency" not in r["stem"]
    assert "× 10¹³" in r["options"]["A"], r["options"]

    q24 = {
        "stem": (
            "24 The diagram shows two waves R and S.\n"
            "displacement\nwave R\n0\n0 time\nwave S\n"
            "Wave R has an amplitude of 8 cm and a period of 30 ms.\n"
            "What are the amplitude and the period of wave S?\n"
            "amplitude / cm period / ms\n"
            "A 2 10\nB 2 90\nC 4 10\nD 4 90\n12"
        ),
        "options": {"A": "2 10", "B": "2 90", "C": "4 10", "D": "4 90"},
    }
    r = sanitize_item("9702_m17_qp_12:q24", q24)
    assert "\nwave R\n" not in "\n" + r["stem"] + "\n"
    assert "0 time" not in r["stem"]
    assert "amplitude / cm" not in r["stem"]
    tbl = r.get("tables") or []
    assert tbl and "amplitude" in " ".join(tbl[0].get("headers") or []), tbl

    q26 = {
        "stem": (
            "26 M and N are two electromagnetic waves.\n"
            "What could M and N be?\n"
            "M N\n"
            "A microwaves visible light\n"
            "B microwaves γ -rays\n"
            "C γ -rays microwaves\n"
            "D visible light microwaves"
        ),
        "options": {
            "A": "microwaves visible light",
            "B": "microwaves γ -rays",
            "C": "γ -rays microwaves",
            "D": "visible light microwaves",
        },
    }
    r = sanitize_item("9702_m17_qp_12:q26", q26)
    assert not r["stem"].startswith("26 "), r["stem"][:40]
    assert "A microwaves" not in r["stem"], r["stem"]
    assert "What could M and N be?" in r["stem"]

    chem = {
        "stem": "10 g of ammonium nitrate is added to water at 25 °C and the mixture stirred.",
        "options": {"A": "x", "B": "y", "C": "z", "D": "w"},
    }
    r = sanitize_item("0620_m19_qp_12:q11", chem)
    assert r["stem"].startswith("10 g"), r["stem"]

    nuclide = {
        "stem": "37 C l\nHow many neutrons are in a nucleus of the nuclide ?",
        "options": {"A": "17", "B": "20", "C": "37", "D": "54"},
    }
    r = sanitize_item("0625_s16_qp_11:q37", nuclide)
    assert r["stem"].startswith("37"), r["stem"]

    bio = {
        "stem": (
            "1 A student has drawn a cell structure as seen using a light microscope.\n"
            "What is the actual length of the cell structure?\n"
            "A 1 × 10 –1 µ m B 1 × 10 0 µ m C 1 × 10 1 µ m D 1 × 10 2 µ m"
        ),
        "options": {
            "A": "1 × 10 –1 µ m",
            "B": "1 × 10 0 µ m",
            "C": "1 × 10 1 µ m",
            "D": "1 × 10 2 µ m",
        },
    }
    r = sanitize_item("9700_m16_qp_12:q1", bio)
    assert r["stem"].startswith("A student"), r["stem"][:40]
    assert "A 1 ×" not in r["stem"], r["stem"]

    ticks = {
        "stem": (
            "10 Which levels of protein structure would be affected?\n"
            "secondary tertiary quaternary\n"
            "A (cid:1) (cid:1) (cid:2) key\n"
            "B (cid:1) (cid:2) (cid:1) (cid:1) = affected\n"
            "C (cid:2) (cid:1) (cid:1) (cid:2) = not affected\n"
            "D (cid:1) (cid:1) (cid:1)"
        ),
        "options": {
            "A": "(cid:1) (cid:1) (cid:2) key",
            "B": "(cid:1) (cid:2) (cid:1) (cid:1) = affected",
            "C": "(cid:2) (cid:1) (cid:1) (cid:2) = not affected",
            "D": "(cid:1) (cid:1) (cid:1)",
        },
    }
    r = sanitize_item("9700_m16_qp_12:q10", ticks)
    assert "(cid:" not in r["stem"] + str(r["options"])
    assert "✓" in r["options"]["A"]
    assert any(t.get("is_option_table") for t in r.get("tables") or [])

    q3 = {
        "stem": (
            "3 A velocity vector is shown.\n"
            "North\n75 m s –1\n30 (cid:1)\nEast\n"
            "What are the components of the velocity vector in the northerly and in the easterly directions?\n"
            "component of vector component of vector\n"
            "in northerly direction in easterly direction\n"
            "/ m s –1 / m s –1\n"
            "A 38 38\nB 38 65\nC 65 38\nD 65 65\n5"
        ),
        "options": {"A": "38 38", "B": "38 65", "C": "65 38", "D": "65 65 5"},
    }
    manometer = {
        "stem": (
            "12 A manometer is being used to measure the pressure of the gas inside a tank. A , B , C and D\n"
            "show the manometer at different times.\n"
            "At which time is the gas pressure inside the tank greatest?\n"
            "A B C D\ngas"
        ),
        "options": {"A": "B", "B": ",", "C": "and", "D": "gas"},
        "options_are_figure": True,
    }
    r = sanitize_item("0625_s06_qp_1:q12", manometer)
    assert "manometer" in r["stem"], r["stem"]

    r = sanitize_item("9702_m21_qp_12:q3", q3)
    assert r["stem"].startswith("A velocity"), r["stem"][:60]
    assert "What are the components" in r["stem"]
    assert r["options"]["A"] != "velocity vector is shown."
    assert "38" in r["options"]["A"]
    assert r["options"]["D"].strip() in {"38 65", "65 65", "65 65"} or r["options"]["D"].endswith("65")

    print("learner_display selftest ok")


if __name__ == "__main__":
    _selftest()
