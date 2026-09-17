#!/usr/bin/env python3
"""Relevant vs stamp learn-by-solve. Template banks are not complete."""
from __future__ import annotations

import json
import re
from pathlib import Path

LETTERS = ("A", "B", "C", "D")
FU_FORMATS = (
    "single_mcq",
    "true_false",
    "multi_mcq",
    "assertion_reason",
    "match",
    "fill_blank",
)
AR_DEFAULT = {
    "A": "Both A and R are true, and R is the correct explanation of A",
    "B": "Both A and R are true, but R is not the correct explanation of A",
    "C": "A is true, but R is false",
    "D": "A is false, but R is true",
}
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
    "what this question is asking for",
    "is what the stem asks for",
    "is not what the stem asks for",
    "Which operation on the stem data",
    "is a distractor. Which operation",
    "What is true of",
    "in the situation the stem describes",
    "does not hold for the situation described",
    # Owner-rejected reprints (9701_m17_qp_12:q33, 9701_m18_qp_12:q18). Never reuse.
    "belongs in the correct 1 / 2 / 3 combination",
    "belongs in the correct combination",
    "What oxidation number should that species actually have here",
    "Option C is “2 and 3 only are correct”",
    "Option A is “1, 2 and 3 are correct”",
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
    "is what the stem asks for",
    "is not what the stem asks for",
    "what the stem asks for",
    "the product, quotient, difference or weighted mean named in the stem",
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


# Wrapper SHAPE — restating the original MCQ as the criterion. Not a synonym list.
_WRAPPER_STEM = re.compile(
    r"\bthe stem (asks|ask|describes|describe|requires|require|does not|is asking)|"
    r"\bby the stem\b|"
    r"what the stem\b|"
    r"\bthis question\b|"
    r"asking for|"
    r"the situation.{0,60}describ|"
    r"what is true of|"
    r"\bholds for\b|"
    r"apply here|"
    r"regarding .{0,120}does that|"
    r"does that description apply|"
    r"in the situation the stem",
    re.I,
)
_WRAPPER_OPT = re.compile(
    r"does not hold for|"
    r"does not hold here|"
    r"fully holds|"
    r"is what .{0,40}asks|"
    r"is not what .{0,40}asks|"
    r"apply here|"
    r"not determined by the stem|"
    r"the stem asks|"
    r"the situation described|"
    r"does not hold for the situation|"
    r"it does not apply here|"
    r"does not apply here",
    re.I,
)


def _without_quotes(s: str) -> str:
    t = re.sub(r"[“”\"].*?[“”\"]", " ", s or "", flags=re.S)
    t = re.sub(r"‘.*?’", " ", t)
    return t


def is_wrapper_shape(stem: str, options: dict | None = None) -> bool:
    body = _without_quotes(stem or "")
    if _WRAPPER_STEM.search(body):
        return True
    blob = _without_quotes(" ".join((options or {}).values()))
    if _WRAPPER_OPT.search(blob) or _WRAPPER_STEM.search(blob):
        return True
    return False


def is_stamp_lbs(lbs: dict | None) -> bool:
    if not lbs:
        return True
    if STAMP_SOLVE in (lbs.get("solve") or ""):
        return True
    for row in (lbs.get("wrong") or {}).values():
        fu = (row or {}).get("followup") or {}
        stem = followup_anchor_text(fu)
        opts = fu.get("options") or {}
        if any(s in stem for s in STAMP_STEM):
            return True
        blob = followup_text_blob(fu)
        if any(s in blob for s in META_OPTION):
            return True
        if is_wrapper_shape(stem, opts):
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


def tf_key(key) -> str | None:
    u = str(key or "").strip().upper()
    if u in ("T", "TRUE", "YES"):
        return "T"
    if u in ("F", "FALSE", "NO"):
        return "F"
    return None


def followup_anchor_text(fu: dict | None) -> str:
    fu = fu or {}
    parts = [fu.get("stem") or "", fu.get("assertion") or "", fu.get("reason") or ""]
    parts.extend(str(v) for v in (fu.get("left") or {}).values())
    return " ".join(parts)


def followup_text_blob(fu: dict | None) -> str:
    fu = fu or {}
    parts = [followup_anchor_text(fu)]
    parts.extend(str(v) for v in (fu.get("options") or {}).values())
    parts.extend(str(v) for v in (fu.get("right") or {}).values())
    parts.extend(str(t) for t in (fu.get("terms") or []))
    return " ".join(parts)


def followup_ok(fu: dict | None) -> bool:
    """Shape check for a hint of any admitted format. Does not score chemistry."""
    if not isinstance(fu, dict):
        return False
    stem = str(fu.get("stem") or "").strip()
    if not stem:
        return False
    why = str(fu.get("why") or "")
    low = why.lower()
    if "the key is" in low or "original question" in low:
        return False
    fmt = fu.get("format") or "single_mcq"
    if fmt not in FU_FORMATS:
        return False
    key = fu.get("key")
    if fmt == "single_mcq":
        opts = fu.get("options") or {}
        if key not in LETTERS:
            return False
        return sum(1 for x in LETTERS if str(opts.get(x) or "").strip()) >= 4
    if fmt == "true_false":
        k = tf_key(key)
        if k not in ("T", "F"):
            return False
        opts = fu.get("options") or {}
        if not opts:
            return True
        keys = {str(x).strip().upper() for x in opts}
        return bool(keys & {"T", "TRUE", "F", "FALSE", "A", "B"})
    if fmt == "assertion_reason":
        if not str(fu.get("assertion") or "").strip() or not str(fu.get("reason") or "").strip():
            return False
        opts = fu.get("options") or AR_DEFAULT
        if key not in LETTERS:
            return False
        return sum(1 for x in LETTERS if str(opts.get(x) or "").strip()) >= 2
    if fmt == "multi_mcq":
        opts = fu.get("options") or {}
        keys = key if isinstance(key, (list, tuple)) else [key]
        keys = [str(k) for k in keys if k is not None and str(k).strip() != ""]
        if not keys or len(opts) < 2:
            return False
        return all(k in opts for k in keys) and all(str(opts.get(k) or "").strip() for k in keys)
    if fmt == "match":
        left = fu.get("left") or {}
        right = fu.get("right") or {}
        km = key if isinstance(key, dict) else {}
        if len(left) < 2 or len(right) < 2 or not isinstance(km, dict):
            return False
        return all(str(left[i]).strip() and km.get(i) in right for i in left)
    if fmt == "fill_blank":
        terms = [str(t) for t in (fu.get("terms") or []) if str(t).strip()]
        if len(terms) < 2:
            return False
        ids = re.findall(r"\[\[(\w+)\]\]", stem)
        if not ids:
            return False
        km = key if isinstance(key, dict) else {"1": str(key or "")}
        if not isinstance(km, dict):
            return False
        return all(i in km and str(km[i]) in terms for i in ids)
    return False


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
    paths = [
        root / "data" / "spectra" / "lbs.json",
        root / "data" / "overlay" / "lbs_electrochem.json",
        root / "data" / "overlay" / "lbs_gold.json",
    ]
    astra = root / "data" / "overlay" / "astra"
    if astra.is_dir():
        paths.extend(sorted(astra.glob("*.json")))
    for p in paths:
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
            if not followup_ok(fu):
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
        if not followup_ok(fu):
            return False
        stem = followup_anchor_text(fu)
        if not followup_anchored(item, L, stem):
            return False
        blob = followup_text_blob(fu)
        if any(s in blob for s in META_OPTION):
            return False
        stems.append(norm(stem))
    if len(stems) >= 2 and len(set(stems)) < 2:
        return False
    return True
