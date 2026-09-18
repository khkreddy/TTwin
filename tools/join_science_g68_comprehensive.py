#!/usr/bin/env python3
"""Join v2 Mx + CI pedagogy onto the grades 6–8 science map.

CI mx_pool is NOT copied as truth. Same contract as build_ncert_comprehensive_map.py.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_SRC = Path("/home/harik/awm_build/reports/paper/src")
MAP = ROOT / "data/maps/science.json"
JSONL = ROOT / "data/maps/mx_v2/construction.jsonl"
OUT = ROOT / "data/maps/science.json"
RECEIPT = ROOT / "data/maps/science_g68_comprehensive_receipt.json"

sys.path.insert(0, str(PAPER_SRC))
from build_ncert_comprehensive_map import (  # noqa: E402
    CI_MX_KEYED_FIELDS,
    CI_PEDAGOGY_FIELDS,
    CIIndex,
    take_ci,
)


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_v2() -> dict[str, dict]:
    last = {}
    if not JSONL.is_file():
        return last
    for line in JSONL.open(encoding="utf-8"):
        rec = json.loads(line)
        if rec.get("unit_id") and rec.get("complete"):
            last[rec["unit_id"]] = rec
    return last


def slim_mx(rows: list) -> list:
    out = []
    for mx in rows:
        if not isinstance(mx, dict):
            continue
        out.append(
            {
                "id": mx.get("mx_id"),
                "type": mx.get("confusion_type"),
                "cwo": mx.get("canonical_wrong_output"),
                "status": "CANDIDATE",
                "mx_class": "LOCAL",
                "confused_element": mx.get("confused_element"),
                "observable_prediction": mx.get("observable_prediction"),
                "corruption_path": mx.get("corruption_path"),
                "neighbor_mechanism": mx.get("neighbor_mechanism") or None,
                "reversed_relation": mx.get("reversed_relation") or None,
                "severity": mx.get("severity"),
                "grounding_strength": mx.get("grounding_strength") or "logic_synthesised",
                "derivation": mx.get("derivation"),
            }
        )
    return out


def mechanism_from_ci(h: dict | None, fallback) -> dict | str | None:
    mech = (h or {}).get("mechanism_core")
    if isinstance(mech, dict) and (mech.get("law") or mech.get("causal_direction")):
        return {
            "law": mech.get("law") or "",
            "causal_direction": mech.get("causal_direction") or "",
            "boundary_conditions": mech.get("boundary_conditions") or [],
            "key_entities": mech.get("key_entities") or [],
        }
    return fallback


def main() -> int:
    doc = json.loads(MAP.read_text(encoding="utf-8"))
    v2 = load_v2()
    idx = CIIndex()
    missing_v2 = []
    missing_ci = []
    coverage = Counter()
    new_units = []
    for u in doc["units"]:
        rec = dict(u)
        uid = rec["unit_id"]
        derived = v2.get(uid)
        h = idx.hinge(uid)
        rec["mechanism"] = mechanism_from_ci(h, rec.get("mechanism"))
        rec.pop("mx_notes", None)
        if not derived:
            rec["mx"] = []
            rec["mx_dispositions"] = None
            rec["n_mx_na"] = 7
            rec["pedagogy_source"] = "mx_derivation_v2_missing"
            missing_v2.append(uid)
        else:
            admitted = [d["mx"] for d in derived["dispositions"] if d.get("disposition") == "admitted" and d.get("mx")]
            rec["mx"] = slim_mx(admitted)
            rec["mx_dispositions"] = [
                {k: d.get(k) for k in ("confusion_type", "disposition", "attempt", "reason", "neighbor_mechanism", "reversed_relation")}
                for d in derived["dispositions"]
            ]
            rec["n_mx_na"] = sum(1 for d in derived["dispositions"] if d.get("disposition") != "admitted")
            rec["pedagogy_source"] = "mx_derivation_v2"
        if not h:
            rec["ci_pedagogy"] = None
            rec["ci_join_status"] = "CI_HINGE_NOT_FOUND"
            missing_ci.append(uid)
        else:
            block = take_ci(h)
            rec["ci_pedagogy"] = block
            rec["ci_join_status"] = "joined"
            for f in block["fields_present"]:
                coverage[f] += 1
        rec["status"] = "hinge_map_candidate"
        new_units.append(rec)

    n_mx = sum(len(u.get("mx") or []) for u in new_units)
    hist = Counter(len(u.get("mx") or []) for u in new_units)
    types = Counter(mx.get("type") for u in new_units for mx in (u.get("mx") or []))
    rr = sum(1 for u in new_units if any(mx.get("type") == "relationship_reversal" for mx in (u.get("mx") or [])))

    doc["units"] = new_units
    doc["n"] = len(new_units)
    doc["mx_protocol"] = "mx_derivation_v2"
    doc["mx_constructor"] = "gpt-6-astra"
    doc["honesty"] = (
        "Hinges from NCERT science chapter intelligence. Mx from mx_derivation_v2 "
        "(7-type construction; prior mx_pool not copied). Status CANDIDATE. "
        "CI mastery/LoK/antigaming attached as ci_pedagogy; CI mx_pool is lineage only. "
        "Kimi-k3 constructor skipped (account suspended). Astra gpt-6-astra ran the same SYS. "
        "Live chemistry/physics/biology maps untouched."
    )
    doc["ci_pedagogy_contract"] = {
        "mx_source": "mx_derivation_v2 on units.mx",
        "pedagogy_source": "chapter_intelligence_hybrid",
        "not_copied_from_ci": ["mx_pool", "mx_pool_ledger"],
        "mx_keyed_ci_era_not_rebound": CI_MX_KEYED_FIELDS,
        "pedagogy_fields": CI_PEDAGOGY_FIELDS,
    }
    doc["census"] = {
        **(doc.get("census") or {}),
        "n_hinges": len(new_units),
        "n_mx": n_mx,
        "n_mx_v2_missing": len(missing_v2),
        "mx_count_histogram": {str(k): hist[k] for k in sorted(hist)},
        "admitted_by_type": dict(types),
        "rr_hinges": rr,
        "rr_share": round(rr / len(new_units), 4) if new_units else 0,
        "zero_mx_hinges": hist.get(0, 0),
    }
    doc["built_utc"] = utc()
    sme = dict(doc.get("astra_sme") or {})
    sme["mx_v2"] = "constructed"
    doc["astra_sme"] = sme

    OUT.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    receipt = {
        "generated_utc": utc(),
        "protocol": "mx_derivation_v2",
        "constructor": "gpt-6-astra",
        "hinges": len(new_units),
        "v2_complete": len(v2),
        "v2_missing": missing_v2,
        "ci_joined": len(new_units) - len(missing_ci),
        "ci_missing": missing_ci,
        "v2_mx_rows": n_mx,
        "mx_count_histogram": {str(k): hist[k] for k in sorted(hist)},
        "admitted_by_type": dict(types),
        "rr_share": doc["census"]["rr_share"],
        "bytes": OUT.stat().st_size,
        "did_not_modify": [
            "data/maps/chemistry.json",
            "data/maps/physics.json",
            "data/maps/biology.json",
            "data/intelligence/chapter_intelligence_hybrid/",
        ],
        "not_copied_from_ci": ["mx_pool", "mx_pool_ledger"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ("hinges", "v2_complete", "v2_mx_rows", "ci_joined", "rr_share", "bytes")}, indent=2))
    print("histogram", receipt["mx_count_histogram"])
    print("types", receipt["admitted_by_type"])
    print("wrote", OUT)
    return 0 if not missing_v2 else 2


if __name__ == "__main__":
    raise SystemExit(main())
