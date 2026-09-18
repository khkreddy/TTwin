# Audit — Four-Pack / Hinge-Join Implementation

**Verdict: APPROVE_WITH_FIXES**

No plan violations found. Owner pin and all four standing defaults are honored in the data. The defects are gatekeeping gaps (provenance, assertion depth, one unverified UI claim), not design errors. Nothing here warrants REJECT.

## What landed — verified faithful

Reconciliation recomputed independently:

```
943 + 60,988 + 23,567 + 822  = 86,320   ✓ exhaustive partition, no orphan/overlap
834 + 109                    = 943      ✓ middle_6_8 internal split
792 + 30                     = 822      ✓ olympiad_iit composition
86,320 − 72,772              = 13,548   ✓ matches stated ~13.5k unbound
72,772 / 86,320              ≈ 84.3%    deterministic hinge coverage
```

- **Packs**: exactly four; `question_bank` dissolved; MathNet held in secondary_9_10 — no bulk route to olympiad (default honored).
- **Science**: subject-level node in middle_6_8, S1–S6 big ideas sourced from science.json, grains as concepts, 109 items ex biology-junior/physics-junior. Matches the owner pin structurally.
- **Vocab**: M4 mislabel corrected ("Euclidean geometry…", not Calculus); M7 calculus correctly excluded from middle_6_8; biology Q1–Q9 with **0 unresolved**; empty physics B-titles not fabricated (default honored).
- **Hinges**: deterministic exact/prefix unit_id join only; `hinges.primary` additive (schema test green); no per-task LLM; remainder explicitly queued for the phase-3 binder.
- **UI**: pack-scoped origin → concept → sub-concept; per-pack lazy nav; legacy pack-id aliases in rag.js.
- **Deferred by design, correctly**: chemistry hinge sentences, enrichment backfill (not a hard gate), JEE chem/phy held in senior pending multi-hinge demand signature, compiler overlay, LLM binder, board layer.

## Defects — must-fix before push

1. **Provenance must travel with the repo.** The four maps stay local, but so does the manifest — that makes every pushed artifact unfalsifiable for anyone else, including future-you. Commit the manifest (sha256 pins) plus a short regeneration note. The maps being withheld is defensible (GitHub size limits); the pins being withheld is not.
2. **Clean-clone gate.** Fresh clone, no local maps, full suite → green. If any test or build step silently reads a withheld map, it must be fixture-backed or explicitly skipped. "Manifest pins locally" is exactly the kind of sentence that hides a broken clone.
3. **Hinge-join assertions are count-only.** 72,772 bound proves volume, not correctness — a wrong-but-present id passes. Add to the test layer: (a) every `hinges.primary` resolves to an existing vocab node id; (b) exactly one primary per question; (c) prefix matching is deterministic longest-prefix-wins with ambiguity count asserted at 0 (the `…:P1` vs `…:P11` collision class). These are one-liners; if any fails, it's a real defect, not a formality.
4. **Owner pin needs UI evidence.** "Science is a subject; teacher picks big idea then concept" is claimed implemented, but no listed test covers it. Produce a screenshot or UI test showing middle_6_8 renders subject (Maths/Science) → big idea (M*/S*) → concept, not a flat origin list. Explicit pins require explicit proof.
5. **Dissolved `question_bank` alias behavior.** Confirm where legacy `question_bank` ids redirect in rag.js, that the target is intentional (not a silent dump into secondary_9_10), and that a warning is logged. User-facing links; verify, don't assume.

## Defects — later (tracked, non-blocking)

- LLM binder for the 13,548 unbound: measure precision on a hand-labeled sample before binding at scale; confirm unbound items stay reachable via existing nav in the interim (API-level retrieval already green).
- LBS compiler overlay re-run: diff lesson output against the pre-hinge baseline and version the result. Until then `hinges.primary` is **latent data** — state that plainly in release notes so nobody assumes hinge-driven lessons are live.
- Enrichment backfill (maths/physics/biology).
- `olympiad_iit` currently maths + AIME only; revisit the pack name when JEE chem/phy land.
- 14MB maths-secondary nav: split per origin, compress, set cache headers; add a request-token guard against pack-switch race (slow-nav-A resolving after nav-B).
- Reserve schema room for multi-hinge (`candidates[]`) before phase 6 to avoid a second migration of 86,320 records.
- Hand-audit ~50 random prefix binds as a sanity layer over assertion 3c.

## Should GitHub ship?

**Yes — after must-fixes 1–4 land and 5 is verified.** All five are cheap; none requires redesign. Be clear-eyed about what origin/main becomes: a derived-artifacts repo for maths, physics, and chemistry, regenerable only with out-of-band data. That is an acceptable posture under GitHub's size constraints **only because** the manifest pins the inputs — which is why fix #1 is a gate, not a nicety. With the gates cleared, the push is faithful to the plan as approved.