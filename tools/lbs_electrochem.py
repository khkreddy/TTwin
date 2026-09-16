#!/usr/bin/env python3
"""ISO-GEN learn-by-solve overlay for Chemistry AS/A Electrochemistry.

Specification before the follow-up: hinge from the packed tags (node C5/H-REDOX
or C5/H-ECHEM) plus the failure mode of that wrong option. Does not rewrite
freeze exam.v1. Gold 9701_m16_qp_12:q1 and spectroscopy uids are not overwritten.
"""
from __future__ import annotations

import hashlib
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
    clip,
    looks_numeric,
    option_text,
    parse_123,
    place,
    seeds_from_lbs,
)
from lbs_quality import AR_DEFAULT, followup_ok, is_stamp_lbs, lbs_relevant

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
    fu.setdefault("format", "single_mcq")
    return {
        "hinge_id": hinge_id,
        "hinge_label": hinge_label,
        "failure_kind": kind,
        "mx_type": mx,
        "pathway": pathway,
        "followup": fu,
    }


def _pick(uid: str, letter: str, n: int) -> int:
    h = hashlib.md5(f"{uid}:{letter}".encode()).hexdigest()
    return int(h, 16) % max(1, n)


def _item_statements(item: dict) -> dict[int, str]:
    out: dict[int, str] = {}
    for x in item.get("statements") or []:
        if isinstance(x, dict) and x.get("n") is not None:
            out[int(x["n"])] = re.sub(r"\s+", " ", str(x.get("text") or "")).strip()
    if len(out) >= 2:
        return out
    return _numbered_statements(item.get("stem") or "")


def _quotes_option(stem: str, option: str) -> bool:
    """True when the hint reprints a combo label or an X/Y/Z row, not when it works a formula."""
    s = re.sub(r"\s+", " ", stem or "")
    o = re.sub(r"\s+", " ", option or "").strip()
    sl = s.lower()
    if "belongs in the correct" in sl or "that species actually have" in sl:
        return True
    if re.search(r"this option is\s+[“\"]", s, re.I) or re.search(r"this option says\s+[“\"]", s, re.I):
        return True
    if re.search(r"option [a-d]\s+is\s+", sl) and _looks_stmt_combo(s):
        return True
    if _looks_stmt_combo(o) and o and o in s:
        return True
    if re.search(r"[XYZ]\s*:\s*[+\-−]?\d+", o) and o[:24] in s:
        return True
    return False


def _os_terms(extra: list[str] | None = None) -> list[str]:
    terms = ["−2", "−1", "0", "+1", "+2", "+3", "+4", "+5", "+6", "+7"]
    for t in extra or []:
        if t not in terms:
            terms.append(t)
    return terms


def _os_term(v: int) -> str:
    if v == 0:
        return "0"
    if v > 0:
        return f"+{v}"
    return f"−{abs(v)}"


