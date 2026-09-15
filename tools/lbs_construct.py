#!/usr/bin/env python3
"""Construct learn-by-solve banks and Mx modify seeds for a keyed MCQ.

Follow-ups zoom onto the scientific contrast between the keyed option and
that wrong option (spectroscopy pattern), not onto mix-up taxonomy.
Pack-time overlay. Does not rewrite freeze exam.v1. mx_type is teacher-only.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from lbs_quality import is_stamp_lbs, lbs_relevant  # noqa: E402

MX = (
    "term_substitution",
    "condition_omission",
    "relationship_reversal",
    "scope_error",
    "surface_feature_capture",
    "mechanism_conflation",
    "operation_confusion",
)

LETTERS = ("A", "B", "C", "D")
THREE = re.compile(
    r"^(?:1\s*,\s*2\s*and\s*3|1,\s*2\s*and\s*3|1 and 2 only|1 and 3 only|2 and 3 only)\s*$",
    re.I,
)
NUMISH = re.compile(r"^[\s0-9.,×xX+\-eE^/%°μmkMGiga]+$")
TOK = re.compile(r"[a-z]{3,}")
REV = (
    ("increase", "decrease"),
    ("higher", "lower"),
    ("greater", "smaller"),
    ("more", "less"),
    ("positive", "negative"),
    ("exothermic", "endothermic"),
    ("oxid", "reduc"),
    ("acid", "alkali"),
    ("anode", "cathode"),
    ("left", "right"),
    ("gain", "loss"),
    ("absorb", "releas"),
    ("contract", "expand"),
    ("artery", "vein"),
    ("xylem", "phloem"),
    ("hot", "cold"),
    ("faster", "slower"),
)
INLINE_OPT = re.compile(r"(?:\(([A-D])\)|\[([A-D])\])\s*", re.I)
FORMULAISH = re.compile(
    r"(?:[A-Z][a-z]?\d|[A-Z][a-z]?\(|OH|NH4|SO4|CO2|HCl|Na2|Mg\(|Cl2|CuSO|H2O|NH₃|NH3)"
)
EQN = re.compile(r"→|->|⇌|<=+>")
SUB_SUP = str.maketrans("₀₁₂₃₄₅₆₇₈₉⁻⁺", "0123456789-+")

_ROOT = Path(__file__).resolve().parents[1]
_JEEBENCH = Path("/home/harik/awm_build/data/corpus_intelligence/awm_corpus/jeebench-dataset.json")
_JEE_BY_UID: dict[str, str] | None = None


def _overlay_records() -> dict[str, dict]:
    """Hand-authored + shard overlay. Constructor must not clobber these."""
    out: dict[str, dict] = {}
    paths = [
        _ROOT / "data" / "spectra" / "lbs.json",
        _ROOT / "data" / "overlay" / "lbs_gold.json",
    ]
    shard = _ROOT / "data" / "overlay" / "shards"
    if shard.is_dir():
        paths.extend(sorted(shard.glob("*.json")))
    for p in paths:
        if not p.is_file():
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for uid, rec in (doc.get("items") or {}).items():
            if isinstance(rec, dict) and rec.get("wrong"):
                out[str(uid)] = rec
    return out


_OVERLAY: dict[str, dict] | None = None


def overlay_records() -> dict[str, dict]:
    global _OVERLAY
    if _OVERLAY is None:
        _OVERLAY = _overlay_records()
    return _OVERLAY


def _preserve_uids() -> set[str]:
    return set(overlay_records())


PRESERVE_UIDS = _preserve_uids()


def clip(s: str, n: int = 110) -> str:
    t = re.sub(r"\s+", " ", (s or "").strip())
    if len(t) <= n:
        return t
    return t[: n - 1].rstrip() + "…"


def _letter_stem(letter: str, q: str) -> str:
    head = f"Option {letter}"
    if (q or "").startswith(head) or (q or "").startswith(f"Look at diagram {letter}"):
        return q
    return f"{head}. {q}"


def tokens(s: str) -> set[str]:
    return set(TOK.findall((s or "").lower()))


def looks_numeric(s: str) -> bool:
    t = (s or "").strip()
    if not t or not any(ch.isdigit() for ch in t):
        return False
    if NUMISH.match(t):
        return True
    # scientific / percent / unit-stripped numbers only — not formulae or genotypes
    if re.fullmatch(r"[\d.,+\-×xX/^eE\s%μµukmMGiga°−–]+", t):
        return True
    return False


def hinge(stem: str) -> str:
    s = re.sub(r"\s+", " ", (stem or "").strip())
    m = re.search(r"((?:What|Which|How|Why|Where|When|Calculate|Find)\b.{8,220}\??)", s, re.I)
    if m:
        return clip(m.group(1), 180)
    q = s.find("?")
    if q >= 0:
        return clip(s[max(0, q - 160) : q + 1], 180)
    return clip(s, 180)


def parse_inline_options(stem: str) -> tuple[str, dict[str, str]]:
    matches = list(INLINE_OPT.finditer(stem or ""))
    if len(matches) < 4:
        return stem or "", {}
    opts: dict[str, str] = {}
    for i, m in enumerate(matches[:4]):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(stem)
        letter = (m.group(1) or m.group(2) or "").upper()
        opts[letter] = re.sub(r"\s+", " ", stem[start:end]).strip()
    if any(not opts.get(L) for L in LETTERS):
        return stem or "", {}
    rest = (stem[: matches[0].start()]).strip()
    return rest, opts


def _jee_question(uid: str) -> str:
    """Pack-time lookup of the JEEBench source stem (options still inline)."""
    global _JEE_BY_UID
    if not uid.startswith("jeebench:srcjson:"):
        return ""
    if _JEE_BY_UID is None:
        _JEE_BY_UID = {}
        if _JEEBENCH.is_file():
            try:
                rows = json.loads(_JEEBENCH.read_text(encoding="utf-8"))
            except Exception:
                rows = []
            for rec in rows:
                if not isinstance(rec, dict):
                    continue
                q = (rec.get("question") or "").strip()
                if not q:
                    continue
                subj = rec.get("subject") or ""
                desc = rec.get("description") or ""
                idx = rec.get("index")
                slug = re.sub(r"[^a-z0-9]+", "_", desc.lower()).strip("_")
                _JEE_BY_UID[f"jeebench:srcjson:{subj}:{slug}:q{idx}"] = q
                if subj in {"math", "mathematics"}:
                    _JEE_BY_UID[f"jeebench:srcjson:math:{slug}:q{idx}"] = q
    return _JEE_BY_UID.get(uid) or ""


def option_from_table(item: dict, letter: str) -> str:
    for table in item.get("tables") or []:
        if not isinstance(table, dict) or not table.get("is_option_table"):
            continue
        labels = [str(x).strip().upper()[:1] for x in (table.get("row_labels") or [])]
        rows = table.get("rows") or []
        if letter in labels:
            i = labels.index(letter)
            cells = rows[i] if i < len(rows) else []
            return " ".join(str(c) for c in cells).strip()
    return ""


def lift_options(item: dict) -> bool:
    """If A–D live in the stem (olympiad) or a table, copy them into options."""
    opts = dict(item.get("options") or {})
    nonempty = [L for L in LETTERS if str(opts.get(L) or "").strip()]
    if len(nonempty) >= 2:
        return False
    stem = item.get("stem") or item.get("stem_lead") or ""
    rest, parsed = parse_inline_options(stem)
    if len(parsed) < 4:
        src = _jee_question(str(item.get("uid") or ""))
        if src:
            rest, parsed = parse_inline_options(src)
    if len(parsed) == 4:
        item["options"] = parsed
        item["stem"] = rest
        item["stem_lead"] = rest
        return True
    tabled = {L: option_from_table(item, L) for L in LETTERS}
    if sum(1 for v in tabled.values() if v) >= 2:
        item["options"] = {L: tabled[L] for L in LETTERS if tabled[L]}
        return True
    return False


def option_text(item: dict, letter: str) -> str:
    opts = item.get("options") or {}
    t = str(opts.get(letter) or "").strip()
    if t:
        return t
    return option_from_table(item, letter)


def option_letters(item: dict) -> list[str]:
    present = [L for L in LETTERS if option_text(item, L)]
    return present or list(LETTERS)


def clauses(text: str) -> list[str]:
    t = re.sub(r"\s+", " ", (text or "").strip())
    parts = re.split(r"\s*;\s*|\s+\|\s+|\s+/\s+|\s+→\s+|\s+->\s+", t)
    parts = [p.strip() for p in parts if p.strip()]
    return parts or [t]


def all_diffs(a: str, b: str) -> list[tuple[int, str, str]]:
    ca, cb = clauses(a), clauses(b)
    n = max(len(ca), len(cb))
    diffs: list[tuple[int, str, str]] = []
    for i in range(n):
        x = ca[i] if i < len(ca) else ""
        y = cb[i] if i < len(cb) else ""
        if x.lower() != y.lower():
            diffs.append((i, x, y))
    if not diffs and (a or "").lower() != (b or "").lower():
        diffs.append((0, (a or "").strip(), (b or "").strip()))
    return diffs


def unique_diff(item: dict, key: str, letter: str) -> tuple[str, str]:
    """Differing clause distinctive to this wrong option, not only the first mismatch."""
    r = option_text(item, key)
    w = option_text(item, letter)
    diffs = all_diffs(r, w)
    if not diffs:
        return (r or "").strip(), (w or "").strip()
    others = [L for L in option_letters(item) if L not in (key, letter)]

    def shared(diff: tuple[int, str, str]) -> int:
        i, _kx, wx = diff
        n = 0
        for L in others:
            for j, _ok, ow in all_diffs(r, option_text(item, L)):
                if j == i and ow.lower() == wx.lower():
                    n += 1
        return n

    diffs.sort(key=lambda d: (shared(d), -d[0]))
    _i, kx, wx = diffs[0]
    return kx, wx


STMT_SET = re.compile(
    r"^(?:[1-4]\s*,\s*)*[1-4](?:\s+and\s+[1-4])?(?:\s+only)?$",
    re.I,
)


def is_statement_subset(s: str) -> bool:
    t = re.sub(r"\s+", " ", (s or "").strip())
    return bool(STMT_SET.match(t))


def parse_123(s: str) -> set[int]:
    sl = re.sub(r"\s+", " ", (s or "").lower())
    if re.search(r"1\s*,\s*2\s*and\s*3", sl) or sl in {"1,2 and 3", "all three"}:
        return {1, 2, 3}
    got = set()
    for n in (1, 2, 3, 4):
        if re.search(rf"\b{n}\b", sl):
            got.add(n)
    return got


def classify(item: dict, key: str, letter: str) -> tuple[str, str, str, str]:
    w = option_text(item, letter)
    r = option_text(item, key)
    k_c, w_c = unique_diff(item, key, letter)
    wl, rl = w.lower(), r.lower()
    if is_statement_subset(w) and is_statement_subset(r):
        extra = parse_123(w) - parse_123(r)
        missing = parse_123(r) - parse_123(w)
        if extra:
            return (
                "scope_error",
                f"including statement {sorted(extra)[0]} which the keyed set rejects",
                k_c,
                w_c,
            )
        if missing:
            return (
                "condition_omission",
                f"dropping statement {sorted(missing)[0]} which the keyed set still requires",
                k_c,
                w_c,
            )
        return ("scope_error", "picking a different subset of the numbered statements", k_c, w_c)
    if looks_numeric(w) and looks_numeric(r) and w != r:
        return (
            "operation_confusion",
            f"computing {clip(w, 40)} instead of the required {clip(r, 40)}",
            r,
            w,
        )
    for a, b in REV:
        if (_has_pole(a, w) and _has_pole(b, r)) or (_has_pole(b, w) and _has_pole(a, r)):
            return (
                "relationship_reversal",
                f"reversing the directed relation ({clip(w_c, 50)} vs {clip(k_c, 50)})",
                k_c,
                w_c,
            )
    st = tokens(item.get("stem") or "")
    wt, rt = tokens(w), tokens(r)
    if w and r and wt and rt:
        jacc = len(wt & rt) / max(1, len(wt | rt))
        if st & wt and not (wt & rt) and jacc < 0.25:
            return (
                "surface_feature_capture",
                f"matching a salient stem word and choosing “{clip(w_c, 50)}” instead of “{clip(k_c, 50)}”",
                k_c,
                w_c,
            )
        if jacc < 0.28:
            return (
                "term_substitution",
                f"swapping the sibling term “{clip(w_c, 50)}” for the required “{clip(k_c, 50)}”",
                k_c,
                w_c,
            )
    if any(k in wl and k not in rl for k in ("because", "due to", "caused by", "so that")):
        return (
            "mechanism_conflation",
            f"naming a neighbour process in “{clip(w, 50)}” instead of “{clip(r, 50)}”",
            k_c,
            w_c,
        )
    return (
        "condition_omission",
        f"dropping a stated condition so “{clip(w_c, 50)}” looked possible instead of “{clip(k_c, 50)}”",
        k_c,
        w_c,
    )


def place(uid: str, letter: str, correct: str, distractors: list[str]) -> tuple[dict[str, str], str]:
    seen = {correct.strip().lower()}
    deds: list[str] = []
    for x in distractors:
        t = (x or "").strip()
        if not t:
            continue
        k = t.lower()
        if k in seen:
            continue
        seen.add(k)
        deds.append(t)
        if len(deds) == 3:
            break
    pad = [
        "that description is not used in this item",
        "both of those descriptions at once",
        "neither description applies here",
    ]
    for p in pad:
        if len(deds) >= 3:
            break
        if p.lower() not in seen:
            deds.append(p)
            seen.add(p.lower())
    while len(deds) < 3:
        deds.append("a description that this item never uses")
    idx = int(hashlib.md5(f"{uid}:{letter}".encode("utf-8")).hexdigest(), 16) % 4
    slots = [""] * 4
    slots[idx] = correct
    j = 0
    for i in range(4):
        if i == idx:
            continue
        slots[i] = deds[j]
        j += 1
    opts = {LETTERS[i]: slots[i] for i in range(4)}
    return opts, LETTERS[idx]


def _has_pole(p: str, text: str) -> bool:
    t = text or ""
    if p in ("oxid", "reduc", "hot", "cold"):
        return re.search(r"\b" + re.escape(p), t, re.I) is not None
    return re.search(r"\b" + re.escape(p) + r"\b", t, re.I) is not None


def _pole(k_c: str, w_c: str) -> tuple[str, str, bool] | None:
    for a, b in REV:
        if _has_pole(a, k_c) and _has_pole(b, w_c):
            return a, b, True
        if _has_pole(b, k_c) and _has_pole(a, w_c):
            return a, b, False
    return None


def _ascii_form(s: str) -> str:
    return (s or "").translate(SUB_SUP).replace("·", ".").replace(" ", "")


def _parse_counts(formula: str) -> dict[str, int]:
    s = re.sub(r"[^A-Za-z0-9()]", "", _ascii_form(formula))
    n = len(s)

    def num(i: int) -> tuple[int, int]:
        j = i
        while j < n and s[j].isdigit():
            j += 1
        return (int(s[i:j]) if j > i else 1), j

    def parse(i: int) -> tuple[dict[str, int], int]:
        counts: dict[str, int] = {}
        while i < n:
            if s[i] == "(":
                inner, i = parse(i + 1)
                k, i = num(i)
                for el, c in inner.items():
                    counts[el] = counts.get(el, 0) + c * k
            elif s[i] == ")":
                return counts, i + 1
            elif s[i].isupper():
                el = s[i]
                i += 1
                if i < n and s[i].islower():
                    el += s[i]
                    i += 1
                k, i = num(i)
                counts[el] = counts.get(el, 0) + k
            else:
                i += 1
        return counts, i

    counts, _ = parse(0)
    return counts


def _oxidation_states(formula: str) -> dict[str, int] | None:
    """Best-effort OS for Cambridge AS formulae. Neutral compounds only."""
    t = _ascii_form(formula)
    if not t or len(t) > 48:
        return None
    known_groups = (
        ("NH4", {"N": -3, "H": 1}),
        ("SO4", {"S": 6, "O": -2}),
        ("SO3", {"S": 4, "O": -2}),
        ("NO3", {"N": 5, "O": -2}),
        ("CO3", {"C": 4, "O": -2}),
        ("PO4", {"P": 5, "O": -2}),
        ("OH", {"O": -2, "H": 1}),
        ("CN", {"C": 2, "N": -3}),
    )
    counts = _parse_counts(t)
    if not counts:
        return None
    g1 = {"Li", "Na", "K", "Rb", "Cs", "Ag"}
    g2 = {"Be", "Mg", "Ca", "Sr", "Ba", "Zn"}
    os: dict[str, int] = {}
    for g, states in known_groups:
        if g in t:
            os.update(states)
    for el in counts:
        if el in os:
            continue
        if el in g1:
            os[el] = 1
        elif el in g2 or el == "Al":
            os[el] = 2 if el != "Al" else 3
        elif el == "F":
            os[el] = -1
        elif el == "O" and "O" not in os:
            os[el] = -2
        elif el == "H" and "H" not in os:
            os[el] = 1
        elif el in {"Cl", "Br", "I"} and "O" not in counts and "F" not in counts:
            os[el] = -1
    unknown = [el for el in counts if el not in os]
    if len(unknown) == 1:
        el = unknown[0]
        rest = sum(os[e] * counts[e] for e in counts if e != el)
        c = counts[el]
        if c and rest % c == 0:
            os[el] = -rest // c
    if any(el not in os for el in counts):
        return None
    total = sum(os[e] * counts[e] for e in counts)
    if total != 0:
        return None
    return os


def _fmt_os(os: dict[str, int]) -> str:
    bits = []
    for el in os:
        v = os[el]
        bits.append(f"{el} {'+' if v > 0 else ''}{v}")
    return ", ".join(bits)


def _formula_followup(uid: str, letter: str, w: str) -> dict | None:
    if not FORMULAISH.search(_ascii_form(w)) or len(w) > 48:
        return None
    t = _ascii_form(w)
    os = _oxidation_states(w)
    if re.search(r"OH", t) and os:
        q = f"{clip(w, 40)} has hydroxide groups. In each OH, what are the oxidation states of O and H?"
        correct = "O is −2 and H is +1, so O and H do not share a state"
        distractors = [
            "Both −1, so two different elements share the same state",
            "Both +1, matching the metal",
            "O is −1 and H is −1 because OH is the hydroxide ion",
        ]
        why = f"Hydroxide is O −2 and H +1. Repeating OH does not give two different elements the same state. ({_fmt_os(os)})"
    elif re.search(r"SO4", t) and os and "S" in os:
        q = f"In {clip(w, 40)}, O is −2. What is the oxidation state of S?"
        correct = f"{os['S']:+d}"
        distractors = ["+2", "+4 (as in sulfite)", "−2"]
        distractors = [d for d in distractors if d != correct][:3]
        while len(distractors) < 3:
            distractors.append("0")
        why = f"Sulfate sulfur is {os['S']:+d}. {_fmt_os(os)}."
    elif re.search(r"NH4", t) and re.search(r"Cl", t):
        q = f"What is the oxidation state of chlorine in {clip(w, 40)}?"
        correct = "−1, as chloride"
        distractors = ["+1, as in HClO", "+5, as in chlorate", "0, as Cl₂"]
        why = f"{clip(w, 30)} is an ammonium halide: Cl is −1."
    elif os:
        q = f"What are the oxidation states of the elements in {clip(w, 40)}?"
        correct = _fmt_os(os)
        els = list(os)
        distractors = [
            _fmt_os({e: (-os[e] if e == els[0] else os[e]) for e in os}),
            "all elements 0",
            _fmt_os({e: os[e] + (1 if i == 0 else 0) for i, e in enumerate(os)}),
        ]
        why = f"{clip(w, 30)} assigns {_fmt_os(os)}."
    else:
        return None
    opts, fu_key = place(uid, letter, correct, distractors)
    return {"stem": _letter_stem(letter, q), "options": opts, "key": fu_key, "why": why}


def _numeric_method(item: dict, uid: str, letter: str, w: str, r: str) -> dict:
    sl = (item.get("stem") or "").lower()
    wv = clip(w, 28)
    if any(s in sl for s in ("relative atomic", "abundance", "isotop")):
        q = f"A working produced {wv}. How should relative atomic mass be obtained from the peaks?"
        correct = "weighted mean: Σ(mass × abundance) / Σ(abundance)"
        distractors = [
            "simple mean of the mass numbers, ignoring abundances",
            "the mass number of the tallest peak only",
            "product of the mass numbers divided by the number of peaks",
        ]
    elif any(s in sl for s in ("efficiency", "useful output", "electrical power")):
        q = f"The value {wv} is not the efficiency. Efficiency is which ratio?"
        correct = "useful output energy (or power) ÷ total input energy (or power)"
        distractors = [
            "total input ÷ useful output",
            "useful output × total input",
            "useful output − total input",
        ]
    elif "density" in sl:
        q = f"The value {wv} is not the density. Density is which ratio?"
        correct = "mass ÷ volume"
        distractors = ["volume ÷ mass", "mass × volume", "mass + volume"]
    elif any(s in sl for s in ("magnification", "actual size", "image size")):
        q = f"A working produced {wv}. Magnification is which ratio?"
        correct = "image size ÷ actual size"
        distractors = ["actual size ÷ image size", "image size × actual size", "image size − actual size"]
    else:
        q = (
            f"A working produced {wv}. Which combination of the stem quantities "
            f"matches the definition of the quantity being asked?"
        )
        correct = "Use the definition of that quantity; do not drop a factor or invert the ratio"
        distractors = [
            f"Treat {wv} as given in the stem and stop",
            "Average the four listed option values",
            "Invert every quantity in the stem",
        ]
    opts, fu_key = place(uid, letter, correct, distractors)
    why = f"Option {letter} ({clip(w, 40)}) is a different operation or operand, not the required working."
    return {"stem": _letter_stem(letter, q), "options": opts, "key": fu_key, "why": why}


_POLE_Q = {
    ("hot", "cold"): (
        "In the process this item describes, is the change faster in hotter conditions or colder conditions?",
        "faster in hotter conditions",
        "faster in colder conditions",
    ),
    ("higher", "lower"): (
        "Under the change described, does the quantity go higher or lower?",
        "higher",
        "lower",
    ),
    ("faster", "slower"): (
        "If the temperature of this system is raised, how do the particles move?",
        "they move faster",
        "they move slower",
    ),
    ("increase", "decrease"): (
        "Does the quantity in this item increase or decrease under the stated change?",
        "it increases",
        "it decreases",
    ),
    ("exothermic", "endothermic"): (
        "Does the reaction in this item give out energy or take in energy?",
        "gives out energy (exothermic)",
        "takes in energy (endothermic)",
    ),
    ("oxid", "reduc"): (
        "Is the species in this item oxidised or reduced?",
        "oxidised",
        "reduced",
    ),
    ("anode", "cathode"): (
        "Which electrode does the stem require?",
        "anode",
        "cathode",
    ),
    ("xylem", "phloem"): (
        "Which tissue does the stem ask about?",
        "xylem",
        "phloem",
    ),
    ("artery", "vein"): (
        "Which vessel does the stem require?",
        "artery",
        "vein",
    ),
}


def _apply_stem_to_option(hinge_q: str, w_show: str) -> str:
    hm = re.sub(r"\s+", " ", hinge_q or "").strip()
    m = re.match(r"Which (.+)\?\s*$", hm, re.I)
    if m:
        return f"Does “{w_show}” match this requirement: {clip(m.group(1), 120)}?"
    m = re.match(r"What (?:is|are) (.+)\?\s*$", hm, re.I)
    if m:
        return f"Is “{w_show}” {clip(m.group(1), 120)}?"
    m = re.match(r"What happens (?:to )?(.+)\?\s*$", hm, re.I)
    if m:
        return f"Taking “{w_show}”, what happens to {clip(m.group(1), 100)}?"
    m = re.match(r"(How|Why|Where|When)\b(.+)\?\s*$", hm, re.I)
    if m:
        return f"For “{w_show}”, {m.group(1).lower()}{clip(m.group(2), 110)}?"
    return f"A student chose “{w_show}”. Does that choice satisfy: {clip(hm, 120)}"


def followup(item: dict, key: str, letter: str, mx: str, k_c: str, w_c: str) -> dict:
    uid = str(item.get("uid") or "")
    r = option_text(item, key)
    w = option_text(item, letter)
    decoy = [
        "this quantity is unchanged",
        "the stem does not determine a direction",
        "both directions at once",
    ]
    figure = bool(item.get("options_are_figure") and (item.get("figure_src") or item.get("tikz")))

    if is_statement_subset(w) and is_statement_subset(r):
        extra = parse_123(w) - parse_123(r)
        missing = parse_123(r) - parse_123(w)
        n = sorted(extra or missing)[0] if (extra or missing) else 3
        need = "Yes" if n in parse_123(r) else "No"
        stem = f"Option {letter} is “{clip(w, 40)}”. Is numbered statement {n} required?"
        opts, fu_key = place(
            uid,
            letter,
            need,
            ["Yes" if need == "No" else "No", "Only if the other statements are false", "The stem does not number statements"],
        )
        why = f"Statement {n} is {'required' if need == 'Yes' else 'not required'}; that is how {letter} differs from {key}."
        return {"stem": stem, "options": opts, "key": fu_key, "why": why}

    if looks_numeric(w) and looks_numeric(r) and w != r:
        return _numeric_method(item, uid, letter, w, r)

    form = _formula_followup(uid, letter, w)
    if form:
        return form

    pole = _pole(k_c, w_c)
    if pole:
        a, b, key_has_a = pole
        spec = _POLE_Q.get((a, b)) or _POLE_Q.get((b, a))
        if spec:
            spec_q, ans_a, ans_b = spec
            correct = ans_a if key_has_a else ans_b
            wrong_p = ans_b if key_has_a else ans_a
            q = _letter_stem(letter, f"This option says “{clip(w_c, 80)}”. {spec_q}")
            opts, fu_key = place(uid, letter, correct, [wrong_p, decoy[0], decoy[1]])
            why = f"Option {letter} used “{clip(w_c, 60)}”; the item needs “{clip(k_c, 60)}”."
            return {"stem": q, "options": opts, "key": fu_key, "why": why}

    if w_c and k_c and w_c.strip().lower() != k_c.strip().lower() and len(w_c.strip()) >= 8:
        q = _letter_stem(letter, f"This option claims “{clip(w_c, 90)}”. Is that true for the situation in the stem?")
        correct = f"No — “{clip(w_c, 70)}” is not what happens here"
        distractors = [
            f"Yes — “{clip(w_c, 70)}” is exactly what happens",
            f"It is true only of a different process not in the stem",
            f"The stem does not mention this part of the option",
        ]
        opts, fu_key = place(uid, letter, correct, distractors)
        why = f"Option {letter} used “{clip(w_c, 60)}”; the item needs “{clip(k_c, 60)}”."
        return {"stem": q, "options": opts, "key": fu_key, "why": why}

    if (not (w or "").strip()) and figure:
        h = hinge(item.get("stem") or item.get("stem_lead") or "")
        q = (
            f"Look at diagram {letter} only. {clip(h, 140)} "
            f"Which required feature is missing or extra on that diagram?"
        )
        correct = "The diagram does not show every feature the stem requires"
        distractors = [
            "The diagram shows every required feature",
            "Letter of the diagram is enough; features do not matter",
            "Any trough on the diagram counts as the required group",
        ]
        opts, fu_key = place(uid, letter, correct, distractors)
        why = f"Diagram {letter} is not the keyed trace."
        return {"stem": q, "options": opts, "key": fu_key, "why": why}

    w_show = clip(w or f"option {letter}", 90)
    h = hinge(item.get("stem") or item.get("stem_lead") or "")
    q = _letter_stem(letter, _apply_stem_to_option(h, w_show))
    correct = f"No. “{clip(w or letter, 55)}” does not satisfy what the stem asks"
    distractors = [
        f"Yes. “{clip(w or letter, 55)}” is exactly what the stem asks for",
        f"“{clip(w or letter, 45)}” would be correct if one stated condition were dropped",
        f"“{clip(w or letter, 45)}” and every other option are equally valid",
    ]
    opts, fu_key = place(uid, letter, correct, distractors)
    why = f"Option {letter} used “{clip(w_c or w, 60)}”; the item needs “{clip(k_c or r, 60)}”."
    return {"stem": q, "options": opts, "key": fu_key, "why": why}


def solve_line(item: dict, key: str) -> str:
    h = hinge(item.get("stem") or item.get("stem_lead") or "")
    r = option_text(item, key)
    bits = [f"{h} Required: {key} — {clip(r, 120)}."]
    for L in option_letters(item):
        if L == key:
            continue
        k_c, w_c = unique_diff(item, key, L)
        if k_c and w_c and k_c.lower() != w_c.lower():
            bits.append(f"{L} would need “{clip(w_c, 70)}”, but the item needs “{clip(k_c, 70)}”.")
        else:
            bits.append(f"{L} ({clip(option_text(item, L), 70)}) does not meet that criterion.")
    return " ".join(bits)


def construct_lbs(item: dict) -> dict | None:
    a = item.get("assessment") or {}
    key = a.get("mcq_key")
    if key not in LETTERS:
        return None
    figure = bool(item.get("options_are_figure") and (item.get("figure_src") or item.get("tikz")))
    present = option_letters(item)
    if figure:
        present = list(LETTERS)
    if not figure:
        if key not in present and not option_text(item, key):
            return None
        if not any(option_text(item, L) for L in present if L != key):
            return None
    wrong = {}
    for L in present:
        if L == key:
            continue
        if not figure and not option_text(item, L) and not option_text(item, key):
            continue
        mx, pathway, k_c, w_c = classify(item, key, L)
        wrong[L] = {
            "mx_type": mx,
            "pathway": pathway,
            "followup": followup(item, key, L, mx, k_c, w_c),
        }
    if not wrong:
        return None
    return {"solve": solve_line(item, key), "wrong": wrong, "key": key}


def seeds_from_lbs(lbs: dict | None, key: str | None) -> list[dict]:
    out = []
    if not lbs:
        return out
    for L, row in (lbs.get("wrong") or {}).items():
        mx = row.get("mx_type") or "condition_omission"
        pathway = (row.get("pathway") or "").rstrip(".")
        pathway = re.sub(r"^(Student|student)\s+", "", pathway)
        out.append(
            {
                "id": f"{L}:{mx}",
                "letter": L,
                "mx_type": mx,
                "label": f"If {L} · {mx.replace('_', ' ')}",
                "instruction": (
                    f"Rewrite this item so option {L} remains the trap for a student {pathway}. "
                    f"Change the numbers, species or wording; rewrite the stem and all four options "
                    f"as one coherent item. Do not print mix-up labels on the learner stem. Recalculate the key."
                ),
            }
        )
    return out


def lbs_complete(lbs: dict | None, key: str, options: dict | None = None, item: dict | None = None) -> bool:
    if not lbs or key not in LETTERS:
        return False
    if item is not None:
        present = option_letters(item)
    else:
        present = [L for L in LETTERS if (options or {}).get(L) not in (None, "")] or list(LETTERS)
    expect = set(present) - {key}
    if not expect:
        expect = set(LETTERS) - {key}
    wrong = lbs.get("wrong") or {}
    if expect - set(wrong):
        return False
    for L in expect:
        fu = (wrong.get(L) or {}).get("followup") or {}
        if not fu.get("stem") or fu.get("key") not in LETTERS or not (fu.get("options") or {}):
            return False
    return True


def _overlay_lbs(rec: dict, key: str) -> dict:
    lbs = {k: rec[k] for k in ("solve", "wrong", "key") if k in rec}
    if "key" not in lbs:
        lbs["key"] = key
    return lbs


def ensure_item(item: dict) -> bool:
    """Attach or replace LBS + modify seeds for a keyed MCQ.

    Keep an already-relevant bank (approved gold / spectroscopy). Else overlay,
    else construct. Stamp/template banks are rebuilt.
    """
    a = dict(item.get("assessment") or {})
    key = a.get("mcq_key")
    if key not in LETTERS or a.get("key_status") != "available":
        return False
    lifted = lift_options(item)
    uid = str(item.get("uid") or "")
    changed = lifted
    lbs = a.get("learn_by_solve")
    ov = overlay_records().get(uid)
    if ov:
        lbs_ov = _overlay_lbs(ov, key)
        if lbs_complete(lbs_ov, key, item.get("options") or {}, item) and not is_stamp_lbs(lbs_ov):
            if a.get("learn_by_solve") != lbs_ov:
                a["learn_by_solve"] = lbs_ov
                changed = True
            seeds_ov = ov.get("modify_seeds")
            if seeds_ov:
                if a.get("modify_seeds") != seeds_ov:
                    a["modify_seeds"] = seeds_ov
                    changed = True
            elif not a.get("modify_seeds"):
                a["modify_seeds"] = seeds_from_lbs(lbs_ov, key)
                changed = True
            if changed:
                item["assessment"] = a
            return changed
    if lbs_relevant(item, lbs, key):
        if not a.get("modify_seeds"):
            a["modify_seeds"] = seeds_from_lbs(lbs, key)
            item["assessment"] = a
            return True
        if changed:
            item["assessment"] = a
        return changed
    built = construct_lbs(item)
    if built and lbs_relevant(item, built, key):
        a["learn_by_solve"] = built
        a["modify_seeds"] = seeds_from_lbs(built, key)
        item["assessment"] = a
        return True
    if lbs:
        a.pop("learn_by_solve", None)
        a.pop("modify_seeds", None)
        item["assessment"] = a
        return True
    if changed:
        item["assessment"] = a
    return changed
