# 70 · Claim ledger

The profile is a **claim ledger**, not a score sheet. No scalar ability.

## States (per skill / five-ID node)

`UNCALIBRATED` → `PROGRESS_EVIDENCE` / `EVIDENCED` → `PENDING_DELAY` → `CONFIRMED`

Learn-by-Solving vocabulary above that (DARK until isomorph families exist):

`SESSION_MASTERY` → `FAMILY_MASTERY` → `STABLE_FAMILY_MASTERY@delay` → `COMPOSED_MASTERY` (optional, declared grain)

There is no undifferentiated `LEARNED` boolean. Within-session evidence supports performance claims only.

Annotations (not progress): `MISCONCEPTION(named, CANDIDATE)` · `LoK`

Default for every skill: **UNCALIBRATED**.

TTwin today can warrant exactly one claim: this learner sat this paper and this happened (`PROGRESS_EVIDENCE`).

## Prohibited transitions (kernel, not the agent)

- EVIDENCED / PROGRESS_EVIDENCE → CONFIRMED in the same session (I5).
- Credit on the same `item_uid` twice for mastery (I6).
- Credit on a Modify/ISO-GEN CANDIDATE item (I2).
- Credit without provenance (uid, session, unassisted).
- CONFIRMED / FAMILY_MASTERY from a single MCQ (I4, I15).
- Any progress movement on error events (I20).
- Skip from PROGRESS_EVIDENCE to family mastery.
- Collapse to a scalar ability score.

## Provenance on every claim

`item_uid`, `session_id`, `utc`, `assisted: false`, `source: scored_paper | correction`, `key_honesty`.

Student data is minimal: pseudonymous id, enrolment, pedagogical events. Queues see needs, not identities. C7 real students OFF.

## Parameter annex

Hint-depth thresholds, “repeated failure” counts, re-probe intervals, queue weights, descent depths, and budgets live in a versioned parameter table when those surfaces light. The word “deterministic” applies only where the table defines the behaviour. Until then those parameters are DARK, not silently defaulted in copy.
