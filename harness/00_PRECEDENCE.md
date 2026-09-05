# 00 · Precedence and agent load contract

When rules collide, this order wins:

1. **Freeze > overlay.** Frozen exam.v1, ISO-GEN L20, live V15, public NCERT map sha are read-only. Adaptation is overlay at pack time (`tools/learner_display.py`). Session Modify, journal notes, and CANDIDATE ISO-GEN never write a freeze.
2. **Deterministic > AI.** If a join, retrieve, typeset, score, or lookup exists, do not call AI. Empty AI is not a reason to dump more context.
3. **Kernel > persona.** Teacher Model and Student Model are harnesses over one kernel. They must not fork state. One store, one identity grammar, one scoring law, one ledger.
4. **Ledger honesty > engagement.** A claim the evidence cannot support is a defect, not a motivation feature.

## Agent load contract

**May execute**

- Deterministic kernel: assemble, hinge pack, alias parse, seeded shuffle, typeset, score, solution lookup.
- The seven legal slots in `15_SLOTS.md`, packets built only by the kernel packet rules in `40_PACKETS.md`.
- Overlay writes in `journal/`, `session/`, `candidate/` namespaces through kernel paths.
- Banner rendering from `95_STRINGS.md`.

**Must refuse**

- Freeze writes (`11_FREEZE.md`).
- Certifying or ratifying anything the same agent drafted (`owner_ratified` has no agent-writable path).
- Treating detection as remediation.
- Dumping the comprehensive map, a node’s full mx list, wiki pages, or V15 into a prompt.
- Rewriting the map via overlay (C4 OFF). Journal is overlay, not a freeze write.
- Vendor or model names in any public-facing text.
- Frequency claims (“most students…”).
- Presenting a chapter list as a hinge map.
- Filling a zero-mx hinge so the map looks busy.
- New AI entry points not in `15_SLOTS.md`.
- Retry-by-context-dump after an empty AI response.
- Serving dark stores as live papers (`91_DARK.md`).
- Persisting `session/` items into the live pool.
- Calling standalone key-inference as an entry point (folded into T-SOLVE).

**Binding without forking.** Slots bind to the live site’s existing AI functions by the registry in `15_SLOTS.md`. The harness adds no new client. Any amendment is a human-authored edit to `harness/`; an agent may propose, never self-amend.

**Pages vs local**

- GitHub Pages: no secret in the repo, no server write. AI slots light only when a teacher pastes a key in Settings (browser-local) or points a proxy at a local study build. Without a key, every slot fails closed. Deterministic browse / retrieve / typeset / score / stored-analysis lookup still run.
- Local `python3 tools/serve.py`: proxy can hold the key server-side and accept `POST /solution` appends. Keys never enter git.

**Conformance.** This harness signs the design. A different agent or the owner checks the live build against `15_SLOTS.md`. Detection is not remediation.
