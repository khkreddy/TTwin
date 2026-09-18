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
    ov = sci.get("candidate_overlay") or {}
    assert ov.get("questions", "").startswith("candidate/")
    assert ov.get("nav", "").startswith("candidate/")
    assert sci["packs"][0]["n"] == 109
    assert sci["n_tagged"] == 109
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


def test_menu_contract_science_then_ideas():
    """Owner pin: Science is a subject; inside it, big idea then concept. No map blobs required."""
    catalog = json.loads((ROOT / "data/subjects.json").read_text(encoding="utf-8"))
    sci = next(s for s in catalog["subjects"] if s["id"] == "science")
    assert sci["label"] == "Science"
    assert [p["id"] for p in sci["packs"]] == ["middle_6_8"]
    vocab = json.loads((ROOT / "data/vocab/science.json").read_text(encoding="utf-8"))
    pack = "middle_6_8"
    origins = [x for x in vocab["ideas"] if x["kind"] == "concept_origin" and pack in x["packs"]]
    grains = [x for x in vocab["ideas"] if x["kind"] == "grain" and pack in x["packs"]]
    assert [x["id"] for x in origins] == ["S1", "S2", "S3", "S4", "S5", "S6"]
    assert all(x.get("parent") in {o["id"] for o in origins} for x in grains)
    assert len(grains) == 16
    maths = json.loads((ROOT / "data/vocab/maths.json").read_text(encoding="utf-8"))
    mid = [x for x in maths["ideas"] if x["kind"] == "concept_origin" and "middle_6_8" in x["packs"]]
    assert "math:M7" not in {x["id"] for x in mid}
    assert any(x["id"] == "math:M4" and "Euclidean" in x["title"] for x in mid)


def test_hinges_shape_and_optional_map_join():
    n_primary = 0
    amb = 0
    for path in (ROOT / "data/questions").glob("*.json"):
        for it in json.loads(path.read_text(encoding="utf-8")):
            h = it.get("hinges")
            if not h:
                continue
            assert isinstance(h.get("primary"), str) and h["primary"].strip()
            assert h["primary"] != it.get("uid")
            supp = h.get("supporting") or []
            assert isinstance(supp, list)
            assert h["primary"] not in supp
            n_primary += 1
            method = (h.get("binder") or {}).get("method")
            if method == "prefix_unit_id":
                field = (h.get("binder") or {}).get("field")
                key = it.get(field) or ""
                if key:
                    assert h["primary"] == key or h["primary"].startswith(key + ".")
    assert n_primary >= 70000
    unit_ids = set()
    maps = [
        ROOT / "data/maps/science.json",
        ROOT / "data/maps/BIOLOGY_MAP.json",
        ROOT / "data/maps/CHEMISTRY_MAP_COMBINED.json",
        ROOT / "data/maps/PHYSICS_MAP.json",
        ROOT / "data/maps/MATHEMATICS_MAP.json",
    ]
    present = [p for p in maps if p.is_file()]
    if len(present) < 5:
        print("skip map-join check; final maps not in clone")
        return
    for p in present:
        doc = json.loads(p.read_text(encoding="utf-8"))
        for row in doc.get("statements") or doc.get("units") or []:
            if row.get("unit_id"):
                unit_ids.add(row["unit_id"])
    missing = 0
    for path in (ROOT / "data/questions").glob("*.json"):
        for it in json.loads(path.read_text(encoding="utf-8")):
            prim = (it.get("hinges") or {}).get("primary")
            if prim and prim not in unit_ids:
                missing += 1
                if missing <= 3:
                    print("unresolved primary", it.get("uid"), prim)
    assert missing == 0, missing


def test_manifest_pins_without_blobs():
    man = json.loads((ROOT / "data/maps/MANIFEST.json").read_text(encoding="utf-8"))
    assert man["schema"] == "ttwin.map_manifest.v1"
    ids = {f["id"] for f in man["files"]}
    assert ids == {"science", "mathematics", "chemistry", "physics", "biology"}
    for f in man["files"]:
        assert len(f["sha256"]) == 64
        if f["id"] == "science":
            assert f["on_github"] is True
        else:
            assert f["on_github"] is False


if __name__ == "__main__":
    test_packs_and_science()
    test_vocab_from_maps()
    test_biology_map_q_nodes()
    test_menu_contract_science_then_ideas()
    test_manifest_pins_without_blobs()
    test_hinges_shape_and_optional_map_join()
    test_corpus_packs_and_hinges()
    print("test_four_pack_plan ok")

