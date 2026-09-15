#!/usr/bin/env python3
"""Join constructed LBS + modify seeds onto packed TTwin question JSON.

Drives lbs_construct.ensure_item (the real constructor). Does not rewrite freeze.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from lbs_construct import ensure_item, lbs_complete, LETTERS

TTWIN = Path(__file__).resolve().parents[1]
QUESTIONS = TTWIN / "data" / "questions"


def census_item(it: dict) -> dict:
    a = it.get("assessment") or {}
    k = a.get("mcq_key")
    keyed = k in LETTERS and a.get("key_status") == "available"
    n_opt = sum(1 for L in LETTERS if str((it.get("options") or {}).get(L) or "").strip())
    eligible = keyed and n_opt >= 2
    lbs = a.get("learn_by_solve")
    seeds = a.get("modify_seeds") or []
    ex = (a.get("examiner_comment") or {}).get("present")
    complete = bool(eligible and lbs_complete(lbs, k, it.get("options") or {}, it))
    return {
        "keyed": keyed,
        "eligible": eligible,
        "lbs_complete": complete,
        "modify_seeds": bool(complete and seeds),
        "examiner": bool(ex),
    }


def census_items(items: list) -> dict:
    n_mcq_key = n_el = n_lbs = n_mod = n_ex = 0
    for it in items:
        c = census_item(it)
        n_mcq_key += int(c["keyed"])
        n_el += int(c.get("eligible") or False)
        n_lbs += int(c["lbs_complete"])
        n_mod += int(c["modify_seeds"])
        n_ex += int(c["examiner"])
    return {
        "n": len(items),
        "n_mcq_key": n_mcq_key,
        "n_mcq_eligible": n_el,
        "n_lbs_complete": n_lbs,
        "n_modify_seeds": n_mod,
        "n_examiner_present": n_ex,
    }


def join_items(items: list) -> tuple[int, dict]:
    n = 0
    for it in items:
        if ensure_item(it):
            n += 1
    return n, census_items(items)


def join_file(path: Path) -> dict:
    items = json.loads(path.read_text(encoding="utf-8"))
    n, stats = join_items(items)
    path.write_text(json.dumps(items, ensure_ascii=False) + "\n", encoding="utf-8")
    stats["file"] = path.name
    stats["n_updated"] = n
    return stats


def join_all(root: Path | None = None) -> dict:
    qdir = (root or TTWIN) / "data" / "questions"
    by = {}
    tot = {"n": 0, "n_mcq_key": 0, "n_mcq_eligible": 0, "n_lbs_complete": 0, "n_modify_seeds": 0, "n_examiner_present": 0, "n_updated": 0}
    for path in sorted(qdir.glob("*.json")):
        stats = join_file(path)
        by[path.name] = stats
        for k in tot:
            tot[k] += stats.get(k, 0)
    return {"by_file": by, **tot}


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if target and target.is_file():
        print(json.dumps(join_file(target), indent=2))
    else:
        print(json.dumps(join_all(target), indent=2))
