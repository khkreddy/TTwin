#!/usr/bin/env python3
"""Astra SME review of the grades 6–8 combined science map.

Astra does not write the map. It approves, requests named fixes, or rejects.
Uses gpt-6-astra via the existing astra_client.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASTRA_SRC = Path("/home/harik/awm_build/data/spectra/canonical/src")
sys.path.insert(0, str(ASTRA_SRC))
from astra_client import ask, extract_json  # noqa: E402

MAP = ROOT / "data/maps/science.json"
OUT = ROOT / "data/maps/science_g68_astra.json"
BRIEF = ROOT / "data/maps/science_g68_astra_brief.json"


def brief(doc: dict) -> dict:
    units = doc.get("units") or []
    by_node: dict[str, list] = {}
    for u in units:
        by_node.setdefault(u.get("node_parent") or u.get("node"), []).append(u)
    samples = []
    for nid, rows in sorted(by_node.items()):
        for u in rows[:2]:
            samples.append(
                {
                    "unit_id": u.get("unit_id"),
                    "node": u.get("node"),
                    "node_parent": u.get("node_parent"),
                    "chapter_title": u.get("chapter_title"),
                    "decision_hinge": u.get("decision_hinge"),
                    "mechanism": u.get("mechanism"),
                    "n_mx": len(u.get("mx") or []),
                    "mx_types": [m.get("type") for m in (u.get("mx") or [])[:4]],
                    "mx0_cwo": ((u.get("mx") or [{}])[0].get("cwo") if u.get("mx") else None),
                }
            )
    chapters = {}
    for u in units:
        chapters[u.get("chapter")] = {
            "title": u.get("chapter_title"),
            "node": u.get("node_parent"),
            "grain": u.get("node"),
        }
    return {
        "census": doc.get("census"),
        "nodes": [
            {k: n.get(k) for k in ("id", "title", "kind", "parent", "sheaf_home", "mechanism")}
            for n in doc.get("nodes") or []
        ],
        "concept_tree": doc.get("concept_tree"),
        "chapter_bindings": chapters,
        "sample_hinges": samples,
        "honesty": doc.get("honesty"),
        "protocol": {
            "mx": "Copied from chapter_intelligence mx_pool. Cartographer must not invent Mx.",
            "nodes": "Concept origins, not chapter titles. A chapter maps to one grain.",
            "status": "hinge_map_candidate until SME + owner sign-off. Not a freeze.",
            "no_rewrite": "Must not rewrite chemistry/physics/biology live maps.",
        },
    }


PROMPT = """You are Astra, subject-matter expert for NCERT grades 6–8 combined Science (one Science book, not three senior subjects).

You are the independent SME. You did NOT author this map. You may APPROVE, APPROVE_WITH_FIXES, or REJECT.

Protocol the cartographer claims to have followed:
- Hinges and Mx are copied from released chapter intelligence (mx_pool). No invented Mx.
- Big ideas are concept origins (what decision the student must make), not chapter names.
- Combined science: physics/chemistry/biology content of grades 6–8 share one tree.
- Grain ids may name a sheaf_home on the senior maps (C/P/L/B) for later join; do not invent new senior nodes.
- Map status stays hinge_map_candidate until you and the owner sign off.

Review:
1. Are S1–S6 jointly enough for NCERT 6–8 science, without collapsing living systems into earth systems or treating magnets as a seventh origin?
2. Is each chapter binding the right home? Flag mis-homes (e.g. acids/bases as living systems).
3. Sample hinges: does the decision_hinge belong on that grain? Name unit_ids that should move.
4. Mx: you cannot re-author Mx. Only flag a sample if the CWO is empty, off-topic, or clearly not a student mix-up of that hinge.
5. Do not demand a comprehensive freeze. Candidate is allowed.

Return ONLY JSON:
{
  "verdict": "APPROVE" | "APPROVE_WITH_FIXES" | "REJECT",
  "summary": "one paragraph",
  "node_tree_ok": true/false,
  "move_chapters": [{"chapter": "science/grade_07/ch_02", "from": "S2/H-CHANGE", "to": "S2/H-MATERIAL", "why": "..."}],
  "move_hinges": [{"unit_id": "...", "to": "S5/H-HEAT", "why": "..."}],
  "mx_flags": [{"unit_id": "...", "issue": "..."}],
  "required_fixes": ["..."],
  "optional_notes": ["..."]
}
"""


def main() -> int:
    doc = json.loads(MAP.read_text(encoding="utf-8"))
    b = brief(doc)
    BRIEF.write_text(json.dumps(b, indent=2, ensure_ascii=False), encoding="utf-8")
    payload = PROMPT + "\n\nMAP BRIEF:\n" + json.dumps(b, ensure_ascii=False)
    print("asking Astra (gpt-6-astra) …", "brief chars", len(payload))
    text = ask(payload, effort="high", name="science_g68_map")
    (ROOT / "data/maps/science_g68_astra.md").write_text(text, encoding="utf-8")
    try:
        verdict = extract_json(text)
    except Exception as e:
        verdict = {"verdict": "REJECT", "summary": f"Astra output was not JSON: {e}", "raw_chars": len(text)}
    OUT.write_text(json.dumps(verdict, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: verdict.get(k) for k in ("verdict", "summary", "node_tree_ok")}, indent=2, ensure_ascii=False)[:2000])
    return 0 if verdict.get("verdict") in {"APPROVE", "APPROVE_WITH_FIXES"} else 1


if __name__ == "__main__":
    sys.exit(main())
