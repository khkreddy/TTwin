#!/usr/bin/env python3
"""Drive extra-bank packing on real source items."""
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from pack_question_bank import (  # noqa: E402
    _assessment,
    _body,
    _item_type_from_label,
    _parse_options,
    _subject,
)
from question_pack import UNMAPPED, compose_item, unmapped_tags  # noqa: E402

K12 = Path("/home/harik/awm_build/data/corpus_intelligence/awm_corpus/K12-Graph/chemistry_9a_rjb.json")
JEE = Path("/home/harik/awm_build/data/corpus_intelligence/awm_corpus/jeebench-dataset.json")
P500 = Path("/home/harik/awm_build/data/corpus_intelligence/awm_corpus/physics-500/physics500_v2_handover/out/records/P001.json")


def test_k12_rjb_projects():
    raw = json.loads(K12.read_text(encoding="utf-8"))
    q = (raw.get("questions") or [])[0]
    opts = _parse_options(q["stem"])
    itype = _item_type_from_label(q.get("type") or "", opts)
    tags = unmapped_tags(q["id"], "chemistry", "question_bank", item_type=itype, bank="k12_graph")
    body = _body(stem=q["stem"], item_type=itype, options=opts)
    item = compose_item(tags, body, _assessment(q.get("answer")))
    assert item["node"] == UNMAPPED
    assert item["chapter_id"] == UNMAPPED
    assert item["pack"] == "question_bank"
    assert item["subject"] == "chemistry"
    assert item["stem"]
    assert item["item_type"] in {"mcq", "open_response", "structured"}
    assert item["assessment"]["key_source"]
    print("k12", item["uid"], item["item_type"], item["node"])


def test_jeebench_subject_and_type():
    rows = json.loads(JEE.read_text(encoding="utf-8"))
    rec = next(x for x in rows if x.get("type") == "MCQ")
    assert _subject(rec["subject"]) in {"physics", "chemistry", "maths"}
    stem = rec["question"]
    assert stem
    gold = rec.get("gold")
    itype = "mcq" if gold in {"A", "B", "C", "D"} else "open_response"
    print("jeebench", rec["subject"], itype, gold)


def test_phy500_stem():
    o = json.loads(P500.read_text(encoding="utf-8"))
    pres = o["presentation"]
    stem = (pres.get("stem") or {}).get("latex") or ""
    assert "Earth" in stem or "Sun" in stem or len(stem) > 20
    print("phy500", o.get("record_id"), "stem_len", len(stem))


if __name__ == "__main__":
    test_k12_rjb_projects()
    test_jeebench_subject_and_type()
    test_phy500_stem()
    print("pack_bank_ok")
