# 83 — Modify harness (slot T-MOD)

Additive to 00–82. Nothing here rewrites numbered law, frozen exam.v1, Lamport L20, live V15, or any public map sha. Where this file and older text disagree, the older text stands unless this file names the change. One change is named: the T-MOD packet defined in `15_SLOTS.md` ("one item, learner-whitelist fields + instruction ≤1k") is superseded by the compiled packet `modify_packet.v1` (`harness/modify/MODIFY_SPEC.md`). Slot legality, budgets (temperature 1, 4096 tokens, 90 s), and "invalid → keep original" from 15 are unchanged. This harness drives the live Test-maker Modify option and replaces the thin-packet defect in `js/kimi.js` `modifyItem`/`modifySys` (named, not pasted, in `harness/modify/MODIFY_TASK.md`).

## First principles

1. **Modify is compilation, not rewriting.** The kernel assembles what is known about the item — hinge, mix-ups, enrichment, mechanism, LBS recipe, modify seeds — by lookup. The model's only job is to design the new item inside that bundle. Same pattern as ISO-GEN (`80_ISOGEN.md`: specification before item) and the LBS compiler (`82_LBS_COMPILER.md`: owned intelligence → recipe → instantiate with zero model calls). Modify is ISO-GEN executed on an existing item: P-ITEM-MODIFY-WHOLE.
2. **Deterministic > AI** (`00_PRECEDENCE.md`). The packet builder makes no model calls. If the model returns empty or invalid, keep the original. An empty AI answer is never a reason to enlarge the packet, add map data, or retry with a fatter prompt.
3. **Fail closed.** Every output passes deterministic gates or the session keeps the source item. A model that cannot honor the spec returns REFUSED; that is a clean failure, not license to drift.
4. **Whitelist projection** (`10_KERNEL.md`). The packet is teacher-side. Learner fields of the result carry no mx_type, no mix-up names, no examiner codes, no SMILES-print, no vendor names. mx intelligence enters as teacher-key seeds that shape distractors; it is never printed on a stem.
5. **Session namespace.** Modify runs only before Take (`15_SLOTS.md`). Output lives in the session: key UNVERIFIED, CANDIDATE, serve_eligible false. It never mints a freeze uid and never touches exam.v1. Revert = drop the session entry; the bank item is untouched. T-MOD output is credit-excluded: no claim-ledger entry, no scalar ability write.

## The packet

`modify_packet.v1` carries four blocks:

- **source** — the item's learner-whitelist fields (stem, options, statements, parts, equations, tables, tikz) plus the original key as a teacher-side reference so parameter and inverse-flip variations re-derive honestly.
- **intelligence** — one resolved hinge row from the loaded slim map, five-click packed tags, mx seeds, enrichment, LBS recipe, modify seeds. What is empty stays empty. The builder does not pad.
- **spec** — teacher instruction (≤1000 chars; may be a modify seed), variation class V1–V8, fidelity mode, target item type, figure mode.
- **caps + assembly** — per-field caps tightened from `40_PACKETS.md`, a deterministic trim order, and the join_status stamp.

The map is never dumped into the packet. Only the single resolved hinge row (title, node labels, mx seeds) crosses. The browser never fetches the 70–140 MB `*_MAP.json`.

## Hinge join

`hinges.primary` resolves against the slim map already loaded (S.map). Hit → join_status BOUND. Miss — common for Cambridge `IGCSE:*` primaries against NCERT-slim maps — the builder proceeds from packed tags and modify seeds, stamps join_status UNBOUND, and the model is forbidden from asserting map titles. Fail closed means: still modify, with less intelligence, honestly stamped. Never fetch the full map to rescue a join.

## Formats

Modify preserves `item_type` or changes it only because the spec says so. In scope: single best answer, one-or-more (multi-correct keys such as BC exist and stay honest), three-statement, structured parts, open response, option-table, options-are-figure. Nothing coerces silently to four-option MCQ. The old output schema assumed four options and one letter; that assumption is revoked.

## Figure law

TikZ rewrite is in scope when the instruction or a seed requires it (V5). The render audit rules hold: exactly one visual; no blank-grid table alongside a TikZ figure; figure and stem must reference each other; no invented figure when the source has none unless the teacher asked and the result specifies the TikZ in full. `figure.mode = add` on a figureless source is legal only through explicit spec.

## Variation and fidelity

Variation classes V1–V8 and the fidelity ladder are defined in `isogen/ISO_GENERATION_PROTOCOL.md`; this harness points and does not restate. The compiler picks the class from seed metadata or the teacher's setting (default V1, parameter) — never the model. If a seed demands a transfer with no bridge, the compiler marks fidelity BLOCKED before the model call and returns the original; no tokens are spent on a known-bad transformation. V6 inverse-flip requires re-deriving the key, not copying it.

## Relationship to LBS

When the resolved (unit, mx/step) has a compiled LBS recipe (`82_LBS_COMPILER.md`), it rides in the packet so new distractors stay gate-true: each wrong option still names a gate, the hint stays a simpler question, retry stays the original unaided (I2/I3). Modify never donates the original key into hints and never reprints options as feedback.

## Governance

- CANDIDATE until a human ratifies. serve_eligible false. owner_ratified has no agent-writable path.
- IIT/Olympiad is a demand pack, not a second ontology. Multi-correct keys are declared as sets. The honesty banner stays until keys and stems are verified. No "JEE style" prompt dumps.
- Public UI says "AI". Vendor names appear nowhere user-facing.
- Claim ledger: no entry, no scalar ability, from any T-MOD output.
