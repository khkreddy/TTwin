# Next session — generate questions with the Modify harness

Paste this as the opening user prompt of a **new** session. It is the handoff from 2026-09-18. Do not treat it as already-done work.

---

You are continuing Teacher's Twin (TTwin) after a closed session. Repo: `/home/harik/TTwin`. Live GitHub: `github.com:khkreddy/TTwin` `main`. Last closed SHA was `07ba988` (Modify harness). Confirm `git log -1` before editing; do not assume the tree is still that commit.

**Goal of this session:** use the **Modify harness** to develop **new questions** (ISO-GEN on existing items, and gap-filling CANDIDATEs). Quality comes from compiling hinge intelligence first, then one bounded model call. Do not free-write stems.

## Read first (this order)

1. `harness/CHECKPOINT_2026-09-18.md` — what is true of the corpus and what is not exam-ready.
2. `harness/00_PRECEDENCE.md` then `15_SLOTS.md` then `83_MODIFY.md`.
3. `harness/modify/README.md`, `MODIFY_SPEC.md`, `MODIFY_TASK.md`, schemas in `harness/modify/schema/`.
4. `harness/isogen/ISO_GENERATION_PROTOCOL.md` (spec-before-item, V1–V8, fidelity ladder). Frozen Lamport L20 is not rewritten.
5. `harness/82_LBS_COMPILER.md` — same compile pattern: lookup → packet → instantiate; no per-option LLM on the corpus.
6. Live wiring: `js/kimi.js` `assembleModifyPacket` / `modifyItem`; Test-maker Modify in `js/app.js`.

## First principles (do not violate)

- **Deterministic > AI.** Assemble the packet from maps, packed tags, `hinges.primary`, mx seeds, enrichment, LBS recipe, modify_seeds. Then one model call. Empty AI is not a reason to enlarge the packet or dump a map.
- **Specification before item.** Name the hinge, variation class (V1–V8), fidelity mode, and `item_type` before generating. Modify is P-ITEM-MODIFY-WHOLE, not a stem tweak that leaves stale options.
- **Fail closed.** Gates G1–G8 in `MODIFY_SPEC.md`. Invalid → keep the source. REFUSED is a clean failure.
- **Session / CANDIDATE.** New items are `serve_eligible: false`, key UNVERIFIED. Never mint a freeze uid. Never rewrite `exam.v1`, live V15, or public map sha. Human ratification only.
- **Learner whitelist.** No mx_type, mix-up names, examiner comments, SMILES-print, hinge codes, or vendor names on the stem/options.
- **One visual.** TikZ or exam crop, not both. No blank-grid HTML table beside TikZ (`0620_m15_qp_12:q20` class). Do not invent a figure unless spec.figure.mode is `add` and TikZ is complete.
- **Formats are first-class.** single_mcq, one_or_more (keys like BC), three_statement, structured_parts, open_response, option_table, options_are_figure. Never silently coerce to four-option MCQ.
- **Pack is demand, not origin.** `middle_6_8` | `secondary_9_10` | `senior_11_12` | `olympiad_iit`. MathNet ≠ olympiad. JEE provenance is evidence, never sufficient alone.
- **Teacher sees labels.** Codes (M1, C5, Q3, S2/H-MATERIAL) stay internal. Vocab titles = map titles. Maths M4 is Euclidean geometry, not Calculus.
- Public UI says **AI**, never a vendor name.

## Where the intelligence lives

| Layer | Path | Join |
|---|---|---|
| Packed questions | `data/questions/*.json` (86,320) | `uid`; `hinges.primary` on 72,772 |
| Slim maps (browser) | `data/maps/{chemistry,biology,physics,maths,science}.json` | `units[].unit_id` |
| Final maps (local, do not GitHub 70–140 MB blobs) | `data/maps/{BIOLOGY_MAP,CHEMISTRY_MAP_COMBINED,MATHEMATICS_MAP,PHYSICS_MAP}.json` + `science.json` | statement `unit_id`; biology Q1–Q9 |
| Vocab | `data/vocab/{science,maths,chemistry,physics,biology}.json` | `ideas[].id` + `packs[]` |
| Enrichment | `data/enrichment/chemistry.json` (others empty) | `serves[]` = unit_id |
| LBS overlay | `data/overlay/` | pack-time; do not donate the original key |
| Manifest | `data/maps/MANIFEST.json` | sha256 of final maps |

Cambridge `IGCSE:*` / `AS_A:*` primaries often **miss** the slim NCERT chemistry map. Stamp `join_status: UNBOUND` and still generate from packed tags + seeds. Do not fetch full maps in the Pages client.

Subjects: **Science** only at 6–8 (S1–S6 then grains). From 9+: maths, chemistry, physics, biology.

## How to generate a good item this session

1. Pick a **named gap** (missing figure, unbound hinge with a real stem, mx family with too few items, format the bank lacks at that hinge, teacher instruction).
2. Load the source item. Run `assembleModifyPacket` (or the same lookup in Python). Inspect join_status, mx seeds, enrichment, LBS recipe. If the packet is empty of pedagogy, **do not** ask a model to invent the pedagogy — pick a better source or stop.
3. Write the spec: instruction ≤1000 chars, variation_class, fidelity_mode, target_item_type, figure mode.
4. One model call on that packet (temperature 1). Validate G1–G8.
5. Store as CANDIDATE in a session/candidate namespace, not in live `data/questions/` until the owner ratifies.
6. If TikZ changes: one `tikzpicture`; circuitikz as tikzpicture; no nest; figure and stem must agree.

Kimi K3 Max (`kimi-k3`, temperature **1**, key `/home/harik/raw/cognitive_core/kimi-api.txt`) is the protocol auditor/author used in the last session. Astra (`gpt-6-astra`) was credit-exhausted; do not pretend Grok output is an Astra verdict.

## Do not spend this session on

- Rewriting frozen exam.v1 or Lamport L20.
- Dumping MathNet into olympiad because of origin.
- Bulk LLM on ~21k LBS letters (`lbs_construct` wrappers are legacy).
- Shipping `BIOLOGY_MAP.json` etc. to GitHub (file size).
- Claiming the corpus is exam-ready. It is not: **5,233** `has_figure` with no drawing; **556** option-figures with no drawing; **13,548** unbound hinges; maths/physics/biology enrichment empty.

## Suggested first slice (unless the owner names another)

Start with **BOUND chemistry items** that already have TikZ and a hinge row on the slim map (so the packet is rich). Produce a small CANDIDATE tray (parameter / figure / inverse-flip: V1, V5, V6) across single_mcq and one_or_more. Show the owner the packet + result, not a pile of ungrounded stems. Then expand.

Live site: https://khkreddy.github.io/TTwin/ (GitHub Pages from `main`). Local: `python3 tools/serve.py` → http://127.0.0.1:8766/

---

End of handoff.
