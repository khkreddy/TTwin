#!/usr/bin/env python3
"""Relevant vs stamp learn-by-solve. Template banks are not complete."""
from __future__ import annotations

import json
import re
from pathlib import Path

LETTERS = ("A", "B", "C", "D")
THREE = re.compile(
    r"^(?:1\s*,\s*2\s*and\s*3|1,\s*2\s*and\s*3|1 and 2 only|1 and 3 only|2 and 3 only)\s*$",
    re.I,
)
SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉⁻⁺–—", "0123456789-+--")
STOP = {
    "the", "and", "for", "that", "this", "with", "from", "only", "both", "than",
    "into", "over", "then", "when", "what", "which", "does", "are", "was", "not",
}

STAMP_SOLVE = "The keyed choice is"
STAMP_STEM = (
    "What did they drop?",
    "Which description of that error",
    "What kind of boundary error",
    "Which description fits?",
    "What mixed two processes?",
    "A directed relation (cause/effect",
    "Over- or under-extending which cases",
    "Which claim does the item actually require?",
    "Which value is required?",
    "A working that is consistent with this item gives",
    "A student answered as if a different condition held",
    "Which check is required?",
    "Which rule is required?",
    "The stem names a specific species or process",
    "A word or symbol in the stem is easy to spot",
    "A student obtained a different numerical value from the working this item requires",
    "Keep the stem's stated conditions",
    "Match the named species or process; do not swap",
    "Use the operative criterion in the stem, not a salient",
    "This option claims",
    "Is that true for the situation in the stem?",
    "is not what happens here",
    "Does that choice satisfy:",
    "A student chose",
    "match this requirement:",
    "fit this requirement",
    "correctly answer this",
    "A working produced",
    "Which combination of the stem quantities",
)
META_OPTION = (
    "A stated condition that still applies",
    "A directed relation (cause/effect",
    "Keep the stem's stated conditions",
    "Reverse the stated direction",
    "Drop the stated condition and guess",
    "Ignore the stem and pick the longest option",
    "Swap in a neighbouring name from the option list",
    "Ignore names and pick the longest option",
    "Any sibling name is acceptable",
    "Match the most visible word or colour and stop",
    "Surface features override the stated criterion",
    "the stem does not decide between these claims",
    "an unrelated claim not used in this item",
    "is exactly what is required",
    "does not meet that requirement",
    "would be correct only if the stem asked a different question",
    "and every other option are equally valid",
    "Use the definition of that quantity",
    "Average the four listed option values",
    "Invert every quantity in the stem",
    "as given in the stem and stop",
)


def norm(s: str) -> str:
    t = (s or "").translate(SUB).lower()
    t = t.replace("μ", "u").replace("µ", "u")
    return re.sub(r"\s+", " ", t).strip()


def distinctive_tokens(text: str) -> list[str]:
    n = norm(text)
    raw = re.findall(r"[a-z0-9][a-z0-9.%]*", n)
    out = []
    for t in raw:
        if t in STOP:
            continue
        if t.isdigit() and len(t) == 1:
            continue
        if len(t) < 2:
            continue
        out.append(t)
    return out


def is_stamp_lbs(lbs: dict | None) -> bool:
    if not lbs:
        return True
    if STAMP_SOLVE in (lbs.get("solve") or ""):
        return True
    for row in (lbs.get("wrong") or {}).values():
        fu = (row or {}).get("followup") or {}
        stem = fu.get("stem") or ""
        if any(s in stem for s in STAMP_STEM):
            return True
        blob = " ".join((fu.get("options") or {}).values())
        if any(s in blob for s in META_OPTION):
            return True
    return False


def option_text_of(item: dict, letter: str) -> str:
    opts = item.get("options") or {}
    t = str(opts.get(letter) or "").strip()
    if t:
        return t
    for table in item.get("tables") or []:
        if not isinstance(table, dict) or not table.get("is_option_table"):
            continue
        labels = [str(x).strip().upper()[:1] for x in (table.get("row_labels") or [])]
        rows = table.get("rows") or []
        if letter in labels:
            i = labels.index(letter)
            cells = rows[i] if i < len(rows) else []
            return " ".join(str(c) for c in cells).strip()
    return ""


