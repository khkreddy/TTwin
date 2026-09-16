#!/usr/bin/env python3
"""LBS compiler CLI — snapshot / index / plan. No model calls.

Instantiation of packed items must not import tools.lbs_ai.
See harness/82_LBS_COMPILER.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "data/maps/chemistry.json"
ENRICH = ROOT / "data/enrichment/chemistry.json"
PROJ = ROOT / "data/projection.json"
PACKED = ROOT / "data/questions/chemistry-senior.json"
NEVER = ROOT / "data/lbs/never_cases.v1.json"
PRESERVE = ROOT / "data/lbs/preserve_uids.v1.json"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_snapshot(out: Path) -> dict:
    sources = {
        "maps/chemistry.json": MAP,
        "enrichment/chemistry.json": ENRICH,
        "projection.json": PROJ,
        "questions/chemistry-senior.json": PACKED,
        "lbs/never_cases.v1.json": NEVER,
        "lbs/preserve_uids.v1.json": PRESERVE,
    }
    catalog = {}
    for rel, path in sources.items():
        catalog[rel] = {
            "path": str(path.relative_to(ROOT)),
            "exists": path.is_file(),
            "bytes": path.stat().st_size if path.is_file() else 0,
            "file_sha256": _sha256_file(path) if path.is_file() else None,
        }
    doc = {"schema": "lbs.snapshot.v1", "sources": catalog}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def cmd_index() -> dict:
    units = json.loads(MAP.read_text(encoding="utf-8")).get("units") or []
    enrich = json.loads(ENRICH.read_text(encoding="utf-8")).get("items") or []
    by_node: dict[str, int] = {}
    empty_steps = 0
    redox = echem = 0
    for u in units:
        node = str(u.get("node") or "")
        by_node[node] = by_node.get(node, 0) + 1
        steps = ((u.get("mechanism") or {}).get("steps")) or []
        if not any(str(s.get("step") or "").strip() for s in steps if isinstance(s, dict)):
            empty_steps += 1
        if node == "C5/H-REDOX":
            redox += 1
        if node == "C5/H-ECHEM":
            echem += 1
    served = {uid for it in enrich for uid in (it.get("serves") or [])}
    return {
        "schema": "lbs.index.v1",
        "n_units": len(units),
        "n_enrichment": len(enrich),
        "n_units_with_enrichment": sum(1 for u in units if u.get("unit_id") in served),
        "empty_mechanism_steps": empty_steps,
        "h_redox": redox,
        "h_echem": echem,
        "pilot_unit_cap": redox + echem,
        "pilot_llm_call_cap_if_slots_legal": 2 * (redox + echem),
        "note": "Empty steps fail closed. LLM cap is unit-level, never per packed item.",
    }


def cmd_plan(scope: str) -> dict:
    if scope != "electrochem":
        raise SystemExit(f"scope {scope!r} not authorised; electrochem only")
    packed = json.loads(PACKED.read_text(encoding="utf-8"))
    eligible = [
        it
        for it in packed
        if it.get("chapter_id") == "cam:9701:6"
        and it.get("pack") == "senior_11_12_as_a"
        and ((it.get("assessment") or {}).get("mcq_key") in {"A", "B", "C", "D"})
    ]
    idx = cmd_index()
    return {
        "schema": "lbs.compile_plan.v1",
        "scope": {
            "pack": "senior_11_12_as_a",
            "chapter_id": "cam:9701:6",
            "nodes": ["chem:C5/H-REDOX", "chem:C5/H-ECHEM"],
        },
        "n_keyed_parents": len(eligible),
        "map_units_h_redox": idx["h_redox"],
        "map_units_h_echem": idx["h_echem"],
        "author_calls_max": idx["h_redox"] + idx["h_echem"],
        "examiner_calls_max": idx["h_redox"] + idx["h_echem"],
        "instantiate_model_calls": 0,
        "surface_source": "deterministic",
        "ai_import_forbidden_on_instantiate": True,
        "preserve": json.loads(PRESERVE.read_text(encoding="utf-8")),
        "never": json.loads(NEVER.read_text(encoding="utf-8")),
        "gaps_expected": [
            "EMPTY_MECHANISM_STEPS",
            "MISSING_CAMBRIDGE_GRAIN until data/lbs/grain_bindings.v1.json is reviewed",
            "MISSING_MX_MATCH until route_bindings.v1.json is reviewed",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="LBS proof compiler (no model calls)")
    p.add_argument("command", choices=["snapshot", "index", "plan"])
    p.add_argument("--scope", default="electrochem")
    p.add_argument("--out", default="")
    args = p.parse_args(argv)
    if args.command == "snapshot":
        out = Path(args.out) if args.out else ROOT / "build/lbs/snapshot.json"
        doc = cmd_snapshot(out)
        print(json.dumps({"wrote": str(out), "n_sources": len(doc["sources"])}))
        return 0
    if args.command == "index":
        print(json.dumps(cmd_index(), indent=2))
        return 0
    if args.command == "plan":
        print(json.dumps(cmd_plan(args.scope), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