def _os_formula(uid: str, letter: str, w: str, hinge_id: str, hinge_label: str, mx: str, pathway: str) -> dict | None:
    os = _oxidation_states(w)
    t = _ascii_form(w)
    if re.search(r"OH", t) and os:
        fu = {
            "format": "fill_blank",
            "stem": (
                f"{clip(w, 40)} has hydroxide groups. In each OH, O is [[O]] and H is [[H]]."
            ),
            "terms": _os_terms(),
            "key": {"O": "−2", "H": "+1"},
            "why": "Hydroxide is O −2 and H +1. Repeating OH does not give two different elements the same state.",
        }
        return _wrap(fu, letter, hinge_id, hinge_label, mx, pathway, "intermediate_omission")
    if re.search(r"SO4", t) and os and "S" in os:
        fu = {
            "format": "fill_blank",
            "stem": f"In {clip(w, 40)}, oxygen is −2. The oxidation number of S is [[S]].",
            "terms": _os_terms(),
            "key": {"S": _os_term(os["S"])},
            "why": f"Sulfate sulfur is {_os_term(os['S'])}. Assign that before using this formula as an option.",
        }
        return _wrap(fu, letter, hinge_id, hinge_label, mx, pathway, "intermediate_omission")
    if re.search(r"NH4", t) and re.search(r"Cl", t):
        fu = {
            "format": "fill_blank",
            "stem": f"In {clip(w, 40)}, the oxidation number of chlorine is [[Cl]].",
            "terms": _os_terms(),
            "key": {"Cl": "−1"},
            "why": f"{clip(w, 30)} is an ammonium halide: Cl is −1.",
        }
        return _wrap(fu, letter, hinge_id, hinge_label, mx, pathway, "intermediate_omission")
    if os:
        el = next((e for e in os if e not in ("O", "H")), list(os)[0])
        fu = {
            "format": "fill_blank",
            "stem": f"In {clip(w, 40)}, the oxidation number of {el} is [[{el}]].",
            "terms": _os_terms([_os_term(os[el])]),
            "key": {el: _os_term(os[el])},
            "why": f"{clip(w, 30)} assigns {el} {_os_term(os[el])}. That assignment is the missing step for this option.",
        }
        return _wrap(fu, letter, hinge_id, hinge_label, mx, pathway, "intermediate_omission")
    fu = _formula_followup(uid, letter, w)
    if not fu:
        return None
    fu = dict(fu)
    fu.setdefault("format", "single_mcq")
    why = fu.get("why") or ""
    if "keyed" in why.lower() or "original" in why.lower():
        fu["why"] = why.split(".")[0] + "."
    return _wrap(fu, letter, hinge_id, hinge_label, mx, pathway, "intermediate_omission")


def _redox_equation(uid: str, letter: str, w: str, hinge_id: str, hinge_label: str, mx: str) -> dict | None:
    if not EQN.search(w) or len(w) < 8:
        return None
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
    pathway = f"Student judged {clip(w, 40)} without assigning oxidation numbers on both sides."
    if name and os_left:
        el = next((e for e in os_left if e not in ("O", "H")), list(os_left)[0])
        fu = {
            "format": "fill_blank",
            "stem": (
                f"In {clip(w, 80)}, on the left the oxidation number of {el} in {name} is [[{el}]]."
            ),
            "terms": _os_terms([_os_term(os_left[el])]),
            "key": {el: _os_term(os_left[el])},
            "why": (
                f"Assign oxidation numbers on each side before deciding whether it is redox. "
                f"On the left, {el} in {name} is {_os_term(os_left[el])}."
            ),
        }
        return _wrap(fu, letter, hinge_id, hinge_label, mx, pathway, "intermediate_omission")
    fu = {
        "format": "fill_blank",
        "stem": (
            f"In {clip(w, 90)}, the equation is redox only if some element’s oxidation number [[1]]."
        ),
        "terms": ["changes", "stays the same", "equals the ion charge", "is zero for every atom"],
        "key": {"1": "changes"},
        "why": (
            "A reaction is redox only if some element’s oxidation number changes. "
            "Work that check on this equation before using it as an option."
        ),
    }
    return _wrap(fu, letter, hinge_id, hinge_label, mx, pathway, "intermediate_omission")


def _fill(stem: str, terms: list[str], key: dict, why: str) -> dict:
    return {"format": "fill_blank", "stem": stem, "terms": terms, "key": key, "why": why}


def _tf(stem: str, truth: bool, why: str) -> dict:
    return {
        "format": "true_false",
        "stem": stem,
        "options": {"T": "True", "F": "False"},
        "key": "T" if truth else "F",
        "why": why,
    }


def _xyz_cells(s: str) -> dict[str, str]:
    return {
        lab: val.replace("−", "-")
        for lab, val in re.findall(r"([A-Z])\s*:\s*([+\-−]?\d+)", s or "")
    }


def _sulfur_xyz_ident(lab: str) -> tuple[str, str, str] | None:
    return {
        "X": (
            "SO₂",
            "+4",
            "Sulfur burns in air to sulfur dioxide. In SO₂, S is +4, not −2 (that value is sulfide, e.g. H₂S).",
        ),
        "Y": (
            "SO₃",
            "+6",
            "SO₂ is oxidised to SO₃. In SO₃, S is +6, not +4.",
        ),
        "Z": (
            "H₂SO₄",
            "+6",
            "SO₃ reacts with water to give sulfuric acid. Sulfur stays +6; dissolving it does not reduce sulfur.",
        ),
    }.get(lab)


