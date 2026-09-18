#!/usr/bin/env python3
"""Apply the Kimi four-pack / map-alignment plan (CANDIDATE owner-approved).

Pins the five final maps, regenerates vocab from map titles, remaps packs
by demand (not origin), moves grades 6–8 science under subject Science,
relabels code-shaped names, binds hinges when a statement unit_id matches,
rebuilds nav and subjects.json.

Does not rewrite frozen exam.v1 or chemistry hinge sentences.
Does not git-add the large *_MAP.json blobs.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "data/maps"
QDIR = ROOT / "data/questions"
VOCAB = ROOT / "data/vocab"
NAV = ROOT / "data/nav"

FINAL = {
    "science": MAPS / "science.json",
    "mathematics": MAPS / "MATHEMATICS_MAP.json",
    "chemistry": MAPS / "CHEMISTRY_MAP_COMBINED.json",
    "physics": MAPS / "PHYSICS_MAP.json",
    "biology": MAPS / "BIOLOGY_MAP.json",
}

PACKS = ("middle_6_8", "secondary_9_10", "senior_11_12", "olympiad_iit")
PACK_LABEL = {
    "middle_6_8": "Middle School · Grades 6–8",
    "secondary_9_10": "Secondary · Grades 9–10",
    "senior_11_12": "Senior Secondary · Grades 11–12",
    "olympiad_iit": "Olympiad / IIT Practice",
}
OLD_PACK = {
    "junior_6_8": "middle_6_8",
    "igcse_9_10": "secondary_9_10",
    "senior_11_12_as_a": "senior_11_12",
    "olympiad_iit": "olympiad_iit",
    "middle_6_8": "middle_6_8",
    "secondary_9_10": "secondary_9_10",
    "senior_11_12": "senior_11_12",
}

PREFIX = {"chemistry": "chem:", "physics": "phy:", "biology": "bio:", "maths": "math:", "science": ""}

# Live biology vocab used L*; final map uses Q*. Questions were tagged with L*.
BIO_NODE_REMAP = {
    "L1": "Q1",
    "L1/H-MEMBRANE": "Q1/H-MEMBRANE-TRANSPORT",
    "L2": "Q1/H-BIOMOLECULES",
    "L2/H-ENZYMES": "Q1/H-BIOMOLECULES",
    "L3": "Q7",
    "L3/H-DNA": "Q7/H-DNA",
    "L4": "Q3",
    "L5": "Q5",
    "L5/H-ATP": "Q5/H-ATP-YIELD",
    "L6": "Q4",
    "L6/H-IMMUNITY": "Q8/H-IMMUNITY",
    "L7": "Q6",
    "L8": "Q9",
    "L8/H-CYCLES": "Q9",
    "UNRESOLVED": "Q3",
}

CODE_RE = re.compile(
    r"^(chem|phy|bio|math|sci):|^cam:|^IGCSE:|^AS_A:|^[A-Z]\d+(\/|$)|^(M|C|P|Q|S|L|B)\d+$",
    re.I,
)

NAV_FIELDS = (
    "uid", "subject", "pack", "grade_band", "node", "chapter_id", "chapter_label",
    "subtopic_id", "subtopic_label", "complete_exam", "cam_family", "ncert_family",
    "item_type",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def strip_prefix(node: str) -> str:
    s = str(node or "").strip()
    if ":" in s and s.split(":", 1)[0] in ("chem", "phy", "bio", "math", "sci"):
        return s.split(":", 1)[1]
    return s


def looks_like_code(s: str) -> bool:
    t = str(s or "").strip()
    if not t:
        return True
    return bool(CODE_RE.search(t))


def load_final_maps() -> dict:
    out = {}
    for key, path in FINAL.items():
        if not path.is_file():
            raise SystemExit(f"missing final map {path}")
        out[key] = json.loads(path.read_text(encoding="utf-8"))
    return out


def iter_nodes(doc) -> list[dict]:
    nodes = doc.get("nodes")
    if isinstance(nodes, dict):
        rows = []
        for nid, n in nodes.items():
            if not isinstance(n, dict):
                continue
            rec = dict(n)
            rec.setdefault("id", nid)
            rows.append(rec)
        return rows
    if isinstance(nodes, list):
        return [n for n in nodes if isinstance(n, dict)]
    return []


def iter_statements(doc) -> list[dict]:
    if isinstance(doc.get("statements"), list):
        return doc["statements"]
    if isinstance(doc.get("units"), list):
        return doc["units"]
    return []


def statement_packs(stmt: dict, subject_key: str) -> set[str]:
    packs: set[str] = set()
    if subject_key == "science":
        return {"middle_6_8"}
    g = stmt.get("grade")
    try:
        g = int(g) if g is not None else None
    except (TypeError, ValueError):
        g = None
    syl = str(stmt.get("syllabus") or "")
    gb = str(stmt.get("grade_band") or "")
    if g in (6, 7, 8) or "MIDDLE" in syl:
        packs.add("middle_6_8")
    if g in (9, 10) or syl in {
        "NCERT_SECONDARY", "CAMBRIDGE_IGCSE_CORE", "CAMBRIDGE_IGCSE_SUPPLEMENT", "CISCE_ICSE",
    } or gb in {"SECONDARY", "CORE", "SUPPLEMENT"}:
        packs.add("secondary_9_10")
    if g in (11, 12) or syl in {
        "NCERT_SENIOR_SECONDARY", "CAMBRIDGE_AS", "CAMBRIDGE_A_LEVEL", "CISCE_ISC",
    } or gb in {"SENIOR_SECONDARY", "AS", "A_LEVEL"}:
        packs.add("senior_11_12")
    if "senior_11_12" in packs:
        packs.add("olympiad_iit")
    # IGCSE-only occupancy still visible at secondary; olympiad uses senior spine.
    return packs or {"secondary_9_10"}


def build_vocab(final: dict) -> dict[str, dict]:
    """Teacher-facing ideas from final maps. Origins = big ideas; hubs/grains = concepts."""
    spec = {
        "science": ("science", "science", None),
        "mathematics": ("maths", "mathematics", "math:"),
        "chemistry": ("chemistry", "chemistry", "chem:"),
        "physics": ("physics", "physics", "phy:"),
        "biology": ("biology", "biology", "bio:"),
    }
    vocabs = {}
    node_spans: dict[str, list[int]] = {}
    unit_by_id: dict[str, dict] = {}
    node_packs: dict[tuple[str, str], set[str]] = defaultdict(set)
    node_titles: dict[tuple[str, str], dict] = {}

    for key, (subj, _mapk, pfx) in spec.items():
        doc = final[key]
        pfx = pfx or ""
        for n in iter_nodes(doc):
            nid = n.get("id")
            if not nid:
                continue
            title = (n.get("title") or "").strip()
            kind = n.get("kind") or "concept_origin"
            if kind == "beside_spine":
                continue
            if not title or title == nid:
                continue
            parent = n.get("parent")
            rec = {
                "id": f"{pfx}{nid}",
                "title": title,
                "kind": "grain" if kind == "grain" else ("hub" if kind == "hub" else "concept_origin"),
                "parent": (f"{pfx}{parent}" if parent else None),
                "mechanism": n.get("mechanism"),
                "packs": [],
            }
            node_titles[(subj, nid)] = rec
            span = n.get("ncert_grade_span") or []
            if isinstance(span, list) and span:
                node_spans[nid] = [int(x) for x in span if str(x).isdigit() or isinstance(x, int)]
        for stmt in iter_statements(doc):
            uid = stmt.get("unit_id")
            if uid:
                unit_by_id[uid] = {"subject": subj, "map": key, **{k: stmt.get(k) for k in (
                    "unit_id", "node", "decision_hinge", "chapter", "chapter_title",
                    "grade", "grade_band", "syllabus", "board",
                )}}
            packs = statement_packs(stmt, key)
            nid = stmt.get("node") or stmt.get("node_parent")
            if nid:
                node_packs[(subj, nid)] |= packs
                parent = str(nid).split("/")[0]
                if parent != nid:
                    node_packs[(subj, parent)] |= packs

    for (subj, nid), rec in node_titles.items():
        packs = node_packs.get((subj, nid)) or set()
        if rec["kind"] == "concept_origin" and not packs:
            # still list if any child has packs
            for (s2, nid2), ps in node_packs.items():
                if s2 == subj and (nid2 == nid or str(nid2).startswith(nid + "/")):
                    packs |= ps
        if rec["kind"] == "concept_origin":
            # olympiad shows the senior spine
            if "senior_11_12" in packs:
                packs.add("olympiad_iit")
        rec["packs"] = [p for p in PACKS if p in packs]
        if subj == "science":
            rec["packs"] = ["middle_6_8"]

    for subj in ("science", "maths", "chemistry", "physics", "biology"):
        ideas = [rec for (s, _), rec in node_titles.items() if s == subj]
        ideas.sort(key=lambda r: (0 if r["kind"] == "concept_origin" else 1, r["id"]))
        vocabs[subj] = {
            "schema": "ttwin.vocab.v1",
            "subject": subj,
            "n": len(ideas),
            "ideas": ideas,
            "authority": "final_maps",
        }
    return {"vocabs": vocabs, "node_spans": node_spans, "unit_by_id": unit_by_id, "node_titles": node_titles}


def build_unit_indexes(unit_by_id: dict) -> tuple[dict, dict]:
    exact = dict(unit_by_id)
    prefixes: dict[str, list[str]] = defaultdict(list)
    for uid in exact:
        if uid.startswith("IGCSE:") or uid.startswith("AS_A:"):
            parts = uid.split(".")
            for i in range(2, len(parts)):
                prefixes[".".join(parts[:i])].append(uid)
        if uid.startswith("science/") or uid.startswith("math/"):
            # chapter path without hinge
            if "/H" in uid:
                prefixes[uid.rsplit("/H", 1)[0]].append(uid)
    return exact, prefixes


def bind_hinges(it: dict, exact: dict, prefixes: dict) -> dict | None:
    for key in ("subtopic_id", "ncert_family", "chapter_id"):
        val = it.get(key)
        if val and val in exact:
            return {
                "primary": val,
                "supporting": [],
                "binder": {
                    "method": "exact_unit_id",
                    "model": None,
                    "confidence": 1.0,
                    "bound_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "field": key,
                },
            }
    val = it.get("subtopic_id") or ""
    kids = prefixes.get(val) or []
    if len(kids) == 1:
        return {
            "primary": kids[0],
            "supporting": [],
            "binder": {
                "method": "prefix_unit_id",
                "model": None,
                "confidence": 0.8,
                "bound_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "field": "subtopic_id",
            },
        }
    if len(kids) > 1:
        node = strip_prefix(it.get("node") or "")
        preferred = [u for u in kids if exact[u].get("node") == node or str(exact[u].get("node") or "").startswith(node)]
        pick = (preferred or kids)[0]
        rest = [u for u in (preferred or kids)[1:4]]
        return {
            "primary": pick,
            "supporting": rest,
            "binder": {
                "method": "prefix_unit_id",
                "model": None,
                "confidence": 0.7,
                "bound_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "field": "subtopic_id",
                "n_candidates": len(kids),
            },
        }
    ch = it.get("chapter_id") or ""
    kids = prefixes.get(ch) or []
    if kids:
        node = strip_prefix(it.get("node") or "")
        preferred = [u for u in kids if exact[u].get("node") == node] or kids
        return {
            "primary": preferred[0],
            "supporting": preferred[1:3],
            "binder": {
                "method": "chapter_prefix",
                "model": None,
                "confidence": 0.6,
                "bound_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }
    return None


def assign_pack(it: dict, node_spans: dict) -> str:
    old = it.get("pack")
    if old in OLD_PACK and old != "question_bank":
        return OLD_PACK[old]
    g = it.get("grade")
    try:
        g = int(g) if g is not None else None
    except (TypeError, ValueError):
        g = None
    if g in (6, 7, 8) or it.get("subject") == "science":
        return "middle_6_8"
    if g in (9, 10):
        return "secondary_9_10"
    if g in (11, 12):
        return "senior_11_12"
    if it.get("bank") == "aime":
        return "olympiad_iit"
    bare = strip_prefix(it.get("node") or "")
    span = node_spans.get(bare) or node_spans.get(bare.split("/")[0], [])
    if span:
        mn, mx = min(span), max(span)
        if mx <= 8:
            return "middle_6_8"
        if mn >= 11:
            return "senior_11_12"
        return "secondary_9_10"
    gb = str(it.get("grade_band") or "")
    if gb in {"SENIOR_SECONDARY", "AS", "A_LEVEL", "olympiad-iit"}:
        return "senior_11_12"
    return "secondary_9_10"


def remap_bio_node(node: str) -> str:
    s = str(node or "")
    pfx, bare = ("bio:", s[4:]) if s.startswith("bio:") else ("", s)
    if not s.startswith("bio:"):
        bare = strip_prefix(s)
        pfx = "bio:"
    if bare in BIO_NODE_REMAP:
        return pfx + BIO_NODE_REMAP[bare]
    if bare.startswith("L"):
        root = bare.split("/")[0]
        if root in BIO_NODE_REMAP:
            return pfx + BIO_NODE_REMAP[root]
    if bare == "UNRESOLVED":
        return "bio:Q3"
    return s if s.startswith("bio:") else ("bio:" + bare if bare else s)


def science_labels(final_science: dict) -> tuple[dict, dict, dict]:
    by_chapter = {}
    by_node = {}
    by_unit = {}
    for u in final_science.get("units") or []:
        by_chapter[u.get("chapter")] = u.get("chapter_title")
        by_node[u.get("node")] = u.get("node")
        by_unit[u.get("unit_id")] = u
    node_title = {n["id"]: n.get("title") for n in iter_nodes(final_science)}
    return by_chapter, node_title, by_unit


def relabel(it: dict, by_chapter: dict, node_title: dict, by_unit: dict, vocab_title: dict) -> None:
    node = strip_prefix(it.get("node") or "")
    if looks_like_code(it.get("chapter_label") or ""):
        ch = it.get("chapter_id")
        if ch in by_chapter and by_chapter[ch]:
            it["chapter_label"] = by_chapter[ch]
        elif node in node_title:
            it["chapter_label"] = node_title[node]
        elif node.split("/")[0] in node_title:
            it["chapter_label"] = node_title[node.split("/")[0]]
        elif it.get("node") in vocab_title:
            it["chapter_label"] = vocab_title[it["node"]]
    if looks_like_code(it.get("subtopic_label") or ""):
        uid = it.get("subtopic_id")
        u = by_unit.get(uid) if uid else None
        if u and u.get("decision_hinge"):
            it["subtopic_label"] = u["decision_hinge"]
        elif node in node_title:
            it["subtopic_label"] = node_title[node]
        elif it.get("node") in vocab_title:
            it["subtopic_label"] = vocab_title[it["node"]]


def nav_row(it: dict) -> dict:
    return {k: it.get(k) for k in NAV_FIELDS}


def project_biology_slim(final_bio: dict) -> None:
    slim_path = MAPS / "biology.json"
    slim = json.loads(slim_path.read_text(encoding="utf-8"))
    nodes = []
    for n in iter_nodes(final_bio):
        title = (n.get("title") or "").strip()
        if not title or title == n.get("id"):
            continue
        nodes.append({
            "id": n.get("id"),
            "title": title,
            "kind": n.get("kind"),
            "mechanism": n.get("mechanism"),
            "parent": n.get("parent"),
            "map_id": n.get("id"),
        })
    slim["nodes"] = nodes
    by = {s["unit_id"]: s.get("node") for s in final_bio.get("statements") or []}
    for u in slim.get("units") or []:
        uid = u.get("unit_id")
        if uid in by and by[uid]:
            u["node"] = by[uid]
    note = "Nodes and unit.node joined from BIOLOGY_MAP.json; hinge sentences not rewritten."
    hon = slim.get("honesty")
    if isinstance(hon, dict):
        hon["projected_from"] = "BIOLOGY_MAP.json"
        hon["note"] = note
        slim["honesty"] = hon
    else:
        slim["projected_from"] = "BIOLOGY_MAP.json"
        slim["projection_note"] = note
    dump(slim_path, slim)


def write_manifest(final: dict) -> dict:
    files = []
    for key, path in FINAL.items():
        files.append({
            "id": key,
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "schema": (final[key].get("schema") or final[key].get("artifact")),
            "n_nodes": len(iter_nodes(final[key])),
            "n_statements": len(iter_statements(final[key])),
            "on_github": path.name == "science.json",
        })
    doc = {
        "schema": "ttwin.map_manifest.v1",
        "status": "CANDIDATE",
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "plan": "data/maps/KIMI_K3_MAX_FOUR_PACK_HINGE_PLAN.md",
        "files": files,
        "note": "Full BIOLOGY/CHEMISTRY/PHYSICS/MATHEMATICS maps are local authority blobs (too large for GitHub). Vocab, slim biology projection, and questions consume them. science.json is on GitHub.",
    }
    (MAPS / "MANIFEST.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return doc


def main() -> int:
    print("loading final maps…", flush=True)
    final = load_final_maps()
    manifest = write_manifest(final)
    print("manifest", [(f["id"], f["n_statements"]) for f in manifest["files"]], flush=True)

    built = build_vocab(final)
    vocabs = built["vocabs"]
    node_spans = built["node_spans"]
    vocab_title = {}
    for subj, doc in vocabs.items():
        for idea in doc["ideas"]:
            vocab_title[idea["id"]] = idea["title"]
        dump(VOCAB / f"{subj}.json", doc)
        print("vocab", subj, doc["n"], "origins", sum(1 for i in doc["ideas"] if i["kind"] == "concept_origin"), flush=True)

    exact, prefixes = build_unit_indexes(built["unit_by_id"])
    by_chapter, sci_node_title, by_unit = science_labels(final["science"])
    # merge chapter titles from other maps
    for key in ("mathematics", "chemistry", "physics", "biology"):
        for s in iter_statements(final[key]):
            if s.get("chapter") and s.get("chapter_title"):
                by_chapter.setdefault(s["chapter"], s["chapter_title"])
            if s.get("unit_id"):
                by_unit.setdefault(s["unit_id"], s)
    for n in iter_nodes(final["mathematics"]):
        sci_node_title.setdefault(n.get("id"), n.get("title"))
    for n in iter_nodes(final["chemistry"]):
        sci_node_title.setdefault(n.get("id"), n.get("title"))
    for n in iter_nodes(final["physics"]):
        sci_node_title.setdefault(n.get("id"), n.get("title"))
    for n in iter_nodes(final["biology"]):
        sci_node_title.setdefault(n.get("id"), n.get("title"))

    print("projecting biology slim map…", flush=True)
    project_biology_slim(final["biology"])

    print("rewriting questions…", flush=True)
    science_rows = []
    stats = Counter()
    pack_counts = Counter()
    bound_n = 0
    all_rows_by_file: dict[str, list] = {}

    for path in sorted(QDIR.glob("*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        out = []
        for it in rows:
            stats["n"] += 1
            # move junior science into Science
            is_junior_sci = path.name in {"biology-junior.json", "physics-junior.json"}
            if it.get("subject") == "biology" and not is_junior_sci:
                it["node"] = remap_bio_node(it.get("node") or "")
            if is_junior_sci:
                it["subject"] = "science"
                node = str(it.get("node") or "")
                if ":" in node and node.split(":", 1)[0] in ("bio", "phy", "chem", "math"):
                    node = strip_prefix(node)
                it["node"] = node
                it["pack"] = "middle_6_8"
                science_rows.append(it)
                stats["to_science"] += 1
            else:
                it["pack"] = assign_pack(it, node_spans)
                out.append(it)
            relabel(it, by_chapter, sci_node_title, by_unit, vocab_title)
            h = bind_hinges(it, exact, prefixes)
            if h:
                it["hinges"] = h
                bound_n += 1
            pack_counts[it["pack"]] += 1
        if path.name in {"biology-junior.json", "physics-junior.json"}:
            all_rows_by_file[path.name] = []
        else:
            all_rows_by_file[path.name] = out
        print(" ", path.name, "in", len(rows), "out", len(out), flush=True)

    dump(QDIR / "science-junior.json", science_rows)
    print("science-junior", len(science_rows), flush=True)
    (QDIR / "biology-junior.json").unlink(missing_ok=True)
    (QDIR / "physics-junior.json").unlink(missing_ok=True)

    for name, rows in all_rows_by_file.items():
        if name in {"biology-junior.json", "physics-junior.json"}:
            continue
        dump(QDIR / name, rows)

    # nav per subject-pack
    print("rebuilding nav…", flush=True)
    by_subj_pack: dict[tuple[str, str], list] = defaultdict(list)
    file_for: dict[tuple[str, str], set[str]] = defaultdict(set)
    leftover_files = {
        "biology-igcse.json": "biology",
        "biology-senior.json": "biology",
        "chemistry-bank.json": "chemistry",
        "chemistry-igcse.json": "chemistry",
        "chemistry-senior.json": "chemistry",
        "maths-bank.json": "maths",
        "maths-igcse.json": "maths",
        "maths-junior.json": "maths",
        "maths-olympiad.json": "maths",
        "maths-senior.json": "maths",
        "physics-bank.json": "physics",
        "physics-igcse.json": "physics",
        "physics-senior.json": "physics",
        "science-junior.json": "science",
    }
    for name, subj in leftover_files.items():
        path = QDIR / name
        if not path.is_file():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        for it in rows:
            p = it.get("pack")
            by_subj_pack[(subj, p)].append(nav_row(it))
            file_for[(subj, p)].add(f"data/questions/{name}")

    for old in NAV.glob("*.json"):
        # keep until rewritten; we overwrite known names
        pass

    subjects_out = []
    catalog_order = [
        ("science", "Science", "data/maps/science.json", "hinge_map_candidate", "S1"),
        ("maths", "Mathematics", "data/maps/maths.json", "hinge_map_candidate", "math:M1"),
        ("chemistry", "Chemistry", "data/maps/chemistry.json", "comprehensive", "chem:C1"),
        ("physics", "Physics", "data/maps/physics.json", "hinge_map_candidate", "phy:P1"),
        ("biology", "Biology", "data/maps/biology.json", "hinge_map_candidate", "bio:Q1"),
    ]

    # remove stale nav
    for p in NAV.glob("*.json"):
        p.unlink()

    for subj, label, mapp, status, default_node in catalog_order:
        packs = []
        n_tagged = 0
        default_pack = None
        for pack in PACKS:
            rows = by_subj_pack.get((subj, pack)) or []
            if not rows:
                continue
            n_tagged += len(rows)
            files = sorted(file_for[(subj, pack)])
            nav_path = NAV / f"{subj}-{pack}.json"
            dump(nav_path, rows)
            qfield: str | list = files[0] if len(files) == 1 else files
            packs.append({
                "id": pack,
                "label": PACK_LABEL[pack],
                "questions": qfield,
                "nav": f"data/nav/{subj}-{pack}.json",
                "n": len(rows),
                "n_complete_exam": sum(1 for r in rows if r.get("complete_exam")),
                "n_stems": sum(1 for r in rows if True),
            })
            if default_pack is None:
                default_pack = pack
        if not packs:
            continue
        # prefer secondary as default when present
        if any(p["id"] == "secondary_9_10" for p in packs):
            default_pack = "secondary_9_10"
        if subj == "science":
            default_pack = "middle_6_8"
        default_nav = next((p["nav"] for p in packs if p["id"] == default_pack), packs[0]["nav"])
        spec = {
            "id": subj,
            "label": label,
            "nav": default_nav,
            "vocab": f"data/vocab/{subj}.json",
            "has_map": True,
            "map": mapp,
            "map_status": status,
            "n_map_units": len(iter_statements(final[{
                "maths": "mathematics", "chemistry": "chemistry", "physics": "physics",
                "biology": "biology", "science": "science",
            }[subj]])),
            "n_tagged": n_tagged,
            "n_complete_exam": n_tagged,
            "packs": packs,
            "default_node": default_node,
            "default_pack": default_pack,
        }
        if subj == "chemistry":
            spec["enrichment"] = "data/enrichment/chemistry.json"
            spec["projection"] = "data/projection.json"
        elif subj in {"maths", "physics", "biology"}:
            spec["enrichment"] = f"data/enrichment/{subj}.json"
            proj = ROOT / f"data/projection/{subj}.json"
            if proj.is_file():
                spec["projection"] = f"data/projection/{subj}.json"
        subjects_out.append(spec)

    catalog = {"schema": "ttwin.subjects.v1", "default": "chemistry", "subjects": subjects_out}
    (ROOT / "data/subjects.json").write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    meta_path = ROOT / "data/meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
    meta["schema"] = meta.get("schema") or "ttwin.showcase.v2"
    meta["built_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta["subjects"] = [s["id"] for s in subjects_out]
    meta["n_questions"] = stats["n"]
    meta["n_complete_exam"] = stats["n"]
    meta["question_schema"] = "data/schema/ttwin.question.v1.json"
    meta["packs"] = PACK_LABEL
    meta["map_manifest"] = "data/maps/MANIFEST.json"
    meta["four_pack_plan"] = "data/maps/KIMI_K3_MAX_FOUR_PACK_HINGE_PLAN.md"
    dump(meta_path, meta)

    receipt = {
        "schema": "ttwin.four_pack_apply.v1",
        "built_utc": meta["built_utc"],
        "n": stats["n"],
        "to_science": stats["to_science"],
        "hinges_bound": bound_n,
        "pack_counts": dict(pack_counts),
        "subjects": [{k: s[k] for k in ("id", "n_tagged", "default_pack")} | {"packs": [(p["id"], p["n"]) for p in s["packs"]]} for s in subjects_out],
    }
    (MAPS / "FOUR_PACK_APPLY_RECEIPT.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
