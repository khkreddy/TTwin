# 30 · Student Model

The layer that delivers a paper to a learner and records what they did. Instructional invariants live here (`60_INVARIANTS.md`).

## Sees

The learner paper. Their responses. After **Finish**, the score and an IIP-legal evaluability slice per missed item.

## Never sees

Map, mx catalog, enrichment, journal, answer key, seeds, freeze internals, other learners, teacher Modify tools.

## Authority

**No retrieval.** Cannot call `assemble`. Cannot pull extra items. The paper is the paper. Ledger: append own response and feedback events only.

## One legal AI slot

**Feedback after a scored paper.** Packet: scored items + chosen letters + keys + per-miss slice (chemistry: hinge + at most one CANDIDATE mx matched to the chosen distractor; phy/bio/maths: chapter/skill only — mx empty, do not invent).

Must detect, localise, interpret, act **without printing the mix-up ledger**.

No hints during the sitting (I2, I3). No live “Incorrect” coaching that donates the criterion before they finish.

## Take mode (now)

- A–D become select controls; option tables: select a **row**.
- Modify hidden. Answer key hidden.
- Finish → kernel scores → one feedback call → score card.
- Keys: Modify keys if the teacher rewrote the item; else stored analysis; else first-write analysis. Always: **not a published mark scheme**.

## Honesty banners the student may see

- UNCALIBRATED (default until evidence).
- Generated analysis — not a published mark scheme.
- Phy/bio: “this map is a chapter list until a hinge map exists.”
- Maths Pack C / MathNet / Phy-500: do not surface as live papers (0 stems or wrong type).
