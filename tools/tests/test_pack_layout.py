#!/usr/bin/env python3
"""Drive the real pack transform on representative source exam items."""
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from question_pack import (  # noqa: E402
    hold_reason,
    map_item_type,
    project_exam_item,
)

CHEM_JOINED = Path("/home/harik/awm_build/data/awm_product/generated/exam_v1_chem_joined/items.jsonl")
CORPUS = Path("/home/harik/awm_build/data/awm_product/generated/exam_v1_corpus/items.jsonl")
TTWIN_Q = ROOT / "data/questions"


def _load_uids(path: Path, want: set[str]) -> dict:
    found = {}
    if not path.is_file():
        return found
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            o = json.loads(line)
            uid = o.get("item_uid")
            if uid in want:
                found[uid] = o
                if len(found) == len(want):
                    break
    return found


def _first_matching(path: Path, pred, limit: int = 1) -> list:
    out = []
    if not path.is_file():
        return out
    with path.open(encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            if pred(o):
                out.append(o)
                if len(out) >= limit:
                    break
    return out


def _tikz_ok(o: dict) -> bool:
    fig = o.get("figure") if isinstance(o.get("figure"), dict) else {}
    tj = fig.get("tikz") if isinstance(fig.get("tikz"), dict) else {}
    code = (tj or {}).get("code") or ""
    return "\\begin{tikzpicture}" in code or "\\begin{circuitikz}" in code


def test_map_item_type_free_response():
    assert map_item_type("free_response") == "open_response"
    assert map_item_type("structured") == "structured"
    assert map_item_type("not_a_type") is None


def test_pack_chemistry_structured_table():
    rows = _first_matching(
        CHEM_JOINED,
        lambda o: o.get("item_type") == "structured"
        and (o.get("tables") or [])
        and not hold_reason(o),
    )
    assert rows, "need a chemistry structured item with a table"
    src = rows[0]
    packed = project_exam_item(src)
    assert packed is not None
    assert packed["item_type"] == "structured"
    assert packed.get("tables"), src.get("item_uid")
    assert packed.get("parts"), src.get("item_uid")
    src_parts = src.get("parts") or []
    assert len(packed["parts"]) == len(src_parts)
    if src_parts and src_parts[0].get("marks") is not None:
        assert packed["parts"][0].get("marks") == src_parts[0].get("marks")
    if any((p.get("subparts") or []) for p in src_parts if isinstance(p, dict)):
        assert any(p.get("subparts") for p in packed["parts"])
    print("chem_structured_table", src.get("item_uid"), "parts", len(packed["parts"]), "tables", len(packed["tables"]))


def test_pack_physics_structured_tikz():
    rows = _first_matching(
        CORPUS,
        lambda o: str(o.get("item_uid") or "").startswith(("0625_", "9702_"))
        and o.get("item_type") == "structured"
        and _tikz_ok(o)
        and not hold_reason(o),
    )
    assert rows, "need a physics structured item with TikZ"
    src = rows[0]
    packed = project_exam_item(src)
    assert packed is not None
    assert packed["item_type"] == "structured"
    assert packed.get("tikz"), src.get("item_uid")
    assert "\\begin{tikzpicture}" in packed["tikz"] or "\\begin{circuitikz}" in packed["tikz"]
    assert packed.get("parts")
    print("phy_structured_tikz", src.get("item_uid"), "tikz_len", len(packed["tikz"]))


def test_pack_free_response_becomes_open_response():
    rows = _first_matching(CHEM_JOINED, lambda o: o.get("item_type") == "free_response")
    if not rows:
        rows = _first_matching(CORPUS, lambda o: o.get("item_type") == "free_response")
    assert rows, "need a free_response source item"
    src = rows[0]
    packed = project_exam_item(src)
    assert packed is not None
    assert packed["item_type"] == "open_response"
    assert map_item_type(src.get("item_type")) == "open_response"
    if src.get("parts"):
        assert packed.get("parts")
    print("free_response", src.get("item_uid"), "->", packed["item_type"])


def test_repack_flattened_maths_structured_uid():
    """Drive the packer on a maths structured uid that TTwin had stem-flattened."""
    packed_uid = "0580_m16_qp_12:q19"
    in_ttwin = False
    for path in sorted(TTWIN_Q.glob("maths-*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        if any(it.get("uid") == packed_uid for it in rows):
            in_ttwin = True
            break
    if not in_ttwin:
        for path in sorted(TTWIN_Q.glob("maths-*.json")):
            for it in json.loads(path.read_text(encoding="utf-8")):
                if it.get("item_type") == "structured":
                    packed_uid = it.get("uid")
                    in_ttwin = True
                    break
            if in_ttwin:
                break
    assert in_ttwin, "need a maths structured uid already in TTwin"
    found = _load_uids(CORPUS, {packed_uid})
    src = found.get(packed_uid)
    assert src, packed_uid
    packed = project_exam_item(src)
    assert packed is not None
    assert packed["item_type"] == "structured"
    assert packed.get("parts"), packed_uid
    src_parts = [p for p in (src.get("parts") or []) if isinstance(p, dict)]
    assert len(packed["parts"]) == len(src_parts)
    print("maths_flattened", packed_uid, "parts", len(packed["parts"]))


if __name__ == "__main__":
    test_map_item_type_free_response()
    test_pack_chemistry_structured_table()
    test_pack_physics_structured_tikz()
    test_pack_free_response_becomes_open_response()
    test_repack_flattened_maths_structured_uid()
    print("pack_layout_ok")
