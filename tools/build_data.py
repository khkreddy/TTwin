#!/usr/bin/env python3
"""Build slim TeacherTwin showcase JSON from the live AWM tree.

Does not rewrite frozen exam.v1, live V15, the public NCERT map, or POOL_ID.
Output is a derived static pack for GitHub Pages.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from learner_display import (
    infer_tikz_packages,
    normalize_tikz_source,
    pgfplots_spectrum_to_tikz,
    sanitize_item,
    separate_tikz_figures,
)

AWM = Path("/home/harik/awm_build")
OUT = Path(__file__).resolve().parents[1] / "data"

COMP = AWM / "reports/paper/data/NCERT_CHEMISTRY_MAP_COMPREHENSIVE.json"
WORKING = AWM / "reports/paper/data/NCERT_CHEMISTRY_MAP.json"
PUBLIC = AWM / "reports/paper/data/NCERT_CHEMISTRY_MAP_PUBLIC.json"
ENRICH = AWM / "reports/paper/data/supplement_ncert_hinges.jsonl"
DOCS = AWM / "data/chem_curriculum/supplement/documents.json"
NAV = AWM / "data/awm_product/generated/nav_mcq/items.jsonl"
NAV_MATHS_CAM = AWM / "data/awm_product/generated/nav_mcq/items_maths_cambridge.jsonl"
PROJ = AWM / "data/awm_product/generated/nav_mcq/vocab/projection_chem_v1.json"
EXAM = AWM / "data/chem_curriculum/item_envelope/exam_json/items.jsonl"
CORPUS = AWM / "data/awm_product/generated/exam_v1_corpus/items.jsonl"
CHEM_JOINED = AWM / "data/awm_product/generated/exam_v1_chem_joined/items.jsonl"
MATH_MAP = AWM / "data/intelligence/MATHEMATICS_MAP.json"
PHY_MAP = AWM / "data/intelligence/PHYSICS_MAP.json"
BIO_MAP = AWM / "data/intelligence/BIOLOGY_MAP.json"
MATHNET_ROOT = AWM / "data/corpus_intelligence/awm_corpus/mathnet_v1"
JEEBENCH = AWM / "data/corpus_intelligence/awm_corpus/jeebench-dataset.json"
MATH_V1_INDEX = AWM / "data/corpus_intelligence/awm_corpus/math_v1/INDEX.json"
VOCAB_DIR = AWM / "data/awm_product/generated/nav_mcq/vocab"

SUBJECT_ORDER = ["chemistry", "biology", "physics", "maths"]
SUBJECT_LABEL = {
    "chemistry": "Chemistry",
    "biology": "Biology",
    "physics": "Physics",
    "maths": "Mathematics",
}
VOCAB_FILE = {
    "chemistry": VOCAB_DIR / "big_ideas_chem.json",
    "biology": VOCAB_DIR / "big_ideas_bio.json",
    "physics": VOCAB_DIR / "big_ideas_phy.json",
    "maths": VOCAB_DIR / "big_ideas_math.json",
}
CHAPTER_VOCAB = {
    "physics": VOCAB_DIR / "chapters_phy.json",
    "biology": VOCAB_DIR / "chapters_bio.json",
}
PACK_SLUG = {
    "igcse_9_10": "igcse",
    "senior_11_12_as_a": "senior",
    "olympiad_iit": "olympiad",
}
PACK_LABEL = {
    "igcse_9_10": "A · Grades 9–10 / IGCSE",
    "senior_11_12_as_a": "B · Grades 11–12 / AS–A",
    "olympiad_iit": "C · Olympiad / IIT",
}
FIVE_IDS = ("pack", "subject", "big_idea_id", "chapter_id", "subtopic_id")
LEGACY_QUESTION_FILES = (
    "questions-igcse.json",
    "questions-senior.json",
    "questions-olympiad.json",
    "nav.json",
)

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
    rel = path.relative_to(OUT) if path.is_relative_to(OUT) else path.name
    print(f"  {str(rel):40s} {path.stat().st_size:9d} B")


def completely_tagged(row: dict) -> bool:
    return all(row.get(k) not in (None, "") for k in FIVE_IDS)


def slim_vocab(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    ideas = []
    for idea in raw.get("ideas") or []:
        if not isinstance(idea, dict):
            continue
        ideas.append(
            {
                "id": idea.get("id"),
                "title": idea.get("label") or idea.get("title"),
                "kind": idea.get("kind"),
                "mechanism": idea.get("mechanism"),
            }
        )
    return {
        "schema": "ttwin.vocab.v1",
        "subject": raw.get("subject"),
        "namespace": raw.get("namespace"),
        "n": len(ideas),
        "ideas": ideas,
    }


def question_relpath(subject: str, pack: str) -> str:
    slug = PACK_SLUG.get(pack, pack.replace("_", "-"))
    return f"questions/{subject}-{slug}.json"


def chapter_family(unit_id: str) -> str:
    parts = (unit_id or "").split("/")
    return "/".join(parts[:3]) if len(parts) >= 3 else unit_id


# Published NCERT chapter titles. Interim map only — not a hinge/mx freeze.
NCERT_SYLLABUS = {
    "physics": [
        (9, "SECONDARY", "ch_08", "Motion", "phy:P1"),
        (9, "SECONDARY", "ch_09", "Force and Laws of Motion", "phy:P1"),
        (9, "SECONDARY", "ch_10", "Gravitation", "phy:P5"),
        (9, "SECONDARY", "ch_11", "Work and Energy", "phy:P2"),
        (9, "SECONDARY", "ch_12", "Sound", "phy:P3"),
        (10, "SECONDARY", "ch_10", "Light — Reflection and Refraction", "phy:P3"),
        (10, "SECONDARY", "ch_11", "The Human Eye and the Colourful World", "phy:P3"),
        (10, "SECONDARY", "ch_12", "Electricity", "phy:P4"),
        (10, "SECONDARY", "ch_13", "Magnetic Effects of Electric Current", "phy:P5"),
        (10, "SECONDARY", "ch_14", "Sources of Energy", "phy:P2"),
        (11, "SENIOR_SECONDARY", "phy_ch_101", "Units and Measurements", "phy:P1/H-VECTORS"),
        (11, "SENIOR_SECONDARY", "phy_ch_102", "Motion in a Straight Line", "phy:P1"),
        (11, "SENIOR_SECONDARY", "phy_ch_103", "Motion in a Plane", "phy:P1"),
        (11, "SENIOR_SECONDARY", "phy_ch_104", "Laws of Motion", "phy:P1"),
        (11, "SENIOR_SECONDARY", "phy_ch_105", "Work, Energy and Power", "phy:P2"),
        (11, "SENIOR_SECONDARY", "phy_ch_106", "System of Particles and Rotational Motion", "phy:P1"),
        (11, "SENIOR_SECONDARY", "phy_ch_107", "Gravitation", "phy:P5"),
        (11, "SENIOR_SECONDARY", "phy_ch_201", "Mechanical Properties of Solids", "phy:B3"),
        (11, "SENIOR_SECONDARY", "phy_ch_202", "Mechanical Properties of Fluids", "phy:B3"),
        (11, "SENIOR_SECONDARY", "phy_ch_203", "Thermal Properties of Matter", "phy:P6"),
        (11, "SENIOR_SECONDARY", "phy_ch_204", "Thermodynamics", "phy:P6"),
        (11, "SENIOR_SECONDARY", "phy_ch_205", "Kinetic Theory", "phy:P6"),
        (11, "SENIOR_SECONDARY", "phy_ch_206", "Oscillations", "phy:P3/H-SHM"),
        (11, "SENIOR_SECONDARY", "phy_ch_207", "Waves", "phy:P3"),
        (12, "SENIOR_SECONDARY", "phy_ch_101", "Electric Charges and Fields", "phy:P5"),
        (12, "SENIOR_SECONDARY", "phy_ch_102", "Electrostatic Potential and Capacitance", "phy:P5"),
        (12, "SENIOR_SECONDARY", "phy_ch_103", "Current Electricity", "phy:P4"),
        (12, "SENIOR_SECONDARY", "phy_ch_104", "Moving Charges and Magnetism", "phy:P5"),
        (12, "SENIOR_SECONDARY", "phy_ch_105", "Magnetism and Matter", "phy:P5"),
        (12, "SENIOR_SECONDARY", "phy_ch_106", "Electromagnetic Induction", "phy:P5/H-INDUCTION"),
        (12, "SENIOR_SECONDARY", "phy_ch_107", "Alternating Current", "phy:P5/H-INDUCTION"),
        (12, "SENIOR_SECONDARY", "phy_ch_108", "Electromagnetic Waves", "phy:P5"),
        (12, "SENIOR_SECONDARY", "phy_ch_201", "Ray Optics and Optical Instruments", "phy:P3"),
        (12, "SENIOR_SECONDARY", "phy_ch_202", "Wave Optics", "phy:P3/H-SUPERPOSITION"),
        (12, "SENIOR_SECONDARY", "phy_ch_203", "Dual Nature of Radiation and Matter", "phy:P8"),
        (12, "SENIOR_SECONDARY", "phy_ch_204", "Atoms", "phy:P7"),
        (12, "SENIOR_SECONDARY", "phy_ch_205", "Nuclei", "phy:P7"),
        (12, "SENIOR_SECONDARY", "phy_ch_206", "Semiconductor Electronics", "phy:B4"),
    ],
    "biology": [
        (9, "SECONDARY", "ch_05", "The Fundamental Unit of Life", "bio:L1"),
        (9, "SECONDARY", "ch_06", "Tissues", "bio:L1"),
        (9, "SECONDARY", "ch_07", "Diversity in Living Organisms", "bio:L2"),
        (9, "SECONDARY", "ch_13", "Why Do We Fall Ill", "bio:L5"),
        (9, "SECONDARY", "ch_14", "Natural Resources", "bio:L6"),
        (9, "SECONDARY", "ch_15", "Improvement in Food Resources", "bio:L6"),
        (10, "SECONDARY", "ch_06", "Life Processes", "bio:L3"),
        (10, "SECONDARY", "ch_07", "Control and Coordination", "bio:L4"),
        (10, "SECONDARY", "ch_08", "How do Organisms Reproduce", "bio:L4"),
        (10, "SECONDARY", "ch_09", "Heredity and Evolution", "bio:L4"),
        (10, "SECONDARY", "ch_15", "Our Environment", "bio:L6"),
        (10, "SECONDARY", "ch_16", "Management of Natural Resources", "bio:L6"),
        (11, "SENIOR_SECONDARY", "bio_ch_101", "The Living World", "bio:L2"),
        (11, "SENIOR_SECONDARY", "bio_ch_102", "Biological Classification", "bio:L2"),
        (11, "SENIOR_SECONDARY", "bio_ch_103", "Plant Kingdom", "bio:L2"),
        (11, "SENIOR_SECONDARY", "bio_ch_104", "Animal Kingdom", "bio:L2"),
        (11, "SENIOR_SECONDARY", "bio_ch_105", "Morphology of Flowering Plants", "bio:L2"),
        (11, "SENIOR_SECONDARY", "bio_ch_106", "Anatomy of Flowering Plants", "bio:L1"),
        (11, "SENIOR_SECONDARY", "bio_ch_107", "Structural Organisation in Animals", "bio:L1"),
        (11, "SENIOR_SECONDARY", "bio_ch_108", "Cell: The Unit of Life", "bio:L1"),
        (11, "SENIOR_SECONDARY", "bio_ch_109", "Biomolecules", "bio:L3"),
        (11, "SENIOR_SECONDARY", "bio_ch_110", "Cell Cycle and Cell Division", "bio:L1"),
        (11, "SENIOR_SECONDARY", "bio_ch_111", "Photosynthesis in Higher Plants", "bio:L3"),
        (11, "SENIOR_SECONDARY", "bio_ch_112", "Respiration in Plants", "bio:L3"),
        (11, "SENIOR_SECONDARY", "bio_ch_113", "Plant Growth and Development", "bio:L4"),
        (11, "SENIOR_SECONDARY", "bio_ch_114", "Breathing and Exchange of Gases", "bio:L3"),
        (11, "SENIOR_SECONDARY", "bio_ch_115", "Body Fluids and Circulation", "bio:L3"),
        (11, "SENIOR_SECONDARY", "bio_ch_116", "Excretory Products and their Elimination", "bio:L3"),
        (11, "SENIOR_SECONDARY", "bio_ch_117", "Locomotion and Movement", "bio:L3"),
        (11, "SENIOR_SECONDARY", "bio_ch_118", "Neural Control and Coordination", "bio:L4"),
        (11, "SENIOR_SECONDARY", "bio_ch_119", "Chemical Coordination and Integration", "bio:L4"),
        (12, "SENIOR_SECONDARY", "bio_ch_101", "Sexual Reproduction in Flowering Plants", "bio:L4"),
        (12, "SENIOR_SECONDARY", "bio_ch_102", "Human Reproduction", "bio:L4"),
        (12, "SENIOR_SECONDARY", "bio_ch_103", "Reproductive Health", "bio:L5"),
        (12, "SENIOR_SECONDARY", "bio_ch_104", "Principles of Inheritance and Variation", "bio:L4"),
        (12, "SENIOR_SECONDARY", "bio_ch_105", "Molecular Basis of Inheritance", "bio:L4"),
        (12, "SENIOR_SECONDARY", "bio_ch_106", "Evolution", "bio:L2"),
        (12, "SENIOR_SECONDARY", "bio_ch_107", "Human Health and Disease", "bio:L5"),
        (12, "SENIOR_SECONDARY", "bio_ch_108", "Microbes in Human Welfare", "bio:L5"),
        (12, "SENIOR_SECONDARY", "bio_ch_109", "Biotechnology: Principles and Processes", "bio:L5"),
        (12, "SENIOR_SECONDARY", "bio_ch_110", "Biotechnology and its Applications", "bio:L5"),
        (12, "SENIOR_SECONDARY", "bio_ch_111", "Organisms and Populations", "bio:L6"),
        (12, "SENIOR_SECONDARY", "bio_ch_112", "Ecosystem", "bio:L6"),
        (12, "SENIOR_SECONDARY", "bio_ch_113", "Biodiversity and Conservation", "bio:L6"),
    ],
}


def _syllabus_row(subject: str, grade: int, band: str, slug: str, ch_title: str, node: str, vocab_ideas: list) -> dict:
    mech = {i.get("id"): i.get("mechanism") for i in vocab_ideas if isinstance(i, dict)}
    title = {i.get("id"): i.get("title") for i in vocab_ideas if isinstance(i, dict)}
    ns = f"science/grade_{grade}/{slug}"
    return {
        "subject": subject,
        "unit_id": f"ncert/grade_{grade:02d}/{subject}/{slug}",
        "node": node.split(":")[-1] if ":" in node else node,
        "node_id": node,
        "grade_band": band,
        "grade": grade,
        "chapter": ns,
        "chapter_title": ch_title,
        "decision_hinge": f"Work a question inside NCERT Class {grade} “{ch_title}”.",
        "mechanism": mech.get(node) or title.get(node) or "",
        "mx": [],
        "n_mx_na": 0,
        "pedagogy": {},
        "status": "syllabus_interim",
    }


def _slug_index(subject: str) -> dict[str, tuple]:
    out = {}
    for grade, band, slug, ch_title, node in NCERT_SYLLABUS.get(subject, []):
        out[slug] = (grade, band, ch_title, node)
        out[f"science/grade_{grade}/{slug}"] = (grade, band, ch_title, node)
    return out


def syllabus_map(subject: str, vocab_ideas: list) -> list[dict]:
    """Interim NCERT chapter map. Not a hinge freeze; mx empty until a complete map exists.

    Class 11–12 titles come from the existing nav vocab
    (`ncert_chapter_candidates_pack_c`). Class 9–10 are the published Science
    book chapters for that subject. Do not copy candidate chapter_intelligence.
    """
    idx = _slug_index(subject)
    rows: list[dict] = []
    seen: set[str] = set()

    for grade, band, slug, ch_title, node in NCERT_SYLLABUS.get(subject, []):
        if grade >= 11:
            continue
        rec = _syllabus_row(subject, grade, band, slug, ch_title, node, vocab_ideas)
        rows.append(rec)
        seen.add(rec["chapter"])

    path = CHAPTER_VOCAB.get(subject)
    if path and path.is_file():
        raw = json.loads(path.read_text(encoding="utf-8"))
        for cand in raw.get("ncert_chapter_candidates_pack_c") or []:
            if not isinstance(cand, dict):
                continue
            ns = (cand.get("chapter_namespace") or "").strip()
            if not ns or ns in seen:
                continue
            parts = ns.split("/")
            slug = parts[-1] if parts else ""
            try:
                grade = int(parts[1].split("_")[-1]) if len(parts) >= 2 else 11
            except ValueError:
                grade = 11
            meta = idx.get(ns) or idx.get(slug)
            band = "SENIOR_SECONDARY" if grade >= 11 else "SECONDARY"
            ch_title = (cand.get("label") or "").strip()
            node = ""
            if meta:
                grade, band, fallback_title, node = meta
                ch_title = ch_title or fallback_title
            rec = _syllabus_row(subject, grade, band, slug, ch_title or slug, node, vocab_ideas)
            rows.append(rec)
            seen.add(rec["chapter"])
    else:
        for grade, band, slug, ch_title, node in NCERT_SYLLABUS.get(subject, []):
            if grade < 11:
                continue
            rec = _syllabus_row(subject, grade, band, slug, ch_title, node, vocab_ideas)
            if rec["chapter"] in seen:
                continue
            rows.append(rec)
            seen.add(rec["chapter"])

    rows.sort(key=lambda r: (r.get("grade") or 0, r.get("chapter") or ""))
    return rows


def pack_map_doc(subject: str, status: str, units: list, *, nodes: list | None = None, extra: dict | None = None) -> dict:
    rows = []
    for u in units or []:
        rec = dict(u)
        rec["subject"] = subject
        rows.append(rec)
    doc = {
        "schema": "ttwin.map.v1",
        "subject": subject,
        "label": SUBJECT_LABEL.get(subject, subject),
        "map_status": status,
        "n": len(rows),
        "nodes": nodes or [],
        "units": rows,
    }
    if extra:
        doc.update(extra)
    return doc


def pack_enrichment_doc(subject: str, items: list) -> dict:
    stamped = []
    for it in items or []:
        rec = dict(it)
        rec["subject"] = subject
        stamped.append(rec)
    return {
        "schema": "ttwin.enrichment.v1",
        "subject": subject,
        "label": SUBJECT_LABEL.get(subject, subject),
        "n": len(stamped),
        "items": stamped,
    }


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


def slim_tables(tables) -> list:
    out = []
    for t in tables or []:
        if not isinstance(t, dict):
            continue
        row = {
            "headers": t.get("headers") or [],
            "rows": t.get("rows") or [],
            "row_labels": t.get("row_labels") or [],
            "caption": t.get("caption"),
        }
        if t.get("is_option_table"):
            row["is_option_table"] = True
        out.append(row)
    return out


def extract_structures(o: dict) -> list:
    """SMILES for drawing only. Learner paper must not print the SMILES string."""
    fig = o.get("figure") if isinstance(o.get("figure"), dict) else {}
    enc = o.get("encoding") if isinstance(o.get("encoding"), dict) else {}
    raw = fig.get("structures") or enc.get("structures") or []
    out = []
    if isinstance(raw, list):
        for s in raw:
            if isinstance(s, dict) and s.get("smiles"):
                out.append({"label": s.get("label"), "smiles": s.get("smiles")})
            elif isinstance(s, str) and s.strip():
                out.append({"label": None, "smiles": s.strip()})
    if out:
        return out
    sm = fig.get("smiles") or enc.get("smiles") or []
    if isinstance(sm, str) and sm.strip():
        sm = [sm]
    labs = list("ABCD")
    if isinstance(sm, list):
        for i, x in enumerate(sm):
            if isinstance(x, str) and x.strip():
                lab = labs[i] if i < 4 else str(i + 1)
                out.append({"label": lab, "smiles": x.strip()})
    return out


def extract_tikz(o: dict) -> tuple[str | None, list[str]]:
    """Return (tikz source, extra TeX packages). Never copy SMILES."""
    fig = o.get("figure") if isinstance(o.get("figure"), dict) else {}
    enc = o.get("encoding") if isinstance(o.get("encoding"), dict) else {}
    tj = fig.get("tikz") if isinstance(fig.get("tikz"), dict) else None
    if not (tj and tj.get("code")):
        tj = enc.get("tikz") if isinstance(enc.get("tikz"), dict) else None
    if not (tj and isinstance(tj.get("code"), str) and tj["code"].strip()):
        return None, []
    code = tj["code"]
    native = pgfplots_spectrum_to_tikz(code)
    if native:
        return native, []
    pkgs = infer_tikz_packages(code, tj.get("preamble_packages") or [])
    return separate_tikz_figures(normalize_tikz_source(code)), pkgs


MATH_SYL_PACK = {
    "0580": ("igcse_9_10", "SECONDARY"),
    "0606": ("igcse_9_10", "SECONDARY"),
    "0607": ("igcse_9_10", "SECONDARY"),
    "9709": ("senior_11_12_as_a", "SENIOR_SECONDARY"),
    "9231": ("senior_11_12_as_a", "SENIOR_SECONDARY"),
}


def _tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-z]{3,}", (s or "").lower()))


def _mechanism_text(mech) -> str:
    if isinstance(mech, dict):
        return str(mech.get("law") or "")
    return str(mech or "")


def reconcile_map_node(subject: str, node: str, recon) -> str:
    bare = str(node or "")
    if subject == "biology" and isinstance(recon, list):
        for row in recon:
            if isinstance(row, dict) and row.get("constructed") == bare:
                frozen = str(row.get("frozen") or "")
                if ":" in frozen:
                    return frozen.split(":", 1)[-1]
                if frozen:
                    return frozen
    return bare


def slim_subject_map(path: Path, subject: str) -> tuple[list[dict], list[dict], dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    recon = (raw.get("node_layer") or {}).get("frozen_vocab_reconciliation")
    ch_meta = raw.get("chapters") or {}
    nodes_src = raw.get("nodes") or {}
    nodes = []
    for nid, n in nodes_src.items():
        shown = reconcile_map_node(subject, nid, recon)
        if isinstance(n, dict):
            nodes.append(
                {
                    "id": shown,
                    "title": n.get("title") or n.get("label") or shown,
                    "kind": n.get("kind"),
                    "mechanism": n.get("mechanism") or n.get("title"),
                    "map_id": nid,
                }
            )
        else:
            nodes.append({"id": shown, "title": str(n), "map_id": nid})
    units = []
    proj_ncert = []
    proj_cam = []
    for s in raw.get("statements") or []:
        uid = s.get("unit_id")
        node = reconcile_map_node(subject, s.get("node"), recon)
        ch = s.get("chapter") or chapter_family(uid or "")
        title = s.get("chapter_title")
        if not title and isinstance(ch_meta.get(ch), dict):
            title = ch_meta[ch].get("title") or ch_meta[ch].get("chapter_title")
        band = s.get("grade_band")
        if band in {"CORE", "EXTENDED", "AS", "A_LEVEL", "CAMBRIDGE_IGCSE_CORE", "CAMBRIDGE_IGCSE_SUPPLEMENT"}:
            band = "SECONDARY" if str(s.get("syllabus") or "").startswith("CAMBRIDGE_IGCSE") else "SENIOR_SECONDARY"
        if band not in {"SECONDARY", "SENIOR_SECONDARY"}:
            g = s.get("grade")
            band = "SENIOR_SECONDARY" if isinstance(g, int) and g >= 11 else (s.get("grade_band") or "SECONDARY")
            if band not in {"SECONDARY", "SENIOR_SECONDARY"}:
                band = "SENIOR_SECONDARY" if str(ch).find("grade_1") >= 0 else "SECONDARY"
        units.append(
            {
                "subject": subject,
                "unit_id": uid,
                "node": node,
                "grade_band": band if band in {"SECONDARY", "SENIOR_SECONDARY"} else "SECONDARY",
                "chapter": ch,
                "chapter_title": title or ch,
                "decision_hinge": s.get("decision_hinge") or s.get("statement"),
                "mechanism": _mechanism_text(s.get("mechanism")),
                "cognitive_operation": s.get("cognitive_operation"),
                "board": s.get("board"),
                "mx": slim_mx(s.get("mx")),
                "n_mx_na": len(s.get("mx_dispositions") or []) if isinstance(s.get("mx_dispositions"), list) else 0,
                "status": raw.get("map_status") or "hinge_map_candidate",
            }
        )
        rec = {
            "unit_id": uid,
            "node": node,
            "grade_band": units[-1]["grade_band"],
            "chapter_family": ch,
        }
        if s.get("board") == "CAMBRIDGE" or str(uid).startswith(("IGCSE:", "AS_A:")):
            rec["chapter_prefix"] = ".".join(str(uid).split(".")[:2]) if "." in str(uid) else str(uid)
            proj_cam.append(rec)
        else:
            proj_ncert.append(rec)
    ns = {"biology": "bio", "physics": "phy", "maths": "math", "mathematics": "math"}.get(subject, "chem")
    projection = {
        "schema": f"ttwin.projection.{ns}.v1",
        "subject": "maths" if subject == "mathematics" else subject,
        "ncert": proj_ncert,
        "cambridge": proj_cam,
        "honesty": "Derived from the hinge-map candidate. Does not rewrite question tags.",
    }
    return units, nodes, projection


def load_math_bank_stems(uids: set[str]) -> dict:
    found = {}
    want_mn = {u for u in uids if u.startswith("mathnet:")}
    want_jee = {u for u in uids if u.startswith("jeebench:")}
    for shard in ("m1", "m2", "m3", "m4"):
        recdir = MATHNET_ROOT / shard / "records"
        if not recdir.is_dir():
            continue
        for uid in list(want_mn):
            slug = uid.split(":", 1)[-1]
            path = recdir / f"mathnet_{slug}.json"
            if not path.is_file():
                continue
            d = json.loads(path.read_text(encoding="utf-8"))
            stem = ((d.get("presentation") or {}).get("stem") or "").strip()
            if not stem:
                continue
            found[uid] = sanitize_item(
                uid,
                {
                    "stem": stem,
                    "stem_lead": stem,
                    "item_type": "open_response",
                    "options": {},
                    "statements": [],
                    "has_figure": False,
                    "options_are_figure": False,
                    "equations": [],
                },
            )
            want_mn.discard(uid)
        if not want_mn:
            break
    if want_jee and JEEBENCH.is_file():
        rows = json.loads(JEEBENCH.read_text(encoding="utf-8"))
        by_uid = {}
        for rec in rows:
            subj = rec.get("subject") or ""
            desc = rec.get("description") or ""
            idx = rec.get("index")
            slug = re.sub(r"[^a-z0-9]+", "_", desc.lower()).strip("_")
            json_u = f"jeebench:srcjson:{subj}:{slug}:q{idx}"
            by_uid[json_u] = rec
            if subj in {"math", "mathematics"}:
                by_uid[f"jeebench:srcjson:math:{slug}:q{idx}"] = rec
        for uid in want_jee:
            rec = by_uid.get(uid)
            if not rec:
                continue
            stem = (rec.get("question") or "").strip()
            if not stem:
                continue
            gold = rec.get("gold")
            found[uid] = sanitize_item(
                uid,
                {
                    "stem": stem,
                    "stem_lead": stem,
                    "item_type": "mcq",
                    "options": {},
                    "statements": [],
                    "has_figure": False,
                    "options_are_figure": False,
                    "equations": [],
                    "correct": gold if gold in {"A", "B", "C", "D"} else None,
                },
            )
    return found


def tag_cambridge_maths(existing: set[str]) -> list[dict]:
    if not MATH_MAP.is_file() or not CORPUS.is_file():
        return []
    raw = json.loads(MATH_MAP.read_text(encoding="utf-8"))
    cam_stmts = [s for s in (raw.get("statements") or []) if s.get("board") == "CAMBRIDGE"]
    buckets: dict[str, list[tuple[set[str], dict]]] = defaultdict(list)
    for s in cam_stmts:
        uid = str(s.get("unit_id") or "")
        m = re.match(r"^(?:IGCSE|AS_A):(\d{4})\.", uid)
        if not m:
            continue
        syl = m.group(1)
        blob = " ".join(
            [
                str(s.get("chapter_title") or ""),
                str(s.get("decision_hinge") or s.get("statement") or ""),
                str((s.get("mechanism") or {}).get("law") if isinstance(s.get("mechanism"), dict) else s.get("mechanism") or ""),
            ]
        )
        buckets[syl].append((_tokens(blob), s))
    index_topics = {}
    usable = set()
    if MATH_V1_INDEX.is_file():
        idx = json.loads(MATH_V1_INDEX.read_text(encoding="utf-8"))
        for it in idx.get("items") or []:
            uid = it.get("item_uid")
            if not uid:
                continue
            if it.get("usable"):
                usable.add(uid)
            topics = it.get("topics") or []
            index_topics[uid] = " ".join(topics if isinstance(topics, list) else [str(topics)])
    rows = []
    with CORPUS.open(encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            uid = o.get("item_uid") or ""
            if uid in existing:
                continue
            m = re.match(r"^(\d{4})_", uid)
            if not m or m.group(1) not in MATH_SYL_PACK:
                continue
            syl = m.group(1)
            itype = str(o.get("item_type") or "")
            keep = itype.startswith("mcq") or uid in usable
            if not keep:
                continue
            stem = (o.get("complete_stem") or o.get("stem_lead") or "").strip()
            if not stem:
                continue
            pack, band = MATH_SYL_PACK[syl]
            qtok = _tokens(index_topics.get(uid, "") + " " + stem[:400])
            best, best_n = None, 0
            for tok, stmt in buckets.get(syl) or []:
                n = len(qtok & tok)
                if n > best_n:
                    best, best_n = stmt, n
            node = "M1"
            chapter_id = f"cam:{syl}"
            chapter_label = "Mathematics"
            subtopic_id = f"cam:{syl}"
            subtopic_label = chapter_label
            if best:
                node = best.get("node") or node
                lo = str(best.get("unit_id") or "")
                parts = lo.split(":")[-1].split(".") if lo else []
                topic = parts[1] if len(parts) > 1 else parts[0] if parts else ""
                if topic:
                    chapter_id = f"cam:{syl}:{topic}"
                    subtopic_id = lo if lo.startswith(("IGCSE:", "AS_A:")) else f"cam:{syl}:{topic}"
                chapter_label = best.get("chapter_title") or chapter_label
                subtopic_label = (best.get("decision_hinge") or chapter_label)[:80]
            rec = {
                "schema": "awm.nav.mcq.v1",
                "item_uid": uid,
                "status": "tagged",
                "subject": "maths",
                "pack": pack,
                "grade_band": band,
                "big_idea_id": f"math:{node}",
                "chapter_id": chapter_id,
                "chapter_label": chapter_label,
                "subtopic_id": subtopic_id,
                "subtopic_label": subtopic_label,
                "complete_exam": True,
                "family_ids": {"cambridge_chapter": chapter_id},
                "origin": {"bank": "exam_v1_corpus", "syllabus_code": syl, "board": "Cambridge"},
                "provenance": {
                    "assigned_by": "tag_maths_from_map",
                    "source": "MATHEMATICS_MAP.json",
                    "map_lo": (best or {}).get("unit_id"),
                    "score": best_n,
                },
            }
            rows.append(rec)
    return rows


def nav_record(o: dict) -> dict | None:
    if not completely_tagged(o):
        return None
    subject = o.get("subject")
    if subject not in SUBJECT_ORDER:
        return None
    fam = o.get("family_ids") if isinstance(o.get("family_ids"), dict) else {}
    return {
        "uid": o.get("item_uid"),
        "subject": subject,
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


def load_exam_index(uids: set[str]) -> dict:
    found = {}
    paths = [EXAM]
    if CORPUS.is_file():
        paths.append(CORPUS)
    if CHEM_JOINED.is_file():
        paths.append(CHEM_JOINED)
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
                    "tables": slim_tables(o.get("tables")),
                    "structures": extract_structures(o),
                }
                if tikz:
                    rec["tikz"] = tikz
                    if tikz_packages:
                        rec["tikz_packages"] = tikz_packages
                if not rec["tables"]:
                    rec.pop("tables")
                if not rec["structures"]:
                    rec.pop("structures")
                rec = sanitize_item(uid, rec)
                if not rec.get("tables"):
                    rec.pop("tables", None)
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


def write_enrichment_dir(enrich: list) -> None:
    (OUT / "enrichment").mkdir(parents=True, exist_ok=True)
    by_enr = {s: [] for s in SUBJECT_ORDER}
    for row in enrich:
        by_enr.setdefault(row.get("subject") or "chemistry", []).append(row)
    for s in SUBJECT_ORDER:
        dump(OUT / "enrichment" / f"{s}.json", pack_enrichment_doc(s, by_enr.get(s) or []))
    for stale in ("hinges.json", "enrichment.json"):
        p = OUT / stale
        if p.is_file():
            p.unlink()
            print(f"  removed legacy {stale}")


def main() -> int:
    maps_only = "--maps-only" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "questions").mkdir(exist_ok=True)
    (OUT / "nav").mkdir(exist_ok=True)
    (OUT / "vocab").mkdir(exist_ok=True)
    (OUT / "maps").mkdir(exist_ok=True)
    (OUT / "enrichment").mkdir(exist_ok=True)

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
                "subject": "chemistry",
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
                    "subject": "chemistry",
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

    if maps_only:
        print("maps-only: writing maps + enrichment, leaving question packs untouched")
        dump(
            OUT / "maps" / "chemistry.json",
            pack_map_doc(
                "chemistry",
                "comprehensive",
                hinges,
                nodes=nodes,
                extra={
                    "source": str(COMP.relative_to(AWM)),
                    "source_sha256": sha256_file(COMP),
                    "honesty": "Derived from the NCERT chemistry comprehensive map (523 statements). The 46 MB source blob is not copied into Pages; this file is the live map.",
                },
            ),
        )
        dump(OUT / "nodes.json", nodes)
        for subject, mpath in (("physics", PHY_MAP), ("biology", BIO_MAP)):
            if mpath.is_file():
                mrows, mnodes, _proj = slim_subject_map(mpath, subject)
                dump(
                    OUT / "maps" / f"{subject}.json",
                    pack_map_doc(
                        subject,
                        "hinge_map_candidate",
                        mrows,
                        nodes=mnodes,
                        extra={
                            "source": str(mpath.relative_to(AWM)),
                            "source_sha256": sha256_file(mpath),
                            "honesty": "Slim pack of the hinge-map candidate. Source blob is not copied. Mix-ups are teacher-facing CANDIDATE.",
                        },
                    ),
                )
            else:
                vocab = slim_vocab(VOCAB_FILE[subject])
                mrows = syllabus_map(subject, vocab.get("ideas") or [])
                dump(
                    OUT / "maps" / f"{subject}.json",
                    pack_map_doc(
                        subject,
                        "syllabus_interim",
                        mrows,
                        extra={
                            "honesty": "Published NCERT chapter list. Mix-ups empty until a complete hinge map exists.",
                        },
                    ),
                )
        write_enrichment_dir(enrich)
        subj_path = OUT / "subjects.json"
        subjects_doc = json.loads(subj_path.read_text(encoding="utf-8"))
        for s in subjects_doc.get("subjects") or []:
            sid = s.get("id")
            s["enrichment"] = f"data/enrichment/{sid}.json"
            if sid == "chemistry":
                s["map"] = "data/maps/chemistry.json"
                s["map_status"] = "comprehensive"
                s["n_map_units"] = len(hinges)
                s["has_map"] = True
        dump(subj_path, subjects_doc)
        meta_path = OUT / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
        meta["n_nodes"] = len(nodes)
        meta["n_hinges"] = len(hinges)
        meta["n_enrichment"] = len(enrich)
        files = dict(meta.get("files") or {})
        files["maps"] = [
            s.get("map") for s in subjects_doc.get("subjects") or [] if s.get("map")
        ]
        files["enrichment"] = [f"data/enrichment/{s}.json" for s in SUBJECT_ORDER]
        meta["files"] = files
        sources = dict(meta.get("sources") or {})
        sources["comprehensive_map"] = str(COMP.relative_to(AWM))
        sources["comprehensive_sha256"] = sha256_file(COMP)
        sources["enrichment"] = str(ENRICH.relative_to(AWM))
        meta["sources"] = sources
        meta["built_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        dump(OUT / "meta.json", meta)
        (OUT / "RECEIPT.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print("done (maps-only)")
        return 0

    print("loading nav tags (all subjects)…")
    by_subject: dict[str, list] = {s: [] for s in SUBJECT_ORDER}
    skipped = 0
    seen: set[str] = set()
    with NAV.open(encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            rec = nav_record(o)
            if not rec:
                skipped += 1
                continue
            by_subject[rec["subject"]].append(rec)
            seen.add(rec["uid"])

    print("tagging Cambridge maths from MATHEMATICS_MAP + exam pack…")
    math_extra = tag_cambridge_maths(seen)
    if math_extra:
        NAV_MATHS_CAM.parent.mkdir(parents=True, exist_ok=True)
        with NAV_MATHS_CAM.open("w", encoding="utf-8") as fh:
            for row in math_extra:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"  wrote {len(math_extra)} {NAV_MATHS_CAM.relative_to(AWM)}")
        for o in math_extra:
            rec = nav_record(o)
            if rec:
                by_subject["maths"].append(rec)
                seen.add(rec["uid"])

    uids = {r["uid"] for rows in by_subject.values() for r in rows}

    n_tagged = sum(len(v) for v in by_subject.values())
    print(f"  tagged {n_tagged}  skipped {skipped}  stem-join uids {len(uids)}")
    for s in SUBJECT_ORDER:
        n = len(by_subject[s])
        nce = sum(1 for r in by_subject[s] if r.get("complete_exam"))
        print(f"    {s:12s} tagged={n:5d} complete_exam_flag={nce:5d}")

    print(f"joining exam stems for {len(uids)} tagged uids…")
    stems = load_exam_index(uids)
    print(f"  exam stems {len(stems)}")
    bank = load_math_bank_stems(uids - set(stems))
    stems.update(bank)
    print(f"  + math-bank stems {len(bank)}  total {len(stems)}")
    missing = [u for u in uids if u not in stems]
    print(f"  still missing {len(missing)}")

    print("loading projection…")
    proj = json.loads(PROJ.read_text(encoding="utf-8"))
    projection = slim_projection(proj)

    print("writing vocab / nav / questions…")
    catalog = []
    n_stems_total = 0
    n_tikz = 0
    n_struct = 0
    n_table = 0
    question_files: list[str] = []

    for subject in SUBJECT_ORDER:
        rows = by_subject[subject]
        rows.sort(key=lambda r: (r.get("pack") or "", r.get("uid") or ""))
        vocab = slim_vocab(VOCAB_FILE[subject])
        dump(OUT / "vocab" / f"{subject}.json", vocab)
        dump(OUT / "nav" / f"{subject}.json", rows)

        packs_present: dict[str, list] = defaultdict(list)
        for row in rows:
            uid = row["uid"]
            body = stems.get(uid)
            item = dict(row)
            if body:
                item.update(body)
                item["complete_exam"] = True
                n_stems_total += 1
                if item.get("tikz"):
                    n_tikz += 1
                if item.get("structures"):
                    n_struct += 1
                if item.get("tables"):
                    n_table += 1
            packs_present[row.get("pack") or "unknown"].append(item)

        pack_entries = []
        for pack in ("igcse_9_10", "senior_11_12_as_a", "olympiad_iit"):
            items = packs_present.get(pack) or []
            if not items:
                continue
            rel = question_relpath(subject, pack)
            dump(OUT / rel, items)
            question_files.append("data/" + rel)
            pack_entries.append(
                {
                    "id": pack,
                    "label": PACK_LABEL.get(pack, pack),
                    "questions": "data/" + rel,
                    "n": len(items),
                    "n_complete_exam": sum(1 for it in items if it.get("complete_exam")),
                    "n_stems": sum(1 for it in items if (it.get("stem") or "").strip()),
                }
            )

        map_path = None
        map_status = None
        n_map_units = 0
        if subject == "chemistry":
            dump(
                OUT / "maps" / "chemistry.json",
                pack_map_doc(
                    "chemistry",
                    "comprehensive",
                    hinges,
                    nodes=nodes,
                    extra={
                        "source": str(COMP.relative_to(AWM)),
                        "source_sha256": sha256_file(COMP),
                        "honesty": "Derived from the NCERT chemistry comprehensive map (523 statements). The 46 MB source blob is not copied into Pages; this file is the live map.",
                    },
                ),
            )
            map_path = "data/maps/chemistry.json"
            map_status = "comprehensive"
            n_map_units = len(hinges)
        elif subject in ("physics", "biology", "maths"):
            mpath = {"physics": PHY_MAP, "biology": BIO_MAP, "maths": MATH_MAP}[subject]
            map_subj = "mathematics" if subject == "maths" else subject
            if mpath.is_file():
                mrows, mnodes, proj = slim_subject_map(mpath, map_subj)
                dump(
                    OUT / "maps" / f"{subject}.json",
                    pack_map_doc(
                        subject,
                        "hinge_map_candidate",
                        mrows,
                        nodes=mnodes,
                        extra={
                            "source": str(mpath.relative_to(AWM)),
                            "source_sha256": sha256_file(mpath),
                            "honesty": "Slim pack of the hinge-map candidate. Source blob is not copied.",
                        },
                    ),
                )
                dump(OUT / "projection" / f"{subject}.json", proj)
                map_path = f"data/maps/{subject}.json"
                map_status = "hinge_map_candidate"
                n_map_units = len(mrows)
            elif subject in ("physics", "biology"):
                mrows = syllabus_map(subject, vocab.get("ideas") or [])
                dump(
                    OUT / "maps" / f"{subject}.json",
                    pack_map_doc(
                        subject,
                        "syllabus_interim",
                        mrows,
                        extra={
                            "honesty": "Published NCERT chapter list. Mix-ups empty until a complete hinge map exists.",
                        },
                    ),
                )
                map_path = f"data/maps/{subject}.json"
                map_status = "syllabus_interim"
                n_map_units = len(mrows)
            else:
                map_path = None
                map_status = None
                n_map_units = 0

        catalog.append(
            {
                "id": subject,
                "label": SUBJECT_LABEL[subject],
                "nav": f"data/nav/{subject}.json",
                "vocab": f"data/vocab/{subject}.json",
                "has_map": bool(map_path),
                "map": map_path,
                "enrichment": f"data/enrichment/{subject}.json",
                "map_status": map_status,
                "n_map_units": n_map_units,
                "n_tagged": len(rows),
                "n_complete_exam": sum(p.get("n_complete_exam") or 0 for p in pack_entries),
                "projection": (
                    "data/projection.json" if subject == "chemistry"
                    else f"data/projection/{subject}.json"
                ),
                "packs": pack_entries,
                "default_node": (vocab["ideas"][0]["id"] if vocab["ideas"] else ""),
                "default_pack": pack_entries[0]["id"] if pack_entries else "",
            }
        )

    subjects_doc = {
        "schema": "ttwin.subjects.v1",
        "default": "chemistry",
        "subjects": catalog,
    }

    meta = {
        "schema": "ttwin.showcase.v2",
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "subjects": SUBJECT_ORDER,
        "board_home": "NCERT chemistry map + physics/biology/mathematics hinge-map candidates + Cambridge-tagged question bank",
        "n_nodes": len(nodes),
        "n_hinges": len(hinges),
        "n_enrichment": len(enrich),
        "n_questions": n_tagged,
        "n_complete_exam": sum(s["n_complete_exam"] for s in catalog),
        "n_stems": n_stems_total,
        "n_tikz": n_tikz,
        "n_structures": n_struct,
        "n_tables": n_table,
        "by_subject": {
            s["id"]: {
                "n_tagged": s["n_tagged"],
                "n_complete_exam": s["n_complete_exam"],
                "packs": {p["id"]: p["n"] for p in s["packs"]},
            }
            for s in catalog
        },
        "files": {
            "subjects": "data/subjects.json",
            "questions": question_files,
            "nav": [f"data/nav/{s}.json" for s in SUBJECT_ORDER],
            "vocab": [f"data/vocab/{s}.json" for s in SUBJECT_ORDER],
            "maps": [
                s.get("map") for s in catalog if s.get("map")
            ],
            "enrichment": [f"data/enrichment/{s}.json" for s in SUBJECT_ORDER],
            "solutions": "data/solutions/index.json",
        },
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
            "Questions keep Cambridge syllabus coordinates (chapter_id / subtopic_id). "
            "NCERT join for chemistry is node × grade_band via the projection table, not a rewrite of tags. "
            "Physics, biology and mathematics Maps are slim packs of hinge-map candidates (not the 60–140 MB source blobs). "
            "Existing five-ID tags are not rewritten. Cambridge maths items are tagged from the mathematics map + exam pack. "
            "Chemistry stems missing from the all-subject pack are joined from exam_v1_chem_joined. "
            "IR spectra using pgfplots are redrawn as native TikZ at pack time so TikZJax can display them. "
            "Chemistry map lives at data/maps/chemistry.json (loaded from the comprehensive map). "
            "Enrichment is per-subject under data/enrichment/{subject}.json; every row carries subject. "
            "Mx and enrichment are teacher-facing; they are not printed on the learner paper. "
            "ISO-GEN authors CANDIDATE items; it does not rewrite frozen L20. Test-maker Modify is session-only and "
            "does not rewrite frozen exam.v1. Student-take keys for unmodified exam items are AI-inferred, not a "
            "published mark scheme. Solution analysis is a sub-layer of the question bank (item_uid × item_sha256): "
            "first assembly writes it; later assemblies retrieve it with zero provider calls. Mix-ups stay off the learner paper. "
            "Cambridge wording is for retrieval demonstration, not a republished past-paper pack."
        ),
        "kimi": {
            "model": "kimi-k3",
            "endpoint": "https://api.moonshot.ai/v1/chat/completions",
            "roles": ["prompt_selector", "isogen_author", "lesson_prose", "item_modify", "paper_grade", "solution_analysis"],
        },
    }

    print("packing solution analysis index…")
    sol_dir = OUT / "solutions"
    sol_dir.mkdir(parents=True, exist_ok=True)
    by_sol: dict = {}
    idx_path = sol_dir / "index.json"
    if idx_path.is_file():
        try:
            by_sol = json.loads(idx_path.read_text(encoding="utf-8")).get("by_uid") or {}
        except Exception:
            by_sol = {}
    jsonl = sol_dir / "items.jsonl"
    if jsonl.is_file():
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            uid = row.get("item_uid")
            if uid:
                by_sol[uid] = row
    sol_doc = {"schema": "ttwin.solutions.v1", "n": len(by_sol), "by_uid": by_sol}
    dump(sol_dir / "index.json", sol_doc)
    meta["n_solutions"] = len(by_sol)

    print("writing catalog…")
    dump(OUT / "subjects.json", subjects_doc)
    dump(OUT / "meta.json", meta)
    dump(OUT / "nodes.json", nodes)
    dump(OUT / "projection.json", projection)
    write_enrichment_dir(enrich)
    (OUT / "RECEIPT.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    for name in LEGACY_QUESTION_FILES:
        p = OUT / name
        if p.is_file():
            p.unlink()
            print(f"  removed legacy {name}")

    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
