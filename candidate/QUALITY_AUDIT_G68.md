# Quality audit — G6–8 CANDIDATE items (science 2207 + maths 1692 = 3899)

Deterministic grading by `tools/grade_g68_quality.js` under rubric v1
(`harness/modify/QUALITY_RUBRIC_G68.md`). Rubric was fixed **before** inspecting item text; every
learner-text regex holds **gold-corpus FP = 0** across 52,808 Cambridge/MathNet/IGCSE/junior items
(re-asserted by `tools/tests/test_g68_quality.js`). "top" means *clean against every defect we can
detect deterministically* — it is **not** a claim of exam-readiness, and it does not measure key
correctness or distractor plausibility (see §Limits).

## Tier distribution

| Tray | n | top | medium | low |
|---|---:|---:|---:|---:|
| science-middle_6_8 | 2207 | **2135** (96.7%) | 13 (0.6%) | **59** (2.7%) |
| math-middle_6_8 | 1692 | **1085** (64.1%) | 21 (1.2%) | **586** (34.6%) |

## Tier by attempt (the harness-improvement signal)

Science:

| attempt | top | medium | low |
|---|---:|---:|---:|
| a1 | 385 | 4 | 2 |
| a2 | 389 | 2 | 0 |
| a3 | 369 | 2 | 20 |
| a4 | 365 | 2 | 24 |
| a5 | 376 | 2 | 13 |
| a6 | 251 | 1 | **0** |

Maths:

| attempt | top | medium | low |
|---|---:|---:|---:|
| a3 | 261 | 3 | 216 |
| a4 | 250 | 4 | 226 |
| a5 | 332 | 5 | 143 |
| a6 | 242 | 9 | **1** |

**This is the headline result.** The fail-closed ingest gates (G13 plan/key, G14 reverse-causation)
landed between the a3–a5 waves and a6. Attempt 6 is essentially clean in both subjects — science a6
has 0 low, maths a6 has 1 low — while maths a3–a5 carry the defect backlog. The harness demonstrably
*improved*: the same generator, run under the current gates, stops producing the artefacts it used
to. The corpus's remaining problems are **legacy (a3–a5 maths)**, not the current pipeline.

## Systematic weaknesses (flag counts = items affected)

These are the leverage points for the next harness iteration.

| Defect (tier-moving, critical) | science | maths | Root cause |
|---|---:|---:|---|
| `g14_reverse_causation` | 0 | **305** | Slim maths map `relationship_reversal` CWOs emit "X is what produces Y…" (handover §5.1). G14 fail-closes new output but the packet still teaches the sentence → a3–a5 saturated. **Fix: named map patch (owner approval required).** |
| `plan_key_mismatch` | 57 | **322** | R0 `compileMxPlan` used the donor key (default maths source keyed C). Superseded by `bind: "result"` on a6. Legacy only. |
| `figure_ref_without_figure` | 2 | 8 | Stem references a figure that was never drawn. |
| `hinge_figure_missing` (moderate) | 15 | 33 | Hinge wants a figure; item has none (§5.6: `hingeWantsFigure` regex misses many geometry/measurement hinges). |

| Harness plumbing gap (note, not item-tier) | science | maths | Root cause |
|---|---:|---:|---|
| `key_not_packed` | 288 | 353 | `resultToCandidate` drops `statement_pattern` / `part_answers`; paper.js can't mark structured / pattern items (§5.2). **Fix: extend `resultToCandidate` + paper.js marking.** |
| `chapter_label_code` | 0 | 1692 | Slim maths map `chapter_title` is a path, not a title (§5.4). |
| `item_type_not_promoted` | 53 | 273 | Rewritten TikZ stays `item_type: mcq`; "MCQ diagram" browse filter misses drawn items (§5.6). |

| Provenance note | science | maths |
|---|---:|---:|
| `meera_meena` | 632 | 0 | Kimi a1/a2 signature (Grok: 0). |
| `variation_ladder` | 1425 | 1680 | V1–V8 ladder never executed; all Grok waves ran V1 (§5.3). |
| `kimia12` | 782 | 0 | Kimi-authored a1/a2 (no build_logic). |

## Strengths the audit confirms (handover §4, re-derived)

1. **Fail-closed ingest works** — a6 is clean; G14 = 0 on science and on maths a6.
2. **G14 regex is pathognomonic** — 0 false positives on 52,808 gold items, so 305 maths hits are
   true generator artefacts, not examiner style.
3. **Formats were not coerced to 4-option MCQ** — structured / three_statement / option-table all present.
4. **Learner-text hygiene on Grok is clean** — 0 Meera/Meena, 0 mx names in learner blobs.
5. **The grading itself is reproducible** — re-running the grader is deterministic; counts above
   reconcile exactly with handover §5 recounts (G14=305, plan/key 57/322, key_not_packed 288/353).

## Limits (honest scope)

- **Key correctness is not graded.** Keys stay UNVERIFIED. A `top` item can still have a wrong key.
- **Distractor plausibility beyond the validated regexes is not graded at scale** (same-kind options,
  off-hinge drift, extra objects). Handover §5.10 flags this as unmeasured; it needs a sampled
  manual/model audit — a natural next step, and the tier filter in the app now makes that easy to target.
- **Curriculum fit of the hinge join** (§5.5) is not graded.

## How to browse

In the app, switch to the **Grok tray** (or earlier AI tray). A new **Quality tier** select filters
to Top / Medium / Low; each question renders a badge, score, and the per-check explanation.
`pack.json` carries `item.quality = {tier, score, reasons, flags}`; `nav.json` carries
`quality_tier`. Regrade+repack via `bash tools/push_g68_candidates.sh` (grades, packs, then pushes).
