#!/usr/bin/env python3
"""mx_derivation_v2 for NCERT science grades 6–8.

Same 7-type author as reports/paper/src/derive_ncert_mx_v2.py.
Does not feed prior mx_pool. Does not rewrite CI source or chem/phy/bio maps.
Mechanism comes from chapter intelligence mechanism_core, not the thinned map string.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_SRC = Path("/home/harik/awm_build/reports/paper/src")
CHEM_LIB = Path("/home/harik/awm_build/data/chem_curriculum/v14_build")
ASTRA_SRC = Path("/home/harik/awm_build/data/spectra/canonical/src")
CI_ROOT = Path("/home/harik/awm_build/data/intelligence/chapter_intelligence_hybrid/science")
MAP = ROOT / "data/maps/science.json"
CANARIES = ROOT / "data/maps/science_g68_mx_canaries.json"
OUTDIR = ROOT / "data/maps/mx_v2"
JSONL = OUTDIR / "construction.jsonl"
RAW = OUTDIR / "construction_raw.jsonl"
LOG = OUTDIR / "construction_runlog.jsonl"
SUMMARY = ROOT / "data/maps/science_g68_mx_v2_summary.json"

sys.path.insert(0, str(PAPER_SRC))
sys.path.insert(0, str(CHEM_LIB))
sys.path.insert(0, str(ASTRA_SRC))
import derive_ncert_mx_v2 as V2  # noqa: E402
from astra_client import client as astra_client, extract_json as astra_extract_json  # noqa: E402

# Kimi K3 (original v2 author) is suspended (insufficient balance). Same SYS + normalize,
# constructor gpt-6-astra. Receipt records the model swap.


def astra_call(prompt: str) -> tuple[str, dict]:
    c = astra_client()
    resp = c.responses.create(
        model="gpt-6-astra",
        reasoning={"effort": "medium"},
        input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
    )
    txt = resp.output_text or ""
    usage = getattr(resp, "usage", None)
    usage_d = usage.model_dump() if usage is not None and hasattr(usage, "model_dump") else {}
    if not str(txt).strip():
        raise ValueError("zero-char Astra response")
    return txt, usage_d


class CIIndex:
    def __init__(self) -> None:
        self._ch: dict[tuple[str, str], dict] = {}

    def hinge(self, unit_id: str) -> dict | None:
        parts = unit_id.split("/")
        if len(parts) < 4:
            return None
        key = (parts[1], parts[2])
        if key not in self._ch:
            path = CI_ROOT / parts[1] / parts[2] / "chapter_intelligence.json"
            if not path.is_file():
                self._ch[key] = {}
            else:
                art = json.loads(path.read_text(encoding="utf-8"))
                self._ch[key] = {h.get("hinge_id"): h for h in (art.get("hinges") or []) if h.get("hinge_id")}
        return self._ch[key].get(unit_id)


def pack_stmt(unit: dict, ci: dict | None) -> dict:
    mech = (ci or {}).get("mechanism_core") if isinstance((ci or {}).get("mechanism_core"), dict) else {}
    law = mech.get("law") or ""
    if not law and isinstance(unit.get("mechanism"), str):
        law = unit["mechanism"]
    return {
        "unit_id": unit["unit_id"],
        "decision_hinge": unit.get("decision_hinge") or (ci or {}).get("decision_hinge") or "",
        "statement": unit.get("decision_hinge") or "",
        "cognitive_operation": unit.get("cognitive_operation") or (ci or {}).get("cognitive_operation") or "",
        "node": unit.get("node") or "",
        "mechanism": {
            "law": law,
            "causal_direction": mech.get("causal_direction") or "",
            "boundary_conditions": mech.get("boundary_conditions") or [],
            "key_entities": mech.get("key_entities") or [],
        },
    }


def node_lookup(doc: dict) -> dict:
    return {n.get("id"): n for n in (doc.get("nodes") or []) if n.get("id")}


def load_done(path: Path) -> set[str]:
    done = set()
    if path.is_file():
        for line in path.open(encoding="utf-8"):
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("unit_id") and rec.get("complete"):
                done.add(rec["unit_id"])
    return done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canary", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--assemble-only", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    lock_path = OUTDIR / ".derive.lock"
    lock_fh = lock_path.open("w")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("another derive_science_g68_mx_v2.py is running", file=sys.stderr)
        return 3
    lock_fh.write(str(os.getpid()))
    lock_fh.flush()

    doc = json.loads(MAP.read_text(encoding="utf-8"))
    units = {u["unit_id"]: u for u in doc["units"]}
    nodes = node_lookup(doc)
    spec = json.loads(CANARIES.read_text(encoding="utf-8"))
    idx = CIIndex()

    if args.canary:
        todo_ids = [c["unit_id"] for c in spec["canaries"]]
        jsonl, raw, log, summ_path = (
            OUTDIR / "construction_canary.jsonl",
            OUTDIR / "construction_canary_raw.jsonl",
            OUTDIR / "construction_canary_runlog.jsonl",
            ROOT / "data/maps/science_g68_mx_v2_canary_summary.json",
        )
    else:
        todo_ids = [u["unit_id"] for u in doc["units"]]
        jsonl, raw, log, summ_path = JSONL, RAW, LOG, SUMMARY
    if args.limit:
        todo_ids = todo_ids[: args.limit]

    done = load_done(jsonl)
    work = [uid for uid in todo_ids if uid not in done]
    print(f"todo {len(work)}  already {len(done & set(todo_ids))}  mode={'canary' if args.canary else 'full'}", flush=True)

    if not args.assemble_only:
        out_f = jsonl.open("a", encoding="utf-8")
        raw_f = raw.open("a", encoding="utf-8")
        log_f = log.open("a", encoding="utf-8")
        write_lock = threading.Lock()
        consec = {"n": 0}
        done_n = {"n": 0}

        def one(uid: str):
            unit = units[uid]
            ci = idx.hinge(uid)
            stmt = pack_stmt(unit, ci)
            hinge = V2.pack_mechanism(stmt)
            if not (hinge["law"] or hinge["decision_hinge"]):
                return uid, None, "", RuntimeError("no mechanism"), hinge
            prompt = V2.build_prompt(hinge, nodes.get(hinge["node"]) or {})
            try:
                txt, usage = astra_call(prompt)
                obj = astra_extract_json(txt)
                if isinstance(obj, list):
                    obj = obj[0]
                rec, errs = V2.normalize(obj, uid, hinge["law"])
                rec["usage"] = usage
                rec["author_errors"] = errs
                rec["derivation"] = {
                    "protocol": "mx_derivation_v2",
                    "model": "gpt-6-astra",
                    "kimi_k3": "skipped: moonshot org suspended (insufficient balance)",
                    "scope": "science_g6_8",
                }
                for d in rec.get("dispositions") or []:
                    mx = d.get("mx")
                    if isinstance(mx, dict) and isinstance(mx.get("derivation"), dict):
                        mx["derivation"]["model"] = "gpt-6-astra"
                        mx["derivation"]["author"] = "grok+gpt-6-astra-constructor"
                return uid, rec, txt, None, hinge
            except Exception as e:
                return uid, None, locals().get("txt", "") or "", e, hinge

        def commit(uid, rec, txt, err) -> bool:
            with write_lock:
                if err is not None:
                    consec["n"] += 1
                    log_f.write(json.dumps({"unit_id": uid, "status": "error", "error": repr(err)[:300], "utc": V2.utc()}) + "\n")
                    log_f.flush()
                    raw_f.write(json.dumps({"unit_id": uid, "raw": txt, "error": repr(err)[:300]}) + "\n")
                    raw_f.flush()
                    print(f"  ERR {uid}: {err}", flush=True)
                    return consec["n"] >= 8
                consec["n"] = 0
                out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out_f.flush()
                raw_f.write(json.dumps({"unit_id": uid, "raw": txt}) + "\n")
                raw_f.flush()
                done_n["n"] += 1
                n_ad = sum(1 for d in rec["dispositions"] if d["disposition"] == "admitted")
                print(
                    f"  {done_n['n']}/{len(work)} {uid} admitted={n_ad} complete={rec['complete']} errs={len(rec.get('author_errors') or [])}",
                    flush=True,
                )
                log_f.write(json.dumps({"unit_id": uid, "status": "ok", "admitted": n_ad, "errs": rec.get("author_errors"), "utc": V2.utc()}) + "\n")
                log_f.flush()
                return False

        abort = False
        workers = max(1, args.workers)
        if workers == 1:
            for uid in work:
                uid, rec, txt, err, _h = one(uid)
                if rec is None and err and str(err) == "no mechanism":
                    print(f"SKIP no mechanism {uid}", flush=True)
                    continue
                if commit(uid, rec, txt, err):
                    abort = True
                    break
                if err is not None:
                    time.sleep(min(20 * consec["n"], 120))
        else:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futs = [pool.submit(one, uid) for uid in work]
                for fut in as_completed(futs):
                    uid, rec, txt, err, _h = fut.result()
                    if rec is None and err and str(err) == "no mechanism":
                        print(f"SKIP no mechanism {uid}", flush=True)
                        continue
                    if commit(uid, rec, txt, err):
                        abort = True
                        for f in futs:
                            f.cancel()
                        break
        if abort:
            print("ABORT after 8 consecutive failures", file=sys.stderr)
            return 3

    recs = []
    if jsonl.is_file():
        last = {}
        for line in jsonl.open(encoding="utf-8"):
            rec = json.loads(line)
            if rec.get("unit_id") in todo_ids and rec.get("complete"):
                last[rec["unit_id"]] = rec
        recs = [last[uid] for uid in todo_ids if uid in last]

    summ = V2.census(recs)
    summ["scope"] = "science_g6_8"
    summ_path.write_text(json.dumps(summ, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summ, indent=2), flush=True)

    if args.canary:
        fails = V2.check_canaries(recs, spec)
        cpath = OUTDIR / "canary_result.json"
        cpath.write_text(json.dumps({"fails": fails, "n": len(recs), "utc": V2.utc()}, indent=2) + "\n", encoding="utf-8")
        if fails:
            print("CANARY FAIL", *fails, sep="\n  ", flush=True)
            return 2
        print("CANARY PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
