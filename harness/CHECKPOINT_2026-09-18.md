# Checkpoint 2026-09-18

What TTwin is at this date, what works, and what is not ready. Plain state; no claims beyond it.

## Shape

TTwin is a teacher-side twin: demand-driven packs, sheaf-mapped syllabus data, pedagogical intelligence per hinge, compiled generation and feedback. Frozen exam.v1 (Lamport L20) and live V15 stand. Public map sha unchanged.

## Demand packs

Four packs: middle_6_8, secondary_9_10, senior_11_12, olympiad_iit. Origin does not decide pack; demand does. Subjects: Science for grades 6–8 (units S1–S6); maths, chemistry, physics, biology from grade 9 up.

## Maps and vocabulary

Final maps are local authority (only science.json is on GitHub): BIOLOGY_MAP Q1–Q9, CHEMISTRY_MAP_COMBINED, MATHEMATICS_MAP M1–M8, PHYSICS_MAP, science.json. Vocabulary titles equal map titles; teachers see labels, not codes. The browser loads slim maps (chemistry slim: 523 NCERT hinges). Full maps run 70–140 MB and never ship to Pages.

## Hinge join

72,772 of 86,320 items carry `hinges.primary` (Cambridge/chapter unit_id). The remaining 13,548 are unbound. Cambridge `IGCSE:*` primaries often miss the slim NCERT maps. Policy everywhere, including the new Modify harness: fail closed, proceed from packed tags and seeds, stamp UNBOUND, backfill later. Never fetch a full map in the browser to rescue a join.

## Renderer

One visual per item. Blank-grid tables are skipped when TikZ exists. Known gap: 5,233 items carry has_figure with no drawing. The corpus is not exam-ready on figures.

## Generation and feedback

ISO-GEN (`80_ISOGEN.md`, `isogen/ISO_GENERATION_PROTOCOL.md`): specification before item; variation classes V1–V8; fidelity ladder FAITHFUL_TRANSFER … BLOCKED; CANDIDATE lifecycle. LBS compiler (`82_LBS_COMPILER.md`): owned intelligence → snapshot/index → recipe per (unit, mx/step) → instantiate with zero model calls per item. Wrong options name gates; hints are simpler questions; retry is the original unaided. `tools/lbs_construct.py` wrappers are legacy. Both are packaged as law and protocol.

## Modify harness (added at this checkpoint)

`harness/83_MODIFY.md` plus `harness/modify/` (spec, task, two schemas). T-MOD now sends a compiled `modify_packet.v1`: the source item (whitelist fields + teacher-side key), one resolved hinge row, packed tags, mx seeds, enrichment, LBS recipe, modify seeds, and a spec (instruction, variation class, fidelity mode, target item type, figure mode). Capped at 16,000 chars; the map is never dumped. One bounded model call, then gates G1–G8. Pass writes a session item (key UNVERIFIED, CANDIDATE, serve_eligible false); fail keeps the original. Formats beyond four-option MCQ are first-class: one-or-more (multi-correct keys such as BC), three-statement, structured parts, open response, option-table, options-are-figure. Figure rewrite is in scope via spec; one visual; no invented figures. Status: law and contract landed; the `js/kimi.js` wiring is the open implementer task (`MODIFY_TASK.md`).

## Not exam-ready yet

- **Figures**: 5,233 items reference a figure that has no drawing.
- **LBS quality**: recipes compile; classroom quality is unproven.
- **Unbound hinges**: 13,548 items without a resolved primary.
- **Enrichment**: empty for maths, physics, biology; present mainly in chemistry/science. Empty fields stay empty; packets do not pad.
- **IIT/Olympiad**: multi-correct keys exist (e.g., BC); the honesty banner stays until keys and stems are verified.
- **Modify wiring**: `assembleModifyPacket` is live in `js/kimi.js`; T-MOD sends `modify_packet.v1`. Gate fail keeps the original. Full G1–G8 coverage and format-change acceptance checks are still thin.

## Governance state

CANDIDATE until human ratification; owner_ratified has no agent-writable path. Claim ledger only; no scalar ability. C7 real students OFF. The UI says "AI".
