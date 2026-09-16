# 81 · Learn-by-solve hints (ISO-GEN authoring + IIP runtime)

Frozen exam.v1 is not rewritten. Hints are a **pack-time overlay**. Mix-up type names stay teacher-key only.

## Why this exists

A wrong A–D is a **named gate**, not a cue to donate the original key. ISO-GEN’s rule is specification-before-item: the spec for a hint is the **hinge the parent item is tagged to** plus the **failure mode of that option** (an overlooked intermediate step, or a V2 mix-up). The hint is a simpler question that tests that gate. After the hint, the student **re-attempts the original** unaided.

## Spec (exists before the follow-up is written)

For parent item `P` tagged to hinge `H` (five-click: pack, subject, big idea, chapter, subtopic; chemistry hub `node` e.g. `chem:C5/H-REDOX`):

1. **Hinge.** Copy `P.node` / chapter / subtopic. Prefer a map `decision_hinge` under that hub when the stem matches it. Do not invent a hinge.
2. **Failure mode of the chosen wrong letter.** Either:
   - **intermediate_omission** — a required step (oxidation number of one element, electrode identity, electron count) was skipped; or
   - a V2 mx (`term_substitution` · `condition_omission` · `relationship_reversal` · `scope_error` · `surface_feature_capture` · `mechanism_conflation` · `operation_confusion`).
3. **Unlock question.** A new four-option MCQ whose subject is **that option’s content**, one rung simpler than `P`, whose answer is the missing step or the corrected mix-up. It must not state or imply `P`’s keyed letter or keyed option text.
4. **Explanation (`why`).** Tells the result of the **hint**, not of `P`. Then the student returns to `P`.

## Runtime (instructional integrity)

| Step | Learner sees | Must not see |
|---|---|---|
| Wrong letter on `P` | Hint stem + A–D | Original key, original solve, mx_type |
| Answers the hint | Hint key mark + `why` of the hint + **Try the original again** | “Original question: the key is …” |
| Retry | Original stem/options unlocked, previous letter cleared | Donated original answer |
| Finish | Score on the **last unaided pick of `P`** | Credit for the hint |

I2: the hint is a different question; it does not credit `P`. I3: the student produces `P`’s answer after the explanation, not before. I20: needing a hint is not progress.

## Overlay files

- Spectroscopy (hand): `data/spectra/lbs.json`
- Approved gold: `data/overlay/lbs_gold.json` (`9701_m16_qp_12:q1`)
- Chemistry AS/A Electrochemistry (this protocol): `data/overlay/lbs_electrochem.json`
- Join: `tools/join_lbs.py`. Gold and spectroscopy win on their uids. Constructor templates are not this protocol.

Do not scale a chapter overlay until the owner has checked a packed sample of that chapter.
