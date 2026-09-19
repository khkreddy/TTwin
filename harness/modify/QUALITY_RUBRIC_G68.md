# QUALITY_RUBRIC_G68 — deterministic quality tiers for G6–8 CANDIDATEs

Status: rubric **v1**, written 2026-09-19 **before** mass inspection of item text. Anchored in
owner law (`HANDOVER_G68_2026-09-19.md` §6), `83_MODIFY.md` first principles, and
`MODIFY_SPEC.md` gates G1–G8 / `modify_g68.js` gates G9–G16. Nothing here is tuned by looking
at candidate outputs; every learner-text regex must additionally show **false-positive count 0
on the gold corpus** (`data/questions/*` — Cambridge IGCSE, MathNet-style banks, science-junior)
before it may affect a tier. That is the same law as handover §7 ("Do not … add regex gates
from examiner adjectives without a gold-corpus FP count of zero").

## Tiers

| Tier | Meaning | Rule |
|---|---|---|
| `top` | Clean, keyable, no known defect. Approaches human-expert draft shape. | No critical defect, no moderate defect, score ≥ 85 |
| `medium` | Usable draft with a real but non-fatal flaw (marking, labelling, or format-honesty gap). | No critical defect; ≥1 moderate defect or score 60–84 |
| `low` | Fails a validity requirement or carries a known generator artefact. | ≥1 critical defect or score < 60 |

Scoring: start 100. Critical −40 each, moderate −15 each, floor 0. Notes are informational and
never move a tier. Tier is decided by defects first, score second.

## Checks

### Critical (any hit → `low`)

| id | What it detects | Basis |
|---|---|---|
| `key_missing` | MCQ-family item with no `assessment.mcq_key`; three_statement with neither key nor a statement pattern anywhere (item or results) | G6 key existence; an unkeyable MCQ is not an assessment item |
| `key_letter_invalid` | Key letter not present among option ids; one_or_more key letters not distinct | G6 |
| `mx_on_key` | `mx_option_map` names a key letter (a "wrong-option mix-up" bound to the correct answer) | G13 |
| `plan_key_mismatch` | `build_logic.option_plan` null-set ≠ actual key set (letters A–D only) — the recorded plan claims different letters are correct than the result key. Includes the R0 donor-key-C leftover | R0 root cause, handover §5.7 |
| `g14_reverse_causation` | Wrong option matches grouped `/\bis what (creates\|produces)\b/i` — the template-garbled reverse-causation artefact | G14; gold-corpus FP 0 (handover §4.2, re-validated by grader `--gold`) |
| `figure_ref_without_figure` | Stem/part text references "the figure / the diagram / the graph / the circuit shown" but item has no tikz, no options-figure, and no table — learner cannot answer | G3 figure–stem agreement |
| `whitelist_leak` | mx type names, "CANDIDATE", or vendor names in learner-facing text | G4 whitelist projection |
| `gate_bypass` | Any G10/G11/G15/G16 violation (these fail closed at ingest; a live hit means a gate bypass) | G10–G16 |
| `structure_broken` | Empty stem, or MCQ family with <2 non-empty options | G1/G2 format honesty |

### Moderate (caps at `medium`) — item-intrinsic quality flaws

| id | What it detects | Basis |
|---|---|---|
| `tikz_without_reference` | tikz present but stem/parts never reference a figure | G3, other direction |
| `hinge_figure_missing` | Map hinge wants a figure (`figure\|diagram\|circuit\|food webs?\|ray\|graph\|apparatus`) and item has none | Handover §5.6 |
| `one_or_more_short_key` | Declared `one_or_more` but key holds <2 letters (law: exactly two key letters) | Handover §6 |
| `multi_key_single_flag` | Multi-letter key without the one_or_more flag | G2 consistency |

### Notes (informational only, never move a tier)

Two kinds. **(a) Systemic harness/plumbing gaps** — describe the harness pipeline or map data, not
the item's authored content, so they are reported separately in the audit and must not drag an
otherwise-clean item out of `top`. **(b) Provenance/cosmetic signatures.**

| id | Kind | What it records |
|---|---|---|
| `key_not_packed` | systemic | structured parts / pattern three_statement: key exists only in `results/*.json`; packed item cannot be auto-marked. Handover §5.2 — a `resultToCandidate` packing bug, **not an authoring miss** |
| `chapter_label_code` | systemic | `chapter_label` is a machine path (`math/grade_06/ch_01`) not a teacher-facing title. Handover §5.4 — a slim-map data gap (all 1692 maths items), **not an authoring miss** |
| `meera_meena` | cosmetic | Kimi-era recurring character names (632 science a1/a2 items) |
| `item_type_not_promoted` | systemic | tikz present but `item_type` stayed `mcq` (browse "MCQ diagram" filter misses it; handover §5.6) |
| `variation_ladder` | provenance | variation_class V1 on attempt ≥3 (the V1–V8 ladder was not executed; handover §5.3) |
| `kimia12` | provenance | Kimi-authored a1/a2 wrapper (no build_logic provenance) |

> Calibration note: `key_not_packed` and `chapter_label_code` were first modelled as moderate
> defects. On the real corpus they fire on every structured item and every maths item
> respectively — uniform pipeline/map defects, not item-quality signals — and leaving them
> tier-moving suppressed all maths items out of `top`. They were reclassified as notes so the
> tier measures **authoring quality** while the audit still surfaces them as systematic harness
> weaknesses.

## Explanation contract

Every graded item carries `reasons[]` in learner-safe English: each triggered check emits one
sentence naming the defect and the evidence (offending letter + truncated text). Clean items get
positive reasons derived from the checks they pass (keyable, distractors mx-bound, no known
artefacts, format honest). The UI shows this verbatim; it is the per-item audit trail.

## What this rubric deliberately does NOT measure (v1 honesty)

- Semantic correctness of the key (is C *really* right?) — needs human or model review; keys stay UNVERIFIED.
- Distractor plausibility beyond the validated regexes (same-kind options, off-hinge drift, extra objects) — flagged by handover §5.10 as unmeasured at scale; a sampled manual audit accompanies the audit report.
- Curriculum fit of the hinge join (handover §5.5).

These gaps are stated so the tier counts are not over-claimed. `top` means "clean against every
defect we know how to detect deterministically", not "exam-ready".