def _formula_os_pairs(s: str) -> list[tuple[str, str]]:
    return re.findall(
        r"([A-Za-z][A-Za-z0-9₀-₉()₂₃₄₅₆₇₈₉⁺⁻+\-]*)\s*:\s*([+\-−]?\d+)",
        s or "",
    )


def _os_row(item: dict, uid: str, letter: str, w: str, r: str, hinge_id: str, hinge_label: str, mx: str) -> dict | None:
    """Thinking-prod on the species the row got wrong. Never reprint the row."""
    pairs_w = _formula_os_pairs(w)
    pairs_r = _formula_os_pairs(r)
    xyz_labels = {a for a, _ in pairs_w} <= set("XYZW") and all(len(a) == 1 for a, _ in pairs_w)
    if len(pairs_w) >= 2 and len(pairs_r) >= 2 and not xyz_labels:
        rw = {a.replace("−", "-"): b.replace("−", "-") for a, b in pairs_w}
        rr = {a.replace("−", "-"): b.replace("−", "-") for a, b in pairs_r}
        diffs = [name for name in rw if rr.get(name) != rw.get(name)]
        if diffs:
            name = diffs[0]
            os = _oxidation_states(name) or _oxidation_states(_ascii_form(name))
            # Elemental S / SO2 / thiosulfate
            if name in {"S", "S(s)"} or re.fullmatch(r"S", name):
                fu = _fill(
                    "In elemental sulfur, S(s), the oxidation number of sulfur is [[S]].",
                    _os_terms(["0"]),
                    {"S": "0"},
                    "An uncombined element has oxidation number 0.",
                )
                return _wrap(fu, letter, hinge_id, hinge_label, mx, "Student did not assign 0 to S(s).", "intermediate_omission")
            if os:
                el = next((e for e in os if e not in ("O", "H", "Na", "K") or len(os) == 1), list(os)[0])
                if "S" in os and ("s2o3" in _ascii_form(name).lower() or name.startswith("Na")):
                    el = "S"
                osn = _os_term(os[el])
                fu = _fill(
                    f"In {name}, the oxidation number of {el} is [[{el}]].",
                    _os_terms([osn]),
                    {el: osn},
                    f"Assign the usual oxidation numbers in {name}; {el} is {osn}.",
                )
                return _wrap(fu, letter, hinge_id, hinge_label, mx, f"Student mis-assigned {el} in {name}.", "intermediate_omission")
    cells_w = _xyz_cells(w)
    cells_r = _xyz_cells(r)
    sl = (item.get("stem") or "").lower()
    sulfur = ("sulfur" in sl or "sulphur" in sl) and ("burn" in sl or "oxidis" in sl)
    if cells_w and cells_r and sulfur:
        diffs = [lab for lab in cells_w if cells_w.get(lab) != cells_r.get(lab)]
        if not diffs:
            diffs = list(cells_w)
        # Prefer a label unique to this wrong row among other wrongs.
        others = []
        opts = item.get("options") or {}
        key = (item.get("assessment") or {}).get("mcq_key")
        for L, txt in opts.items():
            if L in (key, letter):
                continue
            others.append(_xyz_cells(txt))
        ranked = sorted(diffs, key=lambda lab: sum(1 for o in others if o.get(lab) == cells_w.get(lab)))
        lab = ranked[0]
        ident = _sulfur_xyz_ident(lab)
        if ident:
            name, osn, sci = ident
            fu = _fill(
                f"In {name}, the oxidation number of sulfur is [[S]].",
                _os_terms([osn]),
                {"S": osn},
                sci,
            )
            return _wrap(
                fu, letter, hinge_id, hinge_label, mx,
                f"Student assigned the wrong oxidation number to {name} in the X/Y/Z sequence.",
                "intermediate_omission",
            )
    if not re.search(r"[+\-−]\s*\d", w) and "oxidation" not in w.lower():
        return None
    # Generic OS-row: ask a named species from the stem, never quote the option row.
    if sulfur:
        fu = _fill(
            "When sulfur burns in air, the oxidation number of sulfur in the gaseous product is [[S]].",
            _os_terms(["+4"]),
            {"S": "+4"},
            "The combustion product is SO₂, in which sulfur is +4.",
        )
        return _wrap(fu, letter, hinge_id, hinge_label, mx, "Student skipped identifying the combustion product.", "intermediate_omission")
    return None


