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
3. **Unlock question.** A **thinking-prod**: first a short scientifically correct account of why that option is wrong, then a *new* small task (calculate an oxidation number, identify a species, true/false on a named compound) that makes the student discover that reason. Format fits the gate. It must not state or imply `P`’s keyed letter, and it must **not reprint the option the student just read**.
4. **Explanation (`why`).** Tells the result of the **hint**, not of `P`. Submitting the hint **returns the student to `P`** with the previous letter cleared.

## NEVER (owner-rejected reprints)

These were served as hints and must not be generated again. They restate the clicked option; the student has already read that text. They are not a task.

**`9701_m17_qp_12:q33` option C (bad):**
> Option C is “2 and 3 only are correct”. The numbered statement “The oxidation number of chlorine in a compound is negative.” belongs in the correct 1 / 2 / 3 combination.

The gate is that statement 3 is not always true. The unlock is a calculation, e.g. oxidation number of Cl in HClO (it is +1).

**`9701_m18_qp_12:q18` option B (bad):**
> This option is “X: −2; Y: +4; Z: +6” and assigns “Y: +4”. What oxidation number should that species actually have here?

“That species” is undefined. The unlock is to identify Y as SO₃ (from oxidising the combustion product) and find S is +6, or identify X as SO₂ (S +4), not sulfide.

Banned stem shapes: `Option C is “2 and 3 only…”`, `belongs in the correct 1 / 2 / 3 combination`, `This option is “X: −2; Y: +4…”`, `What oxidation number should that species actually have here?`

## Runtime (instructional integrity)

| Step | Learner sees | Must not see |
|---|---|---|
| Wrong letter on `P` | Hint in the format that fits the gate | Original key, original solve, mx_type |
| Answers the hint | Returned to `P`; `why` of the hint under the original | “Original question: the key is …” |
| Retry | Original stem/options unlocked, previous letter cleared | Donated original answer |
| Finish | Score on the **last unaided pick of `P`** | Credit for the hint |

I2: the hint is a different question; it does not credit `P`. I3: the student produces `P`’s answer after the explanation, not before. I20: needing a hint is not progress.

## Overlay files

- Spectroscopy (hand): `data/spectra/lbs.json`
- Approved gold: `data/overlay/lbs_gold.json` (`9701_m16_qp_12:q1`)
- Chemistry AS/A Electrochemistry (this protocol): `data/overlay/lbs_electrochem.json`
- Join: `tools/join_lbs.py`. Gold and spectroscopy win on their uids. Constructor templates are not this protocol.

The production architecture is the **proof-carrying compiler** in `82_LBS_COMPILER.md` (Astra spec `harness/lbs_compiler/ASTRA_SPEC.md`): map unit + mx/step → hashed `unlock_recipe.v1` library → deterministic instantiate. No LLM per packed option. `tools/lbs_construct.py` is legacy audit only.

Do not scale a chapter overlay until the owner has checked a packed sample of that chapter.
