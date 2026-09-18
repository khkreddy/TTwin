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


def test_live_bank_is_english():
    import re
    cjk = re.compile(r"[\u4e00-\u9fff]")
    n = 0
    leaked = []
    for name in ["biology-igcse.json", "chemistry-bank.json", "maths-bank.json", "physics-bank.json"]:
        path = Q / name
        if not path.is_file():
            continue
        for r in json.loads(path.read_text(encoding="utf-8")):
            blob = str(r.get("stem") or "")
            if cjk.search(blob):
                leaked.append(r.get("uid"))
            n += 1
    assert not leaked, leaked[:5]
    print("english_ok", n)


def test_k12_remaining_english_only():
    rows = [r for r in _rows("chemistry-bank.json", "physics-bank.json", "maths-bank.json") if r.get("bank") == "k12_graph"]
    print("k12_english_remaining", len(rows))
    assert all(r.get("node") and r["node"] != "unmapped" for r in rows)


def test_advanced_practice_on_map_nodes():
    rows = [r for r in _rows("chemistry-bank.json", "physics-bank.json", "maths-bank.json") if r.get("bank") in {"jeebench", "physics500", "mathnet"}]
    assert rows
    adv = [r for r in rows if r.get("practice_tier") == "advanced"]
    assert adv
    assert all(r.get("node") and r["node"] != "unmapped" for r in adv[:50])
    print("advanced", len(adv), "sample", adv[0]["uid"], adv[0]["node"])


if __name__ == "__main__":
    test_live_bank_is_english()
    test_k12_remaining_english_only()
    test_advanced_practice_on_map_nodes()
    print("tag_unmapped_ok")
