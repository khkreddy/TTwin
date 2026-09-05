# 20 · Teacher Model

A working copy of how the teacher thinks: retrieve, brief, cut a paper, modify an item, journal. Mix-ups stay on this side of the glass.

## Sees

Map (chemistry hinges; phy/bio chapter list), CANDIDATE mx, enrichment, journal overlay, answer key, solution analysis, seeds, ledger.

## Writes

Journal (teacher-authored only). Session Modify (not the freeze). CANDIDATE ISO-GEN tray (local). First-write solution analysis into overlay / `POST /solution` when local.

AI **never** writes the journal.

## Four legal AI slots

| Slot | When | Packet | Output |
|---|---|---|---|
| Fuzzy intent | Alias compile fails | Closed node list + teacher prompt | Selector JSON or one clarifying ask |
| ISO-GEN / Modify | Teacher asks for a new or changed item | `hinge_pack` + source item (Modify) | CANDIDATE MCQ; session-only for Modify; not live pool |
| First-write solution analysis | Assemble hits unknown `item_uid×sha` | Stem + options + capped map slice | Key + distractor notes; label: not a published mark scheme |
| Lesson prose | Teacher toggles AI on a built digest | Same digest already typeset | Zinsser prose; no fact outside the packet |

## Operating loop

1. Try deterministic alias retrieve. If fuzzy, AI restates; teacher confirms; `assemble` runs. AI never emits item rows.
2. Every synthesis call gets `hinge_pack(unit_id)` or a capped map slice. Nothing else. Truncate and log on overflow.
3. Lesson: typeset digest first; optional prose over the identical packet. Short sentences. One obligation per paragraph. Teacher copy may name CANDIDATE mx. Learner copy must not.
4. Modify: whole item (stem + A–D + figure if needed). Credit-excluded. Revert restores packed item.
5. ISO-GEN: frozen L20 engine is not rewritten. Promotion to the live pool is a human protocol.
6. Solution analysis: write once, RAG thereafter.
7. Diagnosis: three-state only (`90_DIAGNOSIS.md`). Never a scalar ability. Never “most students…”.

## Zinsser law (lesson prose)

Concrete verbs. No clutter. Use the hinge, the supplied mx (marked unverified), enrichment citations as given (null URL stays null), and journal as the teacher’s prior — not as publication.
