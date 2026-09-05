# 20 · Teacher Model

A working copy of how the teacher thinks: retrieve, brief, cut a paper, modify an item, journal. Mix-ups stay on this side of the glass.

This file is **first-class agent law**. Slots: `15_SLOTS.md`. Kernel: `10_KERNEL.md`.

## Sees

Map (chemistry hinges; phy/bio chapter list), CANDIDATE mx (chemistry only, always labeled unverified), enrichment, journal overlay, answer key, solution analysis, seeds, ledger, CANDIDATE ISO-GEN tray.

## Never sees

A learner-rendered paper carrying banned fields (the kernel prevents it). Frequency statistics over mix-ups. Any CANDIDATE without its label. Real-student identities (C7 OFF). Dark stores presented as live papers.

## Writes

- Journal overlay entries — **body is teacher-authored always**. AI never writes the note.
- Session overlays via Modify (`session/` namespace).
- First-write solution analyses via T-SOLVE (write-once).
- CANDIDATE ISO-GEN tray (local). Flags `serve_eligible: false` and `owner_ratified: false` are set by the kernel, not by the model.

AI **never** writes the journal body. Promotion of a CANDIDATE into the live pool is a **human** protocol. The agent that drafted a CANDIDATE cannot ratify it.

## Six legal AI slots

| Slot | When | Packet | Output |
|---|---|---|---|
| T-SEL | Alias compile fails or is ambiguous | Closed node list + teacher prompt | Selector JSON or one clarifying ask |
| T-UNIT | ISO-GEN idea, or journal note bind | Closed unit list (chem hinges / phy/bio chapters) | Restated intent + 1 unit (ISO) or 1–4 bindings (journal) |
| T-AUTHOR | Teacher asks for a new item after T-UNIT | `hinge_pack` or syllabus chapter with `mx: []` | One CANDIDATE MCQ; not live pool |
| T-MOD | Teacher asks to change an assembled item | Source item (whitelist fields) + instruction | Whole item, session-only, key UNVERIFIED |
| T-SOLVE | Assemble hits unknown `item_uid × sha` | Stem + options + capped map slice | Key + distractor notes; not a published mark scheme |
| T-BRIEF | Teacher toggles AI on a built digest | Same digest already typeset | Zinsser prose; no fact outside the packet |

## Operating loop

1. **Intent.** Try deterministic alias retrieve. If it resolves, stop — no AI. If fuzzy, T-SEL restates against the closed node list; the teacher confirms; `assemble` runs. AI never emits item rows and never fires a guess silently.
2. **Assemble.** Kernel only. Whitelisted stores. `provider_calls: 0`.
3. **Preview.** Kernel typesets the learner overlay. The teacher previews **exactly** what a learner would see. If a banned field is visible, that is a kernel defect, not a prompt defect.
4. **Lesson.** Typeset the digest first (map + enrichment + journal overlay). T-BRIEF is an optional pass over the identical packet. Packs render regardless; prose failure removes nothing.
5. **Journal.** Teacher writes the note. T-UNIT (k≤4) suggests bindings. Teacher confirms. Overlay write. Never a freeze write. Bindings are CANDIDATE until saved.
6. **ISO-GEN.** Specification before item. Teacher states an idea in ordinary language — not a hinge code. T-UNIT (k=1) grounds it; teacher confirms the spec; T-AUTHOR drafts one CANDIDATE. Frozen L20 is not rewritten. New work is a new run id.
7. **Modify.** Whole item (stem + all four options; TikZ only if the change needs it). Text-only items included. Credit-excluded. Revert restores the packed item. Session ends → the variant ceases to exist.
8. **Paper.** Seeded shuffle. Paper is fixed from this moment. Modify is the only mutation, and only before Take begins.
9. **Solution analysis.** Lookup first. Absent → T-SOLVE first-write, write-once at `uid × sha256`, labeled *generated analysis — not a published mark scheme*. Still nothing → unscorable banner. Never regenerate on cache hit.
10. **Diagnosis.** Three-state only (`90_DIAGNOSIS.md`). Never a scalar ability. Never “most students…”.

## Zinsser law (T-BRIEF and all teacher prose)

Short sentences. Concrete verbs. No clutter, no throat-clearing, no jargon for its own sake. One obligation per paragraph. Every claim traceable to pack content. No “research shows”. No frequency claims about students. If a sentence cannot point at a pack line, it is cut.

Use the hinge, the supplied mx (marked unverified), enrichment citations as given (null URL stays null), and journal as the teacher’s prior — not as publication.

Teacher copy may name CANDIDATE mx. Learner copy must not.

## Journal law

Overlay, not freeze. Body is teacher-authored; AI binds only. A journal note changes no map sha. Mapped notes reappear on the matching lesson and go into the T-BRIEF pack.

## ISO-GEN and Modify law

See `80_ISOGEN.md`. Short form:

- L20 stays frozen at 20 CANDIDATE.
- New drafts join the candidate namespace, never the live pool.
- `owner_ratified` has no agent-writable path.
- Modify = ISO-GEN on the whole item. Recalculate the key. Stamp UNVERIFIED. Session-only.
- Olympiad / JEE / MathNet / Phy-500 generation stays bannered until those banks have stems and structured options on TTwin.

## Mix-ups without printing them

The teacher uses mix-ups in planning and diagnosis — as CANDIDATE, unverified, no counts. The learner paper is built from the whitelist only. There is no code path from the ledger to the learner copy. S-FEED’s packet has mx fields stripped at the builder. Bans are enforced in code, not in prompts.

Phy/bio: mx is empty. T-AUTHOR’s interim packet carries the explicit `mx: []` marker so the absence is visible. Do not invent a mix-up ledger. Zero admitted mx on a chemistry hinge is a census outcome, not a gap to fill.

## What the teacher is for

High-quality focused support using the corpus already on the system: the right hinge pack, the right paper, a CANDIDATE item when the bank has a hole, a first-write analysis when no mark scheme exists, a briefing the teacher can act on in twenty minutes. Not a second author of the map. Not a publisher of mark schemes. Not a source of classroom-frequency claims.
