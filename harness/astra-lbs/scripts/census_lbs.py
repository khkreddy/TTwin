#!/usr/bin/env python3
"""Census packed TTwin LBS completeness. Resume-safe; does not construct."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from join_lbs import census_items  # noqa: E402

TTWIN = Path(__file__).resolve().parents[1]


def main() -> dict:
    qdir = TTWIN / "data" / "questions"
    by = {}
    tot = {
        "n": 0,
        "n_mcq_key": 0,
        "n_mcq_eligible": 0,
        "n_lbs_complete": 0,
        "n_lbs_relevant": 0,
        "n_stamp": 0,
        "n_modify_seeds": 0,
        "n_examiner_present": 0,
    }
    for path in sorted(qdir.glob("*.json")):
        items = json.loads(path.read_text(encoding="utf-8"))
        stats = census_items(items)
        stats["file"] = path.name
        by[path.name] = stats
        for k in tot:
            tot[k] += stats[k]
    doc = {
        "by_file": by,
        **tot,
        "complete": tot["n_lbs_relevant"] == tot["n_mcq_eligible"] == tot["n_modify_seeds"]
        and tot["n_mcq_eligible"] <= tot["n_mcq_key"]
        and tot["n_stamp"] == 0,
        "n_skipped_no_options": tot["n_mcq_key"] - tot["n_mcq_eligible"],
    }
    return doc


if __name__ == "__main__":
    doc = main()
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    text = json.dumps(doc, indent=2)
    if out:
        out.write_text(text + "\n", encoding="utf-8")
    print(text)
