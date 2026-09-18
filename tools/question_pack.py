#!/usr/bin/env python3
"""Project exam.v1 items onto ttwin.question.v1 and pack remaining complete rows.

Does not rewrite frozen exam.v1, live maps, or live enrichment.
Learner layout keeps source parts / tables / TikZ. Source free_response → open_response.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

AWM = Path("/home/harik/awm_build")
OUT = ROOT / "data"
CORPUS = AWM / "data/awm_product/generated/exam_v1_corpus/items.jsonl"
CHEM_JOINED = AWM / "data/awm_product/generated/exam_v1_chem_joined/items.jsonl"

ITEM_TYPE_ENUM = (
    "mcq",
    "mcq_diagram",
    "mcq_table",
    "three_statement",
    "structured",
    "open_response",
)
WRITTEN_TYPES = {"structured", "open_response"}
MCQ_FAMILY = {"mcq", "mcq_diagram", "mcq_table", "three_statement"}
NODE_PREFIX = {
    "chemistry": "chem",
    "biology": "bio",
    "physics": "phy",
    "maths": "math",
}
SYL_META = {
    "0620": ("chemistry", "igcse_9_10", "SECONDARY"),
    "9701": ("chemistry", "senior_11_12_as_a", "SENIOR_SECONDARY"),
    "0610": ("biology", "igcse_9_10", "SECONDARY"),
    "9700": ("biology", "senior_11_12_as_a", "SENIOR_SECONDARY"),
    "0625": ("physics", "igcse_9_10", "SECONDARY"),
    "9702": ("physics", "senior_11_12_as_a", "SENIOR_SECONDARY"),
    "0580": ("maths", "igcse_9_10", "SECONDARY"),
    "0606": ("maths", "igcse_9_10", "SECONDARY"),
    "0607": ("maths", "igcse_9_10", "SECONDARY"),
    "9709": ("maths", "senior_11_12_as_a", "SENIOR_SECONDARY"),
    "9231": ("maths", "senior_11_12_as_a", "SENIOR_SECONDARY"),
}
PLACEHOLDER_RE = re.compile(
    r"\[(?:figure|diagram|image|see attached)\]|see attached figure|<<<|TODO|PLACEHOLDER",
    re.I,
)
TOKEN_RE = re.compile(r"[a-z]{3,}")
MIN_TAG_SCORE = 2
MAX_PACK_BYTES = 90 * 1024 * 1024
HELD_JSONL = OUT / "held_questions.jsonl"
HELD_SUMMARY = OUT / "held_questions_summary.json"
PACK_SLUG = {
    "igcse_9_10": "igcse",
    "senior_11_12_as_a": "senior",
    "olympiad_iit": "olympiad",
    "question_bank": "bank",
}
PACK_LABEL = {
    "igcse_9_10": "A · Grades 9–10 / IGCSE",
    "senior_11_12_as_a": "B · Grades 11–12 / AS–A",
    "olympiad_iit": "C · Olympiad / IIT",
    "question_bank": "D · Advanced / extra practice",
}
UNMAPPED = "unmapped"
SUBJECT_ORDER = ["chemistry", "biology", "physics", "maths"]
FIVE_IDS = ("pack", "subject", "node", "chapter_id", "subtopic_id")
NAV_FIELDS = (
    "uid",
    "subject",
    "pack",
    "grade_band",
    "node",
    "chapter_id",
    "chapter_label",
    "subtopic_id",
    "subtopic_label",
    "complete_exam",
    "cam_family",
    "ncert_family",
    "item_type",
)


def map_item_type(raw) -> str | None:
    t = str(raw or "").strip()
    if t == "free_response":
        return "open_response"
    if t in ITEM_TYPE_ENUM:
        return t
    return None


def _tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall((text or "").lower()))


def slim_parts(parts) -> list[dict]:
    out = []
    for p in parts or []:
        if not isinstance(p, dict):
            continue
        sub = []
        for sp in p.get("subparts") or []:
            if not isinstance(sp, dict):
                continue
            sub.append(
                {
                    "id": sp.get("id"),
                    "stem": sp.get("stem") or "",
                    "marks": sp.get("marks"),
                }
            )
        out.append(
            {
                "id": p.get("id"),
                "stem": p.get("stem") or "",
                "marks": p.get("marks"),
                "subparts": sub,
            }
        )
    return out


def _first_written_part(parts) -> dict | None:
    first = None
    for p in parts or []:
        if not isinstance(p, dict):
            continue
        if first is None:
            first = p
        if str(p.get("id") or "").strip():
            return p
    return first


def stem_before_parts(stem: str, parts) -> str:
    """Keep the lead-in only. Packed parts render the (a)/(b) body."""
    text = str(stem or "")
    if not text or not parts:
        return text.strip()
    first = _first_written_part(parts)
    if not first:
        return text.strip()
    cuts: list[int] = []
    pid = str(first.get("id") or "").strip()
    if pid:
        pat = re.compile(
            r"(?:^|\n)(?:[ \t]*\d+[ \t]+)?[ \t]*\(" + re.escape(pid) + r"\)(?:[ \t\n]|\(|$)",
            re.I,
        )
        m = pat.search(text)
        if m:
            cuts.append(m.start())
    body = str(first.get("stem") or "").strip()
    body = re.sub(r"^\([a-z0-9ivx]+\)\s*", "", body, flags=re.I)
    key = body.split("\n", 1)[0].strip()
    if len(key) >= 24:
        idx = text.find(key[:80])
        if idx > 0:
            cuts.append(idx)
    if not cuts:
        return text.strip()
    cut = min(cuts)
    lead = text[:cut].strip()
    lead = re.sub(r"\n\[Total:[^\]]*\]\s*$", "", lead, flags=re.I).strip()
    return lead


def parts_have_text(parts) -> bool:
    for p in parts or []:
        if not isinstance(p, dict):
            continue
        if str(p.get("stem") or "").strip():
            return True
        for sp in p.get("subparts") or []:
            if isinstance(sp, dict) and str(sp.get("stem") or "").strip():
                return True
    return False


def tikz_code(o: dict) -> str:
    fig = o.get("figure") if isinstance(o.get("figure"), dict) else {}
    enc = o.get("encoding") if isinstance(o.get("encoding"), dict) else {}
    for blob in (fig, enc):
        tj = blob.get("tikz") if isinstance(blob.get("tikz"), dict) else None
        if tj and isinstance(tj.get("code"), str) and tj["code"].strip():
            return tj["code"]
        if isinstance(blob.get("tikz"), str) and blob["tikz"].strip():
            return blob["tikz"]
    return ""


def has_compilable_tikz(o: dict) -> bool:
    code = tikz_code(o)
    return "\\begin{tikzpicture}" in code or "\\begin{circuitikz}" in code


def has_smiles(o: dict) -> bool:
    fig = o.get("figure") if isinstance(o.get("figure"), dict) else {}
    enc = o.get("encoding") if isinstance(o.get("encoding"), dict) else {}
    for blob in (fig, enc):
        st = blob.get("structures") or []
        if isinstance(st, list) and any(
            (isinstance(s, dict) and str(s.get("smiles") or "").strip())
            or (isinstance(s, str) and s.strip())
            for s in st
        ):
            return True
        sm = blob.get("smiles")
        if isinstance(sm, str) and sm.strip():
            return True
        if isinstance(sm, list) and any(str(x).strip() for x in sm):
            return True
    return False


def hold_reason(o: dict) -> str | None:
    """Named hold for exam-complete remainder that must not ship."""
    itype = map_item_type(o.get("item_type"))
    if itype is None:
        return "item_type_not_in_schema"
    stem = str(o.get("complete_stem") or o.get("stem_lead") or "").strip()
    if not stem:
        return "empty_stem"
    if PLACEHOLDER_RE.search(stem):
        return "placeholder_in_stem"
    if itype in WRITTEN_TYPES and not parts_have_text(o.get("parts")):
        return "written_parts_empty"
    if o.get("has_drawn_figure") and not has_compilable_tikz(o) and not has_smiles(o):
        return "figure_code_missing"
    return None


def subject_pack_of(uid: str) -> tuple[str, str, str] | None:
    m = re.match(r"^(\d{4})_", uid or "")
    if not m:
        return None
    return SYL_META.get(m.group(1))


def prefix_node(subject: str, node: str) -> str:
    bare = str(node or "").strip()
    if not bare or bare.upper() == "UNRESOLVED":
        return ""
    pref = NODE_PREFIX.get(subject, subject)
    if ":" in bare:
        head, rest = bare.split(":", 1)
        if head in NODE_PREFIX.values():
            return f"{pref}:{rest}" if rest else ""
        return f"{pref}:{bare}"
    return f"{pref}:{bare}"


def project_exam_item(o: dict) -> dict | None:
    """Learner body on ttwin.question.v1. No five-ID tags. No assessment.

    This is the function that writes packed layout fields (stem, parts, tables, tikz).
    """
    from build_data import (  # noqa: WPS433 — shared extractors, avoid import cycle at load
        extract_structures,
        extract_tikz,
        sanitize_item,
        slim_tables,
    )

    itype = map_item_type(o.get("item_type"))
    if itype is None:
        return None
    uid = o.get("item_uid") or o.get("uid") or ""
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
    parts = slim_parts(o.get("parts")) if itype in WRITTEN_TYPES else []
    lead = str(o.get("stem_lead") or "").strip()
    complete = str(o.get("complete_stem") or "").strip()
    if itype in WRITTEN_TYPES:
        stem = stem_before_parts(lead or complete, parts)
    else:
        stem = complete or lead
    rec = {
        "stem": stem,
        "stem_lead": lead or stem,
        "item_type": itype,
        "options": options,
        "statements": stmts,
        "has_figure": bool(o.get("has_drawn_figure") or o.get("options_are_figure")),
        "options_are_figure": bool(o.get("options_are_figure")),
        "equations": [
            (e.get("text") if isinstance(e, dict) else e)
            for e in (o.get("equations") or [])[:8]
        ],
        "tables": slim_tables(o.get("tables")),
        "structures": extract_structures(o),
    }
    if parts:
        rec["parts"] = parts
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
    if not rec.get("structures"):
        rec.pop("structures", None)
    if itype in WRITTEN_TYPES and parts:
        rec["parts"] = parts
        rec["item_type"] = itype
        lead_in = stem_before_parts(rec.get("stem") or rec.get("stem_lead") or stem, parts)
        rec["stem"] = lead_in
        rec["stem_lead"] = lead_in
    return rec


def source_query_text(o: dict, projected: dict | None = None) -> str:
    bits = [
        str(o.get("stem_lead") or ""),
        str(o.get("complete_stem") or "")[:800],
    ]
    for p in o.get("parts") or []:
        if not isinstance(p, dict):
            continue
        bits.append(str(p.get("stem") or ""))
        for sp in p.get("subparts") or []:
            if isinstance(sp, dict):
                bits.append(str(sp.get("stem") or ""))
    if projected:
        bits.append(str(projected.get("stem") or "")[:400])
    return " ".join(bits)


class MapTagger:
    def __init__(self, units_by_subject: dict[str, list[dict]]):
        self.buckets: dict[str, dict[str, list[tuple[set[str], dict]]]] = {}
        self.all_units: dict[str, list[tuple[set[str], dict]]] = {}
        for subject, units in units_by_subject.items():
            by_syl: dict[str, list[tuple[set[str], dict]]] = defaultdict(list)
            all_u: list[tuple[set[str], dict]] = []
            for u in units:
                node = u.get("node")
                if not node or str(node).upper() == "UNRESOLVED":
                    continue
                blob = " ".join(
                    [
                        str(u.get("chapter_title") or ""),
                        str(u.get("decision_hinge") or u.get("statement") or ""),
                        str(u.get("mechanism") or ""),
                    ]
                )
                tok = _tokens(blob)
                if len(tok) < 3:
                    continue
                pair = (tok, u)
                all_u.append(pair)
                uid = str(u.get("unit_id") or "")
                m = re.match(r"^(?:IGCSE|AS_A):(\d{4})\.", uid)
                if m:
                    by_syl[m.group(1)].append(pair)
            self.buckets[subject] = by_syl
            self.all_units[subject] = all_u

    @classmethod
    def from_ttwin_maps(cls, data_dir: Path | None = None) -> "MapTagger":
        root = data_dir or OUT
        by = {}
        for subject in SUBJECT_ORDER:
            path = root / "maps" / f"{subject}.json"
            if not path.is_file():
                by[subject] = []
                continue
            doc = json.loads(path.read_text(encoding="utf-8"))
            by[subject] = list(doc.get("units") or [])
        return cls(by)

    def tag(self, o: dict, projected: dict | None = None) -> dict | None:
        uid = o.get("item_uid") or o.get("uid") or ""
        meta = subject_pack_of(uid)
        if not meta:
            return None
        subject, pack, band = meta
        qtok = _tokens(source_query_text(o, projected))
        if not qtok:
            return None
        syl = uid[:4]
        candidates = self.buckets.get(subject, {}).get(syl) or []
        best, best_n = _best_unit(qtok, candidates)
        if best_n < MIN_TAG_SCORE:
            best2, n2 = _best_unit(qtok, self.all_units.get(subject) or [])
            if n2 > best_n:
                best, best_n = best2, n2
        if best is None or best_n < MIN_TAG_SCORE:
            return None
        node = prefix_node(subject, best.get("node") or "")
        if not node:
            return None
        unit_id = str(best.get("unit_id") or "")
        chapter_label = best.get("chapter_title") or best.get("chapter") or subject
        subtopic_label = (best.get("decision_hinge") or chapter_label)[:80]
        cam_family = None
        ncert_family = None
        chapter_id = unit_id
        subtopic_id = unit_id
        m = re.match(r"^(IGCSE|AS_A):(\d{4})\.(.+)$", unit_id)
        if m:
            topic = str(m.group(3)).split(".")[0]
            chapter_id = f"cam:{m.group(2)}:{topic}"
            subtopic_id = unit_id
            cam_family = chapter_id
        elif unit_id.startswith("science/") or unit_id.startswith("math/"):
            ncert_family = unit_id
            chapter_id = unit_id
            subtopic_id = unit_id
            cam_family = f"cam:{syl}"
        else:
            cam_family = f"cam:{syl}"
        return {
            "uid": uid,
            "subject": subject,
            "pack": pack,
            "grade_band": band,
            "node": node,
            "chapter_id": chapter_id,
            "chapter_label": chapter_label,
            "subtopic_id": subtopic_id,
            "subtopic_label": subtopic_label,
            "complete_exam": True,
            "cam_family": cam_family,
            "ncert_family": ncert_family,
            "item_type": (projected or {}).get("item_type") or map_item_type(o.get("item_type")),
        }


def _best_unit(qtok: set[str], candidates: list[tuple[set[str], dict]]):
    best, best_n = None, 0
    for tok, unit in candidates:
        n = len(qtok & tok)
        if n > best_n:
            best, best_n = unit, n
    return best, best_n


def unmapped_tags(uid: str, subject: str, pack: str, *, item_type: str, bank: str | None = None) -> dict:
    """Fill required five-ID fields without inventing a map node."""
    rec = {
        "uid": uid,
        "subject": subject,
        "pack": pack,
        "grade_band": None,
        "node": UNMAPPED,
        "chapter_id": UNMAPPED,
        "chapter_label": "Unmapped — pending sheaf tag",
        "subtopic_id": UNMAPPED,
        "subtopic_label": "Unmapped — pending sheaf tag",
        "complete_exam": False,
        "cam_family": None,
        "ncert_family": None,
        "item_type": item_type,
    }
    if bank:
        rec["bank"] = bank
    return rec


def compose_item(tags: dict, body: dict, assessment: dict) -> dict:
    item = dict(tags)
    item.update(body)
    item["uid"] = tags["uid"]
    item["subject"] = tags["subject"]
    item["pack"] = tags["pack"]
    item["node"] = tags["node"]
    item["chapter_id"] = tags["chapter_id"]
    item["subtopic_id"] = tags["subtopic_id"]
    item["item_type"] = body.get("item_type") or tags.get("item_type")
    item["complete_exam"] = True
    item["assessment"] = assessment
    return item


def merge_layout(existing: dict, body: dict) -> dict:
    """Keep tags + assessment (including LBS). Restore parts on written items.

    MCQ-family stems/options stay as packed (LBS is keyed to that text).
    """
    out = dict(existing)
    itype = body.get("item_type") or existing.get("item_type")
    if itype:
        out["item_type"] = itype
    if itype in WRITTEN_TYPES:
        for k in (
            "stem",
            "stem_lead",
            "parts",
            "tables",
            "structures",
            "tikz",
            "tikz_packages",
            "equations",
            "statements",
            "has_figure",
        ):
            if k in body:
                out[k] = body[k]
        if not body.get("parts"):
            out.pop("parts", None)
    else:
        out.pop("parts", None)
        for k in ("tables", "structures", "tikz", "tikz_packages"):
            if body.get(k) and not out.get(k):
                out[k] = body[k]
    return out


def nav_from_item(it: dict) -> dict:
    rec = {k: it.get(k) for k in NAV_FIELDS}
    rec["uid"] = it.get("uid") or it.get("item_uid")
    rec["complete_exam"] = bool(it.get("complete_exam", True))
    return rec


def question_relpath(subject: str, pack: str) -> str:
    slug = PACK_SLUG.get(pack, pack.replace("_", "-"))
    return f"questions/{subject}-{slug}.json"


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    path.write_text(text, encoding="utf-8")
    print(f"  {path.relative_to(ROOT)}  {path.stat().st_size:9d} B")


def load_existing_questions() -> dict[str, dict]:
    found: dict[str, dict] = {}
    qdir = OUT / "questions"
    if not qdir.is_dir():
        return found
    for path in sorted(qdir.glob("*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        for it in rows:
            uid = it.get("uid")
            if uid:
                found[uid] = it
    return found


def iter_source_items():
    """chem_joined first (chemistry supersets), then all-subject corpus."""
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


def pack_remaining(*, data_dir: Path | None = None, write: bool = True) -> dict:
    """Re-project existing rows (parts/type) and append remaining exam-complete items."""
    from build_data import assessment_for, load_comment_sha, load_testmaker_assessment, luna_exam_tikz

    out_dir = data_dir or OUT
    tagger = MapTagger.from_ttwin_maps(out_dir)
    print("loading existing TTwin questions…")
    existing = load_existing_questions()
    print(f"  existing {len(existing)}")
    print("loading extracted assessment…")
    tm_assess = load_testmaker_assessment(load_comment_sha())
    print(f"  assessment rows {len(tm_assess)}")

    held: list[dict] = []
    held_n = Counter()
    n_reproject = 0
    n_new = 0
    n_skip_unknown = 0
    considered = set()

    print("streaming exam sources…")
    n_seen = 0
    for o in iter_source_items():
        uid = o.get("item_uid")
        considered.add(uid)
        n_seen += 1
        if n_seen % 5000 == 0:
            print(f"  scanned {n_seen}  new {n_new}  held {len(held)}  reproject {n_reproject}")
        body = project_exam_item(o)
        if uid in existing:
            if body:
                prev = existing[uid]
                luna = luna_exam_tikz(uid)
                if luna and not prev.get("tikz") and not prev.get("figure_src"):
                    body["tikz"] = luna
                    body.pop("tikz_packages", None)
                existing[uid] = merge_layout(prev, body)
                n_reproject += 1
            continue
        if body is None:
            held.append({"uid": uid, "reason": "item_type_not_in_schema"})
            held_n["item_type_not_in_schema"] += 1
            continue
        reason = hold_reason(o)
        if reason:
            held.append(
                {
                    "uid": uid,
                    "reason": reason,
                    "item_type": o.get("item_type"),
                    "subject": (subject_pack_of(uid) or (None, None, None))[0],
                }
            )
            held_n[reason] += 1
            continue
        if not subject_pack_of(uid):
            n_skip_unknown += 1
            held.append({"uid": uid, "reason": "unknown_subject", "item_type": o.get("item_type")})
            held_n["unknown_subject"] += 1
            continue
        tags = tagger.tag(o, body)
        if not tags:
            held.append(
                {
                    "uid": uid,
                    "reason": "untaggable",
                    "item_type": body.get("item_type"),
                    "subject": subject_pack_of(uid)[0],
                }
            )
            held_n["untaggable"] += 1
            continue
        luna = luna_exam_tikz(uid)
        if luna:
            body["tikz"] = luna
            body.pop("tikz_packages", None)
        gold = None
        if isinstance(o.get("options"), dict):
            pass
        existing[uid] = compose_item(tags, body, assessment_for(uid, gold, tm_assess.get(uid)))
        n_new += 1

    print(f"  reprojected {n_reproject}  new {n_new}  held {len(held)}  unknown_skip {n_skip_unknown}")

    by_pack: dict[tuple[str, str], list] = defaultdict(list)
    by_subject: dict[str, list] = defaultdict(list)
    type_counts = Counter()
    n_tikz = n_struct = n_table = n_parts = 0
    n_mcq_key = n_ms = n_ex = 0
    for uid, it in existing.items():
        subj = it.get("subject")
        pack = it.get("pack")
        if subj not in SUBJECT_ORDER or not pack:
            continue
        by_pack[(subj, pack)].append(it)
        by_subject[subj].append(nav_from_item(it))
        type_counts[(subj, it.get("item_type"))] += 1
        if it.get("tikz"):
            n_tikz += 1
        if it.get("structures"):
            n_struct += 1
        if it.get("tables"):
            n_table += 1
        if it.get("parts"):
            n_parts += 1
        a = it.get("assessment") or {}
        if a.get("mcq_key"):
            n_mcq_key += 1
        if a.get("mark_scheme"):
            n_ms += 1
        if (a.get("examiner_comment") or {}).get("present"):
            n_ex += 1

    question_files = []
    catalog_packs: dict[str, list] = defaultdict(list)
    if write:
        (out_dir / "questions").mkdir(parents=True, exist_ok=True)
        (out_dir / "nav").mkdir(parents=True, exist_ok=True)
        for subject in SUBJECT_ORDER:
            for pack in ("igcse_9_10", "senior_11_12_as_a", "olympiad_iit", "question_bank"):
                items = by_pack.get((subject, pack)) or []
                if not items:
                    continue
                items.sort(key=lambda r: r.get("uid") or "")
                rel = question_relpath(subject, pack)
                path = out_dir / rel
                dump_json(path, items)
                if path.stat().st_size > MAX_PACK_BYTES:
                    print(f"  WARNING {rel} exceeds {MAX_PACK_BYTES} bytes")
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
            rows = by_subject.get(subject) or []
            rows.sort(key=lambda r: (r.get("pack") or "", r.get("uid") or ""))
            dump_json(out_dir / "nav" / f"{subject}.json", rows)

        held_path = out_dir / "held_questions.jsonl"
        with held_path.open("w", encoding="utf-8") as fh:
            for row in held:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        summary = {
            "schema": "ttwin.held_questions.v1",
            "n": len(held),
            "by_reason": dict(held_n),
            "n_existing": n_reproject,
            "n_new": n_new,
            "n_packed": len(existing),
        }
        dump_json(out_dir / "held_questions_summary.json", summary)

        _update_catalog(out_dir, catalog_packs, existing, question_files)

    census = {
        "n_packed": len(existing),
        "n_reprojected": n_reproject,
        "n_new": n_new,
        "n_held": len(held),
        "held_by_reason": dict(held_n),
        "by_subject_type": {f"{s}:{t}": n for (s, t), n in sorted(type_counts.items())},
        "n_tikz": n_tikz,
        "n_structures": n_struct,
        "n_tables": n_table,
        "n_with_parts": n_parts,
        "n_mcq_key": n_mcq_key,
        "n_mark_scheme": n_ms,
        "n_examiner_comment": n_ex,
        "question_files": question_files,
    }
    return census


def _update_catalog(
    out_dir: Path,
    catalog_packs: dict[str, list],
    existing: dict[str, dict],
    question_files: list[str],
) -> None:
    subj_path = out_dir / "subjects.json"
    subjects_doc = json.loads(subj_path.read_text(encoding="utf-8")) if subj_path.is_file() else {
        "schema": "ttwin.subjects.v1",
        "default": "chemistry",
        "subjects": [],
    }
    by_id = {s.get("id"): s for s in subjects_doc.get("subjects") or []}
    type_by_subj = Counter()
    for it in existing.values():
        type_by_subj[it.get("subject")] += 1
    for subject in SUBJECT_ORDER:
        rec = by_id.get(subject) or {"id": subject, "label": subject.title()}
        packs = catalog_packs.get(subject) or rec.get("packs") or []
        rec["packs"] = packs
        rec["n_tagged"] = type_by_subj.get(subject, 0)
        rec["n_complete_exam"] = rec["n_tagged"]
        rec["nav"] = f"data/nav/{subject}.json"
        by_id[subject] = rec
    subjects_doc["subjects"] = [by_id[s] for s in SUBJECT_ORDER if s in by_id]
    dump_json(subj_path, subjects_doc)

    meta_path = out_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
    n_tikz = sum(1 for it in existing.values() if it.get("tikz"))
    n_struct = sum(1 for it in existing.values() if it.get("structures"))
    n_table = sum(1 for it in existing.values() if it.get("tables"))
    n_mcq_key = sum(1 for it in existing.values() if (it.get("assessment") or {}).get("mcq_key"))
    n_ms = sum(1 for it in existing.values() if (it.get("assessment") or {}).get("mark_scheme"))
    n_ex = sum(
        1
        for it in existing.values()
        if ((it.get("assessment") or {}).get("examiner_comment") or {}).get("present")
    )
    n_parts = sum(1 for it in existing.values() if it.get("parts"))
    meta["built_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta["n_questions"] = len(existing)
    meta["n_complete_exam"] = len(existing)
    meta["n_stems"] = sum(1 for it in existing.values() if str(it.get("stem") or "").strip())
    meta["n_tikz"] = n_tikz
    meta["n_structures"] = n_struct
    meta["n_tables"] = n_table
    meta["n_mcq_key"] = n_mcq_key
    meta["n_mark_scheme"] = n_ms
    meta["n_examiner_comment"] = n_ex
    meta["n_with_parts"] = n_parts
    meta["question_schema"] = "data/schema/ttwin.question.v1.json"
    by_subject = {}
    for subject in SUBJECT_ORDER:
        rec = by_id.get(subject) or {}
        by_subject[subject] = {
            "n_tagged": rec.get("n_tagged") or 0,
            "n_complete_exam": rec.get("n_complete_exam") or 0,
            "packs": {p["id"]: p["n"] for p in rec.get("packs") or []},
        }
    meta["by_subject"] = by_subject
    files = dict(meta.get("files") or {})
    files["questions"] = question_files
    files["nav"] = [f"data/nav/{s}.json" for s in SUBJECT_ORDER]
    files["held"] = "data/held_questions.jsonl"
    meta["files"] = files
    dump_json(meta_path, meta)


def main() -> int:
    write = "--dry-run" not in sys.argv
    census = pack_remaining(write=write)
    print(json.dumps({k: v for k, v in census.items() if k != "question_files"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
