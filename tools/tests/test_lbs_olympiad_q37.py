#!/usr/bin/env python3
"""q37 LBS must unlock the unipotent expansion, not reprint 52/201/205."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from lbs_quality import followup_ok, is_stamp_lbs  # noqa: E402

UID = "jeebench:srcjson:math:jee_adv_2016_paper_2:q37"
BANNED = (
    "52 is the required",
    "Does the required working actually give",
    "Option A. Does the required",
    "would need “52”",
)


def test_q37_lbs_is_a_gate_not_a_wrapper():
    rows = json.loads((ROOT / "data/questions/maths-olympiad.json").read_text(encoding="utf-8"))
    it = next(x for x in rows if x.get("uid") == UID)
    lbs = (it.get("assessment") or {}).get("learn_by_solve") or {}
    assert lbs, "missing LBS"
    assert not is_stamp_lbs(lbs)
    blob = json.dumps(lbs)
    for b in BANNED:
        assert b not in blob, b
    wrong = lbs.get("wrong") or {}
    assert set(wrong) == {"A", "C", "D"}
    a_stem = wrong["A"]["followup"]["stem"]
    assert "I + N" in a_stem or "I+N" in a_stem
    d_stem = wrong["D"]["followup"]["stem"]
    assert "binom" in d_stem or "N^2" in d_stem or "N^{2}" in d_stem
    for L, row in wrong.items():
        assert followup_ok(row.get("followup")), L
    print("q37_lbs_ok", wrong["A"]["followup"]["key"], wrong["C"]["followup"]["key"], wrong["D"]["followup"]["key"])


if __name__ == "__main__":
    test_q37_lbs_is_a_gate_not_a_wrapper()
