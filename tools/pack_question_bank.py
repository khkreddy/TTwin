#!/usr/bin/env python3
"""Ship leftover extra-bank corpora into TTwin question_bank packs.

Unmapped items get node/chapter_id/subtopic_id = "unmapped" (required strings,
no invented map node). Figures: copy TikZ when present; otherwise keep source
figure blobs under figure_pending for later TTwin-side encoding.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from question_pack import (  # noqa: E402
    OUT,
    PACK_LABEL,
    SUBJECT_ORDER,
    UNMAPPED,
    compose_item,
    dump_json,
    load_existing_questions,
    map_item_type,
    nav_from_item,
    project_exam_item,
    question_relpath,
    stem_before_parts,
    subject_pack_of,
    unmapped_tags,
)
from build_data import (  # noqa: E402
    CORPUS,
    CHEM_JOINED,
    assessment_for,
    extract_tikz,
    extract_structures,
    slim_tables,
)

AWM_CORPUS = Path("/home/harik/awm_build/data/corpus_intelligence/awm_corpus")
K12 = AWM_CORPUS / "K12-Graph"
HELD = OUT / "held_questions.jsonl"
PENDING = OUT / "question_bank_pending.json"
PENDING_JSONL = OUT / "question_bank_pending.jsonl"
MAX_PACK_BYTES = 90 * 1024 * 1024
MCQ_LETTERS = {"A", "B", "C", "D"}
OPTION_RE = re.compile(
    r"(?m)^\s*(?:[(（])?([A-Da-d])(?:[)）.\、]|、)\s+(.*?)(?=(?:\n\s*(?:[(（])?[A-Da-d](?:[)）.\、]|、))|\Z)",
    re.S,
)
TIKZ_BLOCK = re.compile(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", re.S)

SUBJ_MAP = {
    "phy": "physics",
    "physics": "physics",
    "chem": "chemistry",
    "chemistry": "chemistry",
    "化学": "chemistry",
    "bio": "biology",
    "biology": "biology",
    "生物": "biology",
    "math": "maths",
    "maths": "maths",
    "mathematics": "maths",
    "数学": "maths",
}


def _subject(raw) -> str | None:
    return SUBJ_MAP.get(str(raw or "").strip().lower()) or SUBJ_MAP.get(str(raw or "").strip())


def _item_type_from_label(label: str, options: dict | None) -> str:
    t = str(label or "")
    if options and sum(1 for k in MCQ_LETTERS if str((options or {}).get(k) or "").strip()) >= 2:
        return "mcq"
    if any(x in t for x in ("选择", "MCQ", "mcq", "客观")):
        return "mcq"
    return "open_response"


def _parse_options(stem: str) -> dict:
    found = {}
    for m in OPTION_RE.finditer(stem or ""):
        found[m.group(1).upper()] = m.group(2).strip()
    if len(found) >= 2:
        return {k: found[k] for k in "ABCD" if k in found}
    return {}


def _assessment(answer, *, gold_letter=None) -> dict:
    letter = gold_letter if gold_letter in MCQ_LETTERS else None
    if not letter and isinstance(answer, str):
        a = answer.strip().upper()
        if a in MCQ_LETTERS:
            letter = a
    if letter:
        return {
            "key_source": "olympiad_gold",
            "key_status": "available",
            "mcq_key": letter,
            "mark_scheme": None,
            "examiner_comment": {"present": False},
        }
    text = ""
    if isinstance(answer, str) and answer.strip():
        text = answer.strip()
    elif isinstance(answer, dict) and answer.get("text"):
        text = str(answer["text"]).strip()
    if text:
        rec = {
            "key_source": "none",
            "key_status": "not_applicable",
            "mcq_key": None,
            "mark_scheme": {"text": text[:8000]},
            "examiner_comment": {"present": False},
        }
        return rec
    return assessment_for("", None, None)


def _body(*, stem: str, item_type: str, options=None, tikz=None, tables=None, parts=None, structures=None, figure_pending=None) -> dict:
    rec = {
        "stem": stem or "",
        "stem_lead": stem or "",
        "item_type": item_type,
        "options": options or {},
        "statements": [],
        "has_figure": bool(tikz or figure_pending),
        "options_are_figure": False,
        "equations": [],
    }
    if tables:
        rec["tables"] = tables
    if structures:
        rec["structures"] = structures
    if tikz:
        rec["tikz"] = tikz
    if parts:
        rec["parts"] = parts
        rec["stem"] = stem_before_parts(stem, parts)
        rec["stem_lead"] = rec["stem"]
    if figure_pending:
        rec["figure_pending"] = figure_pending
    return rec


def _extract_tikz_tex(text: str) -> str | None:
    if not text:
        return None
    blocks = TIKZ_BLOCK.findall(text)
    if not blocks:
        return None
    return "\n".join(blocks)


def iter_source_exam():
    seen = set()
    for path in (CHEM_JOINED, CORPUS):
        if not path.is_file():
            continue
        with path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                o = json.loads(line)
                uid = o.get("item_uid")
                if not uid or uid in seen:
                    continue
                seen.add(uid)
                yield o


def _exam_meta(uid: str):
    meta = subject_pack_of(uid)
    if meta:
        return meta
    u = uid or ""
    if "jeebench" in u:
        if ":phy" in u or ":physics" in u:
            return ("physics", "question_bank", None)
        if ":chem" in u:
            return ("chemistry", "question_bank", None)
        if ":math" in u:
            return ("maths", "question_bank", None)
    if "class-12-physics" in u:
        return ("physics", "senior_11_12_as_a", "SENIOR_SECONDARY")
    if "class-12-chemistry" in u or "class-12-chem" in u:
        return ("chemistry", "senior_11_12_as_a", "SENIOR_SECONDARY")
    return None


def pack_held_exam(existing: dict[str, dict], pending: list) -> int:
    """Ship previously held exam.v1 items with unmapped tags; keep figure blobs."""
    from question_pack import hold_reason

    n = 0
    for o in iter_source_exam():
        uid = o.get("item_uid")
        if uid in existing:
            continue
        meta = _exam_meta(uid)
        if not meta:
            continue
        subject, pack, band = meta
        body = project_exam_item(o)
        if body is None:
            itype = map_item_type(o.get("item_type")) or "open_response"
            stem = str(o.get("complete_stem") or o.get("stem_lead") or "").strip()
            if not stem:
                continue
            tikz, pkgs = extract_tikz(o)
            body = _body(stem=stem, item_type=itype, options=o.get("options") or {}, tikz=tikz)
            if pkgs:
                body["tikz_packages"] = pkgs
        reason = hold_reason(o)
        fig = o.get("figure") if isinstance(o.get("figure"), dict) else {}
        enc = o.get("encoding") if isinstance(o.get("encoding"), dict) else {}
        if not body.get("tikz") and (fig or enc):
            body["figure_pending"] = {"figure": fig or None, "encoding": enc or None, "reason": reason}
            pending.append({"uid": uid, "task": "tikz_encode", "origin": "exam_v1", "reason": reason})
        pending.append({"uid": uid, "task": "node_map", "origin": "exam_v1", "reason": reason or "untaggable"})
        tags = unmapped_tags(uid, subject, pack, item_type=body["item_type"], bank="exam_v1_held")
        tags["grade_band"] = band
        tags["complete_exam"] = True
        existing[uid] = compose_item(tags, body, assessment_for(uid, None, None))
        n += 1
    return n


def _add(existing, pending, uid, subject, pack, body, assessment, bank, tasks=None):
    if not uid or uid in existing:
        return False
    if subject not in SUBJECT_ORDER:
        return False
    itype = body.get("item_type") or "open_response"
    tags = unmapped_tags(uid, subject, pack, item_type=itype, bank=bank)
    existing[uid] = compose_item(tags, body, assessment)
    for task in tasks or ["node_map"]:
        pending.append({"uid": uid, "task": task, "origin": bank})
    return True


def pack_k12(existing, pending) -> int:
    n = 0
    # graph Exercise nodes
    for fname, subject in (("biology.json", "biology"), ("chemistry.json", "chemistry"), ("physics.json", "physics"), ("math.json", "maths")):
        path = K12 / fname
        if not path.is_file():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        for node in raw.get("nodes") or []:
            if not isinstance(node, dict) or node.get("label") != "Exercise":
                continue
            props = node.get("properties") or {}
            stem = str(props.get("stem") or node.get("name") or "").strip()
            if not stem:
                continue
            uid = str(node.get("id") or "").strip()
            opts = _parse_options(stem)
            itype = _item_type_from_label(props.get("type") or "", opts)
            ans = props.get("answer")
            body = _body(stem=stem, item_type=itype, options=opts)
            if props.get("analysis"):
                a = _assessment(ans)
                if (a.get("examiner_comment") or {}).get("present") is False and props.get("analysis"):
                    a["examiner_comment"] = {"present": True, "text": str(props["analysis"])[:4000]}
            else:
                a = _assessment(ans)
            if _add(existing, pending, uid, subject, "question_bank", body, a, "k12_graph"):
                n += 1
    # rjb question files
    for path in sorted(K12.glob("*.json")):
        if path.name in {"biology.json", "chemistry.json", "physics.json", "math.json", "Mathematics.json", "nodes.json", "edges.json"}:
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        qs = raw.get("questions") or []
        subj = _subject(raw.get("subject")) or "maths"
        for q in qs:
            if not isinstance(q, dict):
                continue
            uid = str(q.get("id") or "").strip()
            stem = str(q.get("stem") or "").strip()
            if not uid or not stem:
                continue
            opts = _parse_options(stem)
            itype = _item_type_from_label(q.get("type") or "", opts)
            a = _assessment(q.get("answer"))
            if q.get("analysis"):
                a["examiner_comment"] = {"present": True, "text": str(q["analysis"])[:4000]}
            body = _body(stem=stem, item_type=itype, options=opts)
            if _add(existing, pending, uid, subj, "question_bank", body, a, "k12_graph"):
                n += 1
    # Mathematics.json (Chinese high-school items)
    mathp = K12 / "Mathematics.json"
    if mathp.is_file():
        rows = json.loads(mathp.read_text(encoding="utf-8"))
        for i, q in enumerate(rows, 1):
            stem = str(q.get("试题题目内容") or "").strip()
            if not stem:
                continue
            uid = f"k12graph:mathematics:{q.get('序号') or i}"
            opts = _parse_options(stem)
            itype = _item_type_from_label(q.get("题型") or "", opts)
            a = _assessment(q.get("试题答案"))
            if q.get("标准解题过程"):
                if a.get("mark_scheme") is None and itype != "mcq":
                    a["mark_scheme"] = {"text": str(q["标准解题过程"])[:8000]}
                else:
                    a["examiner_comment"] = {"present": True, "text": str(q["标准解题过程"])[:4000]}
            body = _body(stem=stem, item_type=itype, options=opts)
            if _add(existing, pending, uid, "maths", "question_bank", body, a, "k12_graph"):
                n += 1
    # train.jsonl Q&A
    tr = K12 / "train.jsonl"
    if tr.is_file():
        with tr.open(encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                q = json.loads(line)
                stem = str(q.get("question") or "").strip()
                if not stem:
                    continue
                uid = f"k12graph:train:{i}"
                body = _body(stem=stem, item_type="open_response")
                a = _assessment(q.get("answer"))
                blob = stem + str(q.get("answer") or "")
                subj = "maths"
                if re.search(r"蛋白|细胞|生物|enzyme|photosynth", blob):
                    subj = "biology"
                elif re.search(r"化学|分子|原子|acid|mole", blob):
                    subj = "chemistry"
                elif re.search(r"电场|磁场|速度|力的|velocity|newton", blob, re.I):
                    subj = "physics"
                if _add(existing, pending, uid, subj, "question_bank", body, a, "k12_graph"):
                    n += 1
    return n


def pack_jeebench(existing, pending) -> int:
    path = AWM_CORPUS / "jeebench-dataset.json"
    if not path.is_file():
        return 0
    rows = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for rec in rows:
        subj = _subject(rec.get("subject"))
        if not subj:
            continue
        desc = rec.get("description") or ""
        idx = rec.get("index")
        slug = re.sub(r"[^a-z0-9]+", "_", str(desc).lower()).strip("_")
        uid = f"jeebench:srcjson:{rec.get('subject')}:{slug}:q{idx}"
        stem = str(rec.get("question") or "").strip()
        if not stem:
            continue
        opts = _parse_options(stem)
        gold = rec.get("gold")
        gold_L = gold if gold in MCQ_LETTERS else (str(gold).strip().upper() if gold else None)
        itype = "mcq" if (str(rec.get("type") or "").upper() == "MCQ" or gold_L in MCQ_LETTERS) else "open_response"
        body = _body(stem=stem, item_type=itype, options=opts)
        a = _assessment(None, gold_letter=gold_L if gold_L in MCQ_LETTERS else None)
        if gold and gold_L not in MCQ_LETTERS:
            a = _assessment(str(gold))
        if _add(existing, pending, uid, subj, "question_bank", body, a, "jeebench"):
            n += 1
    return n


def pack_phy500(existing, pending) -> int:
    recdir = AWM_CORPUS / "physics-500/physics500_v2_handover/out/records"
    tikdir = AWM_CORPUS / "physics-500/physics500_v2_handover/out/assets/tikz_source"
    if not recdir.is_dir():
        return 0
    n = 0
    for path in sorted(recdir.glob("P*.json")):
        o = json.loads(path.read_text(encoding="utf-8"))
        uid = o.get("record_id") or path.stem
        pres = o.get("presentation") or {}
        stem_obj = pres.get("stem") or {}
        stem = ""
        if isinstance(stem_obj, dict):
            stem = str(stem_obj.get("latex") or stem_obj.get("text") or "").strip()
        else:
            stem = str(stem_obj or "").strip()
        if not stem:
            continue
        num = re.search(r"p(\d+)", str(uid), re.I)
        tikz_parts = []
        pending_fig = []
        if num and tikdir.is_dir():
            pat = f"physics-with-answers-500-p{int(num.group(1)):03d}-fig-"
            for tex in sorted(tikdir.glob(pat + "*.tex")):
                code = _extract_tikz_tex(tex.read_text(encoding="utf-8", errors="replace"))
                if code:
                    tikz_parts.append(code)
                else:
                    pending_fig.append({"tex": str(tex.name)})
        figs = pres.get("figures") or []
        if figs and not tikz_parts:
            pending_fig.append({"figures": figs})
        tikz = "\n".join(tikz_parts) if tikz_parts else None
        tasks = ["node_map"]
        if pending_fig and not tikz:
            tasks.append("tikz_encode")
        ans = ((o.get("assessment") or {}).get("answer"))
        ans_txt = ans.get("latex") if isinstance(ans, dict) else ans
        body = _body(stem=stem, item_type="open_response", tikz=tikz, figure_pending=pending_fig or None)
        if _add(existing, pending, uid, "physics", "question_bank", body, _assessment(ans_txt), "physics500", tasks):
            n += 1
    return n


def pack_phybench(existing, pending) -> int:
    path = AWM_CORPUS / "PHYBench-questions_v1.json"
    if not path.is_file():
        return 0
    rows = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for rec in rows:
        uid = f"phybench:{rec.get('id')}"
        stem = str(rec.get("content") or "").strip()
        if not stem:
            continue
        body = _body(stem=stem, item_type="open_response")
        a = _assessment(rec.get("answer") or rec.get("solution"))
        if rec.get("solution") and not (a.get("mark_scheme") or {}).get("text"):
            a["mark_scheme"] = {"text": str(rec["solution"])[:8000]}
        if _add(existing, pending, uid, "physics", "question_bank", body, a, "phybench"):
            n += 1
    return n


def pack_mathnet(existing, pending) -> int:
    n = 0
    for shard in ("m1", "m2", "m3", "m4"):
        recdir = AWM_CORPUS / "mathnet_v1" / shard / "records"
        if not recdir.is_dir():
            continue
        paths = list(recdir.glob("*.json"))
        for i, path in enumerate(paths, 1):
            if i % 2000 == 0:
                print(f"    {shard} {i}/{len(paths)}")
            o = json.loads(path.read_text(encoding="utf-8"))
            uid = o.get("item_uid") or f"mathnet:{path.stem}"
            pres = o.get("presentation") or {}
            stem = str(pres.get("stem") or "").strip()
            if not stem:
                continue
            figs = pres.get("figures") or []
            tikz = None
            pending_fig = None
            if figs:
                # rasters live in AWM; keep pointers for later TikZ work
                pending_fig = {"paths": figs, "home": f"mathnet_v1/{shard}"}
            itype = "open_response"
            opts = _parse_options(stem)
            if opts:
                itype = "mcq"
            ans = (o.get("assessment") or {}).get("final_answer")
            body = _body(stem=stem, item_type=itype, options=opts, tikz=tikz, figure_pending=pending_fig)
            tasks = ["node_map"]
            if pending_fig:
                tasks.append("tikz_encode")
            if _add(existing, pending, uid, "maths", "question_bank", body, _assessment(ans), "mathnet", tasks):
                n += 1
    return n


def pack_aime(existing, pending) -> int:
    recdir = AWM_CORPUS / "aime_v1/records"
    n = 0
    if recdir.is_dir():
        for path in recdir.glob("*.json"):
            o = json.loads(path.read_text(encoding="utf-8"))
            uid = o.get("item_uid") or path.stem
            pres = o.get("presentation") or {}
            stem = str(pres.get("stem") or "").strip()
            if not stem:
                continue
            ans = (o.get("assessment") or {}).get("final_answer")
            body = _body(stem=stem, item_type="open_response")
            if _add(existing, pending, uid, "maths", "question_bank", body, _assessment(ans), "aime"):
                n += 1
    return n


def pack_scibench(existing, pending) -> int:
    root = AWM_CORPUS / "scibench-original"
    n = 0
    subj_of = {
        "atkins": "chemistry",
        "chemmc": "chemistry",
        "matter": "chemistry",
        "quan": "chemistry",
        "thermo": "chemistry",
        "calculus": "maths",
        "diff": "maths",
        "stat": "maths",
        "class": "physics",
        "fund": "physics",
    }
    if not root.is_dir():
        return 0
    for path in sorted(root.glob("*.json")):
        if path.name.endswith("_sol.json"):
            continue
        key = path.stem
        subj = subj_of.get(key, "physics")
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            continue
        for rec in rows:
            pid = rec.get("problemid") or rec.get("problem_id") or rec.get("id")
            uid = f"scibench:{key}:{pid}"
            stem = str(rec.get("problem_text") or rec.get("problem") or "").strip()
            if not stem:
                continue
            ans = rec.get("answer_latex") or rec.get("answer_number") or rec.get("answer")
            body = _body(stem=stem, item_type="open_response")
            if _add(existing, pending, uid, subj, "question_bank", body, _assessment(ans), "scibench"):
                n += 1
    return n


def pack_superchem(existing, pending) -> int:
    recdir = AWM_CORPUS / "superchem_v1/records"
    n = 0
    if not recdir.is_dir():
        return 0
    for path in recdir.glob("*.json"):
        o = json.loads(path.read_text(encoding="utf-8"))
        uid = o.get("item_uid") or path.stem
        pres = o.get("presentation") or {}
        stem = str(pres.get("stem") or "").strip()
        if not stem:
            continue
        figs = pres.get("figures") or []
        pending_fig = {"paths": figs} if figs else None
        ans = (o.get("assessment") or {}).get("final_answer")
        body = _body(stem=stem, item_type="open_response", figure_pending=pending_fig)
        tasks = ["node_map"] + (["tikz_encode"] if pending_fig else [])
        if _add(existing, pending, uid, "chemistry", "question_bank", body, _assessment(ans), "superchem", tasks):
            n += 1
    return n


def pack_hicogmath(existing, pending) -> int:
    path = AWM_CORPUS / "HiCogMath Dataset.csv"
    if not path.is_file():
        return 0
    n = 0
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            uid = str(row.get("Item_ID") or "").strip()
            stem = str(row.get("Item") or "").strip()
            if not uid or not stem:
                continue
            uid = f"hicogmath:{uid}"
            body = _body(stem=stem, item_type="open_response")
            if _add(existing, pending, uid, "maths", "question_bank", body, assessment_for(uid, None, None), "hicogmath"):
                n += 1
    return n


def write_bank_files(existing: dict[str, dict]) -> list[str]:
    by: dict[tuple[str, str], list] = defaultdict(list)
    for it in existing.values():
        subj, pack = it.get("subject"), it.get("pack")
        if subj in SUBJECT_ORDER and pack:
            by[(subj, pack)].append(it)
    question_files = []
    catalog_packs: dict[str, list] = defaultdict(list)
    (OUT / "questions").mkdir(parents=True, exist_ok=True)
    (OUT / "nav").mkdir(parents=True, exist_ok=True)
    for subject in SUBJECT_ORDER:
        nav_rows = []
        for pack in ("middle_6_8", "secondary_9_10", "senior_11_12", "olympiad_iit"):
            items = by.get((subject, pack)) or []
            if not items:
                continue
            items.sort(key=lambda r: r.get("uid") or "")
            if pack == "question_bank":
                # split oversized
                chunks = [items]
                rels = []
                slug = "bank"
                # write one file first; split if needed after dump
                rel = f"questions/{subject}-{slug}.json"
                path = OUT / rel
                dump_json(path, items)
                if path.stat().st_size > MAX_PACK_BYTES:
                    # split by half
                    mid = len(items) // 2
                    dump_json(OUT / f"questions/{subject}-{slug}-1.json", items[:mid])
                    dump_json(OUT / f"questions/{subject}-{slug}-2.json", items[mid:])
                    path.unlink()
                    rels = [f"data/questions/{subject}-{slug}-1.json", f"data/questions/{subject}-{slug}-2.json"]
                else:
                    rels = ["data/" + rel]
                question_files.extend(rels)
                catalog_packs[subject].append(
                    {
                        "id": pack,
                        "label": PACK_LABEL[pack],
                        "questions": rels if len(rels) > 1 else rels[0],
                        "n": len(items),
                        "n_complete_exam": sum(1 for it in items if it.get("complete_exam")),
                        "n_stems": sum(1 for it in items if str(it.get("stem") or "").strip()),
                    }
                )
            else:
                rel = question_relpath(subject, pack)
                dump_json(OUT / rel, items)
                question_files.append("data/" + rel)
                catalog_packs[subject].append(
                    {
                        "id": pack,
                        "label": PACK_LABEL.get(pack, pack),
                        "questions": "data/" + rel,
                        "n": len(items),
                        "n_complete_exam": sum(1 for it in items if it.get("complete_exam")),
                        "n_stems": sum(1 for it in items if str(it.get("stem") or "").strip()),
                    }
                )
            nav_rows.extend(nav_from_item(it) for it in items)
        nav_rows.sort(key=lambda r: (r.get("pack") or "", r.get("uid") or ""))
        dump_json(OUT / "nav" / f"{subject}.json", nav_rows)
    _update_subjects_meta(catalog_packs, existing, question_files)
    return question_files


def _update_subjects_meta(catalog_packs, existing, question_files):
    from datetime import datetime, timezone

    subj_path = OUT / "subjects.json"
    subjects_doc = json.loads(subj_path.read_text(encoding="utf-8")) if subj_path.is_file() else {
        "schema": "ttwin.subjects.v1",
        "default": "chemistry",
        "subjects": [],
    }
    by_id = {s.get("id"): s for s in subjects_doc.get("subjects") or []}
    counts = Counter(it.get("subject") for it in existing.values())
    for subject in SUBJECT_ORDER:
        rec = by_id.get(subject) or {"id": subject, "label": subject.title()}
        rec["packs"] = catalog_packs.get(subject) or rec.get("packs") or []
        rec["n_tagged"] = counts.get(subject, 0)
        rec["n_complete_exam"] = rec["n_tagged"]
        rec["nav"] = f"data/nav/{subject}.json"
        by_id[subject] = rec
    subjects_doc["subjects"] = [by_id[s] for s in SUBJECT_ORDER if s in by_id]
    dump_json(subj_path, subjects_doc)
    meta_path = OUT / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
    meta["built_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta["n_questions"] = len(existing)
    meta["n_complete_exam"] = sum(1 for it in existing.values() if it.get("complete_exam"))
    meta["n_stems"] = sum(1 for it in existing.values() if str(it.get("stem") or "").strip())
    meta["n_unmapped"] = sum(1 for it in existing.values() if it.get("node") == UNMAPPED)
    files = dict(meta.get("files") or {})
    files["questions"] = question_files
    files["pending"] = "data/question_bank_pending.json"
    meta["files"] = files
    dump_json(meta_path, meta)


def main() -> int:
    print("loading existing TTwin questions…")
    existing = load_existing_questions()
    print(f"  existing {len(existing)}")
    pending: list[dict] = []
    added = {}
    print("shipping held exam.v1 remainder…")
    added["exam_v1_held"] = pack_held_exam(existing, pending)
    print("  ", added["exam_v1_held"])
    print("K12-Graph…")
    added["k12_graph"] = pack_k12(existing, pending)
    print("  ", added["k12_graph"])
    print("JEEBench…")
    added["jeebench"] = pack_jeebench(existing, pending)
    print("  ", added["jeebench"])
    print("Phy-500…")
    added["physics500"] = pack_phy500(existing, pending)
    print("  ", added["physics500"])
    print("PHYBench…")
    added["phybench"] = pack_phybench(existing, pending)
    print("  ", added["phybench"])
    print("MathNet…")
    added["mathnet"] = pack_mathnet(existing, pending)
    print("  ", added["mathnet"])
    print("AIME…")
    added["aime"] = pack_aime(existing, pending)
    print("  ", added["aime"])
    print("SciBench…")
    added["scibench"] = pack_scibench(existing, pending)
    print("  ", added["scibench"])
    print("SUPERChem…")
    added["superchem"] = pack_superchem(existing, pending)
    print("  ", added["superchem"])
    print("HiCogMath…")
    added["hicogmath"] = pack_hicogmath(existing, pending)
    print("  ", added["hicogmath"])

    print("writing packs…")
    write_bank_files(existing)

    task_n = Counter(p["task"] for p in pending)
    origin_n = Counter(p["origin"] for p in pending)
    with PENDING_JSONL.open("w", encoding="utf-8") as fh:
        for row in pending:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = {
        "schema": "ttwin.question_bank_pending.v1",
        "n_packed_total": len(existing),
        "n_added_this_run": sum(added.values()),
        "added_by_bank": added,
        "pending_n": len(pending),
        "pending_by_task": dict(task_n),
        "pending_by_origin": dict(origin_n),
        "tasks": [
            {
                "id": "node_map",
                "n": task_n.get("node_map", 0),
                "note": "Fill sheaf node/chapter/subtopic from TTwin maps. Do not invent nodes.",
            },
            {
                "id": "tikz_encode",
                "n": task_n.get("tikz_encode", 0),
                "note": "Compile figure_pending into TikZ. Raster/path blobs stay on the item until then.",
            },
            {
                "id": "option_parse",
                "note": "MathNet/JEE stems may still inline A–D in LaTeX; split into options when possible.",
            },
            {
                "id": "lbs_keyed_mcq",
                "note": "Join LBS only for keyed MCQ in the bank pack.",
            },
        ],
        "home": "TTwin GitHub. Do not return to AWM for question bytes.",
    }
    dump_json(PENDING, summary)
    print(json.dumps({"added": added, "n_total": len(existing), "pending": dict(task_n)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
