#!/usr/bin/env python3
"""Four demand packs, map-titled vocab, Science 6–8, no origin-as-pack."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

PACKS = {"middle_6_8", "secondary_9_10", "senior_11_12", "olympiad_iit"}


def test_packs_and_science():
    catalog = json.loads((ROOT / "data/subjects.json").read_text(encoding="utf-8"))
    ids = [s["id"] for s in catalog["subjects"]]
    assert "science" in ids, ids
    sci = next(s for s in catalog["subjects"] if s["id"] == "science")
    assert sci["packs"][0]["id"] == "middle_6_8"
    assert len(sci["packs"]) == 1
    for s in catalog["subjects"]:
        for p in s["packs"]:
            assert p["id"] in PACKS, (s["id"], p["id"])
            assert "IGCSE" not in p["label"] and "A ·" not in p["label"]


def test_vocab_from_maps():
    maths = json.loads((ROOT / "data/vocab/maths.json").read_text(encoding="utf-8"))
    m4 = next(x for x in maths["ideas"] if x["id"] == "math:M4")
    assert "Euclidean" in m4["title"], m4["title"]
    assert "Calculus" not in m4["title"]
    m7 = next(x for x in maths["ideas"] if x["id"] == "math:M7")
    assert "middle_6_8" not in (m7.get("packs") or [])
    sci = json.loads((ROOT / "data/vocab/science.json").read_text(encoding="utf-8"))
    origins = [x for x in sci["ideas"] if x["kind"] == "concept_origin"]
    assert {x["id"] for x in origins} == {"S1", "S2", "S3", "S4", "S5", "S6"}
    bio = json.loads((ROOT / "data/vocab/biology.json").read_text(encoding="utf-8"))
    assert any(x["id"] == "bio:Q1" for x in bio["ideas"])
    assert not any(x["id"].startswith("bio:L") for x in bio["ideas"])


def test_corpus_packs_and_hinges():
    import jsonschema
    schema = json.loads((ROOT / "data/schema/ttwin.question.v1.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    n = 0
    bound = 0
    sci = 0
    old = 0
    for path in sorted((ROOT / "data/questions").glob("*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        for it in rows:
            n += 1
            errs = list(validator.iter_errors(it))
            assert not errs, (path.name, it.get("uid"), errs[0].message)
            assert it["pack"] in PACKS, (it.get("uid"), it["pack"])
            if it.get("hinges", {}).get("primary"):
                bound += 1
            if it["subject"] == "science":
                sci += 1
                assert it["pack"] == "middle_6_8"
                assert str(it.get("node") or "").startswith("S")
    assert n == 86320
    assert sci == 109
    assert bound >= 70000
    assert old == 0
    print("ok", n, "bound", bound, "science", sci)


def test_biology_map_q_nodes():
    doc = json.loads((ROOT / "data/maps/biology.json").read_text(encoding="utf-8"))
    ids = {n["id"] for n in doc["nodes"]}
    assert "Q1" in ids and "UNRESOLVED" not in ids
    assert not any(u.get("node") == "UNRESOLVED" for u in doc["units"])


if __name__ == "__main__":
    test_packs_and_science()
    test_vocab_from_maps()
    test_biology_map_q_nodes()
    test_corpus_packs_and_hinges()
    print("test_four_pack_plan ok")
