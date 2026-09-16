#!/usr/bin/env python3
"""ISO-GEN learn-by-solve overlay for Chemistry AS/A Electrochemistry.

Specification before the follow-up: hinge from the packed tags (node C5/H-REDOX
or C5/H-ECHEM) plus the failure mode of that wrong option. Does not rewrite
freeze exam.v1. Gold 9701_m16_qp_12:q1 and spectroscopy uids are not overwritten.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from lbs_construct import (
    EQN,
    FORMULAISH,
    LETTERS,
    _ascii_form,
    _formula_followup,
    _oxidation_states,
    classify,
    _letter_stem,
    clip,
    looks_numeric,
    option_text,
    parse_123,
    place,
    seeds_from_lbs,
)
from lbs_quality import is_stamp_lbs, lbs_relevant

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "data" / "questions" / "chemistry-senior.json"
MAP = ROOT / "data" / "maps" / "chemistry.json"
GOLD = ROOT / "data" / "overlay" / "lbs_gold.json"
SPECTRA = ROOT / "data" / "spectra" / "lbs.json"
OUT = ROOT / "data" / "overlay" / "lbs_electrochem.json"

CHAPTER = "cam:9701:6"
HUB = {
    "chem:C5/H-REDOX": "Redox — electron transfer and oxidation number",
    "chem:C5/H-ECHEM": "Electrochemistry — redox driven by a potential difference",
}


def _skip_uids() -> set[str]:
    out: set[str] = set()
    for p in (GOLD, SPECTRA):
        if not p.is_file():
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        out.update((doc.get("items") or {}).keys())
    return out


def _map_units() -> list[dict]:
    if not MAP.is_file():
        return []
    doc = json.loads(MAP.read_text(encoding="utf-8"))
    return list(doc.get("units") or [])


def match_hinge(item: dict, units: list[dict]) -> tuple[str, str]:
    node = str(item.get("node") or "")
    label = HUB.get(node) or (item.get("subtopic_label") or node)
    stem = (item.get("stem") or "").lower()
    hub = node.replace("chem:", "")
    best = None
    best_n = 0
    for u in units:
        if str(u.get("node") or "") != hub:
            continue
        dec = (u.get("decision_hinge") or "").lower()
        toks = [t for t in re.findall(r"[a-z]{4,}", dec) if t not in {"that", "which", "from", "with", "this"}]
        n = sum(1 for t in toks if t in stem)
        if n > best_n:
            best_n = n
            best = u
    if best and best_n >= 2:
        return (
            str(best.get("unit_id") or node),
            str(best.get("decision_hinge") or label),
        )
    return node, label


def _numbered_statements(stem: str) -> dict[int, str]:
    found: dict[int, str] = {}
    for m in re.finditer(r"(?m)^\s*(\d+)\s+(.+?)\s*$", stem or ""):
        found[int(m.group(1))] = re.sub(r"\s+", " ", m.group(2)).strip()
    if len(found) >= 2:
        return found
    blob = re.sub(r"\s+", " ", stem or "")
    for m in re.finditer(r"(\d+)\s+([A-Z][^0-9]{8,160}?)(?=\s+\d+\s+[A-Z]|$)", blob):
        found[int(m.group(1))] = m.group(2).strip().rstrip(".")
    return found


def _looks_stmt_combo(s: str) -> bool:
    sl = re.sub(r"\s+", " ", (s or "").lower())
    return bool(
        re.search(r"1\s*,\s*2\s*and\s*3", sl)
        or re.search(r"1 and 2 only|1 and 3 only|2 and 3 only", sl)
        or re.search(r"\b1 only\b", sl)
    )


def _stmt_set(s: str) -> set[int]:
    if not _looks_stmt_combo(s):
        return set()
    sl = re.sub(r"\s+", " ", (s or "").lower())
    if re.search(r"1\s*,\s*2\s*and\s*3", sl):
        return {1, 2, 3}
    got = set()
    if re.search(r"\b1\b", sl):
        got.add(1)
    if re.search(r"\b2\b", sl):
        got.add(2)
    if re.search(r"\b3\b", sl):
        got.add(3)
    if "only" in sl and got:
        return got
    return parse_123(s)


def _wrap(row: dict, letter: str, hinge_id: str, hinge_label: str, mx: str, pathway: str, kind: str) -> dict:
    fu = dict(row)
    fu["stem"] = _letter_stem(letter, fu.get("stem") or "")
    return {
        "hinge_id": hinge_id,
        "hinge_label": hinge_label,
        "failure_kind": kind,
        "mx_type": mx,
        "pathway": pathway,
        "followup": fu,
    }


def _os_formula(uid: str, letter: str, w: str, hinge_id: str, hinge_label: str, mx: str, pathway: str) -> dict | None:
    fu = _formula_followup(uid, letter, w)
    if not fu:
        os = _oxidation_states(w)
        if not os:
            return None
        q = f"What are the oxidation numbers of the elements in {clip(w, 40)}?"
        correct = ", ".join(f"{e} {'+' if os[e] > 0 else ''}{os[e]}" for e in os)
        distractors = ["all 0", "oxygen +2, others −1", "each element −1"]
        opts, fu_key = place(uid, letter, correct, distractors)
        fu = {
            "stem": q,
            "options": opts,
            "key": fu_key,
            "why": f"{clip(w, 30)} assigns {correct}. That is the missing step for this option.",
        }
    why = fu.get("why") or ""
    if "keyed" in why.lower() or "original" in why.lower():
        fu["why"] = why.split(".")[0] + "."
    return _wrap(fu, letter, hinge_id, hinge_label, mx, pathway, "intermediate_omission")


def _redox_equation(uid: str, letter: str, w: str, hinge_id: str, hinge_label: str, mx: str) -> dict | None:
    if not EQN.search(w) or len(w) < 8:
        return None
    q = f"In {clip(w, 90)}, does any element change oxidation number?"
    # Prefer a computed OS if a simple left-hand species exists.
    left = re.split(r"→|->|⇌", w, maxsplit=1)[0]
    species = re.findall(r"[A-Z][a-z]?(?:[A-Z][a-z]?|\d|\(|\))*", left)
    os_left = None
    name = None
    for sp in species:
        if sp.count("(") != sp.count(")"):
            continue
        if FORMULAISH.search(_ascii_form(sp)) and 1 < len(sp) <= 24:
            os_left = _oxidation_states(sp)
            if os_left:
                name = sp
                break
    if name and os_left:
        q = f"In {clip(w, 80)}, what is the oxidation number of the highlighted species {name} on the left?"
        correct = ", ".join(f"{e} {'+' if os_left[e] > 0 else ''}{os_left[e]}" for e in os_left)
        distractors = ["all 0 because it is a reactant", "all −1", "cannot be assigned"]
        why = (
            f"Assign oxidation numbers on each side of this equation before deciding "
            f"whether it is redox. On the left, {name} is {correct}."
        )
    else:
        correct = "Check each element on both sides; a change means redox"
        distractors = [
            "If a compound appears, it cannot be redox",
            "Only reactions with O₂ are redox",
            "Ionic equations are never redox",
        ]
        why = (
            "A reaction is redox only if some element’s oxidation number changes. "
            "Work that check on this equation before using it as the original answer."
        )
    opts, fu_key = place(uid, letter, correct, distractors)
    pathway = f"Student judged {clip(w, 40)} without assigning oxidation numbers on both sides."
    return _wrap(
        {"stem": q, "options": opts, "key": fu_key, "why": why},
        letter,
        hinge_id,
        hinge_label,
        mx,
        pathway,
        "intermediate_omission",
    )


def _os_row(uid: str, letter: str, w: str, k_c: str, w_c: str, hinge_id: str, hinge_label: str, mx: str) -> dict | None:
    if not re.search(r"[+\-−]\s*\d", w) and "oxidation" not in w.lower():
        return None
    focus = w_c if w_c and w_c != k_c else w
    q = (
        f"This option is “{clip(w, 70)}” and assigns “{clip(focus, 50)}”. "
        f"What oxidation number should that species actually have here?"
    )
    if k_c and k_c.strip() != (w_c or "").strip():
        correct = clip(k_c, 70)
        distractors = [clip(w_c or w, 70), "0 for every element", "the oxidation number of oxygen only"]
        why = (
            f"The missing step is the oxidation number of that species. "
            f"It is not “{clip(w_c or w, 50)}” in this reaction."
        )
        # Do not put the original keyed full option as the only correct if it leaks the whole row.
        if len(k_c) > 80:
            correct = "Recompute from the formula: group 1 = +1, O = −2, then the remaining element"
            distractors = [clip(focus, 70), "treat every atom as 0", "copy the charge of the ion onto every atom"]
            why = "Use the usual oxidation-number rules on the formula in this option, not a neighbouring element."
    else:
        return None
    opts, fu_key = place(uid, letter, correct, distractors)
    pathway = f"Student kept “{clip(focus, 40)}” without finishing the oxidation-number assignment."
    return _wrap(
        {"stem": q, "options": opts, "key": fu_key, "why": why},
        letter,
        hinge_id,
        hinge_label,
        mx,
        pathway,
        "intermediate_omission",
    )


def _three_stmt(item: dict, uid: str, letter: str, w: str, r: str, hinge_id: str, hinge_label: str, mx: str) -> dict | None:
    if not (_looks_stmt_combo(w) and _looks_stmt_combo(r)):
        return None
    extra = _stmt_set(w) - _stmt_set(r)
    missing = _stmt_set(r) - _stmt_set(w)
    n = sorted(extra or missing)[0] if (extra or missing) else None
    if n is None:
        return None
    stmts = _numbered_statements(item.get("stem") or "")
    body = stmts.get(n) or f"numbered statement {n}"
    need = n in _stmt_set(r)
    q = (
        f"Option {letter} is “{clip(w, 40)}”. "
        f"Is this statement always true in this redox item: “{clip(body, 100)}”?"
    )
    correct = "Yes" if need else "No"
    distractors = [
        "Yes" if not need else "No",
        "Only when the compound is an element",
        "The statement is about electrolysis, not oxidation number",
    ]
    opts, fu_key = place(uid, letter, correct, distractors)
    why = (
        f"Statement {n} is {'required' if need else 'not required'} for the original decision. "
        f"Settle that statement before choosing among 1 / 2 / 3 combinations."
    )
    pathway = f"Student mis-classified statement {n}: {clip(body, 50)}."
    return _wrap(
        {"stem": q, "options": opts, "key": fu_key, "why": why},
        letter,
        hinge_id,
        hinge_label,
        mx,
        pathway,
        "intermediate_omission",
    )


def _electrolysis(item: dict, uid: str, letter: str, w: str, hinge_id: str, hinge_label: str, mx: str) -> dict | None:
    sl = (item.get("stem") or "").lower()
    wl = (w or "").lower()
    if not any(s in sl for s in ("electrolys", "cryolite", "anode", "cathode", "aluminium oxide", "al₂o₃", "al2o3")):
        return None
    if "cryolite" in sl and ("oxid" in wl or "corrosion" in wl or "melting" in wl or "solvent" in wl):
        q = (
            f"This option says “{clip(w, 70)}”. "
            "In the extraction of aluminium, what is the role of cryolite mixed with Al₂O₃?"
        )
        correct = "It lowers the melting point of the electrolyte (and dissolves Al₂O₃)"
        distractors = [
            "It prevents oxidation of aluminium metal",
            "It is the source of Al³⁺ that is reduced",
            "It stops the carbon anode from burning",
        ]
        why = (
            "Cryolite is a solvent that lowers the melting point of aluminium oxide. "
            "Aluminium is still produced by reduction of Al³⁺ at the cathode."
        )
        kind = "term_substitution" if "oxid" in wl else "intermediate_omission"
    elif "anode" in wl or "cathode" in wl or "oxidised" in wl or "reduced" in wl:
        q = (
            f"This option says “{clip(w, 70)}”. "
            "In molten electrolysis of the metal oxide, do cations travel to the cathode or the anode, "
            "and are they oxidised or reduced?"
        )
        correct = "Cathode; Al³⁺ + 3e⁻ → Al (reduction)"
        distractors = [
            "Anode; Al³⁺ + 3e⁻ → Al (reduction)",
            "Cathode; aluminium is oxidised",
            "Anode; oxide ions are reduced to aluminium",
        ]
        why = (
            "Cations are reduced at the cathode. Al³⁺ gains electrons there. "
            "Oxide ions are oxidised at the carbon anode."
        )
        kind = "relationship_reversal"
    else:
        q = (
            f"This option says “{clip(w, 70)}”. "
            "Is that claim about the electrode process or about the solvent?"
        )
        correct = "Check whether the claim names the cathode reduction of Al³⁺ or a different role"
        distractors = [
            "Every labelled part of the cell is oxidised",
            "Cryolite is purified aluminium",
            "Aluminium is liberated at the anode",
        ]
        why = "Separate the solvent role of cryolite from the electrode half-equations before judging this option."
        kind = "intermediate_omission"
    opts, fu_key = place(uid, letter, correct, distractors)
    return _wrap(
        {"stem": q, "options": opts, "key": fu_key, "why": why},
        letter,
        hinge_id,
        hinge_label,
        mx or kind,
        f"Student used “{clip(w, 40)}” without the cathode/cryolite distinction.",
        kind,
    )


def _numeric_redox(item: dict, uid: str, letter: str, w: str, r: str, hinge_id: str, hinge_label: str, mx: str) -> dict | None:
    if not looks_numeric(w) or not looks_numeric(r) or w == r:
        return None
    sl = (item.get("stem") or "").lower()
    wv = clip(w, 24)
    if ("fec2o4" in sl.replace("₂", "2").replace("₄", "4") or "ethanedioate" in sl) and (
        "mno4" in sl.replace("₄", "4") or "manganate" in sl
    ):
        q = (
            f"The listed value is {wv}. For FeC₂O₄ with MnO₄⁻, how many moles of electrons "
            f"does 1 mol of FeC₂O₄ lose (Fe²⁺ and C₂O₄²⁻ together)?"
        )
        correct = "3 mol e⁻ (1 from Fe²⁺→Fe³⁺ and 2 from C₂O₄²⁻→2CO₂)"
        distractors = [
            "1 mol e⁻ (iron only)",
            "2 mol e⁻ (ethanedioate only)",
            "5 mol e⁻ (copied from MnO₄⁻)",
        ]
        why = (
            "Fe²⁺ loses 1e⁻ and C₂O₄²⁻ loses 2e⁻, so 1 mol FeC₂O₄ loses 3 mol e⁻. "
            "MnO₄⁻ gains 5e⁻. Combine those counts before using a listed value."
        )
    elif "mno4" in sl.replace("₄", "4") or "manganate" in sl:
        q = f"The listed value is {wv}. How is the H⁺ coefficient fixed in a MnO₄⁻ half-equation in acid?"
        correct = "MnO₄⁻ + 8H⁺ + 5e⁻ → Mn²⁺ + 4H₂O, then scale with the organic half-equation"
        distractors = [
            f"The H⁺ coefficient is {wv} by inspection",
            "Ignore H⁺ in acidic manganate(VII) balancing",
            "Set H⁺ equal to the MnO₄⁻ coefficient only",
        ]
        why = "Balance the MnO₄⁻ half-equation (8H⁺, 5e⁻) first, then combine. That step is independent of the listed distractor."
    else:
        q = f"The value {wv} is not the required ratio. Which electron-count step must be done before the arithmetic?"
        correct = "Find electrons transferred per formula unit, then form the mole ratio"
        distractors = [
            f"Treat {wv} as already the electron count",
            "Divide the two coefficients that appear first in the stem",
            "Use the oxidation number of oxygen only",
        ]
        why = "The missing intermediate is the electron count for each half-equation, not the distractor arithmetic."
    opts, fu_key = place(uid, letter, correct, distractors)
    return _wrap(
        {"stem": q, "options": opts, "key": fu_key, "why": why},
        letter,
        hinge_id,
        hinge_label,
        mx,
        f"Student obtained {wv} by skipping the electron-count step.",
        "intermediate_omission",
    )


def _default_chem(item: dict, uid: str, letter: str, w: str, k_c: str, w_c: str, hinge_id: str, hinge_label: str, mx: str) -> dict:
    focus = clip(w_c or w, 80)
    q = f"For the species or process “{focus}”, is the element under test oxidised, reduced, or unchanged?"
    correct = "Assign oxidation numbers first, then decide oxidised / reduced / unchanged"
    distractors = [
        "Unchanged, because the formula is written the same on both sides",
        "Oxidised if oxygen is present",
        "Reduced if the species is an ion",
    ]
    why = (
        f"The hinge is oxidation-number change. Settle oxidised / reduced / unchanged for "
        f"“{clip(focus, 50)}” before returning to the original item."
    )
    opts, fu_key = place(uid, letter, correct, distractors)
    return _wrap(
        {"stem": q, "options": opts, "key": fu_key, "why": why},
        letter,
        hinge_id,
        hinge_label,
        mx,
        f"Student selected “{clip(w, 40)}” without the oxidised/reduced check.",
        "intermediate_omission",
    )


def author_wrong(item: dict, letter: str, hinge_id: str, hinge_label: str) -> dict | None:
    uid = str(item.get("uid") or "")
    key = (item.get("assessment") or {}).get("mcq_key")
    w = option_text(item, letter)
    r = option_text(item, key)
    mx, pathway, k_c, w_c = classify(item, key, letter)
    if _stmt_set(w) and _stmt_set(r) and _stmt_set(w) != _stmt_set(r):
        row = _three_stmt(item, uid, letter, w, r, hinge_id, hinge_label, mx)
        if row:
            return row
    el = _electrolysis(item, uid, letter, w, hinge_id, hinge_label, mx)
    if el:
        return el
    num = _numeric_redox(item, uid, letter, w, r, hinge_id, hinge_label, mx)
    if num:
        return num
    if FORMULAISH.search(_ascii_form(w)) and len(w) <= 48 and not EQN.search(w):
        row = _os_formula(uid, letter, w, hinge_id, hinge_label, mx, pathway)
        if row:
            return row
    eq = _redox_equation(uid, letter, w, hinge_id, hinge_label, mx)
    if eq:
        return eq
    row = _os_row(uid, letter, w, k_c, w_c, hinge_id, hinge_label, mx)
    if row:
        return row
    return _default_chem(item, uid, letter, w, k_c, w_c, hinge_id, hinge_label, mx)


def author_item(item: dict, units: list[dict]) -> dict | None:
    a = item.get("assessment") or {}
    key = a.get("mcq_key")
    if key not in LETTERS or a.get("key_status") != "available":
        return None
    hinge_id, hinge_label = match_hinge(item, units)
    wrong = {}
    for L in LETTERS:
        if L == key:
            continue
        if not option_text(item, L) and not item.get("options_are_figure"):
            continue
        row = author_wrong(item, L, hinge_id, hinge_label)
        if not row:
            return None
        wrong[L] = row
    if not wrong:
        return None
    r = option_text(item, key)
    solve = (
        f"{hinge_label}. Required: {key} — {clip(r, 120)}. "
        "Assign oxidation numbers (or electrode half-equations) for each option; "
        "the keyed choice is the one that satisfies the hinge."
    )
    rec = {
        "solve": solve,
        "key": key,
        "hinge_id": hinge_id,
        "hinge_label": hinge_label,
        "wrong": wrong,
    }
    rec["modify_seeds"] = seeds_from_lbs(rec, key)
    return rec


def electrochem_items(all_items: list) -> list:
    out = []
    for it in all_items:
        if it.get("pack") != "senior_11_12_as_a":
            continue
        if it.get("chapter_id") == CHAPTER or (it.get("chapter_label") or "") == "Electrochemistry":
            out.append(it)
    return out


def build() -> dict:
    items = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    units = _map_units()
    skip = _skip_uids()
    authored = {}
    n_skip = n_fail = 0
    for it in electrochem_items(items):
        uid = str(it.get("uid") or "")
        if uid in skip:
            n_skip += 1
            continue
        rec = author_item(it, units)
        if not rec or is_stamp_lbs(rec) or not lbs_relevant(it, rec, rec.get("key")):
            n_fail += 1
            continue
        authored[uid] = rec
    doc = {
        "schema": "ttwin.lbs.gold.v1",
        "note": "ISO-GEN LBS overlay for cam:9701:6 Electrochemistry. Gold and spectroscopy uids excluded. mx_type teacher-key only.",
        "n": len(authored),
        "n_skip_preserve": n_skip,
        "n_fail": n_fail,
        "items": authored,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"n": len(authored), "n_skip_preserve": n_skip, "n_fail": n_fail, "file": str(OUT)}


if __name__ == "__main__":
    stats = build()
    print(json.dumps(stats, indent=2))
    sys.exit(0 if stats["n"] else 1)
