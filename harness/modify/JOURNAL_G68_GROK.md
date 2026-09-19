# JOURNAL — Grok Science 6–8 CANDIDATE authoring (addendum)

Read this after `83_MODIFY.md` and `MODIFY_SPEC.md` if you are authoring or ingesting grades 6–8 Science CANDIDATEs via `tools/modify_g68.js ingest`. Owner paused, corrected, then resumed. **Do not copy these mistakes.**

Scope: Grok-authored files only (`build_logic` or `mx_option_map` on the wrapper). Never edit Kimi a1/a2 items that lack those fields. Never write `data/questions/`. Never copy source `learn_by_solve` onto a retargeted item.

## What went wrong (bad examples)

| uid | Fault | Why it failed the learner |
|---|---|---|
| `…grade_06:ch_05:H003:a3` (before fix) | Option C: `2 m = 0.02 cm, by reversing the 100s.` | Mix-up **recipe** in the option. Gives the construction away. |
| `…grade_06:ch_07:H001:a3` (before) | Option D: reddish/bluish bowls | Objects **not in the stem**. Surface mix-up invented props. |
| `…grade_06:ch_07:H003:a3` (before) | “Nalini’s class in Jaipur”; C “meant only for forehead checks” | City padding. Extra clause **disqualifies** C so it is not a real distractor. Options not parallel. |
| `…grade_06:ch_07:H006:a3` (before) | Option D Kelvin `°K` | **Second idea.** Stem was C/F same temperature. Forced mix-up slot. Too much for grade 6. |
| `…grade_08:ch_05:H001:a3` (before) | Option C pascal | Stem tests **force as push/pull between two objects**. Units are a different hinge. |
| same uid, teacher overlay | Copied IGCSE `learn_by_solve` (oxidation numbers / litmus) | Source chemistry LBS leaked onto a Force item. Key looked like redox. |

Kimi a1 items (no `build_logic`) often keep one grammatical frame across A–D. Learn that structure. Do not copy Meera/Meena monopolies or “Multiple choice question:” prefixes.

## What is good now (keep doing this)

**Force table** `candidate:g68:science:grade_08:ch_05:H001:a3` after correction — owner: “the question is actually good in that way.”

- Stem: one idea — force as a push or pull **between two objects**.
- A (key): kick — push between foot and ball.
- B: ball applies a force to itself (not an interaction pair).
- C: pull acts only on the wagon (still the **interaction** idea, not units).
- D: leaf falls with no objects interacting (still interaction).
- Table rows share one frame: event — claimed force.

**Length** `…ch_05:H003:a3` after correction:

- A `2 m = 2 cm.` B `2 m = 200 cm.` C `2 m = 0.02 cm.` D `2 m = 20 cm.`
- Same frame. No “reversing the 100s.”

**Thermometer** `…ch_07:H003:a3` after correction: four instrument names, no city, no “meant only for…”.

**Touch** `…ch_07:H001:a3` after correction: Yes/No about Nisha’s hands and tap water only.

## Rules (non-negotiable)

1. Distractors are learner-plausible **claims**. Never narrate the mix-up (`by reversing…`, `meant only for…` as a giveaway).
2. Every noun in an option must already be in the stem or figure.
3. **One hinge.** All three wrong answers are wrong about the same idea the key is right about.
4. Four options share one grammatical frame and register.
5. Zinsser: short direct sentences. No city unless the hinge needs a place.
6. Packed Mx: instantiate a CWO **only if** it can be said with the stem’s objects and hinge. Else swap and log `build_logic.mx_swap`. G9 still wants ≥2 distinct mx types on **wrong** letters, but never at the expense of (3).
7. `mx_option_map` is teacher-side. Learner paper never sees mx type names.
8. Do **not** copy `source.assessment.learn_by_solve`. Set `learn_by_solve` null unless you authored an overlay for **this** hinge.
9. CANDIDATE, UNVERIFIED, `serve_eligible` false. Ingest via `tools/modify_g68.js ingest`. No Moonshot `generate` for this corpus.

## Ingest

```
node tools/modify_g68.js ingest --unit UNIT --source SOURCE --result FILE --attempt 3 --item-type single_mcq --variation V1
```

SOURCE: prefer `biology_7a_rjb_exe1` (Science junior) unless the hinge needs a figure — then an IGCSE tikz source + `--figure rewrite`, and keep the tikzpicture. Never invent TikZ from scratch.

## Owner review surface

Science → **Grok tray · unverified**. Hourly job packs `pack.json`/`nav.json` and pushes CANDIDATE-only. Live `science-junior.json` stays 109.
