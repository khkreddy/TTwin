# Modify harness refactor log

Explainable record of T-MOD / `tools/modify_g68.js` changes and measured results. Not exam-ready. Live `data/questions/` is never rewritten from this log.

| id | date | SHA | what changed | independent check | corpus result |
|---|---|---|---|---|---|
| R0 | 2026-09-19 | `f29b4f0` | Stop binding `option_plan` to `packet.source.key`. Stamp letters from the result. Add G13–G16. Rewrite H002 a3/a4. | Kimi K3 on H002 + held-out Grok items. Go, with G15 to be tightened. | New ingest fail-closes reverse-causation prose. **Backlog not repaired:** G14 307, G13 186, G15-old 15. |
| R1 | 2026-09-19 | (this commit) | Tighten G15 against Cambridge MCQs. Grouped G14 lock. Same-kind option instruction. Repair H001 a3 + H002 a5 only. | Kimi K3 vs chemistry/physics/biology IGCSE examiner reports + MathNet. Go on P1–P5. | See §Results R1. |

## Diagnosis (confirmed)

`compileMxPlan` used the **donor** key. Default maths source `math_7b_rjb_ch8_s1_t122` is a linear-equations MCQ keyed C, so hundreds of sequence/geometry items planned C as the key. `relationship_reversal` CWOs were instantiated as “writing/naming X is what creates Y.”

Cambridge Principal Examiner reports describe **live** errors of the same *kind* as the key: wrong electrode, omit “molten”, particle size ≠ surface area, density direction, temperature during change of state, A/W swapped on a blast-furnace diagram. They do **not** describe “writing the formula creates the right angle.”

## Gold-corpus measurement (packed TTwin, not Grok)

| bank | ~MCQ | G14 `is what (creates\|produces)` | G15 as in R0 (comma-numbers in stem) | G15 after R1 |
|---|---|---|---|---|
| chemistry-igcse | 7729 | 0 | 6 (electron configs / Rf) | 0 |
| physics-igcse | 6525 | 0 | 1 | 0 |
| biology-igcse | 5884 | 0 | 1 | 0 |
| maths-igcse | 79 true 4-opt (rest structured; many OCR-split options) | 0 | 5 parse junk | 2 parse junk |
| maths-bank (MathNet/AIME/…) | 2168 four-letter | 0 | 42 | 0 |
| maths-olympiad | 751 | 0 | 3 | 0 |

Phrase `is what creates/produces`: **0 / ~23k live options**, **307 / 2318 Grok CANDIDATEs**.

MathNet stems legitimately use “triangular numbers” and “closed formula”. G16 stays **grade_06 only**.

False-positive that forced R1: `0620_s11_qp_11:q4` (structures 2,4 / 2,8 / 2,8,1 / 2,8,7; options “W and X”). R0 G15 treated `2,8,2` as a sequence list.

## Gates after R1

| gate | rule | fail-closed | Cambridge |
|---|---|---|---|
| G13 | Result key must not carry a mix-up type; if an old plan still nulls a letter, that letter set must equal the result key | yes | n/a (compile invariant) |
| G14 | Distractor (never the key) matches `\bis what (creates\|produces)\b` — grouped, so bare “produces” is safe | yes | 0 hits |
| G15 | Stem both has a numeric / whole-number list **and** asks to continue it; every option contains a digit | yes | 0 on chem/phy/bio after tighten |
| G16 | `grade_06` + (`closed formula` or `triangular numbers` unless hinge says triangular) | yes | not applied to MathNet |

No extra regex gate for “proves a new theorem” / “looks neat” (Kimi: unmeasured FP; same-kind rule lives in `instructionFor`).

## Backlog (blocked, not waived)

Counted on disk after R0, before R1 sibling repair:

- G14 reverse-causation options: **307**
- G13 plan-key ≠ result-key: **186**
- G15 continue-list without a digit (tightened): **2** (H001 a3, H002 a5) — repaired in R1

Those 307+186 stay CANDIDATE / `serve_eligible` false until a dedicated repair wave under G13–G16. New ingest cannot re-enter the reverse-causation pattern.

## Results R1

- Tests: `node tools/tests/test_modify_g68.js`, `node tools/tests/test_g68_overlay.js`.
- Electron-config fixture must pass G15; original H002 a3 still fail-closed G14; rewritten H002 a3/a4 still pass.
- Repaired same-hinge siblings: `math/grade_06/ch_01/H001:a3`, `math/grade_06/ch_01/H002:a5`. Every continue-list option names a next term; H001 B is a wrong add-1 rule, not “explaining creates the evens.”
- Authoring remains paused. Live science-junior **109**. Overlays not exam-ready.

## Examiner pattern to keep using

Wrong options are the same row-shape as the key (P/Q/X labels, gas pair, 1-2-3 combination, density×pressure). The mix-up is a documented student move on those quantities, not a taxonomy sentence.
