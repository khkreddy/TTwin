#!/usr/bin/env python3
"""Construct learn-by-solve banks and Mx modify seeds for a keyed MCQ.

Pack-time overlay. Does not rewrite freeze exam.v1. Mix-up type names are
teacher-key fields; follow-up stems never print mx_type.
"""
from __future__ import annotations

import re
from typing import Any

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
    ("solid", "liquid"),
    ("artery", "vein"),
    ("xylem", "phloem"),
)


def clip(s: str, n: int = 110) -> str:
    t = re.sub(r"\s+", " ", (s or "").strip())
    if len(t) <= n:
        return t
    return t[: n - 1].rstrip() + "…"


def tokens(s: str) -> set[str]:
    return set(TOK.findall((s or "").lower()))


def option_letters(options: dict) -> list[str]:
    present = [L for L in LETTERS if options.get(L) not in (None,)]
    return present or list(LETTERS)


def looks_numeric(s: str) -> bool:
    t = (s or "").strip()
    if not t:
        return False
    if NUMISH.match(t) and any(ch.isdigit() for ch in t):
        return True
    return bool(re.search(r"\d", t)) and len(t) <= 24


def hinge(stem: str) -> str:
    s = re.sub(r"\s+", " ", (stem or "").strip())
    m = re.search(r"((?:What|Which|How|Why|Where|When|Calculate|Find)\b.{8,220}\??)", s, re.I)
    if m:
        return clip(m.group(1), 180)
    q = s.find("?")
    if q >= 0:
        start = max(0, q - 160)
        return clip(s[start : q + 1], 180)
    return clip(s, 180)


def classify(stem: str, options: dict, key: str, letter: str) -> tuple[str, str]:
    w = str(options.get(letter) or "").strip()
    r = str(options.get(key) or "").strip()
    wl, rl = w.lower(), r.lower()
    if THREE.match(w) and THREE.match(r):
        if "1, 2 and 3" in wl.replace(" ", "") or wl.startswith("1,2 and 3") or "1, 2 and 3" in w.lower():
            return (
                "scope_error",
                f"Student treated every numbered statement as true and picked {letter} ({clip(w, 60)}) instead of {key} ({clip(r, 60)}).",
            )
        return (
            "condition_omission",
            f"Student dropped or added a numbered statement, picking {letter} ({clip(w, 60)}) instead of {key} ({clip(r, 60)}).",
        )
    if looks_numeric(w) and looks_numeric(r) and w != r:
        return (
            "operation_confusion",
            f"Student used the wrong operation, operand or rounding and obtained {clip(w, 40)} instead of {clip(r, 40)}.",
        )
    for a, b in REV:
        if (a in wl and b in rl) or (b in wl and a in rl):
            return (
                "relationship_reversal",
                f"Student reversed a directed relation, writing {clip(w, 60)} where the key is {clip(r, 60)}.",
            )
    st = tokens(stem)
    wt, rt = tokens(w), tokens(r)
    if w and r and wt and rt:
        jacc = len(wt & rt) / max(1, len(wt | rt))
        if st & wt and not (wt & rt) and jacc < 0.25:
            return (
                "surface_feature_capture",
                f"Student matched a salient stem word and chose {letter} ({clip(w, 60)}) instead of the operative criterion that yields {key}.",
            )
        if jacc < 0.28:
            return (
                "term_substitution",
                f"Student swapped a named term for a sibling: {clip(w, 60)} instead of {clip(r, 60)}.",
            )
    if any(k in wl and k not in rl for k in ("because", "due to", "caused by", "so that")):
        return (
            "mechanism_conflation",
            f"Student named a neighbour mechanism in {letter} ({clip(w, 60)}) that does not apply to this item.",
        )
    if not w:
        return (
            "surface_feature_capture",
            f"Student picked figure/letter {letter} from a surface feature instead of the criterion that selects {key}.",
        )
    return (
        "condition_omission",
        f"Student dropped a stated condition that still holds, so {letter} ({clip(w, 60)}) looked possible.",
    )


