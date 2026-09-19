# MODIFY_TASK — implementer

Defect to fix: `js/kimi.js` `modifyItem`/`modifySys` sends a thin packet (stem, A–D, statements, equations, tables, tikz) with no hinge, no mx, no enrichment, no mechanism, no LBS, no pack/node labels — and assumes four options and one letter key in the result. That is the brute-force path 83 replaces. Do not write a free-writer over stem + A–D.

## Build

1. **`assembleModifyPacket(item, instruction, S)`** — pure lookup, no model calls:
   - Read the item from the session store: learner-whitelist fields plus the original key (teacher-side).
   - Join `item.hinges.primary` on the already-loaded slim map `S.map`. Hit → BOUND, attach the hinge row (title, ≤8 node labels, mx seeds from the row). Miss → UNBOUND, hinge null. Never fetch `*_MAP.json`.
   - Attach `S.enrichment[unit]` when present. When empty, leave null. Do not pad.
   - Attach the compiled LBS recipe for (unit, mx/step) per `82_LBS_COMPILER.md` when present.
   - Attach the five-click packed tags and the item's modify_seeds.
   - Resolve the spec: variation class from seed metadata or teacher setting (default V1); fidelity (default FAITHFUL_TRANSFER; run the BLOCKED precheck for bridgeless transfers); target_item_type (default preserve); figure mode (default preserve).
   - Apply caps and the deterministic trim order from MODIFY_SPEC; record trimmed fields; stamp join_status and builder name.
2. **Change `modifyItem`** to send the compiled packet. Replace `modifySys` with a thin contract: design the new item inside this bundle; honor variation_class, fidelity_mode, target_item_type, and figure mode; keep learner fields whitelist-clean; return `modify_result.v1` JSON only; return REFUSED when the spec cannot be met. One call. Temperature 1, 4096 tokens, 90 s (`15_SLOTS.md`).
3. **Validate** with gates G1–G8 (MODIFY_SPEC). Pass → write the session item (key UNVERIFIED, CANDIDATE, serve_eligible false, join_status). Fail → keep the original, log the gate id.
4. **Renderer handoff** — the result carries at most one visual; when tikz is present, do not emit a blank-grid table (render audit).

## Hard don'ts

- No per-letter or per-option model calls. One call per modify request.
- No map dump. One hinge row maximum crosses into the packet.
- No fetching full maps in the browser.
- No silent coercion to four-option MCQ. `item_type` changes only via spec.
- No freeze uids. Session references only.
- For Science 6–8 Grok ingest: read `JOURNAL_G68_GROK.md`. Do not copy source LBS. Do not leak mix-up recipes into options. One hinge. Parallel option frames.
- No mx_type, mix-up names, examiner codes, or SMILES-print in learner fields.
- No invented figures. A figure is added only via `spec.figure.mode = add`, TikZ fully specified.
- No claim-ledger or ability writes.
- UI copy says "AI", never a vendor name.

## Acceptance checks

- A multi-correct source (key BC) returns item_type one_or_more with a letter_set; never collapsed to one letter.
- A three-statement source stays three-statement unless the spec says otherwise.
- A Cambridge primary that misses the slim map → join_status UNBOUND; modify still succeeds from tags + seeds; the teacher block names no map title.
- Empty model response → original kept; the packet is unchanged on any retry.
- Instruction "make this open response" → item_type open_response with rubric lines and no letter key.
- Figure rewrite (V5) → exactly one tikz visual; the stem references it; no blank-grid table.
- A maths item with empty enrichment → packet assembles with enrichment null; no padding, no extra fetch.
- A packet with full enrichment + recipe trims in the stated order and stays ≤16000 chars.
