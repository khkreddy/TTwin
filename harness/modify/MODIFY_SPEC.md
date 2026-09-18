# MODIFY_SPEC — modify_packet.v1 / modify_result.v1

Contract for slot T-MOD. Law: `harness/83_MODIFY.md`. Schemas: `schema/modify_packet.v1.json`, `schema/modify_result.v1.json`.

## Pipeline

1. Teacher selects one item and gives an instruction (≤1000 chars; may name a modify seed) in Test-maker, before Take.
2. `assembleModifyPacket` builds the packet by lookup only. No model calls.
3. Fidelity precheck: if the requested transfer has no bridge (e.g., a cross-subject seed on a hinge with no cross-subject seed), stamp fidelity BLOCKED and return the original. No model call.
4. One bounded model call: temperature 1, max 4096 tokens, 90 s (`15_SLOTS.md`). The system contract tells the model to design inside the bundle and return `modify_result.v1` JSON only, or REFUSED.
5. Gates G1–G8 run deterministically.
6. Pass → write session item: key UNVERIFIED, CANDIDATE, serve_eligible false, join_status stamped. Fail → keep the original, log the gate id to the session ledger.

At most one identical retry on transport failure. A content failure (empty, invalid, REFUSED) is never retried with a larger packet.

## Packet blocks

### source
Item reference (session-scoped; never a freeze uid), `item_type`, and the learner-whitelist fields: stem, options[], statements[], parts[], equations[], tables[], tikz. Plus `key`: the original proposed key, teacher-side only, never echoed into learner fields or hints.

### intelligence
- `join_status`: BOUND | UNBOUND (below).
- `hinge`: when BOUND — primary, unit_id, title (map title = the vocabulary the teacher sees), up to 8 node labels. When UNBOUND — null. One row crosses; neighbors and adjacency never do.
- `packed_tags`: the five-click tags. Pack is one of middle_6_8, secondary_9_10, senior_11_12, olympiad_iit. Origin never decides pack.
- `mx`: up to 4 mix-up entries (mx_type, name, teacher_note). Teacher-key only. Seeds for distractor design; never printed to learner fields.
- `enrichment`: mechanism/misconception prose, ≤1500 chars. May be null — maths/physics/biology enrichment is currently empty. Null is a fact, not a defect to fix by prompt.
- `lbs_recipe`: the compiled recipe for (unit, mx/step) per `82_LBS_COMPILER.md` when present: gate names, hint skeleton, retry plan. Keeps new distractors gate-true.
- `modify_seeds`: up to 4 owner-authored seeds, ≤500 chars each.

### spec
- `instruction` ≤1000 chars.
- `variation_class`: V1–V8, from seed metadata or the teacher's setting; default V1 (parameter). The model never chooses the class.
- `fidelity_mode`: the ISO-GEN ladder; default FAITHFUL_TRANSFER; the compiler may set BLOCKED pre-call.
- `target_item_type`: preserve | single_mcq | one_or_more | three_statement | structured_parts | open_response | option_table | options_are_figure.
- `format`: n_options (2–6), n_statements (2–5), n_parts (1–8), as the target needs.
- `figure`: mode preserve | rewrite | add | remove; `tikz_required` bool. `add` is legal only when the teacher asked.

### caps + assembly
Caps tighten `40_PACKETS.md` for this slot.

| field | cap |
|---|---|
| stem | 4000 chars |
| options | ≤6 × 1000 chars (+tikz ≤6000 each) |
| statements | ≤5 × 1000 chars |
| parts | ≤8 × 2000 chars |
| equations / tables | ≤6 × 1000 chars each |
| tikz (source or result) | 6000 chars, one visual |
| instruction | 1000 chars |
| hinge title | 240 chars; node labels ≤8 × 120 |
| mx | 4 × (type 60 / name 120 / note 300) |
| enrichment | 1500 chars |
| lbs_recipe | gates ≤6 × 120; hint 500; retry 300 |
| modify_seeds | 4 × 500 chars |
| hard total | 16000 chars |

Trim order when over budget — deterministic, recorded in `assembly.trimmed[]`: enrichment excerpt → lbs_recipe → mx teacher_notes (keep type + name) → node labels. Never trimmed: stem, options/statements/parts, key, instruction, variation class, fidelity mode, figure spec, packed tags. The map is never inlined.

## Result

`modify_result.v1`: `status` OK | REFUSED (+ `refusal_reason`); `item_type`; learner fields (stem, then options/statements/parts as the type requires, equations, tables, tikz — at most one visual); `answer` with `kind`: single_letter | letter_set | statement_pattern | part_answers | rubric; and a `teacher` block: `proposed_key_status` (const UNVERIFIED), `key_rationale` ≤500, `variation_applied`, `fidelity_selfcheck`, `mx_links`, `figure_note`. Cross-field rules live in the gates, not the schema.

## Gates

- **G1 schema** — result parses and validates against `modify_result.v1`.
- **G2 format honesty** — item_type equals spec.target_item_type (or the preserved source type). single_mcq → exactly one letter present in options. one_or_more → a letter_set of ≥2 distinct letters, all present. three_statement → statements present and the key consistent (combo letter, or a T/F pattern of matching length). structured_parts → every part carries an answer line; marks are non-negative integers ≤20 and match any declared total. open_response → rubric lines, no letter key. option_table / options_are_figure → options carry the table or figure payload.
- **G3 figure–stem agreement** — tikz present if and only if stem or parts reference a figure. Exactly one visual. No blank-grid table beside tikz. Source had no figure and mode ≠ add → result has none. mode remove → none.
- **G4 whitelist projection** — learner fields are scanned against packet mx names, mx_types, examiner codes, SMILES-print patterns, vendor names, and the word CANDIDATE. Any hit → fail.
- **G5 no freeze uid** — no exam.v1 uid anywhere; item_ref stays session-scoped. The result never mints one.
- **G6 key existence** — every key letter exists in options; letters distinct; pattern length equals statements length.
- **G7 variation conformance** — `teacher.variation_applied` equals `spec.variation_class`. A model that cannot conform must return REFUSED; silent drift fails.
- **G8 join honesty** — join_status UNBOUND → the teacher block names no map title or hinge. BOUND → learner fields still name none.

Any failure: keep the original, log the gate id. Empty response: keep the original; do not enlarge the packet.

## UNBOUND join path

Cambridge primaries (e.g., `IGCSE:0620.*`) often miss the loaded NCERT-slim map. The builder then: sets join_status UNBOUND, hinge null, keeps packed tags + modify_seeds + whitelist fields, and tells the model the join is unbound. The session item is stamped UNBOUND for later backfill. The browser never fetches `*_MAP.json` (70–140 MB) to rescue a join. UNBOUND is an honest state, not an error.

## Session, revert, ledger

Output lives in the session namespace only. The original item is untouched. Revert drops the session entry. No claim-ledger entry, no scalar ability write. Human ratification flips key status by the existing teacher path; no agent writes owner_ratified.