def _stmt_thinking(item: dict, uid: str, letter: str, body: str, statement_is_true: bool) -> dict | None:
    """A small chemistry task that tests the disputed statement. Never reprints 1/2/3 combos."""
    b = re.sub(r"<[^>]+>", " ", body or "")
    b = re.sub(r"\s+", " ", b).strip()
    bl = b.lower()
    if not b:
        return None

    if "chlorine" in bl and "negative" in bl:
        # Canonical unlock for this trap: Cl in HClO is +1 (owner example).
        bank = [
            ("HClO", "+1", "H is +1 and O is −2, so Cl in HClO is +1."),
            ("KClO₃", "+5", "K is +1 and three O at −2, so Cl in KClO₃ is +5."),
        ]
        name, osn, sci = bank[0] if letter in {"A", "C"} and uid.endswith(":q33") else bank[_pick(uid, letter, len(bank))]
        if letter == "C":
            name, osn, sci = bank[0]
        return _fill(
            f"In {name}, the oxidation number of chlorine is [[Cl]].",
            _os_terms([osn]),
            {"Cl": osn},
            sci + " Chlorine in a compound is not always negative.",
        )
    if "sodium" in bl and "positive" in bl:
        return _fill(
            "In NaCl, the oxidation number of sodium is [[Na]].",
            _os_terms(["+1"]),
            {"Na": "+1"},
            "Sodium in a salt is +1. That claim is true.",
        )
    if "sum" in bl and "oxidation" in bl and "zero" in bl:
        return _fill(
            "In H₂O, the oxidation numbers of the two hydrogen atoms and the oxygen atom sum to [[sum]].",
            ["0", "+1", "−2", "+2", "the charge of the ion"],
            {"sum": "0"},
            "In a neutral compound the oxidation numbers sum to zero.",
        )
    if "bauxite" in bl and "melting" in bl:
        return _fill(
            "In the extraction of aluminium, [[1]] is mixed with Al₂O₃ to lower the melting point of the electrolyte.",
            ["cryolite", "bauxite", "graphite", "pure alumina"],
            {"1": "cryolite"},
            "Cryolite, not bauxite, is the solvent that lowers the melting point.",
        )
    if "cathode" in bl and ("oxygen" in bl or "graphite" in bl or "co₂" in bl or "co2" in bl):
        return _fill(
            "In molten-Al₂O₃ electrolysis, O²⁻ is oxidised at the carbon [[1]].",
            ["anode", "cathode"],
            {"1": "anode"},
            "Oxygen is liberated at the anode, not the cathode. The carbon anode then burns to CO₂.",
        )
    if "disproportionation" in bl:
        return _tf(
            "In 4KClO₃ → 3KClO₄ + KCl, some chlorine atoms increase in oxidation number and some decrease.",
            True,
            "The same element is both oxidised and reduced: that is disproportionation.",
        )
    m = re.search(
        r"oxidation (?:state|number) of (chlorine|cl) in ([A-Za-z0-9₀-₉()₄₃₂]+)",
        bl,
    )
    if m:
        formula = m.group(2)
        # recover original formula casing from body if possible
        fm = re.search(r"\b(KClO[₃3]|NaClO[₃3]|HClO[₄4]|KClO4|NaClO3)\b", b)
        form = fm.group(1) if fm else formula
        os = _oxidation_states(form) or _oxidation_states(form.replace("₃", "3").replace("₄", "4"))
        if os and "Cl" in os:
            osn = _os_term(os["Cl"])
            return _fill(
                f"In {form}, the oxidation number of chlorine is [[Cl]].",
                _os_terms([osn]),
                {"Cl": osn},
                f"Assign K/Na/H = +1 and O = −2, then Cl is {osn}.",
            )
    if re.search(r"\bh\s*\+|h⁺|h\+\(aq\)", bl) and "oxid" in bl:
        return _tf(
            "In 2H⁺ + 2NO₂⁻ → H₂O + NO + NO₂, the oxidation number of hydrogen increases.",
            False,
            "Hydrogen stays +1. It is not oxidised. Nitrogen disproportionates (NO₂⁻ → NO and NO₂).",
        )
    if EQN.search(b) or re.search(r"→|->", b):
        ascii_b = _ascii_form(b)
        if re.search(r"Br2|Br₂", b) and re.search(r"CaBr|H2SO4|H₂SO₄", b):
            return _fill(
                "In Br₂, the oxidation number of bromine is [[Br]].",
                _os_terms(["0"]),
                {"Br": "0"},
                "Elemental bromine is 0. In CaBr₂ bromine is −1, so that reaction is redox.",
            )
        if re.search(r"H3PO4|H₃PO₄|HBr", b) and re.search(r"CaBr", b):
            return _fill(
                "In CaBr₂ and in HBr, the oxidation number of bromine is [[Br]].",
                _os_terms(["−1"]),
                {"Br": "−1"},
                "Bromine is −1 on both sides, so this metathesis is not redox.",
            )
        if re.search(r"AgNO3|AgNO₃|AgBr", b):
            return _tf(
                "In CaBr₂ + 2AgNO₃ → Ca(NO₃)₂ + 2AgBr, any element changes oxidation number.",
                False,
                "This is precipitation. Oxidation numbers are unchanged, so it is not redox.",
            )
        if re.search(r"SO3|SO₃", b) and re.search(r"H2O|H₂O", b) and re.search(r"H2SO4|H₂SO₄", b):
            return _fill(
                "When SO₃ reacts with water to give H₂SO₄, the oxidation number of sulfur [[1]].",
                ["stays +6", "falls to +4", "rises to +8", "becomes 0"],
                {"1": "stays +6"},
                "S is +6 in both SO₃ and H₂SO₄. Combining with water is not redox.",
            )
        if re.search(r"NaClO|ClO\b", b) and re.search(r"NaCl\b", b):
            return _fill(
                "In NaClO, the oxidation number of chlorine is [[Cl]]; in NaCl it is [[Cl2]].",
                _os_terms(["+1", "−1"]),
                {"Cl": "+1", "Cl2": "−1"},
                "Cl in hypochlorite is +1 and falls to −1 in chloride, so ClO⁻ is reduced.",
            )
        # generic: OS of a simple formula in the equation
        os_hit = None
        for sp in re.findall(r"[A-Z][a-z]?(?:[A-Z][a-z]?|\d|₀-₉|\(|\))*", ascii_b):
            if sp.count("(") != sp.count(")"):
                continue
            if FORMULAISH.search(_ascii_form(sp)) and 1 < len(sp) <= 18:
                os_hit = _oxidation_states(sp)
                if os_hit:
                    el = next((e for e in os_hit if e not in ("O", "H")), list(os_hit)[0])
                    osn = _os_term(os_hit[el])
                    return _fill(
                        f"In {sp}, the oxidation number of {el} is [[{el}]].",
                        _os_terms([osn]),
                        {el: osn},
                        f"Assign oxidation numbers in {sp} before judging whether that reaction is redox.",
                    )
        return _tf(
            f"Deciding whether {clip(b, 70)} is redox requires checking oxidation numbers on both sides.",
            True,
            "A reaction is redox only if some element’s oxidation number changes. Do that check on this equation.",
        )
    m = re.match(r"(aluminium|aluminum|chlorine|nitrogen|sulfur|sulphur|oxygen|manganese|tin)\s+is\s+(oxidised|reduced)", bl)
    if m:
        el_name, verb = m.group(1), m.group(2)
        if el_name.startswith("alum"):
            return _fill(
                "In the shuttle reaction, Al (0) becomes Al in Al₂O₃. Aluminium is [[1]].",
                ["oxidised", "reduced", "unchanged"],
                {"1": "oxidised"},
                "Aluminium’s oxidation number rises from 0 to +3, so it is oxidised.",
            )
        if el_name == "chlorine" and verb == "reduced":
            return _fill(
                "In NH₄ClO₄, Cl is +7; in AlCl₃, Cl is −1. Chlorine is [[1]].",
                ["reduced", "oxidised", "unchanged"],
                {"1": "reduced"},
                "Chlorine’s oxidation number falls, so chlorine is reduced.",
            )
        if el_name == "nitrogen" and verb == "oxidised":
            return _fill(
                "In NH₄⁺, N is −3; in N₂, N is 0. Nitrogen is [[1]].",
                ["oxidised", "reduced", "unchanged"],
                {"1": "oxidised"},
                "Nitrogen’s oxidation number rises from −3 to 0, so nitrogen is oxidised.",
            )
    if "reducing agent" in bl:
        return _tf(
            "A reducing agent is oxidised: its oxidation number increases.",
            True,
            "If chlorine’s oxidation number falls, chlorine is reduced, so it is not acting as a reducing agent.",
        )
    if "three moles of electrons" in bl or "3 mol" in bl:
        return _fill(
            "Al³⁺ + [[n]]e⁻ → Al. How many moles of electrons are needed per mole of Al³⁺?",
            ["1", "2", "3", "6"],
            {"n": "3"},
            "Each Al³⁺ gains three electrons.",
        )
    return None


