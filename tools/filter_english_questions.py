#!/usr/bin/env python3
"""Keep English-only questions. Rebuild nav (core vs bank) and catalog counts.

Drops CJK / Hangul / Kana / Arabic / Devanagari in stem or parts.
K12-Graph is almost all Chinese and will leave the live bank.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from question_pack import OUT, SUBJECT_ORDER, dump_json, nav_from_item  # noqa: E402

NON_EN = re.compile(
    r"[\u0400-\u04FF\u0600-\u06FF\u0900-\u097F\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF]"
)
QDIR = OUT / "questions"
NAV = OUT / "nav"
CORE_PACKS = {"igcse_9_10", "senior_11_12_as_a", "olympiad_iit"}


def blob(it: dict) -> str:
    bits = [str(it.get("stem") or ""), str(it.get("stem_lead") or "")]
    for p in it.get("parts") or []:
        if isinstance(p, dict):
            bits.append(str(p.get("stem") or ""))
            for sp in p.get("subparts") or []:
                if isinstance(sp, dict):
                    bits.append(str(sp.get("stem") or ""))
    return "\n".join(bits)


def is_english(it: dict) -> bool:
    return not NON_EN.search(blob(it))


def main() -> int:
    dropped = []
    kept_n = 0
    by_pack = defaultdict(list)
    for path in sorted(QDIR.glob("*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        keep, drop = [], []
        for it in rows:
            if is_english(it):
                keep.append(it)
            else:
                drop.append({"uid": it.get("uid"), "bank": it.get("bank"), "file": path.name})
        print(f"  {path.name}: {len(rows)} -> {len(keep)} (drop {len(drop)})")
        dump_json(path, keep)
        dropped.extend(drop)
        kept_n += len(keep)
        for it in keep:
            by_pack[(it.get("subject"), it.get("pack"))].append(it)
    dropped_path = OUT / "dropped_non_english.jsonl"
    with dropped_path.open("w", encoding="utf-8") as fh:
        for row in dropped:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    catalog = json.loads((OUT / "subjects.json").read_text(encoding="utf-8"))
    by_id = {s["id"]: s for s in catalog.get("subjects") or []}
    for subject in SUBJECT_ORDER:
        core, bank = [], []
        packs_out = []
        spec = by_id.get(subject) or {"id": subject, "packs": []}
        for pack_ent in spec.get("packs") or []:
            pid = pack_ent.get("id")
            items = by_pack.get((subject, pid)) or []
            items.sort(key=lambda r: r.get("uid") or "")
            pack_ent["n"] = len(items)
            pack_ent["n_complete_exam"] = sum(1 for it in items if it.get("complete_exam"))
            pack_ent["n_stems"] = sum(1 for it in items if str(it.get("stem") or "").strip())
            packs_out.append(pack_ent)
            recs = [nav_from_item(it) for it in items]
            if pid == "question_bank":
                bank.extend(recs)
            else:
                core.extend(recs)
        spec["packs"] = packs_out
        spec["n_tagged"] = sum(p.get("n") or 0 for p in packs_out)
        spec["n_complete_exam"] = spec["n_tagged"]
        if bank:
            spec["nav_bank"] = f"data/nav/{subject}-bank.json"
            dump_json(NAV / f"{subject}-bank.json", bank)
        core.sort(key=lambda r: (r.get("pack") or "", r.get("uid") or ""))
        dump_json(NAV / f"{subject}.json", core)
        by_id[subject] = spec
    catalog["subjects"] = [by_id[s] for s in SUBJECT_ORDER if s in by_id]
    dump_json(OUT / "subjects.json", catalog)
    print(json.dumps({"kept": kept_n, "dropped_non_english": len(dropped)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
