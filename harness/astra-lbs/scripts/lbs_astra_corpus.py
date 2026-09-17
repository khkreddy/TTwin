#!/usr/bin/env python3
"""Astra-harness LBS instantiate for every packed keyed MCQ.

Zero model calls at item grain. Writes data/overlay/astra/<pack>.json.
Does not rewrite freeze exam.v1. Gold and spectroscopy still win at join
(loaded after these files in lbs_construct.overlay_records).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from lbs_astra_electrochem import (  # noqa: E402
    _candidates as _ec_cands,
    _never_hit,
    _pick_unit,
    author_letter,
)
from lbs_construct import LETTERS, option_text  # noqa: E402
from lbs_electrochem import _quotes_option, _tf  # noqa: E402
from lbs_quality import followup_ok  # noqa: E402

QUESTIONS = ROOT / "data/questions"
MAPS = ROOT / "data/maps"
PROJ = ROOT / "data/projection.json"
GRAIN = ROOT / "data/lbs/grain_bindings.v1.json"
OUTDIR = ROOT / "data/overlay/astra"
STOP = {"that", "which", "from", "with", "this", "when", "then", "than", "into", "onto", "have", "does"}


def packed_node(item: dict) -> str:
    n = str(item.get("node") or "")
    for pfx in ("chem:", "phy:", "bio:", "math:"):
        if n.startswith(pfx):
            return n[len(pfx) :]
    return n


def load_maps() -> tuple[dict[str, dict], dict[tuple[str, str], list[str]]]:
    by_id: dict[str, dict] = {}
    by_node: dict[tuple[str, str], list[str]] = {}
    for p in MAPS.glob("*.json"):
        doc = json.loads(p.read_text(encoding="utf-8"))
        subj = doc.get("subject") or p.stem
        for u in doc.get("units") or []:
            if not isinstance(u, dict) or not u.get("unit_id"):
                continue
            uid = str(u["unit_id"])
            by_id[uid] = u
            node = str(u.get("node") or "")
            by_node.setdefault((subj, node), []).append(uid)
    return by_id, by_node


def candidates(item: dict, proj: dict, by_id: dict, by_node: dict) -> list[str]:
    subj = str(item.get("subject") or "")
    node = packed_node(item)
    band = str(item.get("grade_band") or "")
    nb = (proj.get("ncert_by_node_band") or {}).get(f"{node}|{band}") or {}
    ids = [u for u in (nb.get("unit_ids") or []) if u in by_id]
    if ids:
        return ids
    return list(by_node.get((subj, node), []))


def pick_generic(item: dict, cands: list[str], by_id: dict) -> tuple[str, str]:
    stem = (item.get("stem") or "").lower()
    best, best_n = "", -1
    for uid in cands:
        u = by_id.get(uid) or {}
        dec = (u.get("decision_hinge") or "").lower()
        toks = [t for t in re.findall(r"[a-z]{4,}", dec) if t not in STOP]
        n = sum(1 for t in toks if t in stem)
        mech = u.get("mechanism") or {}
        if not isinstance(mech, dict):
            mech = {"law": str(mech)}
        steps = mech.get("steps") or []
        nonempty = any(isinstance(s, dict) and str(s.get("step") or "").strip() for s in steps)
        score = n * 10 + int(nonempty)
        if score > best_n:
            best, best_n = uid, score
    if best:
        return best, f"hinge_score:{best_n}"
    return (cands[0] if cands else ""), "first_candidate"


def match_mx(unit: dict, w: str) -> dict | None:
    wtok = set(re.findall(r"[a-z]{4,}", (w or "").lower()))
    if len(wtok) < 2:
        return None
    ranked: list[tuple[int, dict]] = []
    for mx in unit.get("mx") or []:
        if not isinstance(mx, dict):
            continue
        cwo = mx.get("cwo") or ""
        ctok = set(re.findall(r"[a-z]{4,}", cwo.lower()))
        n = len(wtok & ctok)
        if n >= 3:
            ranked.append((n, mx))
    ranked.sort(key=lambda x: -x[0])
    if not ranked:
        return None
    if len(ranked) > 1 and ranked[0][0] == ranked[1][0]:
        return None
    return ranked[0][1]


def author_generic(item: dict, letter: str, unit: dict) -> tuple[dict | None, dict]:
    hinge = str(unit.get("decision_hinge") or "").strip()
    mech = unit.get("mechanism") or {}
    if not isinstance(mech, dict):
        mech = {"law": str(mech)}
    law = str(mech.get("law") or "").strip()
    w = option_text(item, letter)
    mx = match_mx(unit, w)
    if mx and mx.get("cwo"):
        fu = _tf(
            mx["cwo"][:240],
            False,
            f"That claim is the map CWO ({mx.get('type')}) for {unit.get('unit_id')}. "
            f"{(law or hinge)[:180]}",
        )
        ex = {
            "route": mx.get("type") or "term_substitution",
            "mx_id": mx.get("id"),
            "grounding": "map CWO vs option tokens",
            "fallback": False,
        }
    else:
        claim = law or hinge
        if not claim:
            return None, {"gap": "EMPTY_MECHANISM_STEPS"}
        fu = _tf(
            claim[:240],
            True,
            f"Map hinge: {hinge}. Apply this check, then retry the original.",
        )
        ex = {"route": "intermediate_omission", "step_id": "S1", "fallback": True, "grounding": "hinge_law"}
    if _never_hit(fu.get("stem") or "") or _quotes_option(fu.get("stem") or "", w):
        return None, {"gap": "OPTION_REPRINT"}
    if not followup_ok(fu):
        return None, {"gap": "FOLLOWUP_NOT_OK"}
    return fu, ex


def instantiate_item(item: dict, proj: dict, by_id: dict, by_node: dict, grain: list) -> dict | None:
    key = (item.get("assessment") or {}).get("mcq_key")
    if key not in LETTERS:
        return None
    subj = str(item.get("subject") or "")
    cands = candidates(item, proj, by_id, by_node)
    if subj == "chemistry":
        bind_id, grain_cands, _ev = ("", cands, "")
        # reviewed electrochem grain wins when tags match
        bid, gc, ev = _ec_cands(item, grain)
        if gc:
            bind_id, cands = bid, gc
        unit_id, guard = _pick_unit(item, cands, by_id) if cands else ("", "MISSING_GRAIN")
        author = author_letter
    else:
        unit_id, guard = pick_generic(item, cands, by_id)
        author = author_generic
    unit = by_id.get(unit_id)
    if not isinstance(unit, dict):
        return None
    wrong = {}
    for L in LETTERS:
        if L == key:
            continue
        if not option_text(item, L) and not item.get("options_are_figure"):
            continue
        fu, ex = author(item, L, unit)
        if not fu:
            return None
        mx = ex.get("mx_type") or ex.get("route") or "intermediate_omission"
        if mx not in {
            "term_substitution",
            "condition_omission",
            "relationship_reversal",
            "scope_error",
            "surface_feature_capture",
            "mechanism_conflation",
            "operation_confusion",
            "intermediate_omission",
        }:
            mx = "intermediate_omission"
        wrong[L] = {
            "mx_type": mx if mx != "intermediate_omission" else "intermediate_omission",
            "pathway": ex.get("grounding") or ex.get("route"),
            "followup": fu,
        }
    if not wrong:
        return None
    return {
        "key": key,
        "hinge_id": unit_id,
        "hinge_label": unit.get("decision_hinge"),
        "solve": (unit.get("decision_hinge") or "")[:300],
        "wrong": wrong,
        "guard": guard,
    }


def build(pack_glob: str = "*.json") -> dict:
    proj = json.loads(PROJ.read_text(encoding="utf-8")) if PROJ.is_file() else {}
    grain = (json.loads(GRAIN.read_text(encoding="utf-8")).get("bindings") or []) if GRAIN.is_file() else []
    by_id, by_node = load_maps()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    summary = {}
    for path in sorted(QUESTIONS.glob(pack_glob)):
        items = json.loads(path.read_text(encoding="utf-8"))
        overlay = {}
        n_try = n_ok = 0
        for it in items:
            if (it.get("assessment") or {}).get("mcq_key") not in LETTERS:
                continue
            if (it.get("assessment") or {}).get("key_status") != "available":
                continue
            n_try += 1
            rec = instantiate_item(it, proj, by_id, by_node, grain)
            if rec:
                overlay[str(it.get("uid"))] = rec
                n_ok += 1
        out = OUTDIR / f"{path.stem}.json"
        doc = {
            "schema": "lbs_overlay.v1",
            "source": "astra_harness_corpus",
            "pack_file": path.name,
            "n": len(overlay),
            "n_eligible_try": n_try,
            "items": overlay,
        }
        out.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")
        summary[path.name] = {"n_try": n_try, "n_ok": n_ok, "wrote": str(out)}
        print(json.dumps({"file": path.name, "n_try": n_try, "n_ok": n_ok}), flush=True)
    return summary


if __name__ == "__main__":
    g = sys.argv[1] if len(sys.argv) > 1 else "*.json"
    print(json.dumps(build(g), indent=2))
