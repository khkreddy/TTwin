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
STAMP_SOLVE = "The keyed choice is"
STAMP_STEM = (
    "What did they drop?",
    "Which description of that error",
    "What kind of boundary error",
    "Which description fits?",
    "What mixed two processes?",
    "A directed relation (cause/effect",
    "Over- or under-extending which cases",
    "Which claim does the item actually require?",
    "Which value is required?",
    "A working that is consistent with this item gives",
)

_ROOT = Path(__file__).resolve().parents[1]
_JEEBENCH = Path("/home/harik/awm_build/data/corpus_intelligence/awm_corpus/jeebench-dataset.json")
_JEE_BY_UID: dict[str, str] | None = None


def _preserve_uids() -> set[str]:
    p = _ROOT / "data" / "spectra" / "lbs.json"
    if not p.is_file():
        return set()
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
        return set((doc.get("items") or {}).keys())
    except Exception:
        return set()


PRESERVE_UIDS = _preserve_uids()


def clip(s: str, n: int = 110) -> str:
    t = re.sub(r"\s+", " ", (s or "").strip())
    if len(t) <= n:
        return t
    return t[: n - 1].rstrip() + "…"


def tokens(s: str) -> set[str]:
    return set(TOK.findall((s or "").lower()))


def looks_numeric(s: str) -> bool:
    t = (s or "").strip()
    if not t or not any(ch.isdigit() for ch in t):
        return False
    if NUMISH.match(t):
        return True
    return len(t) <= 24


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


def parse_123(s: str) -> set[int]:
    sl = re.sub(r"\s+", " ", (s or "").lower())
    if re.search(r"1\s*,\s*2\s*and\s*3", sl) or sl in {"1,2 and 3", "all three"}:
        return {1, 2, 3}
    got = set()
    if re.search(r"\b1\b", sl):
        got.add(1)
    if re.search(r"\b2\b", sl):
        got.add(2)
    if re.search(r"\b3\b", sl):
        got.add(3)
    return got


def classify(item: dict, key: str, letter: str) -> tuple[str, str, str, str]:
    w = option_text(item, letter)
    r = option_text(item, key)
    k_c, w_c = unique_diff(item, key, letter)
    wl, rl = w.lower(), r.lower()
    if THREE.match(w) and THREE.match(r):
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
        "the stem does not decide between these claims",
        "both claims are required at once",
        "neither claim can be true",
    ]
    for p in pad:
        if len(deds) >= 3:
            break
        if p.lower() not in seen:
            deds.append(p)
            seen.add(p.lower())
    while len(deds) < 3:
        deds.append("an unrelated claim not used in this item")
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


def _numeric_method(item: dict, uid: str, letter: str, w: str, r: str) -> dict:
    sl = (item.get("stem") or "").lower()
    if any(s in sl for s in ("relative atomic", "abundance", "isotop")):
        q = "How should the relative atomic mass be obtained from the peaks?"
        correct = "weighted mean: Σ(mass × abundance) / Σ(abundance)"
        distractors = [
            "simple mean of the mass numbers, ignoring abundances",
            "the mass number of the tallest peak only",
            "product of the mass numbers divided by the number of peaks",
        ]
    elif any(s in sl for s in ("efficiency", "useful output", "electrical power")):
        q = "Which expression is required for efficiency?"
        correct = "useful output energy (or power) ÷ total input energy (or power)"
        distractors = [
            "total input ÷ useful output",
            "useful output × total input",
            "useful output − total input",
        ]
    elif "density" in sl:
        q = "Which expression is required for density?"
        correct = "mass ÷ volume"
        distractors = ["volume ÷ mass", "mass × volume", "mass + volume"]
    else:
        q = (
            "A student obtained a different numerical value from the working this item requires. "
            "Which check is required?"
        )
        correct = "Repeat the operations the stem requires, without reversing a ratio or dropping a term"
        distractors = [
            "Average the four option values",
            "Invert every quantity in the stem",
            "Treat the first given number as the answer",
        ]
    opts, fu_key = place(uid, letter, correct, distractors)
    why = f"Option {letter} ({clip(w, 40)}) is a different operation or operand, not the required working."
    return {"stem": q, "options": opts, "key": fu_key, "why": why}


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