def _figure(item: dict) -> bool:
    return bool(item.get("options_are_figure") and (item.get("figure_src") or item.get("tikz")))


def followup_anchored(item: dict, letter: str, fu_stem: str) -> bool:
    """Follow-up names this option's content (gold/spectra bar)."""
    w = option_text_of(item, letter)
    fu_n = norm(fu_stem)
    if not fu_n:
        return False
    if THREE.match(w) or (w and re.match(r"^[1-4,\s andonly]+$", w, re.I)):
        if "statement" in fu_n or letter.lower() in fu_n:
            return True
    if _figure(item) and not w:
        if letter.lower() in fu_n or f"diagram {letter.lower()}" in fu_n:
            return True
        toks = [t for t in distinctive_tokens(item.get("stem") or item.get("stem_lead") or "") if len(t) >= 3]
        return sum(1 for t in toks[:12] if t in fu_n) >= 1
    toks = distinctive_tokens(w)
    if not toks:
        return letter.lower() in fu_n and len(fu_n) > 12
    hits = sum(1 for t in toks if t in fu_n)
    if hits >= 1:
        return True
    # whole clipped option inside the follow-up
    clip = norm(w)[:48].rstrip()
    return bool(clip) and clip in fu_n


_PRESERVE: set[str] | None = None


def preserve_uids() -> set[str]:
    """Hand-authored gold + spectroscopy. Token-anchor is not applied to these."""
    global _PRESERVE
    if _PRESERVE is not None:
        return _PRESERVE
    out: set[str] = set()
    root = Path(__file__).resolve().parents[1]
    for p in (
        root / "data" / "spectra" / "lbs.json",
        root / "data" / "overlay" / "lbs_gold.json",
    ):
        if not p.is_file():
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        out.update((doc.get("items") or {}).keys())
    shard = root / "data" / "overlay" / "shards"
    if shard.is_dir():
        for p in shard.glob("*.json"):
            try:
                doc = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            out.update((doc.get("items") or {}).keys())
    _PRESERVE = out
    return out


def lbs_relevant(item: dict, lbs: dict | None = None, key: str | None = None) -> bool:
    """Option-specific unlocking bank. Stamps and generic checks fail."""
    a = item.get("assessment") or {}
    key = key or a.get("mcq_key")
    lbs = lbs if lbs is not None else a.get("learn_by_solve")
    if not lbs or key not in LETTERS or is_stamp_lbs(lbs):
        return False
    if str(item.get("uid") or "") in preserve_uids():
        # Hand-authored overlay is the quality bar (formula vs name, IR diagnostics).
        present = [L for L in LETTERS if option_text_of(item, L)] or list(LETTERS)
        if _figure(item):
            present = list(LETTERS)
        expect = set(present) - {key} or (set(LETTERS) - {key})
        wrong = lbs.get("wrong") or {}
        if expect - set(wrong):
            return False
        for L in expect:
            fu = (wrong.get(L) or {}).get("followup") or {}
            if not fu.get("stem") or fu.get("key") not in LETTERS or not (fu.get("options") or {}):
                return False
        return True
    present = [L for L in LETTERS if option_text_of(item, L)] or list(LETTERS)
    if _figure(item):
        present = list(LETTERS)
    expect = set(present) - {key}
    if not expect:
        expect = set(LETTERS) - {key}
    wrong = lbs.get("wrong") or {}
    if expect - set(wrong):
        return False
    stems = []
    for L in expect:
        fu = (wrong.get(L) or {}).get("followup") or {}
        stem = fu.get("stem") or ""
        if not stem or fu.get("key") not in LETTERS:
            return False
        opts = fu.get("options") or {}
        if sum(1 for x in LETTERS if str(opts.get(x) or "").strip()) < 4:
            return False
        if not followup_anchored(item, L, stem):
            return False
        blob = " ".join(str(opts.get(x) or "") for x in LETTERS)
        if any(s in blob for s in META_OPTION):
            return False
        stems.append(norm(stem))
    if len(stems) >= 2 and len(set(stems)) < 2:
        return False
    return True
