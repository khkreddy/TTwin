#!/usr/bin/env python3
"""Build slim TeacherTwin showcase JSON from the live AWM tree.

Does not rewrite frozen exam.v1, live V15, the public NCERT map, or POOL_ID.
Output is a derived static pack for GitHub Pages.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

AWM = Path("/home/harik/awm_build")
OUT = Path(__file__).resolve().parents[1] / "data"

COMP = AWM / "reports/paper/data/NCERT_CHEMISTRY_MAP_COMPREHENSIVE.json"
WORKING = AWM / "reports/paper/data/NCERT_CHEMISTRY_MAP.json"
PUBLIC = AWM / "reports/paper/data/NCERT_CHEMISTRY_MAP_PUBLIC.json"
ENRICH = AWM / "reports/paper/data/supplement_ncert_hinges.jsonl"
DOCS = AWM / "data/chem_curriculum/supplement/documents.json"
NAV = AWM / "data/awm_product/generated/nav_mcq/items.jsonl"
PROJ = AWM / "data/awm_product/generated/nav_mcq/vocab/projection_chem_v1.json"
EXAM = AWM / "data/chem_curriculum/item_envelope/exam_json/items.jsonl"
CORPUS = AWM / "data/awm_product/generated/exam_v1_corpus/items.jsonl"

CHAPTER_TITLES = {
    "science/grade_09/ch_01": "Matter in Our Surroundings",
    "science/grade_09/ch_02": "Is Matter Around Us Pure",
    "science/grade_09/ch_03": "Atoms and Molecules",
    "science/grade_09/ch_04": "Structure of the Atom",
    "science/grade_09/ch_05": "The Fundamental Unit of Life",
    "science/grade_09/ch_08": "Motion",
    "science/grade_09/ch_09": "Force and Laws of Motion / Atoms (map ch_09)",
    "science/grade_10/ch_01": "Chemical Reactions and Equations",
    "science/grade_10/ch_02": "Acids, Bases and Salts",
    "science/grade_10/ch_03": "Metals and Non-metals",
    "science/grade_10/ch_04": "Carbon and its Compounds",
    "science/grade_11/chem_ch_101": "Some Basic Concepts of Chemistry",
    "science/grade_11/chem_ch_102": "Structure of Atom",
    "science/grade_11/chem_ch_103": "Classification of Elements and Periodicity",
    "science/grade_11/chem_ch_104": "Chemical Bonding and Molecular Structure",
    "science/grade_11/chem_ch_105": "Thermodynamics",
    "science/grade_11/chem_ch_106": "Equilibrium",
    "science/grade_11/chem_ch_207": "Redox Reactions",
    "science/grade_11/chem_ch_208": "Organic Chemistry — Some Basic Principles",
    "science/grade_11/chem_ch_209": "Hydrocarbons",
    "science/grade_12/chem_ch_101": "The Solid State / Solutions (map ch_101)",
    "science/grade_12/chem_ch_102": "Solutions / Electrochemistry",
    "science/grade_12/chem_ch_103": "Electrochemistry / Chemical Kinetics",
    "science/grade_12/chem_ch_104": "Chemical Kinetics / d- and f-Block",
    "science/grade_12/chem_ch_105": "Coordination Compounds",
    "science/grade_12/chem_ch_201": "Haloalkanes and Haloarenes",
    "science/grade_12/chem_ch_202": "Alcohols, Phenols and Ethers",
    "science/grade_12/chem_ch_203": "Aldehydes, Ketones and Carboxylic Acids",
    "science/grade_12/chem_ch_204": "Amines",
    "science/grade_12/chem_ch_205": "Biomolecules",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    path.write_text(text, encoding="utf-8")
    print(f"  {path.name:28s} {path.stat().st_size:9d} B")


def chapter_family(unit_id: str) -> str:
    parts = (unit_id or "").split("/")
    return "/".join(parts[:3]) if len(parts) >= 3 else unit_id


def slim_mx(rows) -> list:
    out = []
    for mx in rows or []:
        if not isinstance(mx, dict):
            continue
        out.append(
            {
                "id": mx.get("mx_id"),
                "type": mx.get("confusion_type"),
                "cwo": mx.get("canonical_wrong_output"),
                "status": mx.get("status"),
            }
        )
    return out


def slim_pedagogy(stmt: dict) -> dict:
    cp = stmt.get("ci_pedagogy") or {}
    ped = cp.get("pedagogy") or {}
    mm = ped.get("mastery_model") or (cp.get("mastery_evidence") or {}).get("mastery_model") or {}
    lok = (cp.get("lack_of_knowledge") or {}).get("lok_model") or ped.get("lok_model") or {}
    ag = cp.get("antigaming") or {}
    pockets = ((ag.get("gaming_pocket_map") or {}).get("pockets")) or []
    facets = ped.get("facets") or []
    facet_names = []
    if isinstance(facets, list):
        for f in facets[:6]:
            if isinstance(f, dict):
                facet_names.append(f.get("facet_id") or f.get("name") or f.get("label"))
            elif isinstance(f, str):
                facet_names.append(f)
    anti = ped.get("anti_narration_constraint") or ag.get("anti_narration_constraint")
    if isinstance(anti, dict):
        anti = anti.get("constraint") or anti.get("text") or json.dumps(anti)[:240]
    return {
        "joined": stmt.get("ci_join_status") == "joined",
        "mastery_signal": (mm.get("mastery_signal") or "")[:400],
        "lok_folk": (lok.get("folk_default") or "")[:280],
        "gaming_pockets": [
            {
                "type": p.get("pocket_type"),
                "apparent_success": (p.get("apparent_success") or "")[:160],
            }
            for p in pockets[:4]
            if isinstance(p, dict)
        ],
        "facets": [n for n in facet_names if n],
        "anti_narration": (str(anti)[:280] if anti else None),
    }


def load_docs() -> dict:
    raw = json.loads(DOCS.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "documents" in raw:
        raw = raw["documents"]
    if isinstance(raw, list):
        return {d.get("doc_id") or d.get("id"): d for d in raw if isinstance(d, dict)}
    return raw if isinstance(raw, dict) else {}


def extract_tikz(o: dict) -> tuple[str | None, list[str]]:
    """Return (tikz source, extra TeX packages). Never copy SMILES."""
    fig = o.get("figure") if isinstance(o.get("figure"), dict) else {}
    enc = o.get("encoding") if isinstance(o.get("encoding"), dict) else {}
    tj = fig.get("tikz") if isinstance(fig.get("tikz"), dict) else None
    if not (tj and tj.get("code")):
        tj = enc.get("tikz") if isinstance(enc.get("tikz"), dict) else None
    if not (tj and isinstance(tj.get("code"), str) and tj["code"].strip()):
        return None, []
    pkgs = []
    for raw in tj.get("preamble_packages") or []:
        name = str(raw).split("[", 1)[0].strip()
        if name and name not in {"tikz", "amsmath", "amssymb"} and name not in pkgs:
            pkgs.append(name)
    return tj["code"], pkgs


def load_exam_index(uids: set[str]) -> dict:
    found = {}
    paths = [EXAM]
    if CORPUS.is_file():
        paths.append(CORPUS)
    for path in paths:
        with path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                # cheap reject
                if '"item_uid"' not in line:
                    continue
                o = json.loads(line)
                uid = o.get("item_uid")
                if uid not in uids or uid in found:
                    continue
                opts = o.get("options") or {}
                if isinstance(opts, dict):
                    options = {str(k): v for k, v in opts.items() if v is not None}
                else:
                    options = {}
                stmts = []
                for s in o.get("statements") or []:
                    if isinstance(s, dict):
                        stmts.append({"n": s.get("n"), "text": s.get("text")})
                    elif s:
                        stmts.append({"text": str(s)})
                tikz, tikz_packages = extract_tikz(o)
                rec = {
                    "stem": o.get("complete_stem") or o.get("stem_lead") or "",
                    "stem_lead": o.get("stem_lead") or "",
                    "item_type": o.get("item_type"),
                    "options": options,
                    "statements": stmts,
                    "has_figure": bool(o.get("has_drawn_figure") or o.get("options_are_figure")),
                    "options_are_figure": bool(o.get("options_are_figure")),
                    "equations": [
                        (e.get("text") if isinstance(e, dict) else e)
                        for e in (o.get("equations") or [])[:4]
                    ],
                }
                if tikz:
                    rec["tikz"] = tikz
                    if tikz_packages:
                        rec["tikz_packages"] = tikz_packages
                found[uid] = rec
                if len(found) == len(uids):
                    return found
    return found


def slim_projection(proj: dict) -> dict:
    ncert = []
    for rec in proj.get("ncert") or []:
        ncert.append(
            {
                "unit_id": rec.get("unit_id"),
                "node": rec.get("node"),
                "grade_band": rec.get("grade_band"),
                "chapter_family": rec.get("chapter_family") or chapter_family(rec.get("unit_id") or ""),
            }
        )
    cambridge = []
    for rec in proj.get("cambridge") or []:
        cambridge.append(
            {
                "unit_id": rec.get("unit_id"),
                "node": rec.get("node"),
                "grade_band": rec.get("grade_band"),
                "chapter_prefix": rec.get("chapter_prefix"),
            }
        )
    return {
        "schema": "ttwin.projection.chem.v1",
        "aliases": proj.get("aliases") or {},
        "named_families": proj.get("named_families") or {},
        "node_parents": proj.get("node_parents") or {},
        "ncert_by_node_band": proj.get("ncert_by_node_band") or {},
        "junior_exo_endo": proj.get("junior_exo_endo"),
        "grain": proj.get("grain"),
        "ncert": ncert,
        "cambridge": cambridge,
        "honesty": proj.get("honesty"),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("loading comprehensive map…")
    comp = json.loads(COMP.read_text(encoding="utf-8"))
    nodes_src = comp.get("nodes") or {}
    nodes = []
    for nid, n in nodes_src.items():
        if isinstance(n, dict):
            nodes.append(
                {
                    "id": n.get("id") or nid,
                    "title": n.get("title") or n.get("label"),
                    "kind": n.get("kind"),
                    "mechanism": n.get("mechanism"),
                }
            )
        else:
            nodes.append({"id": nid, "title": str(n)})

    hinges = []
    for s in comp.get("statements") or []:
        uid = s.get("unit_id")
        ch = chapter_family(uid or "")
        hinges.append(
            {
                "unit_id": uid,
                "node": s.get("node"),
                "grade_band": s.get("grade_band"),
                "chapter": ch,
                "chapter_title": CHAPTER_TITLES.get(ch, ch),
                "decision_hinge": s.get("decision_hinge") or s.get("statement"),
                "mechanism": s.get("mechanism"),
                "cognitive_operation": s.get("cognitive_operation"),
                "mx": slim_mx(s.get("mx")),
                "n_mx_na": len(s.get("mx_na") or s.get("mx_dispositions") or [])
                if isinstance(s.get("mx_na") or s.get("mx_dispositions"), list)
                else 0,
                "pedagogy": slim_pedagogy(s),
            }
        )

    print("loading enrichment…")
    docs = load_docs()
    enrich = []
    with ENRICH.open(encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            tb = o.get("taxonomy_bindings") or {}
            ev = o.get("evidence") or {}
            pi = o.get("pedagogical_intent") or {}
            ep = o.get("epistemic_metadata") or {}
            did = (o.get("provenance") or {}).get("doc_id") or o.get("doc_id")
            doc = docs.get(did) or {}
            url = doc.get("url") or doc.get("source_url")
            enrich.append(
                {
                    "item_id": o.get("item_id"),
                    "type": ev.get("type"),
                    "statement": ev.get("statement"),
                    "node": tb.get("primary_node_id"),
                    "serves": (tb.get("serves_statement_ids") or [])[:16],
                    "readiness": pi.get("classroom_readiness"),
                    "role": ep.get("pedagogical_role"),
                    "attested": ep.get("attested"),
                    "citation": {
                        "title": doc.get("title"),
                        "url": url if isinstance(url, str) and url.startswith("http") else None,
                        "source": doc.get("source"),
                    },
                }
            )

    print("loading nav tags…")
    nav_rows = []
    uids = set()
    with NAV.open(encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            if o.get("subject") != "chemistry":
                continue
            uid = o.get("item_uid")
            fam = o.get("family_ids") if isinstance(o.get("family_ids"), dict) else {}
            rec = {
                "uid": uid,
                "pack": o.get("pack"),
                "grade_band": o.get("grade_band"),
                "node": o.get("big_idea_id"),
                "chapter_id": o.get("chapter_id"),
                "chapter_label": o.get("chapter_label"),
                "subtopic_id": o.get("subtopic_id"),
                "subtopic_label": o.get("subtopic_label"),
                "complete_exam": bool(o.get("complete_exam")),
                "cam_family": fam.get("cambridge_chapter"),
                "ncert_family": fam.get("ncert_chapter"),
            }
            nav_rows.append(rec)
            if rec["complete_exam"]:
                uids.add(uid)

    print(f"joining {len(uids)} complete exam stems…")
    stems = load_exam_index(uids)
    missing = [u for u in uids if u not in stems]
    print(f"  stems found {len(stems)} missing {len(missing)}")

    by_pack = defaultdict(list)
    for row in nav_rows:
        uid = row["uid"]
        body = stems.get(uid)
        item = dict(row)
        if body:
            item.update(body)
        by_pack[row.get("pack") or "unknown"].append(item)

    print("loading projection…")
    proj = json.loads(PROJ.read_text(encoding="utf-8"))
    projection = slim_projection(proj)

    meta = {
        "schema": "ttwin.ncert.chem.showcase.v1",
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "subject": "chemistry",
        "board_home": "NCERT comprehensive map + Cambridge-tagged question bank",
        "n_nodes": len(nodes),
        "n_hinges": len(hinges),
        "n_enrichment": len(enrich),
        "n_questions": len(nav_rows),
        "n_complete_exam": sum(1 for r in nav_rows if r.get("complete_exam")),
        "n_stems": len(stems),
        "sources": {
            "comprehensive_map": str(COMP.relative_to(AWM)),
            "comprehensive_sha256": sha256_file(COMP),
            "public_map_sha256": sha256_file(PUBLIC) if PUBLIC.is_file() else None,
            "nav_items": str(NAV.relative_to(AWM)),
            "nav_sha256": sha256_file(NAV),
            "enrichment": str(ENRICH.relative_to(AWM)),
            "projection": str(PROJ.relative_to(AWM)),
            "exam_pack_sha256": sha256_file(EXAM),
        },
        "honesty": (
            "Questions keep Cambridge syllabus coordinates (cam:9701:5 / AS_A:9701.x.y). "
            "NCERT join is node × grade_band via the projection table, not a rewrite of tags. "
            "Mx and enrichment are teacher-facing; they are not printed on the learner paper. "
            "ISO-GEN on this site authors CANDIDATE items from hinge packs; it does not rewrite frozen L20. "
            "Cambridge wording is for retrieval demonstration, not a republished past-paper pack."
        ),
        "kimi": {
            "model": "kimi-k3",
            "endpoint": "https://api.moonshot.ai/v1/chat/completions",
            "roles": ["prompt_selector", "isogen_author", "lesson_prose"],
        },
    }

    print("writing…")
    dump(OUT / "meta.json", meta)
    dump(OUT / "nodes.json", nodes)
    dump(OUT / "hinges.json", hinges)
    dump(OUT / "enrichment.json", enrich)
    dump(OUT / "projection.json", projection)
    dump(OUT / "nav.json", nav_rows)
    for pack, items in by_pack.items():
        slug = {
            "igcse_9_10": "questions-igcse.json",
            "senior_11_12_as_a": "questions-senior.json",
            "olympiad_iit": "questions-olympiad.json",
        }.get(pack, f"questions-{pack}.json")
        dump(OUT / slug, items)

    (OUT / "RECEIPT.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
