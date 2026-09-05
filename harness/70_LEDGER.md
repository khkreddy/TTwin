# 70 · Claim ledger

The profile is a **claim ledger**, not a score sheet. No scalar ability.

## States (per skill / five-ID node)

`UNCALIBRATED` → `EVIDENCED` → `PENDING_DELAY` → `CONFIRMED`

Annotations (not progress): `MISCONCEPTION(named, CANDIDATE)` · `LoK`

Default for every skill: **UNCALIBRATED**.

## Prohibited transitions (kernel, not the agent)

- EVIDENCED → CONFIRMED in the same session (I5).
- Credit on the same `item_uid` twice for mastery (I6).
- Credit on a Modify/ISO-GEN CANDIDATE item (I2).
- Credit without provenance (uid, session, unassisted).
- CONFIRMED from a single MCQ (I4, I15).
- Any progress movement on error events (I20).

## Provenance on every claim

`item_uid`, `session_id`, `utc`, `assisted: false`, `source: scored_paper | correction`, `key_honesty`.

Student data is minimal: pseudonymous id, enrolment, pedagogical events. Queues see needs, not identities.