def _three_stmt(item: dict, uid: str, letter: str, w: str, r: str, hinge_id: str, hinge_label: str, mx: str) -> dict | None:
    if not (_looks_stmt_combo(w) and _looks_stmt_combo(r)):
        return None
    extra = _stmt_set(w) - _stmt_set(r)
    missing = _stmt_set(r) - _stmt_set(w)
    n = sorted(extra or missing)[0] if (extra or missing) else None
    if n is None:
        return None
    stmts = _item_statements(item)
    body = stmts.get(n) or ""
    statement_is_true = n not in extra
    fu = _stmt_thinking(item, uid, letter, body, statement_is_true)
    if not fu:
        return None
    pathway = f"Student mis-classified statement {n}: {clip(body or str(n), 50)}."
    return _wrap(fu, letter, hinge_id, hinge_label, mx, pathway, "intermediate_omission")


def _electrolysis(item: dict, uid: str, letter: str, w: str, hinge_id: str, hinge_label: str, mx: str) -> dict | None:
    sl = (item.get("stem") or "").lower()
    wl = (w or "").lower()
    if not any(s in sl for s in ("electrolys", "cryolite", "anode", "cathode", "aluminium oxide", "al₂o₃", "al2o3")):
        return None
    if "cryolite" in sl and ("oxid" in wl or "corrosion" in wl):
        fu = {
            "format": "assertion_reason",
            "stem": "Decide assertion and reason about cryolite in the extraction of aluminium.",
            "assertion": clip(w, 90),
            "reason": "Cryolite dissolves Al₂O₃ and lowers the melting temperature of the electrolyte.",
            "options": dict(AR_DEFAULT),
            "key": "D",
            "why": (
                "The option’s claim about oxidation/corrosion is false. "
                "Cryolite is a solvent that lowers the melting point; Al³⁺ is still reduced at the cathode."
            ),
        }
        kind = "term_substitution"
        return _wrap(
            fu, letter, hinge_id, hinge_label, mx or kind,
            f"Student used “{clip(w, 40)}” without the cathode/cryolite distinction.",
            kind,
        )
    if "cryolite" in sl and ("melting" in wl or "solvent" in wl or "cryolite" in wl):
        fu = {
            "format": "multi_mcq",
            "stem": "Which of these are roles of cryolite mixed with Al₂O₃?",
            "options": {
                "A": "It lowers the melting point of the electrolyte",
                "B": "It dissolves aluminium oxide",
                "C": "It is reduced to aluminium metal",
                "D": "It prevents oxidation of the product aluminium",
            },
            "key": ["A", "B"],
            "why": (
                "Cryolite is a solvent that lowers the melting point of aluminium oxide. "
                "Aluminium is still produced by reduction of Al³⁺ at the cathode."
            ),
        }
        kind = "intermediate_omission"
        return _wrap(
            fu, letter, hinge_id, hinge_label, mx or kind,
            f"Student used “{clip(w, 40)}” without the cathode/cryolite distinction.",
            kind,
        )
    if "anode" in wl or "cathode" in wl or "oxidised" in wl or "reduced" in wl:
        fu = {
            "format": "match",
            "stem": "Match each species to its role in molten electrolysis of the metal oxide.",
            "left": {
                "1": "Al³⁺",
                "2": "O²⁻",
                "3": "cryolite",
            },
            "right": {
                "P": "reduced at the cathode",
                "Q": "oxidised at the carbon anode",
                "R": "lowers the melting point of Al₂O₃",
                "S": "oxidised at the cathode",
            },
            "key": {"1": "P", "2": "Q", "3": "R"},
            "why": (
                "Cations are reduced at the cathode. Oxide ions are oxidised at the carbon anode. "
                "Cryolite is the solvent, not a source of aluminium metal."
            ),
        }
        kind = "relationship_reversal"
        return _wrap(
            fu, letter, hinge_id, hinge_label, mx or kind,
            f"Student used “{clip(w, 40)}” without the cathode/cryolite distinction.",
            kind,
        )
    fu = {
        "format": "fill_blank",
        "stem": "Cations are [[1]] at the [[2]]; cryolite is the [[3]].",
        "terms": ["reduced", "oxidised", "cathode", "anode", "solvent"],
        "key": {"1": "reduced", "2": "cathode", "3": "solvent"},
        "why": "Separate the solvent role of cryolite from the electrode half-equations before judging this option.",
    }
    kind = "intermediate_omission"
    return _wrap(
        fu, letter, hinge_id, hinge_label, mx or kind,
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
        fu = {
            "format": "multi_mcq",
            "stem": (
                f"The listed value is {wv}. For FeC₂O₄ with MnO₄⁻, which contributions "
                "make up the electrons lost per 1 mol FeC₂O₄?"
            ),
            "options": {
                "A": "Fe²⁺ → Fe³⁺ (1 e⁻)",
                "B": "C₂O₄²⁻ → 2CO₂ (2 e⁻)",
                "C": "MnO₄⁻ → Mn²⁺ (5 e⁻ copied as the FeC₂O₄ count)",
                "D": "Each oxygen atom in the oxalate loses 2 e⁻",
            },
            "key": ["A", "B"],
            "why": (
                "Fe²⁺ loses 1e⁻ and C₂O₄²⁻ loses 2e⁻, so 1 mol FeC₂O₄ loses 3 mol e⁻. "
                "MnO₄⁻ gains 5e⁻. Combine those counts before using a listed value."
            ),
        }
        return _wrap(
            fu, letter, hinge_id, hinge_label, mx,
            f"Student obtained {wv} by skipping the electron-count step.",
            "intermediate_omission",
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
        {"format": "single_mcq", "stem": q, "options": opts, "key": fu_key, "why": why},
        letter,
        hinge_id,
        hinge_label,
        mx,
        f"Student obtained {wv} by skipping the electron-count step.",
        "intermediate_omission",
    )


def _default_chem(item: dict, uid: str, letter: str, w: str, k_c: str, w_c: str, hinge_id: str, hinge_label: str, mx: str) -> dict:
    focus = clip(w_c or w, 80)
    if _looks_stmt_combo(w) or re.search(r"[XYZ]\s*:", w or "") or _quotes_option(focus, w):
        focus = "the species under test"
    fu = {
        "format": "fill_blank",
        "stem": (
            f"For {focus}, assign oxidation numbers first. "
            "The species is [[1]] if OS increases, [[2]] if OS decreases, or [[3]] if OS stays the same."
        ),
        "terms": ["oxidised", "reduced", "unchanged"],
        "key": {"1": "oxidised", "2": "reduced", "3": "unchanged"},
        "why": (
            f"The hinge is oxidation-number change. Settle oxidised / reduced / unchanged for "
            f"“{clip(focus, 50)}” before returning to this item."
        ),
    }
    return _wrap(
        fu,
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
    if FORMULAISH.search(_ascii_form(w)) and len(w) <= 48 and not EQN.search(w) and not re.search(r":\s*[+\-−]?\d", w):
        row = _os_formula(uid, letter, w, hinge_id, hinge_label, mx, pathway)
        if row:
            return row
    eq = _redox_equation(uid, letter, w, hinge_id, hinge_label, mx)
    if eq:
        return eq
    row = _os_row(item, uid, letter, w, r, hinge_id, hinge_label, mx)
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
        fu = (row or {}).get("followup") or {}
        if not row or not followup_ok(fu) or _quotes_option(fu.get("stem") or "", option_text(item, L)):
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
