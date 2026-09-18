#!/usr/bin/env python3
"""Build NCERT grades 6–8 combined science map from chapter intelligence.

Cartographer only: copies hinges/Mx from released chapter intelligence.
Does not invent Mx. Does not rewrite chemistry/physics/biology live maps.
Astra SME review is a separate step (ask_astra_science_map.py).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "maps"
HYBRID = Path("/home/harik/awm_build/data/intelligence/chapter_intelligence_hybrid/science")

# Big ideas for combined Science (NCERT 6–8 is one book, not three subjects).
# Grain ids reuse TTwin sheaf homes where the junior hinge is the same decision.
NODES = [
    {
        "id": "S1",
        "title": "Scientific inquiry and evidence",
        "kind": "concept_origin",
        "mechanism": "Science is deciding what counts as a fair question, an observation, and a model — not memorising labels.",
        "sheaf_home": "B5",
        "children": [
            {"id": "S1/H-INQUIRY", "title": "What counts as a scientific question or test"},
        ],
    },
    {
        "id": "S2",
        "title": "Matter: materials, particles, mixtures and change",
        "kind": "concept_origin",
        "mechanism": "Stuff is made of materials that can mix, separate, change state, or form new substances; the test is what stays the same and what is new.",
        "sheaf_home": "C2",
        "children": [
            {"id": "S2/H-MATERIAL", "title": "Materials and their properties"},
            {"id": "S2/H-STATES", "title": "States of matter, particles and water"},
            {"id": "S2/H-MIXTURE", "title": "Mixtures, solutions, pure substances and separation"},
            {"id": "S2/H-CHANGE", "title": "Physical vs chemical change"},
        ],
    },
    {
        "id": "S3",
        "title": "Living systems: organisms, health and ecosystems",
        "kind": "concept_origin",
        "mechanism": "Living things share life processes, live in habitats, and depend on food, microbes, and one another — health is not the absence of one symptom.",
        "sheaf_home": "L1",
        "children": [
            {"id": "S3/H-LIFE", "title": "What is living; diversity, life cycles and plant processes"},
            {"id": "S3/H-BODY", "title": "Food, digestion, growth and health"},
            {"id": "S3/H-ECO", "title": "Habitats, microbes and ecosystems"},
        ],
    },
    {
        "id": "S4",
        "title": "Force, motion, magnets and pressure",
        "kind": "concept_origin",
        "mechanism": "Decide which objects interact and what the interaction does: a push or pull can change motion or shape, but need not change motion when forces balance. Magnets and pressure are cases of that interaction.",
        "sheaf_home": "P1",
        "children": [
            {"id": "S4/H-MOTION", "title": "Describing motion"},
            {"id": "S4/H-FORCE", "title": "Force and pressure"},
            {"id": "S4/H-MAGNET", "title": "Magnets and magnetic materials"},
        ],
    },
    {
        "id": "S5",
        "title": "Energy, heat, electricity and light",
        "kind": "concept_origin",
        "mechanism": "Heat, electric current, and light transfer energy in different ways. A simple circuit needs a closed conducting path for sustained current. Light does not need a material medium. Thermal radiation can cross vacuum.",
        "sheaf_home": "P2",
        "children": [
            {"id": "S5/H-HEAT", "title": "Temperature and heat transfer"},
            {"id": "S5/H-CIRCUIT", "title": "Cells, current and magnetic/heating effects"},
            {"id": "S5/H-LIGHT", "title": "Light, mirrors and seeing"},
        ],
    },
    {
        "id": "S6",
        "title": "Earth, sky, time and resources",
        "kind": "concept_origin",
        "mechanism": "What we see in the sky and what we take from Earth are geometry plus materials: rotation, Moon phases, resources, and habitability — not myths about the Sun circling us.",
        "sheaf_home": "B3",
        "children": [
            {"id": "S6/H-SKY", "title": "Sun, Moon, stars and time"},
            {"id": "S6/H-EARTH", "title": "Earth systems, resources and habitability"},
        ],
    },
]

# Chapter → (node, grain, NCERT-facing title). Binding is by chapter obligation, not page order.
CHAPTER = {
    ("06", "ch_01"): ("S1", "S1/H-INQUIRY", "The wonderful world of science"),
    ("06", "ch_02"): ("S3", "S3/H-LIFE", "Diversity in the living world"),
    ("06", "ch_03"): ("S3", "S3/H-BODY", "Mindful eating: a path to a healthy body"),
    ("06", "ch_04"): ("S4", "S4/H-MAGNET", "Exploring magnets"),
    ("06", "ch_05"): ("S4", "S4/H-MOTION", "Measurement of length and motion"),
    ("06", "ch_06"): ("S2", "S2/H-MATERIAL", "Materials around us"),
    ("06", "ch_07"): ("S5", "S5/H-HEAT", "Temperature and its measurement"),
    ("06", "ch_08"): ("S2", "S2/H-STATES", "A journey through states of water"),
    ("06", "ch_09"): ("S2", "S2/H-MIXTURE", "Methods of separation"),
    ("06", "ch_10"): ("S3", "S3/H-LIFE", "Living creatures: exploring their characteristics"),
    ("06", "ch_11"): ("S6", "S6/H-EARTH", "Nature's treasures"),
    ("06", "ch_12"): ("S6", "S6/H-SKY", "Beyond Earth"),
    ("07", "ch_01"): ("S1", "S1/H-INQUIRY", "The ever-evolving world of science"),
    ("07", "ch_02"): ("S2", "S2/H-MATERIAL", "Acids, bases and salts"),
    ("07", "ch_03"): ("S5", "S5/H-CIRCUIT", "Electricity: circuits and cells"),
    ("07", "ch_04"): ("S2", "S2/H-MATERIAL", "The world of metals and non-metals"),
    ("07", "ch_05"): ("S2", "S2/H-CHANGE", "Physical and chemical changes"),
    ("07", "ch_06"): ("S3", "S3/H-BODY", "Adolescence"),
    ("07", "ch_07"): ("S5", "S5/H-HEAT", "Heat transfer"),
    ("07", "ch_08"): ("S4", "S4/H-MOTION", "Measurement of time"),
    ("07", "ch_09"): ("S3", "S3/H-BODY", "Nutrition in animals"),
    ("07", "ch_10"): ("S3", "S3/H-LIFE", "Respiration and transport in plants"),
    ("07", "ch_11"): ("S5", "S5/H-LIGHT", "Light"),
    ("07", "ch_12"): ("S6", "S6/H-SKY", "Earth, Sun and the apparent motion of the sky"),
    ("08", "ch_01"): ("S1", "S1/H-INQUIRY", "Exploring the inquisitive mind"),
    ("08", "ch_02"): ("S3", "S3/H-ECO", "Microorganisms: friend and foe"),
    ("08", "ch_03"): ("S3", "S3/H-BODY", "Health: reaching the unreached"),
    ("08", "ch_04"): ("S5", "S5/H-CIRCUIT", "Electricity: magnetic and heating effects"),
    ("08", "ch_05"): ("S4", "S4/H-FORCE", "Force"),
    ("08", "ch_06"): ("S4", "S4/H-FORCE", "Pressure"),
    ("08", "ch_07"): ("S2", "S2/H-STATES", "Particulate nature of matter"),
    ("08", "ch_08"): ("S2", "S2/H-MIXTURE", "Elements, compounds and mixtures"),
    ("08", "ch_09"): ("S2", "S2/H-MIXTURE", "Solutions and density"),
    ("08", "ch_10"): ("S5", "S5/H-LIGHT", "Light: mirrors and lenses"),
    ("08", "ch_11"): ("S6", "S6/H-SKY", "The night sky: Moon and calendars"),
    ("08", "ch_12"): ("S3", "S3/H-ECO", "Ecosystems and habitats"),
    ("08", "ch_13"): ("S6", "S6/H-EARTH", "Why Earth supports life"),
}

# Individual hinge homes that override the chapter default (Astra SME).
HINGE_OVERRIDE = {
    "science/grade_06/ch_11/H002": ("S3", "S3/H-BODY"),
}


def _mech_text(mech) -> str | None:
    if isinstance(mech, dict):
        return (mech.get("law") or mech.get("causal_direction") or "")[:400] or None
    if isinstance(mech, str) and mech.strip():
        return mech.strip()[:400]
    return None


def _slim_mx(unit_id: str, rows) -> list:
    out = []
    for mx in rows or []:
        if not isinstance(mx, dict):
            continue
        cwo = mx.get("canonical_wrong_output") or mx.get("cwo")
        if not cwo:
            continue
        mid = mx.get("mx_id") or mx.get("id") or "MX"
        out.append(
            {
                "id": f"{unit_id}/{mid}",
                "type": mx.get("confusion_type") or mx.get("type"),
                "cwo": str(cwo)[:400],
                "status": mx.get("status") or "CANDIDATE",
            }
        )
    return out


def _slim_pedagogy(h: dict) -> dict:
    mm = h.get("mastery_model") or {}
    lok = h.get("lok_model") or {}
    gp = h.get("gaming_pocket_map") or {}
    pockets = gp.get("pockets") if isinstance(gp, dict) else []
    anti = h.get("anti_narration_constraint")
    if isinstance(anti, dict):
        anti = anti.get("constraint") or anti.get("text")
    facets = []
    for f in (h.get("facets") or [])[:6]:
        if isinstance(f, dict):
            facets.append(f.get("facet_id") or f.get("name"))
        elif isinstance(f, str):
            facets.append(f)
    return {
        "joined": True,
        "mastery_signal": str((mm.get("mastery_signal") or mm.get("claim") or ""))[:400],
        "lok_folk": str((lok.get("folk_default") or lok.get("description") or ""))[:280],
        "gaming_pockets": [
            {"type": p.get("pocket_type"), "apparent_success": str(p.get("apparent_success") or "")[:160]}
            for p in (pockets or [])[:4]
            if isinstance(p, dict)
        ],
        "facets": [x for x in facets if x],
        "anti_narration": (str(anti)[:280] if anti else None),
    }


def harvest() -> tuple[list, dict]:
    units = []
    skipped = []
    for grade in ("06", "07", "08"):
        gdir = HYBRID / f"grade_{grade}"
        if not gdir.is_dir():
            continue
        for chdir in sorted(gdir.iterdir()):
            path = chdir / "chapter_intelligence.json"
            if not path.is_file():
                skipped.append(str(path))
                continue
            key = (grade, chdir.name)
            bind = CHAPTER.get(key)
            if not bind:
                skipped.append(f"unbound {key}")
                continue
            node, grain, title = bind
            doc = json.loads(path.read_text(encoding="utf-8"))
            ns = doc.get("chapter_namespace") or f"science/grade_{grade}/{chdir.name}"
            for h in doc.get("hinges") or []:
                hid = h.get("hinge_id") or "H"
                uid = hid if "/" in str(hid) else f"{ns}/{hid}"
                use_node, use_grain = node, grain
                if uid in HINGE_OVERRIDE:
                    use_node, use_grain = HINGE_OVERRIDE[uid]
                mx = _slim_mx(uid, h.get("mx_pool"))
                mx_notes = []
                if uid == "science/grade_06/ch_02/H002":
                    mx_notes.append(
                        "Astra SME: first CWO may be a valid grouping (animals), not a mix-up. Left as source mx; not rewritten."
                    )
                units.append(
                    {
                        "subject": "science",
                        "unit_id": uid,
                        "node": use_grain,
                        "node_parent": use_node,
                        "grade": int(grade),
                        "grade_band": "SECONDARY",
                        "chapter": ns,
                        "chapter_title": title,
                        "decision_hinge": h.get("decision_hinge"),
                        "mechanism": _mech_text(h.get("mechanism_core")),
                        "cognitive_operation": h.get("cognitive_operation"),
                        "board": "NCERT",
                        "mx": mx,
                        "n_mx_na": max(0, len(h.get("mx_pool") or []) - len(mx)),
                        "pedagogy": _slim_pedagogy(h),
                        "status": "hinge_map_candidate",
                        "source_release": doc.get("release_status"),
                        **({"mx_notes": mx_notes} if mx_notes else {}),
                    }
                )
    return units, {"skipped": skipped}


def node_docs() -> list:
    out = []
    for n in NODES:
        out.append(
            {
                "id": n["id"],
                "title": n["title"],
                "kind": n["kind"],
                "mechanism": n["mechanism"],
                "map_id": n["id"],
                "sheaf_home": n.get("sheaf_home"),
            }
        )
        for c in n.get("children") or []:
            out.append(
                {
                    "id": c["id"],
                    "title": c["title"],
                    "kind": "grain",
                    "parent": n["id"],
                    "map_id": c["id"],
                    "sheaf_home": n.get("sheaf_home"),
                }
            )
    return out


def concept_tree(units: list) -> dict:
    by_grain = Counter(u.get("node") for u in units)
    tree = []
    for n in NODES:
        children = []
        for c in n.get("children") or []:
            children.append(
                {
                    "id": c["id"],
                    "title": c["title"],
                    "n_hinges": by_grain.get(c["id"], 0),
                }
            )
        tree.append(
            {
                "id": n["id"],
                "title": n["title"],
                "sheaf_home": n.get("sheaf_home"),
                "n_hinges": sum(ch["n_hinges"] for ch in children),
                "concepts": children,
            }
        )
    return {"schema": "ttwin.science_g68.tree.v1", "nodes": tree}


def build() -> dict:
    units, meta = harvest()
    nodes = node_docs()
    tree = concept_tree(units)
    by_grade = Counter(u["grade"] for u in units)
    by_node = Counter(u["node_parent"] for u in units)
    n_mx = sum(len(u.get("mx") or []) for u in units)
    doc = {
        "schema": "ttwin.map.v1",
        "subject": "science",
        "label": "Combined science (NCERT grades 6–8)",
        "map_status": "hinge_map_candidate",
        "n": len(units),
        "nodes": nodes,
        "units": units,
        "concept_tree": tree,
        "source": "data/intelligence/chapter_intelligence_hybrid/science/grade_{06,07,08}",
        "honesty": (
            "Derived from released NCERT science chapter intelligence. "
            "Mx copied from mx_pool; none invented. Big-idea tree is cartographer-authored "
            "and awaits Astra SME approval. Does not rewrite chemistry/physics/biology maps."
        ),
        "census": {
            "n_hinges": len(units),
            "n_mx": n_mx,
            "by_grade": {str(k): by_grade[k] for k in sorted(by_grade)},
            "by_big_idea": dict(by_node),
            "skipped": meta["skipped"],
        },
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "astra_sme": {
            "status": "approve_with_fixes_applied",
            "verdict_file": "data/maps/science_g68_astra.json",
            "applied": [
                "g7 ch_02 default grain S2/H-MATERIAL",
                "g7 ch_08 default grain S4/H-MOTION",
                "science/grade_06/ch_11/H002 -> S3/H-BODY",
                "S4 and S5 mechanism text corrected",
                "S3/H-LIFE, S2/H-STATES, S2/H-MIXTURE labels broadened",
                "unit_id uses chapter_intelligence hinge_id (no doubled namespace)",
                "flagged Mx on grade_06/ch_02/H002 left as source; not rewritten",
            ],
            "owner_signoff": "pending",
        },
    }
    return doc


def main() -> int:
    doc = build()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "science.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    receipt = {
        "n": doc["n"],
        "n_mx": doc["census"]["n_mx"],
        "by_grade": doc["census"]["by_grade"],
        "by_big_idea": doc["census"]["by_big_idea"],
        "tree": doc["concept_tree"],
        "path": "data/maps/science.json",
        "map_status": doc["map_status"],
    }
    (OUT / "science_g68_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    print("wrote", path, path.stat().st_size, "B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
