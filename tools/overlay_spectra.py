#!/usr/bin/env python3
"""Pack-time overlay: 9701 spectroscopy originals + learn-by-solve.

Does not rewrite frozen exam.v1. Patches the derived TTwin question JSON
(chemistry-senior) and copies original crops next to the pack.
Learner papers get the original figure; mx types stay under assessment.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

TTWIN = Path(__file__).resolve().parents[1]
AWM = Path("/home/harik/awm_build")
HARVEST = AWM / "data/spectra/items"
PRACTICE_PACK = AWM / "data/spectra/canonical/practice/static/pack.json"
PRACTICE_LBS = AWM / "data/spectra/canonical/practice/static/lbs.json"
QUESTIONS = TTWIN / "data/questions/chemistry-senior.json"
ORIG_DIR = TTWIN / "data/spectra/originals"
LBS_OUT = TTWIN / "data/spectra/lbs.json"


def _copy_originals(items: list[dict], dest_dir: Path) -> int:
    dest_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for it in items:
        folder = it.get("folder") or (it.get("uid") or "").replace(":", "_")
        src = HARVEST / folder / "original.png"
        if not src.is_file():
            continue
        dest = dest_dir / f"{folder}.png"
        if not dest.is_file() or dest.stat().st_mtime < src.stat().st_mtime:
            shutil.copy2(src, dest)
        n += 1
    return n


def _teacher_lbs(rec: dict) -> dict:
    wrong = {}
    for let, row in (rec.get("wrong") or {}).items():
        fu = row.get("followup") or {}
        wrong[let] = {
            "mx_type": row.get("mx_type"),
            "pathway": row.get("pathway"),
            "followup": {
                "stem": fu.get("stem") or "",
                "options": fu.get("options") or {},
                "key": fu.get("key"),
                "why": fu.get("why") or "",
            },
        }
    return {
        "solve": rec.get("solve") or "",
        "wrong": wrong,
        "key": rec.get("key"),
    }


def apply_to_items(items: list[dict], pack_by: dict, lbs_by: dict) -> dict:
    n_fig = n_lbs = n_stem = 0
    for it in items:
        uid = it.get("uid")
        if not uid:
            continue
        pack = pack_by.get(uid)
        lbs = lbs_by.get(uid)
        if not pack and not lbs:
            continue
        folder = (pack or {}).get("folder") or uid.replace(":", "_")
        orig = ORIG_DIR / f"{folder}.png"
        if orig.is_file():
            it["figure_src"] = f"data/spectra/originals/{folder}.png"
            it["has_figure"] = True
            # Learner paper uses the original crop, not a TikZ redraw of the exam item.
            it.pop("tikz", None)
            it.pop("tikz_packages", None)
            n_fig += 1
        if pack:
            if pack.get("stem"):
                it["stem"] = pack["stem"]
                it["stem_lead"] = pack["stem"]
                n_stem += 1
            if pack.get("options_are_figure"):
                it["options_are_figure"] = True
            if pack.get("options"):
                it["options"] = dict(pack["options"])
        if lbs:
            a = dict(it.get("assessment") or {})
            a["learn_by_solve"] = _teacher_lbs(lbs)
            it["assessment"] = a
            n_lbs += 1
    return {"n_figure_src": n_fig, "n_lbs": n_lbs, "n_stem": n_stem}


def apply_pack(root: Path | None = None) -> dict:
    root = root or TTWIN
    questions = root / "data/questions/chemistry-senior.json"
    orig_dir = root / "data/spectra/originals"
    lbs_out = root / "data/spectra/lbs.json"
    pack = json.loads(PRACTICE_PACK.read_text(encoding="utf-8")) if PRACTICE_PACK.is_file() else {"items": []}
    lbs_doc = json.loads(PRACTICE_LBS.read_text(encoding="utf-8")) if PRACTICE_LBS.is_file() else {"items": {}}
    pack_items = pack.get("items") or []
    n_orig = _copy_originals(pack_items, orig_dir)
    if PRACTICE_LBS.is_file():
        lbs_out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PRACTICE_LBS, lbs_out)
    pack_by = {it["uid"]: it for it in pack_items if it.get("uid")}
    lbs_by = lbs_doc.get("items") or {}
    items = json.loads(questions.read_text(encoding="utf-8"))
    stats = apply_to_items(items, pack_by, lbs_by)
    stats["n_originals_copied"] = n_orig
    stats["n_pack"] = len(pack_by)
    questions.write_text(json.dumps(items, ensure_ascii=False) + "\n", encoding="utf-8")
    meta_p = root / "data/meta.json"
    if meta_p.is_file():
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        meta["n_spectra_items"] = len(pack_by)
        meta["n_spectra_originals"] = stats["n_figure_src"]
        meta["n_spectra_lbs"] = stats["n_lbs"]
        honesty = meta.get("honesty") or ""
        note = (
            "9701 spectroscopy items overlay the original exam crop (figure_src) at pack time; "
            "learn-by-solve follow-ups live under assessment and are not printed on the learner paper."
        )
        if "9701 spectroscopy items overlay" not in honesty:
            meta["honesty"] = (honesty.rstrip() + " " + note).strip()
        meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "spectra overlay",
        f"pack={stats['n_pack']}",
        f"originals={n_orig}",
        f"figure_src={stats['n_figure_src']}",
        f"lbs={stats['n_lbs']}",
        f"stems={stats['n_stem']}",
    )
    return stats


if __name__ == "__main__":
    apply_pack()