def followup(stem: str, options: dict, key: str, letter: str, mx: str, pathway: str) -> dict:
    w = clip(str(options.get(letter) or f"option {letter}"), 90)
    r = clip(str(options.get(key) or f"option {key}"), 90)
    others = [L for L in option_letters(options) if L not in (key, letter)]
    o1 = clip(str(options.get(others[0]) or f"option {others[0]}"), 70) if others else "an unrelated distractor"
    h = hinge(stem)
    probes = {
        "term_substitution": (
            f"{h}\n\nA student wrote {w} in place of {r}. These names are siblings. Which one meets the item's criterion?",
            {"A": r, "B": w, "C": o1, "D": "Either name is acceptable here"},
            "A",
            f"{r} is the keyed term. {w} is a sibling substitution.",
        ),
        "condition_omission": (
            f"{h}\n\nSomeone chose: {w}\nThe key is: {r}\nWhat did they drop?",
            {
                "A": "A stated condition that still applies, so the key remains " + r,
                "B": "Nothing — " + w + " is also allowed",
                "C": "The whole stem, which can be ignored",
                "D": "Units only",
            },
            "A",
            f"The stated condition still holds; that is why {r} is keyed and {w} is not.",
        ),
        "relationship_reversal": (
            f"{h}\n\nCompare {w} with {r}. What is the error in the first?",
            {
                "A": "A directed relation (cause/effect, greater/lesser, or process direction) was reversed",
                "B": "A unit prefix was misread",
                "C": "An extra numbered statement was included",
                "D": "The figure was blank",
            },
            "A",
            f"{w} reverses the directed relation that {r} keeps.",
        ),
        "scope_error": (
            f"{h}\n\nA student selected {w} rather than {r}. What kind of boundary error is that?",
            {
                "A": "Over- or under-extending which cases/statements the criterion covers",
                "B": "A pure arithmetic slip with the same cases",
                "C": "Ignoring the question entirely",
                "D": "Treating the key as unofficial",
            },
            "A",
            f"{w} changes the scope of the true statements relative to {r}.",
        ),
        "surface_feature_capture": (
            f"{h}\n\nWhy is {w} tempting but not keyed, while {r} is?",
            {
                "A": "A salient word, colour, symbol or visible change replaced the operative criterion",
                "B": "The key uses a different syllabus",
                "C": "The numbers were rounded twice",
                "D": "The stem has no criterion",
            },
            "A",
            f"{w} tracks a surface cue; {r} tracks the operative criterion.",
        ),
        "mechanism_conflation": (
            f"{h}\n\nOption {letter} says: {w}\nThe key says: {r}\nWhat mixed two processes?",
            {
                "A": "A neighbour mechanism was named as if it were this one",
                "B": "Only the units differ",
                "C": "The option is identical to the key",
                "D": "No process is named in either",
            },
            "A",
            f"{w} imports a neighbour mechanism; {r} stays on this item's process.",
        ),
        "operation_confusion": (
            f"The keyed value is {r}. A student obtained {w}. Which description fits?",
            {
                "A": "The wrong operation, operand, formula step or rounding was used",
                "B": "The key is an estimate and both are accepted",
                "C": "The stem forbids calculation",
                "D": f"Significant figures are the only issue and {r} equals {w}",
            },
            "A",
            f"{w} is a procedural mix-up; {r} is the result of the required steps.",
        ),
    }
    st, opts, k, why = probes.get(mx) or probes["condition_omission"]
    return {"stem": st, "options": opts, "key": k, "why": why}


def solve_line(stem: str, options: dict, key: str) -> str:
    r = clip(str(options.get(key) or f"option {key}"), 120)
    h = hinge(stem)
    return f"{h} The keyed choice is {key}: {r}."


def construct_lbs(item: dict) -> dict | None:
    a = item.get("assessment") or {}
    key = a.get("mcq_key")
    if key not in LETTERS:
        return None
    options = item.get("options") or {}
    present = option_letters(options)
    if key not in present:
        present = list(LETTERS)
    stem = item.get("stem") or item.get("stem_lead") or ""
    wrong = {}
    for L in present:
        if L == key:
            continue
        mx, pathway = classify(stem, options, key, L)
        wrong[L] = {
            "mx_type": mx,
            "pathway": pathway,
            "followup": followup(stem, options, key, L, mx, pathway),
        }
    if not wrong:
        return None
    return {"solve": solve_line(stem, options, key), "wrong": wrong, "key": key}


def seeds_from_lbs(lbs: dict | None, key: str | None) -> list[dict]:
    out = []
    if not lbs:
        return out
    for L, row in (lbs.get("wrong") or {}).items():
        mx = row.get("mx_type") or "condition_omission"
        pathway = row.get("pathway") or ""
        out.append(
            {
                "id": f"{L}:{mx}",
                "letter": L,
                "mx_type": mx,
                "label": f"If {L} · {mx.replace('_', ' ')}",
                "instruction": (
                    f"Rewrite this item so a student who still {pathway.rstrip('.')} "
                    f"would pick {L}. Change the numbers, species or wording; rewrite the stem "
                    f"and all four options as one coherent item. Do not print mix-up labels "
                    f"on the learner stem. Recalculate the key."
                ),
            }
        )
    return out


def lbs_complete(lbs: dict | None, key: str, options: dict) -> bool:
    if not lbs or key not in LETTERS:
        return False
    present = option_letters(options)
    expect = set(present) - {key}
    if not expect:
        expect = set(LETTERS) - {key}
    wrong = lbs.get("wrong") or {}
    if expect - set(wrong):
        return False
    for L in expect:
        fu = (wrong.get(L) or {}).get("followup") or {}
        if not fu.get("stem") or not fu.get("key") or not (fu.get("options") or {}):
            return False
    return True


def ensure_item(item: dict) -> bool:
    """Attach LBS + modify seeds if this is a keyed MCQ. Preserve complete LBS."""
    a = dict(item.get("assessment") or {})
    key = a.get("mcq_key")
    if key not in LETTERS or a.get("key_status") != "available":
        return False
    options = item.get("options") or {}
    lbs = a.get("learn_by_solve")
    changed = False
    if not lbs_complete(lbs, key, options):
        built = construct_lbs(item)
        if built:
            a["learn_by_solve"] = built
            lbs = built
            changed = True
    if lbs and not a.get("modify_seeds"):
        a["modify_seeds"] = seeds_from_lbs(lbs, key)
        changed = True
    if changed:
        item["assessment"] = a
    return changed
