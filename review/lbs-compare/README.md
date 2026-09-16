# Compare current LBS vs Astra harness (AS/A electrochemistry)

Current overlay `data/overlay/lbs_electrochem.json` is **not** modified.
Packed `chemistry-senior.json` is **not** re-joined.

| File | Role |
|---|---|
| `index.html` | Review app |
| `compare.json` | Side-by-side payload |
| `../../data/overlay/lbs_electrochem_astra.json` | Astra overlay only |
| `../../data/lbs/astra_electrochem_explain.json` | Per-letter proof / join / why |

Open: http://127.0.0.1:8766/review/lbs-compare/

Shortcuts: gold q1, q33 (Cl always negative), q18 (sulfur XYZ), cryolite q3, FeC₂O₄ q10.

## How Astra produced a hint

1. Packed tags `cam:9701:6` or `cam:9701:24` → reviewed `data/lbs/grain_bindings.v1.json` (NCERT Redox ch.207 or Electrochemistry ch.102). Not hinge-word overlap. Coordination/sugars excluded.
2. Task guard picks a **unit** (H005 OS bookkeeping, H018 electrolysis products, H006 OS-change, …).
3. Wrong letter is routed to a **named move**: extra 1-2-3 statement, X/Y/Z species, formula OS, cryolite role, FeC₂O₄ electron count. If none bind, a generic OS-change fill-blank is used (`fallback: true`) — treat those as weaker, not as a win.
4. Surface is a thinking-prod (fill-blank / T/F / AR / match / multi). It must not reprint the clicked option.
5. `why` cites the map **law** or **step** (H005 S1/S3, H018 roles). Mix-up type stays off the learner stem.
6. **Zero model calls per question.** 213 parents × 3 letters instantiated in code.

## What to look for

- q33 C: both systems now ask Cl in HClO. Astra adds the map law in `why` and records unit `…/H005`.
- q18 B: both ask S in SO₂. Astra records the named-species join.
- gold q1: current gold is OH / S / Cl MCQs. Astra computes OS from the formula (OH for B, S in sulfate for C, N in NH₄Cl for D). D is a real disagreement: gold tests Cl as chloride; Astra’s first non-O/H element is N.
- Generic “Assign oxidation numbers first… oxidised/reduced/unchanged” rows are **fallback**. Filter the app on that.
