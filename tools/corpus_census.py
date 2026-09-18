#!/usr/bin/env python3
"""Census TTwin packed rows vs exam-complete source vs held incomplete."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from question_pack import (  # noqa: E402
    CORPUS,
    CHEM_JOINED,
    SYL_META,
    hold_reason,
    map_item_type,
    subject_pack_of,
)

ROOT = TOOLS.parent
QDIR = ROOT / "data/questions"
HELD = ROOT / "data/held_questions.jsonl"


def ttwin_counts():
    by = Counter()
    n = 0
    uids = set()
    n_parts = 0
    for path in sorted(QDIR.glob("*.json")):
        for it in json.loads(path.read_text(encoding="utf-8")):
            n += 1
            uids.add(it.get("uid"))
            by[(it.get("subject"), it.get("item_type"))] += 1
            if it.get("parts"):
                n_parts += 1
    return n, uids, by, n_parts


def source_counts(tt_uids: set[str]):
    complete = Counter()
    shippable = Counter()
    held = Counter()
    not_in_tt_shippable = Counter()
    seen = set()
    for path in (CHEM_JOINED, CORPUS):
        if not path.is_file():
            continue
        with path.open(encoding="utf-8") as f:
            for line in f:
                o = json.loads(line)
                uid = o.get("item_uid")
                if not uid or uid in seen:
                    continue
                seen.add(uid)
                meta = subject_pack_of(uid)
                subj = meta[0] if meta else "other"
                itype = map_item_type(o.get("item_type")) or o.get("item_type") or "unknown"
                complete[(subj, itype)] += 1
                reason = hold_reason(o)
                if reason:
                    held[(subj, itype, reason)] += 1
                else:
                    shippable[(subj, itype)] += 1
                    if uid not in tt_uids:
                        not_in_tt_shippable[(subj, itype)] += 1
    return complete, shippable, held, not_in_tt_shippable


def main() -> int:
    n, uids, by, n_parts = ttwin_counts()
    complete, shippable, held_src, leftover = source_counts(uids)
    held_file = Counter()
    if HELD.is_file():
        with HELD.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    held_file[json.loads(line).get("reason") or "unknown"] += 1
    doc = {
        "n_ttwin": n,
        "n_ttwin_with_parts": n_parts,
        "ttwin_by_subject_type": {f"{s}:{t}": c for (s, t), c in sorted(by.items())},
        "source_complete_by_subject_type": {
            f"{s}:{t}": c for (s, t), c in sorted(complete.items())
        },
        "source_shippable_by_subject_type": {
            f"{s}:{t}": c for (s, t), c in sorted(shippable.items())
        },
        "source_held_by_reason": {
            f"{s}:{t}:{r}": c for (s, t, r), c in sorted(held_src.items())
        },
        "shippable_not_in_ttwin": {
            f"{s}:{t}": c for (s, t), c in sorted(leftover.items()) if c
        },
        "held_ledger_by_reason": dict(held_file),
    }
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    text = json.dumps(doc, indent=2)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(str(out))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
