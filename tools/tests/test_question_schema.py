#!/usr/bin/env python3
"""Load shipped ttwin.question.v1 and real packed rows. No copy of the validator."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "data/schema/ttwin.question.v1.json"
QUESTIONS = ROOT / "data/questions"


def test_every_shipped_question_matches_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    enum = schema["properties"]["item_type"]["enum"]
    required = schema["required"]
    validator = jsonschema.Draft202012Validator(schema)
    n = 0
    by_type = {}
    for path in sorted(QUESTIONS.glob("*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(rows, list), path
        for it in rows:
            n += 1
            errors = sorted(validator.iter_errors(it), key=lambda e: e.path)
            assert not errors, (path.name, it.get("uid"), errors[0].message)
            for key in required:
                assert key in it, (path.name, it.get("uid"), "missing", key)
            itype = it["item_type"]
            assert itype in enum, (it.get("uid"), itype)
            assert itype != "free_response", it.get("uid")
            assert isinstance(it.get("assessment"), dict), it.get("uid")
            for k in ("key_source", "key_status", "examiner_comment"):
                assert k in it["assessment"], (it.get("uid"), k)
            by_type[itype] = by_type.get(itype, 0) + 1
    assert n > 0
    print("schema_ok", n, "by_type", by_type)
    return n, by_type


if __name__ == "__main__":
    test_every_shipped_question_matches_schema()
