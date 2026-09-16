# 82 · LBS hint compiler (proof-carrying, map-driven)

Astra spec (gpt-6-astra): `harness/lbs_compiler/ASTRA_SPEC.md`. Task: `harness/lbs_compiler/ASTRA_TASK.md`. Receipt: `harness/lbs_compiler/ASTRA_RECEIPT.json`. Frozen Lamport L20 is not rewritten. This is a **new TTwin pack-time overlay compiler**.

## Verdict

`tools/lbs_construct.py` (`unique_diff` → guessed mx_type → template) is **not** the compiler. Its 21,124/21,124 census is structural JSON, not LBS validity. A missing hint with a `ProofGap` is better than a wrapper, an option reprint, or an unsupported diagnosis. Do not fall back to the constructor, and do not call an LLM per wrong letter of the ~21k corpus.

## Architecture

```
owned intelligence (maps, enrichment, projection, packed tags)
        → snapshot + element citations (hashes, JSON pointers)
        → exact indexes + approved grain bindings (no embeddings)
        → deterministic recipe specs per (unit, step, mx/omission)
        → optional bounded SURFACE slot (unit-level, not per item)
        → unlock_recipe.v1 library (content-addressed)
        → instantiate packed (P, letter) with ZERO model calls
        → PROVED overlay  |  GAP / REJECTED (no wrapper)
        → join_lbs.py pack-time; preserve-uids first
        → existing runtime (hint → retry original)
```

LLM is allowed only as pack-time **recipe surface** on a whitelist projection of one map unit. Instantiation across packed items is code. Kernel and `join_lbs.py` must not import `tools.lbs_ai`.

## Joins (fail closed)

| From | To | Rule |
|---|---|---|
| Packed five-click tags | NCERT `unit_id` | `data/projection.json` ∩ node ∩ grade-band ∩ **reviewed** `data/lbs/grain_bindings.v1.json`. Not token-overlap of hinge words into the stem. |
| `unit_id` | enrichment | exact `unit_id ∈ serves` |
| Wrong letter | failure route | exact/specialized match to `mx.cwo` AST, or cited `intermediate_omission@step_id`. Not “guess one of seven types”. |
| Route | unlock | lower-rung corpus item, else a **fully specified** tutorial_bridge queue. Thin pool ≠ “ask the model”. |

If two units remain: `AMBIGUOUS_UNIT`. Empty `mechanism.steps`: `EMPTY_MECHANISM_STEPS`. No CWO match: `MISSING_MX_MATCH`. Unresolved X/Y/Z: no instantiate.

## Bounded LLM (optional; off until slots are classified)

Worst-case electrochem pilot: 29 H-REDOX + 24 H-ECHEM = **53 units → ≤53 author + ≤53 examiner = 106 calls**. Full chemistry only after owner expansion: ≤523 + ≤523. Never `(item_uid, letter)` as a call key.

Proposed slots (not live until listed in `15_SLOTS.md` as LEGAL): `T-LBS-RECIPE-SURFACE`, `T-LBS-RECIPE-EXAMINE`. Until then, deterministic phrase-registry rendering only.

## Runtime / IIP (unchanged)

I2 hint does not credit P. I3 retry original, key not shown on hint. I20 error is not progress. mx_type teacher-key only.

## Preserve / NEVER

- Preserve: gold `9701_m16_qp_12:q1`, spectroscopy `data/spectra/lbs.json` uids. Compiler must not overwrite.
- NEVER F3: `data/lbs/never_cases.v1.json` — q33 C combo-reprint; q18 B unnamed “that species”.

## CLI

```
python3 tools/lbs_compile.py snapshot
python3 tools/lbs_compile.py index
python3 tools/lbs_compile.py plan --scope electrochem
python3 tools/lbs_compile.py library --surface-source deterministic
python3 tools/lbs_instantiate.py --scope electrochem --library … --preserve …
```

No AI import on those paths. Owner check before any chapter expansion: q1, q33 C, q18 B, cryolite `9701_s11_qp_11:q3`, FeC₂O₄ `9701_m19_qp_12:q10`.
