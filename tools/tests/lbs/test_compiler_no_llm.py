"""Compiler instantiation path must not import tools.lbs_ai or need a network."""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _py_files():
    yield ROOT / "tools/lbs_compile.py"
    lbs = ROOT / "tools/lbs"
    if lbs.is_dir():
        yield from lbs.rglob("*.py")


def test_no_lbs_ai_import() -> None:
    for path in _py_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert not a.name.startswith("lbs_ai") and "lbs_ai" not in a.name, path
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "lbs_ai" not in node.module, path


def test_never_cases_present() -> None:
    doc = json.loads((ROOT / "data/lbs/never_cases.v1.json").read_text(encoding="utf-8"))
    stems = {c["bad_stem"] for c in doc["cases"]}
    assert any("belongs in the correct 1 / 2 / 3 combination" in s for s in stems)
    assert any("that species actually have" in s for s in stems)


def test_plan_electrochem_zero_instantiate_calls() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "tools"))
    import lbs_compile

    plan = lbs_compile.cmd_plan("electrochem")
    assert plan["instantiate_model_calls"] == 0
    assert plan["n_keyed_parents"] > 0
    assert plan["author_calls_max"] == plan["map_units_h_redox"] + plan["map_units_h_echem"]


if __name__ == "__main__":
    test_no_lbs_ai_import()
    test_never_cases_present()
    test_plan_electrochem_zero_instantiate_calls()
    print("ok")
