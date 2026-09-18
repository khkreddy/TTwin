#!/usr/bin/env python3
"""Shipped bank rows: K12 6–8 science grains, advanced practice on map nodes."""
from __future__ import annotations

import json
from pathlib import Path

Q = Path(__file__).resolve().parents[2] / "data/questions"


def _rows(*names):
    out = []
    for n in names:
        out.extend(json.loads((Q / n).read_text(encoding="utf-8")))
    return out


def test_k12_science_uses_s_grains():
    rows = [r for r in _rows("biology-bank.json", "chemistry-bank.json", "physics-bank.json") if r.get("bank") == "k12_graph"]
    assert rows
    mapped = [r for r in rows if r.get("node") and r["node"] != "unmapped"]
    assert mapped, "k12 science still unmapped"
    s = [r for r in mapped if str(r.get("node")).startswith("S")]
    assert s, "expected science-map grains S1–S6 on k12 science"
    assert all(r.get("practice_tier") == "core" for r in s)
    print("k12_science", len(rows), "mapped", len(mapped), "S-grains", len(s), "sample", s[0]["uid"], s[0]["node"])


def test_k12_maths_mapped():
    rows = [r for r in _rows("maths-bank.json") if r.get("bank") == "k12_graph"]
    un = [r for r in rows if r.get("node") == "unmapped"]
    assert not un, un[:3]
    assert any(str(r.get("node")).startswith("math:") for r in rows)
    print("k12_maths", len(rows), "node0", rows[0]["node"])


def test_advanced_practice_on_map_nodes():
    rows = [r for r in _rows("chemistry-bank.json", "physics-bank.json", "maths-bank.json") if r.get("bank") in {"jeebench", "physics500", "mathnet"}]
    assert rows
    adv = [r for r in rows if r.get("practice_tier") == "advanced"]
    assert adv
    assert all(r.get("node") and r["node"] != "unmapped" for r in adv[:50])
    print("advanced", len(adv), "sample", adv[0]["uid"], adv[0]["node"])


if __name__ == "__main__":
    test_k12_science_uses_s_grains()
    test_k12_maths_mapped()
    test_advanced_practice_on_map_nodes()
    print("tag_unmapped_ok")
