#!/usr/bin/env python3
"""Map leftover unmapped items to a big idea (and grain where possible).

Also strip PDF/OCR junk from learner text. Does not invent map nodes.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from question_pack import OUT, dump_json, nav_from_item, prefix_node  # noqa: E402

CID = re.compile(r"\(cid:\d+\)")
FP = re.compile(r"\s*\[?f\s*p\]?\s*$", re.I)
QDIR = OUT / "questions"


def clean_text(s: str) -> str:
    if not s:
        return s
    t = CID.sub("", s)
    t = t.replace("\u0000", "")
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = FP.sub("", t)
    t = t.replace(" (cid:0)", "").replace("(cid:1)", "")
    t = t.replace("` j", "").replace("ã", "∫")
    return t.strip()


def blob(it: dict) -> str:
    bits = [it.get("stem") or "", it.get("stem_lead") or ""]
    for p in it.get("parts") or []:
        if isinstance(p, dict):
            bits.append(p.get("stem") or "")
            for sp in p.get("subparts") or []:
                if isinstance(sp, dict):
                    bits.append(sp.get("stem") or "")
    return " ".join(bits).lower()


def idea_math(text: str) -> tuple[str, str]:
    t = text
    if re.search(r"partial\s*fraction|d\s*x|integral|∫|differenti|dy/dx|d/dx|ln\s*\d|ascending powers", t):
        return "M7", "Change and accumulation"
    if re.search(r"probab|random variable|\be\s*\(\s*x|var\s*\(|normal distribution|binomial", t):
        return "M8", "Chance and data"
    if re.search(r"position vector|plane p|line l |acute angle between|r\s*=\s*\d", t):
        return "M6", "Vectors and space"
    if re.search(r"m⁻¹|\bmn\b|matrix|inverse", t) or re.search(r"\be\s+[-0-9]", t):
        return "M6", "Matrices"
    if re.search(r"f\s*\(|g\s*\(|gf|f⁻¹|function|parameter", t):
        return "M3", "Functions"
    if re.search(r"triangle|circle|angle|congruent|similar|proof", t):
        return "M4", "Geometry"
    if re.search(r"factoris|factoriz|multiply out|simplify|expand|log\s|inequal|equation", t):
        return "M2", "Algebra"
    if re.search(r"vector|plane", t):
        return "M6", "Vectors and space"
    return "M2", "Algebra"


def idea_chem(text: str) -> tuple[str, str]:
    t = text
    if re.search(r"electrolys|electrode|cell", t):
        return "C5/H-ECHEM", "Electrochemistry"
    if re.search(r"periodic table|isotope|ionisation|ionization|electronic structure|proton", t):
        return "C1", "Atoms and composition"
    if re.search(r"rate of reaction|order reaction|persulfate|catalyst", t):
        return "C7", "Kinetics / rates" if False else "C5"
    if re.search(r"plot|grid|thermometer|measuring cylinder|stop.clock|experiment|graph|best-fit", t):
        return "C5", "Chemical change (practical)"
    if re.search(r"organic|alkene|bromine|chloro|iodoform|enantiomer|ethanol|polymer", t):
        return "C5", "Organic change"
    if re.search(r"acid|salt|crystal", t):
        return "C2", "Bonding and structure"
    return "C5", "Chemical change"


def idea_phy(text: str) -> tuple[str, str]:
    t = text
    if re.search(r"nuclear|fission|fusion", t):
        return "P7", "Atomic and nuclear"
    if re.search(r"magnetic field|earth.s magnetic", t):
        return "P5", "Magnetism"
    if re.search(r"total internal|refract|diffraction|de-broglie|wavelength|lens|glass", t):
        return "P3", "Waves and optics"
    if re.search(r"flux|gauss|dipole|capacit|electrostat|field line|conducting wire", t):
        return "P4", "Electric field and current"
    return "P1", "Mechanics"


def pick_unit(subject: str, node: str) -> dict:
    path = OUT / "maps" / f"{subject}.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    bare = node.split("/")[0]
    for u in doc.get("units") or []:
        n = str(u.get("node") or "")
        if n == node or n.startswith(node + "/") or n == bare:
            return u
    return {"node": node, "unit_id": node, "chapter_title": node, "decision_hinge": ""}


def apply(it: dict, subject: str, node: str, label: str) -> None:
    u = pick_unit(subject, node)
    it["node"] = prefix_node(subject, u.get("node") or node)
    uid = u.get("unit_id") or node
    it["chapter_id"] = uid
    it["chapter_label"] = u.get("chapter_title") or label
    it["subtopic_id"] = uid
    it["subtopic_label"] = (u.get("decision_hinge") or label)[:80]
    it["practice_tier"] = it.get("practice_tier") or ("advanced" if it.get("pack") == "question_bank" else "core")


def clean_item(it: dict) -> bool:
    changed = False
    for k in ("stem", "stem_lead"):
        if isinstance(it.get(k), str):
            c = clean_text(it[k])
            if c != it[k]:
                it[k] = c
                changed = True
    for p in it.get("parts") or []:
        if isinstance(p, dict) and isinstance(p.get("stem"), str):
            c = clean_text(p["stem"])
            if c != p["stem"]:
                p["stem"] = c
                changed = True
        for sp in p.get("subparts") or [] if isinstance(p, dict) else []:
            if isinstance(sp, dict) and isinstance(sp.get("stem"), str):
                c = clean_text(sp["stem"])
                if c != sp["stem"]:
                    sp["stem"] = c
                    changed = True
    return changed


def main() -> int:
    n_map = n_clean = 0
    for path in sorted(QDIR.glob("*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for it in rows:
            if clean_item(it):
                n_clean += 1
                changed = True
            if it.get("node") in (None, "", "unmapped"):
                subj = it.get("subject")
                text = blob(it)
                if subj == "maths":
                    node, lab = idea_math(text)
                elif subj == "chemistry":
                    node, lab = idea_chem(text)
                elif subj == "physics":
                    node, lab = idea_phy(text)
                else:
                    node, lab = "L1", "Living systems"
                apply(it, subj, node, lab)
                n_map += 1
                changed = True
            # dummy chapter_id math:M2 with no real unit → fill label from node
            cid = str(it.get("chapter_id") or "")
            if re.match(r"^math:M\d+$", cid) and not it.get("chapter_label"):
                it["chapter_label"] = cid
                changed = True
        if changed:
            dump_json(path, rows)
            print("wrote", path.name)
    print(json.dumps({"mapped_remaining": n_map, "cleaned": n_clean}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
