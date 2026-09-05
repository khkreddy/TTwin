# 30 · Student Model

The layer that delivers a paper to a learner and records what they did. **Instructional invariants live here** (`60_INVARIANTS.md`). This file is first-class agent law.

The student surface is a paper, a score, and one post-Finish feedback pass. Everything else is DARK or banned.

## Constitution (first principles)

1. **The profile is a claim ledger, not a score sheet.** No scalar “ability” exists anywhere. Default for every skill: UNCALIBRATED.
2. **A warranted learning claim is DIRECTED, EARNED, envelope-indexed, and horizon-tested** — a change in the system’s model of the learner, never a directly observed change in the learner. TTwin today can warrant exactly one claim: *this learner sat this paper and this happened.*
3. **Serving inherits every gate.** Nothing reaches a student that has not passed the protocols behind it.
4. **The student’s data works for the student first** and is minimal: a pseudonymous id, enrolment choices, and pedagogical events. Queues see needs, never identities.
5. **C7 real students are OFF.** Until the owner says otherwise, this model serves the teacher’s “Take as student” dry-run and demo flows only. Learner accounts are not enabled.
6. **TRACE-OR-LABEL** (`05_VISION.md`) applies to every string the student sees.

## Sees

The learner paper (whitelist fields). Their own responses. After **Finish**: the score, honesty banners, stored or first-written analysis shown as a teacher key is **not** on this copy, and one S-FEED feedback pass. Solutions shown post-Finish only by deterministic lookup on the teacher sheet, not on the learner sheet during the sitting.

## Never sees

Map, mx catalog, enrichment, journal, answer key before Finish, seeds, freeze internals, other learners, teacher Modify tools, unlabeled CANDIDATE items (CANDIDATEs are never served live — `serve_eligible: false`), the words “most students”, vendor names, crop paths, printed SMILES, examiner comments.

## Authority

**No retrieval.** Cannot call `assemble`. Cannot pull extra items. Cannot reshuffle. Cannot swap items. The paper is the paper — fixed at seed, mutable only by teacher Modify **before Take begins**. Finish is irrevocable and is the sole gate that lights S-FEED.

Ledger: append own response and feedback events only.

## One legal AI slot — S-FEED

**Feedback after a scored paper.** Packet: scored items + chosen letters/rows + keys + per-miss evaluability slice. **mx and ledger fields are stripped at the builder, not by the prompt.**

Must detect, localise, interpret, act **without printing the mix-up ledger** and **without donating the criterion before Finish**.

No hints during the sitting (I2, I3). No live “Incorrect” coaching that donates the criterion before they finish.

### Evaluability-slice timing (I11–I14)

Slice construction is kernel work, at Finish, never before. Per item: uid, five-ID tags, chosen option/row, key, correct bool, analysis fields (rationale, per-option why) if stored or first-written, else explicit `null`.

| Act | Invariant | Rule |
|---|---|---|
| Detect | I11 | Deterministic correctness per item — a lookup, not a model act. |
| Localise | I12 | Chapter/subtopic via five-ID tags. Chemistry: hinge where the item serves one. Phy/bio: chapter only — “unclassified” is an honest label. |
| Interpret | I13 | Speak from the slice’s per-option why for the option **this student chose**. Chemistry: at most one CANDIDATE mx matched to that distractor, badged unverified, and **not printed as a ledger**. Where analysis is `null`: “No verified notes for this item.” Never invent an interpretation. Phy/bio/maths: Mastery / LoK / unclassified only. |
| Act | I14 | `next_steps` name concrete acts — re-read this chapter, re-attempt a **different** item later, bring item N to your teacher. “Keep practicing” is banned. |

No AI surface exists before Finish. The gate is the Finish event, in code.

## Take mode (now)

- A–D become select controls. Option tables: select a **row**.
- Modify hidden. Answer key hidden. AI dark.
- Finish → kernel scores → one S-FEED call → score card.
- Keys: Modify keys if the teacher rewrote the item (UNVERIFIED); else stored analysis; else first-write analysis (UNVERIFIED). Always: **not a published mark scheme**.
- No-key items are excluded from the denominator with a banner, never silently marked wrong.

## Honesty banners the student may see

- UNCALIBRATED (default until evidence).
- “This feedback was drafted by AI and checked against available notes. It is not a mark scheme.”
- “N of M items had no verified key and were not scored.”
- “This is one paper on one day. It is evidence, not a measure of you.”
- “Generated analysis — not a published mark scheme.”
- Phy/bio: “This map is a chapter list until a hinge map exists.” / “Detailed topic wiring for this subject is in preparation.”
- Maths Pack C / MathNet / Phy-500: do not surface as live papers (0 stems or wrong type). If browsed as metadata: “Additional mathematics items are in preparation.”

## Claim ledger (student-facing)

States: `UNCALIBRATED` (default) → `PROGRESS_EVIDENCE` (the only transition ENFORCE NOW: one finished paper = one event) → `SESSION_MASTERY` → `FAMILY_MASTERY` → `STABLE_FAMILY_MASTERY@delay`.

The last three are **DARK** — isomorph families do not exist on TTwin. With families DARK, no mastery claims at all.

Prohibited transitions (kernel, not the agent):

- Any mastery claim from the same `item_uid` (I6).
- `PROGRESS_EVIDENCE` → family skip.
- Collapse to a scalar ability score.
- Undifferentiated `LEARNED` boolean.
- Any ledger advance on an error event (I20).
- Credit on a Modify/ISO-GEN CANDIDATE item (I2).
- Same-session ceiling above `PROGRESS_EVIDENCE` / `EVIDENCED` (I5).

Provenance on every claim: `item_uid`, `session_id`, `utc`, `assisted: false`, `source: scored_paper | correction`, `key_honesty`.

## Profile pins

**ENFORCE NOW.** Pseudonymous id. Enrolment + pedagogical events as the only data. Events → fold → state. Default UNCALIBRATED. No scalar ability. Serving inherits every gate. Guardian consent and erasure designed in (crypto-shredding compatible with the append-only log). C7 OFF.

**DARK.** Baseline prerequisite frontier. Delayed re-probe scheduler. Constructed-response grading. Profile-driven assembly. LADDER / TRAP / STRUCTURE. Do not simulate them with copy.

## What the student is for

A sitting that cannot lie about learning: unaided, scored, localised, and honest about what the evidence cannot yet support. AI is a post-score tutor of **this paper**, using **this corpus**, not a companion and not a grade.
