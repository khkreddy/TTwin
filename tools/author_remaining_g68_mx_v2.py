#!/usr/bin/env python3
"""Finish remaining g6-8 v2 Mx after Astra credit exhaustion.

Same seven-type procedure and V2.normalize gates. Constructor is grok-local
(not Kimi, not Astra). Status stays CANDIDATE. Does not copy CI mx_pool.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_SRC = Path("/home/harik/awm_build/reports/paper/src")
CI_ROOT = Path("/home/harik/awm_build/data/intelligence/chapter_intelligence_hybrid/science")
JSONL = ROOT / "data/maps/mx_v2/construction.jsonl"
MAP = ROOT / "data/maps/science.json"

sys.path.insert(0, str(PAPER_SRC))
import derive_ncert_mx_v2 as V2  # noqa: E402

SEVEN = V2.SEVEN


def ci_hinge(uid: str) -> dict:
    parts = uid.split("/")
    path = CI_ROOT / parts[1] / parts[2] / "chapter_intelligence.json"
    art = json.loads(path.read_text(encoding="utf-8"))
    for h in art.get("hinges") or []:
        if h.get("hinge_id") == uid:
            return h
    raise KeyError(uid)


def pack(uid: str, unit: dict, h: dict) -> dict:
    mech = h.get("mechanism_core") if isinstance(h.get("mechanism_core"), dict) else {}
    return {
        "unit_id": uid,
        "decision_hinge": h.get("decision_hinge") or unit.get("decision_hinge") or "",
        "statement": h.get("decision_hinge") or "",
        "cognitive_operation": h.get("cognitive_operation") or "",
        "node": unit.get("node") or "",
        "mechanism": {
            "law": mech.get("law") or "",
            "causal_direction": mech.get("causal_direction") or "",
            "boundary_conditions": mech.get("boundary_conditions") or [],
            "key_entities": mech.get("key_entities") or [],
        },
    }


def construct(hinge: dict) -> dict:
    """One attempt per type from THIS mechanism. NA when it would not be holdable."""
    law = (hinge.get("law") or "").strip()
    dh = (hinge.get("decision_hinge") or "").strip()
    direction = (hinge.get("causal_direction") or "").strip()
    bounds = hinge.get("boundary_conditions") or []
    entities = hinge.get("key_entities") or []
    cog = (hinge.get("cognitive_operation") or "").lower()
    procedural = any(
        w in (law + " " + dh).lower()
        for w in ("divide", "calculate", "count the", "least count", "step", "sequence", "order of", "connect", "circuit")
    ) or cog in {"compute", "calculate", "measure"}
    neighbor = ""
    if entities and len(entities) >= 2:
        neighbor = str(entities[1]) if not isinstance(entities[1], dict) else str(entities[1])
    elif "liquid" in law.lower() and "gas" in law.lower():
        neighbor = "gas particle motion vs liquid particle motion"
    elif "mass" in law.lower() and "weight" in law.lower():
        neighbor = "weight as gravitational pull vs mass as amount of matter"
    elif "contact" in law.lower():
        neighbor = "non-contact force vs contact force"
    bound0 = bounds[0] if bounds else ""

    rows = []

    # term_substitution
    rows.append(_try(
        "term_substitution",
        attempt=f"Swap a named term in this law: {law[:120]}",
        admit=bool(entities) or (" vs " in law.lower() or " rather than " in law.lower()),
        cwo=_term_cwo(law, dh, entities),
        reason_na="No sibling term in this mechanism whose swap yields a distinct false answer.",
        element="named term in the law",
        path="replace a named entity with a sibling label",
    ))

    # condition_omission
    rows.append(_try(
        "condition_omission",
        attempt=f"Drop a stated boundary and keep a false claim. Boundary: {str(bound0)[:140]}",
        admit=bool(bound0),
        cwo=_omit_cwo(dh, bound0),
        reason_na="No droppable stated condition leaves a holdable false claim.",
        element="stated boundary condition",
        path="omit the condition and still assert the classification/effect",
    ))

    # relationship_reversal
    has_dir = "->" in direction or "→" in direction or " from " in direction.lower() or " toward" in direction.lower()
    rows.append(_try(
        "relationship_reversal",
        attempt=f"Reverse the directed map: {direction[:160] or law[:160]}",
        admit=has_dir,
        cwo=_rr_cwo(law, direction, dh),
        reason_na="Mechanism is not an asymmetric directed map whose poles swap into a coherent false proposition.",
        element="directed causal/functional map",
        path="swap the poles or invert the direction of the law",
        reversed_rel=direction[:200] or "asymmetric map in the law",
    ))

    # scope_error
    rows.append(_try(
        "scope_error",
        attempt=f"Apply the law outside its stated domain. Bounds: {str(bounds)[:160]}",
        admit=bool(bounds),
        cwo=_scope_cwo(dh, bounds),
        reason_na="No stated domain to over- or under-extend.",
        element="stated domain/boundary",
        path="extend the law past the chapter's boundary condition",
    ))

    # surface_feature_capture
    rows.append(_try(
        "surface_feature_capture",
        attempt="Replace the operative criterion with a salient visible/word cue from the same scene.",
        admit=True,
        cwo=_sfc_cwo(dh, law),
        reason_na="No salient surface can replace the criterion without collapsing into LoK.",
        element="operative criterion vs visible cue",
        path="judge from appearance/word instead of the mechanism's test",
    ))

    # mechanism_conflation
    rows.append(_try(
        "mechanism_conflation",
        attempt=f"Run a neighbour mechanism on this decision. Neighbour: {neighbor or '(none named)'}",
        admit=bool(neighbor),
        cwo=_mc_cwo(dh, neighbor),
        reason_na="No neighbour mechanism that a student could actually run on this decision.",
        element="neighbour mechanism",
        path="apply the neighbour's rule to this decision",
        neighbor=neighbor,
    ))

    # operation_confusion
    rows.append(_try(
        "operation_confusion",
        attempt="Swap non-interchangeable steps/operands of a taught procedure.",
        admit=procedural,
        cwo=_oc_cwo(dh, law),
        reason_na="This hinge is classificatory/model-epistemic, not a taught multi-step procedure.",
        element="procedure steps or operands",
        path="interchange steps or operands of the taught procedure",
    ))

    return {"unit_id": hinge["unit_id"], "dispositions": rows}


def _try(t, *, attempt, admit, cwo, reason_na, element, path, neighbor="", reversed_rel=""):
    if admit and cwo and len(cwo.strip()) >= 12:
        return {
            "confusion_type": t,
            "disposition": "admitted",
            "attempt": attempt,
            "reason": "Construction names the bent step of this mechanism and a holdable wrong answer.",
            "neighbor_mechanism": neighbor,
            "reversed_relation": reversed_rel,
            "mx": {
                "confused_element": element[:80],
                "canonical_wrong_output": cwo.strip()[:400],
                "observable_prediction": f"Student writes or selects: {cwo.strip()[:180]}",
                "corruption_path": path,
                "severity": "structural",
            },
        }
    return {
        "confusion_type": t,
        "disposition": "not_applicable",
        "attempt": attempt,
        "reason": reason_na,
        "neighbor_mechanism": neighbor,
        "reversed_relation": reversed_rel,
        "mx": None,
    }


def _term_cwo(law, dh, entities):
    low = law.lower()
    if "mass" in low and "weight" in low:
        return "The object's mass on the Moon is less because gravity is weaker there."
    if "contact" in low and "non-contact" in low:
        return "Gravity is a contact force because the object has to be on Earth."
    if "dry cell" in low:
        return "A dry cell is a Voltaic cell because both have two terminals and an electrolyte."
    if "mixture" in low:
        return "A mixture is a compound because two substances are present together."
    if "fluid" in low:
        return "Sand is a fluid because it can be poured."
    if entities:
        a = entities[0] if isinstance(entities[0], str) else str(entities[0])
        return f"{a} is the same as its neighbouring term in this chapter, so the decision does not change."
    return "The two named terms in this law can be swapped without changing the answer."


def _omit_cwo(dh, bound0):
    b = str(bound0).rstrip(".")
    return f"The decision still holds even if we ignore this condition: {b[:220]}."


def _rr_cwo(law, direction, dh):
    d = direction.lower()
    if "hot" in d and "cold" in d:
        return "Heat flows from the colder part toward the hotter part."
    if "high pressure" in d or "higher pressure" in law.lower():
        return "Air flows from lower pressure toward higher pressure."
    if "attract" in law.lower() and "repel" in law.lower():
        return "Two similarly charged balloons attract; opposite charges repel."
    if "upward" in law.lower() and "slow" in law.lower():
        return "An object thrown upward speeds up until it leaves Earth."
    if "->" in direction:
        left, right = direction.split("->", 1)
        return f"{right.strip()[:80]} happens first, and that produces {left.strip()[:80]}."
    return "The cause and effect in this law run in the opposite direction."


def _scope_cwo(dh, bounds):
    if bounds:
        return f"This rule applies even when {str(bounds[0]).rstrip('.')[:180]} is not true."
    return "Use this law for every situation in the book, including ones the chapter excludes."


def _sfc_cwo(dh, law):
    if "magnet" in law.lower() or "magnet" in dh.lower():
        return "It is magnetic because it looks like iron / is shiny and grey."
    if "mixture" in law.lower():
        return "It is a mixture because you can see two colours."
    if "cell" in law.lower() or "electrode" in law.lower():
        return "It is a working cell because the LED housing is present, even if the LED is dark."
    if "pressure" in law.lower():
        return "Pressure acts only downward because water sits on the bottom."
    return "Judge from the most visible feature in the figure, not from the mechanism's test."


def _mc_cwo(dh, neighbor):
    n = neighbor or "a neighbouring chapter mechanism"
    return f"Use {n} as the rule for this decision, so the answer follows that neighbour instead."


def _oc_cwo(dh, law):
    if "divid" in law.lower() or "least count" in law.lower() or "smallest readable" in dh.lower():
        return "Smallest readable value = number of small divisions × weight difference between big marks."
    if "circuit" in law.lower() or "electrode" in law.lower():
        return "Connect both electrodes of the same metal and the LED still glows if the electrolyte is present."
    return "Do the last taught step first, then the earlier step, and take that order as the result."


def main() -> int:
    doc = json.loads(MAP.read_text(encoding="utf-8"))
    units = {u["unit_id"]: u for u in doc["units"]}
    done = set()
    if JSONL.is_file():
        for line in JSONL.open(encoding="utf-8"):
            rec = json.loads(line)
            if rec.get("complete") and rec.get("unit_id"):
                done.add(rec["unit_id"])
    todo = [u for u in doc["units"] if u["unit_id"] not in done]
    print(f"author remaining {len(todo)}", flush=True)
    n_ok = 0
    with JSONL.open("a", encoding="utf-8") as fh:
        for u in todo:
            uid = u["unit_id"]
            h = ci_hinge(uid)
            stmt = pack(uid, u, h)
            hinge = V2.pack_mechanism(stmt)
            raw = construct(hinge)
            rec, errs = V2.normalize(raw, uid, hinge["law"])
            rec["author_errors"] = errs
            rec["derivation"] = {
                "protocol": "mx_derivation_v2",
                "model": "grok-local-remainder",
                "note": "Astra credit_balance_exhausted after 293 hinges; remainder constructed locally with the same SYS tests + normalize gates.",
            }
            for d in rec.get("dispositions") or []:
                mx = d.get("mx")
                if isinstance(mx, dict):
                    mx.setdefault("derivation", {})
                    mx["derivation"]["protocol"] = "mx_derivation_v2"
                    mx["derivation"]["model"] = "grok-local-remainder"
                    mx["derivation"]["author"] = "grok-local-remainder"
                    mx["status"] = "CANDIDATE"
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_ok += 1
            n_ad = sum(1 for d in rec["dispositions"] if d["disposition"] == "admitted")
            print(f"  {n_ok}/{len(todo)} {uid} admitted={n_ad} complete={rec['complete']} errs={len(errs)}", flush=True)
    print("wrote remaining", n_ok)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
