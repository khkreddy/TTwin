#!/usr/bin/env python3
"""Restore K12 grades 6–8 from git, translate to English, pack as junior_6_8."""
from __future__ import annotations

import json
import re
import subprocess
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
import sys
sys.path.insert(0, str(TOOLS))
from question_pack import (  # noqa: E402
    OUT,
    PACK_LABEL,
    SUBJECT_ORDER,
    dump_json,
    nav_from_item,
)

COMMIT = "3364d9f"
BANKS = [
    "data/questions/biology-bank.json",
    "data/questions/chemistry-bank.json",
    "data/questions/maths-bank.json",
    "data/questions/physics-bank.json",
]
GRADE_RE = re.compile(r"_([678])[ab]_rjb")
CJK = re.compile(r"[\u4e00-\u9fff]")
CACHE = ROOT / "data" / "k12_g68_en_cache.json"


def git_json(rel: str):
    raw = subprocess.check_output(["git", "show", f"{COMMIT}:{rel}"], cwd=str(ROOT))
    return json.loads(raw)


def translate_one(text: str) -> str:
    if not text or not CJK.search(text):
        return text
    url = (
        "https://translate.googleapis.com/translate_a/single?client=gtx&sl=zh-CN&tl=en&dt=t&q="
        + urllib.parse.quote(text[:4500])
    )
    req = urllib.request.Request(url, headers={"User-Agent": "TTwin/k12-g68"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    chunks = data[0] if data else []
    out = "".join(part[0] for part in chunks if part and part[0])
    return out.strip() or text


def translate_cached(text: str, cache: dict) -> str:
    if not text:
        return text
    if text in cache:
        return cache[text]
    if not CJK.search(text):
        cache[text] = text
        return text
    try:
        en = translate_one(text)
    except Exception:
        time.sleep(1.5)
        en = translate_one(text)
    cache[text] = en
    time.sleep(0.08)
    return en


def translate_item(it: dict, cache: dict) -> dict:
    out = dict(it)
    out["stem"] = translate_cached(str(it.get("stem") or ""), cache)
    out["stem_lead"] = translate_cached(str(it.get("stem_lead") or out["stem"]), cache)
    opts = dict(it.get("options") or {})
    out["options"] = {k: translate_cached(str(v), cache) for k, v in opts.items()}
    parts = []
    for p in it.get("parts") or []:
        if not isinstance(p, dict):
            continue
        q = dict(p)
        q["stem"] = translate_cached(str(p.get("stem") or ""), cache)
        subs = []
        for sp in p.get("subparts") or []:
            if isinstance(sp, dict):
                r = dict(sp)
                r["stem"] = translate_cached(str(sp.get("stem") or ""), cache)
                subs.append(r)
        q["subparts"] = subs
        parts.append(q)
    if parts:
        out["parts"] = parts
    a = dict(it.get("assessment") or {})
    ms = a.get("mark_scheme")
    if isinstance(ms, dict) and ms.get("text"):
        ms = dict(ms)
        ms["text"] = translate_cached(str(ms["text"]), cache)
        a["mark_scheme"] = ms
    ex = a.get("examiner_comment")
    if isinstance(ex, dict) and ex.get("text") and CJK.search(str(ex.get("text") or "")):
        ex = dict(ex)
        ex["text"] = translate_cached(str(ex["text"]), cache)
        a["examiner_comment"] = ex
    out["assessment"] = a
    out["pack"] = "junior_6_8"
    out["grade_band"] = "SECONDARY"
    out["practice_tier"] = "core"
    out["language"] = "en"
    out["source_lang"] = "zh"
    m = GRADE_RE.search(out.get("uid") or "")
    if m:
        out["grade"] = int(m.group(1))
    return out


def still_cjk(it: dict) -> bool:
    blob = " ".join(
        [
            str(it.get("stem") or ""),
            " ".join(str(v) for v in (it.get("options") or {}).values()),
        ]
    )
    return bool(CJK.search(blob))


def main() -> int:
    cache = {}
    if CACHE.is_file():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    recovered = []
    for rel in BANKS:
        for it in git_json(rel):
            if it.get("bank") != "k12_graph":
                continue
            if not GRADE_RE.search(it.get("uid") or ""):
                continue
            recovered.append(it)
    print(f"recovered g6-8 {len(recovered)} cache {len(cache)}", flush=True)
    done_uids = set()
    out_by: dict[str, list] = defaultdict(list)
    for i, it in enumerate(recovered, 1):
        en = translate_item(it, cache)
        if still_cjk(en):
            # retry stem alone
            en["stem"] = translate_cached(it.get("stem") or "", cache)
        out_by[en.get("subject") or "maths"].append(en)
        done_uids.add(en["uid"])
        if i % 25 == 0 or i == len(recovered):
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            print(f"  {i}/{len(recovered)}", flush=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    leftover = sum(1 for rows in out_by.values() for it in rows if still_cjk(it))
    print("still_cjk", leftover)

    # write question files + merge into nav core
    cat = json.loads((OUT / "subjects.json").read_text(encoding="utf-8"))
    by_id = {s["id"]: s for s in cat["subjects"]}
    for subject in SUBJECT_ORDER:
        rows = out_by.get(subject) or []
        if not rows:
            continue
        rows.sort(key=lambda r: r.get("uid") or "")
        path = OUT / "questions" / f"{subject}-junior.json"
        dump_json(path, rows)
        spec = by_id[subject]
        packs = [p for p in (spec.get("packs") or []) if p.get("id") != "junior_6_8"]
        packs.append(
            {
                "id": "junior_6_8",
                "label": PACK_LABEL.get("junior_6_8", "E · Grades 6–8"),
                "questions": f"data/questions/{subject}-junior.json",
                "n": len(rows),
                "n_complete_exam": len(rows),
                "n_stems": sum(1 for it in rows if str(it.get("stem") or "").strip()),
            }
        )
        spec["packs"] = packs
        spec["n_tagged"] = sum(p.get("n") or 0 for p in packs)
        # rebuild core nav = existing core file + junior
        core_path = OUT / "nav" / f"{subject}.json"
        core = json.loads(core_path.read_text(encoding="utf-8")) if core_path.is_file() else []
        core = [r for r in core if r.get("pack") != "junior_6_8"]
        core.extend(nav_from_item(it) for it in rows)
        core.sort(key=lambda r: (r.get("pack") or "", r.get("uid") or ""))
        dump_json(core_path, core)
        by_id[subject] = spec
    cat["subjects"] = [by_id[s] for s in SUBJECT_ORDER if s in by_id]
    dump_json(OUT / "subjects.json", cat)
    print("written", {s: len(out_by[s]) for s in out_by})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