def followup(item: dict, key: str, letter: str, mx: str, k_c: str, w_c: str) -> dict:
    uid = str(item.get("uid") or "")
    r = option_text(item, key)
    w = option_text(item, letter)
    decoy = [
        "this quantity is unchanged",
        "the stem does not determine a direction",
        "both directions at once",
    ]

    if THREE.match(w) and THREE.match(r):
        extra = parse_123(w) - parse_123(r)
        missing = parse_123(r) - parse_123(w)
        n = sorted(extra or missing)[0] if (extra or missing) else 3
        need = "Yes" if n in parse_123(r) else "No"
        stem = f"Is numbered statement {n} required?"
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

    pole = _pole(k_c, w_c)
    if pole:
        a, b, key_has_a = pole
        spec = _POLE_Q.get((a, b)) or _POLE_Q.get((b, a))
        if spec:
            q, ans_a, ans_b = spec
            correct = ans_a if key_has_a else ans_b
            wrong_p = ans_b if key_has_a else ans_a
            opts, fu_key = place(uid, letter, correct, [wrong_p, decoy[0], decoy[1]])
            why = f"Option {letter} used “{clip(w_c, 60)}”; the item needs “{clip(k_c, 60)}”."
            return {"stem": q, "options": opts, "key": fu_key, "why": why}

    if mx == "term_substitution":
        q = "The stem names a specific species or process. Which rule is required?"
        correct = "Match the named species or process; do not swap a sibling name"
        distractors = [
            "Swap in a neighbouring name from the option list",
            "Ignore names and pick the longest option",
            "Any sibling name is acceptable",
        ]
    elif mx == "surface_feature_capture":
        q = "A word or symbol in the stem is easy to spot. Which rule is required?"
        correct = "Use the operative criterion in the stem, not a salient surface word"
        distractors = [
            "Match the most visible word or colour and stop",
            "Ignore the stem once one familiar word appears",
            "Surface features override the stated criterion",
        ]
    else:
        q = "A student answered as if a different condition held. Which check is required?"
        correct = "Keep the stem's stated conditions; do not reverse or drop them"
        distractors = [
            "Reverse the stated direction",
            "Drop the stated condition and guess",
            "Ignore the stem and pick the longest option",
        ]
    opts, fu_key = place(uid, letter, correct, distractors)
    why = f"Option {letter} used “{clip(w_c, 60)}”; the item needs “{clip(k_c, 60)}”."
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
    present = option_letters(item)
    if key not in present and not option_text(item, key):
        return None
    if not any(option_text(item, L) for L in present if L != key):
        return None
    wrong = {}
    for L in present:
        if L == key:
            continue
        if not option_text(item, L) and not option_text(item, key):
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


def is_stamp_lbs(lbs: dict | None) -> bool:
    if not lbs:
        return True
    solve = lbs.get("solve") or ""
    if STAMP_SOLVE in solve:
        return True
    keys = []
    for row in (lbs.get("wrong") or {}).values():
        fu = row.get("followup") or {}
        stem = fu.get("stem") or ""
        if any(s in stem for s in STAMP_STEM):
            return True
        keys.append(fu.get("key"))
    return False


def ensure_item(item: dict) -> bool:
    """Attach or replace LBS + modify seeds for a keyed MCQ.

    Hand-authored spectroscopy rows (not stamps) are kept. Stamp banks are rebuilt.
    """
    a = dict(item.get("assessment") or {})
    key = a.get("mcq_key")
    if key not in LETTERS or a.get("key_status") != "available":
        return False
    lifted = lift_options(item)
    uid = item.get("uid") or ""
    lbs = a.get("learn_by_solve")
    preserve = (
        uid in PRESERVE_UIDS
        and lbs_complete(lbs, key, item.get("options") or {}, item)
        and not is_stamp_lbs(lbs)
    )
    changed = lifted
    if not preserve:
        built = construct_lbs(item)
        if built:
            a["learn_by_solve"] = built
            lbs = built
            changed = True
        elif lbs and is_stamp_lbs(lbs):
            a.pop("learn_by_solve", None)
            lbs = None
            changed = True
    if lbs:
        a["modify_seeds"] = seeds_from_lbs(lbs, key)
        changed = True
    elif a.get("modify_seeds"):
        a.pop("modify_seeds", None)
        changed = True
    if changed:
        item["assessment"] = a
    return changed
