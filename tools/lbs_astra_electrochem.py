#!/usr/bin/env python3
"""Instantiate Astra-harness LBS for AS/A electrochemistry.

Writes a SEPARATE overlay. Does not touch data/overlay/lbs_electrochem.json
or rewrite freeze exam.v1. Zero model calls at packed-item grain.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from lbs_construct import (  # noqa: E402
    LETTERS,
    _oxidation_states,
    option_text,
)
from lbs_electrochem import (  # noqa: E402
    _ascii_form,
    _fill,
    _formula_os_pairs,
    _item_statements,
    _looks_stmt_combo,
    _os_term,
    _os_terms,
    _quotes_option,
    _stmt_set,
    _sulfur_xyz_ident,
    _tf,
    _xyz_cells,
)
from lbs_quality import followup_ok  # noqa: E402

MAP = ROOT / "data/maps/chemistry.json"
PACKED = ROOT / "data/questions/chemistry-senior.json"
GRAIN = ROOT / "data/lbs/grain_bindings.v1.json"
CURRENT = ROOT / "data/overlay/lbs_electrochem.json"
NEVER = ROOT / "data/lbs/never_cases.v1.json"
OUT_OV = ROOT / "data/overlay/lbs_electrochem_astra.json"
OUT_EX = ROOT / "data/lbs/astra_electrochem_explain.json"
OUT_CMP = ROOT / "review/lbs-compare/compare.json"


def _sha(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def _blob(item: dict) -> str:
    opts = item.get("options") or {}
    return " ".join(
        [str(item.get("stem") or "")] + [str(opts.get(L) or "") for L in LETTERS]
    ).lower()


def _load_units() -> dict[str, dict]:
    doc = json.loads(MAP.read_text(encoding="utf-8"))
    return {u["unit_id"]: u for u in doc.get("units") or []}


def _candidates(item: dict, bindings: list[dict]) -> tuple[str, list[str], str]:
    ch = item.get("chapter_id")
    node = str(item.get("node") or "").replace("chem:", "")
    for b in bindings:
        t = b.get("tags") or {}
        if t.get("chapter_id") == ch and t.get("node") == node:
            return b["binding_id"], list(b.get("candidates") or []), b.get("evidence") or ""
    return "", [], "MISSING_CAMBRIDGE_GRAIN"


def _pick_unit(item: dict, cands: list[str], units: dict[str, dict]) -> tuple[str, str]:
    blob = _blob(item)
    ascii_blob = _ascii_form(blob).lower()
    stem = (item.get("stem") or "").lower()
    guards = [
        ("cryolite" in blob or ("al2o3" in ascii_blob and "electro" in blob), "H018"),
        ("faraday" in blob or re.search(r"\b(coulomb|ampere|deposited mass)\b", blob), "H017"),
        ("disproportion" in blob, "H009"),
        ("average oxidation" in blob or "fractional" in blob, "H010"),
        (bool(_xyz_cells(" ".join((item.get("options") or {}).values()))), "H005"),
        ("oxidation number" in blob or "oxidation state" in blob, "H005"),
        ("which of the following statements" in stem and "always" in stem, "H005"),
        ("anode" in blob or "cathode" in blob or "electrolys" in blob, "H018"),
        ("fec2o4" in ascii_blob or "ethanedioate" in blob or "oxalate" in blob, "H006"),
        ("oxidised" in blob or "reduced" in blob or "oxidizing" in blob or "reducing agent" in blob, "H006"),
        ("redox" in blob, "H001"),
        ("half-reaction" in blob or "half reaction" in blob, "H003"),
    ]
    for ok, hid in guards:
        if not ok:
            continue
        for uid in cands:
            if uid.endswith("/" + hid) and uid in units:
                return uid, f"task_guard:{hid}"
    if cands and cands[0] in units:
        return cands[0], "grain_default_first_candidate"
    return "", "AMBIGUOUS_UNIT"


def _wrap_fu(fu: dict, unit: dict, mx: dict | None, step_id: str, why_join: str) -> dict:
    fu = dict(fu)
    fu.setdefault("format", "single_mcq")
    return fu


def _never_hit(stem: str) -> bool:
    s = stem or ""
    if "belongs in the correct" in s.lower():
        return True
    if "that species actually have" in s.lower():
        return True
    if re.search(r"option [a-d] is\s+[“\"]", s, re.I) and "are correct" in s.lower():
        return True
    if re.search(r"this option is\s+[“\"]", s, re.I):
        return True
    return False


def _route_combo(item: dict, letter: str, w: str, r: str, unit: dict) -> tuple[dict | None, dict]:
    extra = _stmt_set(w) - _stmt_set(r)
    missing = _stmt_set(r) - _stmt_set(w)
    n = sorted(extra or missing)[0] if (extra or missing) else None
    if n is None:
        return None, {"gap": "MISSING_MX_MATCH", "detail": "combo sets equal"}
    stmts = _item_statements(item)
    body = stmts.get(n) or ""
    bl = body.lower()
    law = ((unit.get("mechanism") or {}).get("law") or "")
    explain = {
        "statement_n": n,
        "statement_body": body,
        "included_wrong": n in extra,
    }
    if "chlorine" in bl and "negative" in bl:
        fu = _fill(
            "In HClO, the oxidation number of chlorine is [[Cl]].",
            _os_terms(["+1"]),
            {"Cl": "+1"},
            "H is +1 and O is −2, so Cl in HClO is +1. Chlorine in a compound is not always negative. "
            + (f"Map law: {law}" if law else ""),
        )
        explain.update(
            {
                "route": "intermediate_omission",
                "step_id": "S3",
                "mx_id": None,
                "grounding": "HClO counterexample licensed by H005 neutral-sum rule",
                "why_unit": unit.get("decision_hinge"),
            }
        )
        return fu, explain
    if "sodium" in bl and "positive" in bl:
        fu = _fill(
            "In NaCl, the oxidation number of sodium is [[Na]].",
            _os_terms(["+1"]),
            {"Na": "+1"},
            "Sodium in a salt is +1. " + (law or ""),
        )
        explain.update({"route": "intermediate_omission", "step_id": "S3", "grounding": "NaCl"})
        return fu, explain
    if "sum" in bl and "zero" in bl:
        fu = _fill(
            "In H₂O, the oxidation numbers of the two hydrogen atoms and the oxygen atom sum to [[sum]].",
            ["0", "+1", "−2", "+2"],
            {"sum": "0"},
            "In a neutral compound oxidation numbers sum to zero.",
        )
        explain.update({"route": "intermediate_omission", "step_id": "S3", "grounding": "H2O"})
        return fu, explain
    if "bauxite" in bl and "melting" in bl:
        fu = _fill(
            "In aluminium extraction, [[1]] is mixed with Al₂O₃ to lower the melting point of the electrolyte.",
            ["cryolite", "bauxite", "graphite", "pure alumina"],
            {"1": "cryolite"},
            "Cryolite, not bauxite, lowers the melting point of alumina.",
        )
        explain.update({"route": "term_substitution", "grounding": "cryolite vs bauxite"})
        return fu, explain
    os = _oxidation_states(body) or _oxidation_states(_ascii_form(body))
    if os:
        el = next((e for e in os if e not in ("O", "H")), list(os)[0])
        fu = _fill(
            f"In the species named in statement {n}, the oxidation number of {el} is [[{el}]].",
            _os_terms([_os_term(os[el])]),
            {el: _os_term(os[el])},
            f"Assign usual oxidation numbers; {el} is {_os_term(os[el])}.",
        )
        explain.update({"route": "intermediate_omission", "step_id": "S3", "grounding": f"OS of {el}"})
        return fu, explain
    return None, {"gap": "UNSUPPORTED_TASK_GRAMMAR", "detail": f"statement {n} not bound", "body": body[:160]}


def _route_xyz(item: dict, letter: str, w: str, r: str, unit: dict) -> tuple[dict | None, dict]:
    cells_w, cells_r = _xyz_cells(w), _xyz_cells(r)
    if not (cells_w and cells_r):
        return None, {"gap": "MISSING_MX_MATCH"}
    sl = (item.get("stem") or "").lower()
    sulfur = ("sulfur" in sl or "sulphur" in sl) and ("burn" in sl or "oxidis" in sl)
    diffs = [lab for lab in cells_w if cells_w.get(lab) != cells_r.get(lab)] or list(cells_w)
    lab = diffs[0]
    ident = _sulfur_xyz_ident(lab) if sulfur else None
    if ident:
        name, osn, sci = ident
        fu = _fill(
            f"In {name}, the oxidation number of sulfur is [[S]].",
            _os_terms([osn]),
            {"S": osn},
            sci + " Map hinge: " + str(unit.get("decision_hinge") or ""),
        )
        return fu, {
            "route": "intermediate_omission",
            "step_id": "S3",
            "label": lab,
            "species": name,
            "why_anchor": f"Wrong cell {lab} maps to named species {name}; not 'that species'.",
        }
    return None, {"gap": "UNRESOLVED_ENTITY_REFERENCE", "detail": "X/Y/Z not bound to a named species"}


def _route_formula(w: str, unit: dict) -> tuple[dict | None, dict]:
    pairs = _formula_os_pairs(w)
    if len(pairs) >= 2 and not ({a for a, _ in pairs} <= set("XYZW")):
        name = pairs[0][0]
        os = _oxidation_states(name) or _oxidation_states(_ascii_form(name))
        if name in {"S", "S(s)"}:
            fu = _fill(
                "In elemental sulfur, S(s), the oxidation number of sulfur is [[S]].",
                _os_terms(["0"]),
                {"S": "0"},
                "An uncombined element has oxidation number 0 (H005 S1).",
            )
            return fu, {"route": "intermediate_omission", "step_id": "S1", "species": "S(s)"}
        if os:
            el = "S" if "S" in os else next(iter(os))
            osn = _os_term(os[el])
            fu = _fill(
                f"In {name}, the oxidation number of {el} is [[{el}]].",
                _os_terms([osn]),
                {el: osn},
                f"H005 bookkeeping: {el} in {name} is {osn}.",
            )
            return fu, {"route": "intermediate_omission", "step_id": "S3", "species": name, "element": el}
    os = _oxidation_states(w) or _oxidation_states(_ascii_form(w))
    t = _ascii_form(w)
    if re.search(r"OH", t) and os:
        fu = _fill(
            f"{w[:40]} has hydroxide groups. In each OH, O is [[O]] and H is [[H]].",
            _os_terms(),
            {"O": "−2", "H": "+1"},
            "Hydroxide is O −2 and H +1 (H005 rules). Repeating OH is the same elements.",
        )
        return fu, {"route": "scope_error", "step_id": "S3", "species": w[:40]}
    if os:
        el = next((e for e in os if e not in ("O", "H")), list(os)[0])
        fu = _fill(
            f"In {w[:40]}, the oxidation number of {el} is [[{el}]].",
            _os_terms([_os_term(os[el])]),
            {el: _os_term(os[el])},
            f"H005: {el} is {_os_term(os[el])}.",
        )
        return fu, {"route": "intermediate_omission", "step_id": "S3", "species": w[:40], "element": el}
    return None, {"gap": "UNSUPPORTED_TASK_GRAMMAR"}


def _route_electrolysis(item: dict, w: str, unit: dict) -> tuple[dict | None, dict]:
    wl, sl = w.lower(), _blob(item)
    if "cryolite" in sl and ("oxid" in wl or "corrosion" in wl):
        fu = {
            "format": "assertion_reason",
            "stem": "Decide assertion and reason about cryolite in aluminium extraction.",
            "assertion": (w or "")[:90],
            "reason": "Cryolite dissolves Al₂O₃ and lowers the melting temperature of the electrolyte.",
            "options": {
                "A": "Both A and R are true, and R is the correct explanation of A",
                "B": "Both A and R are true, but R is not the correct explanation of A",
                "C": "A is true, but R is false",
                "D": "A is false, but R is true",
            },
            "key": "D",
            "why": "The oxidation/corrosion claim is false. Cryolite is the solvent that lowers melting point (H018 products/roles).",
        }
        return fu, {"route": "term_substitution", "mx_hint": "cryolite as anti-oxidant", "step_id": "S1"}
    if "cryolite" in sl:
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
            "why": "Cryolite is solvent + melting-point lowerer. Al metal still comes from Al³⁺ at the cathode (H018).",
        }
        return fu, {"route": "intermediate_omission", "step_id": "S1"}
    if "anode" in wl or "cathode" in wl or "oxidised" in wl or "reduced" in wl:
        fu = {
            "format": "match",
            "stem": "Match each species to its role in molten electrolysis of the metal oxide.",
            "left": {"1": "Al³⁺", "2": "O²⁻", "3": "cryolite"},
            "right": {
                "P": "reduced at the cathode",
                "Q": "oxidised at the carbon anode",
                "R": "lowers the melting point of Al₂O₃",
                "S": "oxidised at the cathode",
            },
            "key": {"1": "P", "2": "Q", "3": "R"},
            "why": "Cations reduced at cathode; oxide oxidised at carbon anode; cryolite is solvent (H003/H018).",
        }
        return fu, {"route": "relationship_reversal", "step_id": "S2"}
    fu = _fill(
        "Cations are [[1]] at the [[2]]; cryolite is the [[3]].",
        ["reduced", "oxidised", "cathode", "anode", "solvent"],
        {"1": "reduced", "2": "cathode", "3": "solvent"},
        "Electrode identity is the missing step (H003).",
    )
    return fu, {"route": "intermediate_omission", "step_id": "S2"}


def _route_default(unit: dict, w: str) -> tuple[dict, dict]:
    hinge = unit.get("decision_hinge") or "oxidation-number change"
    law = ((unit.get("mechanism") or {}).get("law") or "").strip()
    fu = _fill(
        "Assign oxidation numbers first. The species is [[1]] if OS increases, [[2]] if OS decreases, or [[3]] if OS stays the same.",
        ["oxidised", "reduced", "unchanged"],
        {"1": "oxidised", "2": "reduced", "3": "unchanged"},
        (law or hinge) + " This is the hinge move, not a reprint of the clicked option.",
    )
    return fu, {"route": "intermediate_omission", "step_id": "S1", "fallback": True, "hinge": hinge}


def author_letter(item: dict, letter: str, unit: dict) -> tuple[dict | None, dict]:
    key = (item.get("assessment") or {}).get("mcq_key")
    w = option_text(item, letter)
    r = option_text(item, key)
    uid_unit = unit.get("unit_id")
    blob = _blob(item)
    fu, ex = None, {}
    if _looks_stmt_combo(w) and _looks_stmt_combo(r) and _stmt_set(w) != _stmt_set(r):
        fu, ex = _route_combo(item, letter, w, r, unit)
    if fu is None and (_xyz_cells(w) and _xyz_cells(r)):
        fu, ex = _route_xyz(item, letter, w, r, unit)
    if fu is None and ("cryolite" in blob or "electrolys" in blob or "anode" in blob or "cathode" in blob):
        fu, ex = _route_electrolysis(item, w, unit)
    ascii_all = _ascii_form(_blob(item) + " " + (w or ""))
    if fu is None and ("fec2o4" in ascii_all or "ethanedioate" in blob or "oxalate" in blob):
        fu = {
            "format": "multi_mcq",
            "stem": (
                "For FeC₂O₄ with MnO₄⁻, which contributions make up the electrons "
                "lost per 1 mol FeC₂O₄?"
            ),
            "options": {
                "A": "Fe²⁺ → Fe³⁺ (1 e⁻)",
                "B": "C₂O₄²⁻ → 2CO₂ (2 e⁻)",
                "C": "MnO₄⁻ → Mn²⁺ (5 e⁻ copied as the FeC₂O₄ count)",
                "D": "Each oxygen atom in the oxalate loses 2 e⁻",
            },
            "key": ["A", "B"],
            "why": (
                "Fe²⁺ loses 1e⁻ and C₂O₄²⁻ loses 2e⁻ (H006 OS-change). "
                "MnO₄⁻ gaining 5e⁻ is the titrant count, not the FeC₂O₄ count."
            ),
        }
        ex = {"route": "intermediate_omission", "step_id": "S1", "grounding": "FeC2O4 electron count"}
    if fu is None:
        fu, ex = _route_formula(w, unit)
        if fu is None:
            fu, ex = _route_default(unit, w)
    if not fu or _never_hit(fu.get("stem") or "") or _quotes_option(fu.get("stem") or "", w):
        return None, {"gap": "OPTION_REPRINT" if fu and _never_hit(fu.get("stem") or "") else ex.get("gap") or "QUALITY_GATE"}
    if not followup_ok(fu):
        return None, {"gap": "FOLLOWUP_NOT_OK", "stem": (fu.get("stem") or "")[:160]}
    ex = dict(ex)
    ex.update(
        {
            "unit_id": uid_unit,
            "decision_hinge": unit.get("decision_hinge"),
            "map_law": ((unit.get("mechanism") or {}).get("law") or "")[:280],
            "mx_type": ex.get("route") if ex.get("route") in {
                "term_substitution", "condition_omission", "relationship_reversal",
                "scope_error", "surface_feature_capture", "mechanism_conflation", "operation_confusion",
            } else "intermediate_omission",
        }
    )
    return fu, ex


def build() -> dict:
    units = _load_units()
    bindings = (json.loads(GRAIN.read_text(encoding="utf-8")).get("bindings") or [])
    packed = json.loads(PACKED.read_text(encoding="utf-8"))
    current = (json.loads(CURRENT.read_text(encoding="utf-8")).get("items") or {}) if CURRENT.is_file() else {}
    scope = [
        it
        for it in packed
        if it.get("pack") == "senior_11_12_as_a"
        and it.get("chapter_id") in ("cam:9701:6", "cam:9701:24")
        and (it.get("assessment") or {}).get("mcq_key") in LETTERS
    ]
    overlay: dict = {}
    explain: dict = {}
    compare: list = []
    n_gap = n_ok = 0
    for it in scope:
        uid = it["uid"]
        key = it["assessment"]["mcq_key"]
        bind_id, cands, evidence = _candidates(it, bindings)
        unit_id, guard = _pick_unit(it, cands, units) if cands else ("", "MISSING_CAMBRIDGE_GRAIN")
        unit = units.get(unit_id) or {}
        wrong = {}
        letters_ex = {}
        cur = current.get(uid) or ((it.get("assessment") or {}).get("learn_by_solve") or {})
        for L in LETTERS:
            if L == key:
                continue
            if not option_text(it, L) and not it.get("options_are_figure"):
                continue
            fu, ex = (None, {"gap": "AMBIGUOUS_UNIT"}) if not unit else author_letter(it, L, unit)
            cur_fu = ((cur.get("wrong") or {}).get(L) or {}).get("followup") or {}
            if not fu:
                n_gap += 1
                letters_ex[L] = {
                    "status": "GAP",
                    "gap": ex.get("gap"),
                    "detail": ex,
                    "grain": {"binding_id": bind_id, "candidates": cands, "unit_id": unit_id, "guard": guard, "evidence": evidence},
                    "current_stem": cur_fu.get("stem"),
                    "astra_stem": None,
                }
                continue
            n_ok += 1
            mx = ex.get("mx_type") or "intermediate_omission"
            wrong[L] = {
                "mx_type": mx,
                "pathway": ex.get("why_anchor") or ex.get("grounding") or ex.get("route"),
                "followup": fu,
                "hinge_id": unit_id,
                "hinge_label": unit.get("decision_hinge"),
            }
            letters_ex[L] = {
                "status": "PROVED",
                "grain": {"binding_id": bind_id, "candidates": cands, "unit_id": unit_id, "guard": guard, "evidence": evidence},
                "route": ex.get("route"),
                "step_id": ex.get("step_id"),
                "mx_type": mx,
                "grounding": ex.get("grounding") or ex.get("species"),
                "map_law": ex.get("map_law"),
                "decision_hinge": unit.get("decision_hinge"),
                "why_this_hint": fu.get("why"),
                "current_stem": cur_fu.get("stem"),
                "astra_stem": fu.get("stem"),
                "astra_format": fu.get("format"),
                "current_format": cur_fu.get("format") or "single_mcq",
                "same_as_current": (cur_fu.get("stem") or "") == (fu.get("stem") or ""),
                "fallback": bool(ex.get("fallback")),
            }
        if wrong:
            overlay[uid] = {
                "key": key,
                "hinge_id": unit_id,
                "hinge_label": unit.get("decision_hinge"),
                "wrong": wrong,
            }
        explain[uid] = {
            "key": key,
            "unit_id": unit_id,
            "guard": guard,
            "binding_id": bind_id,
            "letters": letters_ex,
        }
        compare.append(
            {
                "uid": uid,
                "stem": it.get("stem"),
                "options": it.get("options") or {},
                "statements": it.get("statements") or [],
                "key": key,
                "chapter_id": it.get("chapter_id"),
                "node": it.get("node"),
                "subtopic_label": it.get("subtopic_label"),
                "current": cur,
                "astra": overlay.get(uid),
                "explain": explain[uid],
            }
        )
    ov_doc = {
        "schema": "lbs_overlay.v1",
        "source": "astra_harness",
        "n": len(overlay),
        "n_proved_letters": n_ok,
        "n_gap_letters": n_gap,
        "note": "Does not replace data/overlay/lbs_electrochem.json. Instantiation used zero model calls.",
        "items": overlay,
    }
    ex_doc = {
        "schema": "lbs.explain.v1",
        "how_to_read": (
            "Each letter is PROVED or GAP. grain.unit_id is the NCERT map hinge. "
            "route/step_id/map_law are why this unlock exists. "
            "Astra did not reprint the clicked option. Compare astra_stem with current_stem."
        ),
        "architecture": "projection ∩ reviewed grain_bindings → task_guard → map unit → mechanism/mx route → thinking-prod instantiate",
        "model_calls_at_item_grain": 0,
        "n_items": len(explain),
        "n_proved_letters": n_ok,
        "n_gap_letters": n_gap,
        "items": explain,
    }
    cmp_doc = {
        "schema": "lbs.compare.v1",
        "title": "AS/A Electrochemistry LBS: current overlay vs Astra harness",
        "n": len(compare),
        "n_proved_letters": n_ok,
        "n_gap_letters": n_gap,
        "items": compare,
    }
    OUT_OV.parent.mkdir(parents=True, exist_ok=True)
    OUT_EX.parent.mkdir(parents=True, exist_ok=True)
    OUT_CMP.parent.mkdir(parents=True, exist_ok=True)
    OUT_OV.write_text(json.dumps(ov_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_EX.write_text(json.dumps(ex_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_CMP.write_text(json.dumps(cmp_doc, ensure_ascii=False), encoding="utf-8")
    return {
        "n_items": len(scope),
        "n_overlay": len(overlay),
        "n_proved_letters": n_ok,
        "n_gap_letters": n_gap,
        "wrote": [str(OUT_OV), str(OUT_EX), str(OUT_CMP)],
    }


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
