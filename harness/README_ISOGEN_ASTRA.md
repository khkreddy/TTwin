# ISO-GEN and the Astra LBS harness

These two folders are the finished law and the finished machinery for generating items and for writing learn-by-solve hints.

They do not replace the numbered files in `harness/` (read those first). They collect the signed protocols and the Astra compiler so a new session can find them.

## What they are for

**ISO-GEN** writes a new question only when a named gap exists. The specification comes first. The item is a projection of that spec, not a story the model invents. A generated item is CANDIDATE until a human ratifies it. The kernel never calls a model.

**Learn-by-solve (LBS)** is what happens after a student picks a wrong A–D. The system does not give the original key. It asks a simpler question about the gate that produced that letter. Then the student tries the original again. The hint does not count toward the score.

**Astra LBS** is the pack-time compiler that fills those hints. It reads the map, the mix-up list, and the packed tags. It does not call a model once per option of the 21,000-item corpus. Instantiation is code. A missing hint is better than a reprint of the option the student just read.

## Where to look

### `harness/isogen/` — ISO-GEN, signed

| File | What it is |
|---|---|
| `ISO_GENERATION_PROTOCOL.md` | ISO-GEN v1.3. Specification before item. Fail-closed gates. |
| `LBS_PROTOCOL.md` | Learn-by-solve. Diagnosis is a lookup. |
| `ISOGEN_KNOWLEDGE_WIKI.md` | How the protocol sits on the rest of the system. |
| `INSTRUCTIONAL_INTEGRITY_PROTOCOL_IIP_2_0.txt` | I2 (no assisted credit), I3 (retry the original). |
| `80_ISOGEN.ttwin.md` | TTwin slice: CANDIDATE lifecycle, Modify, honesty. |

Do not rewrite frozen Lamport L20. New work is a new run id.

### `harness/astra-lbs/` — Astra compiler, snapshot

| File | What it is |
|---|---|
| `81_LBS.md` | Hint spec and NEVER reprints (q33 C, q18 B). |
| `82_LBS_COMPILER.md` | Compiler contract. Zero model calls at item grain. |
| `ASTRA_TASK.md` / `ASTRA_SPEC.md` | The task we gave Astra and the spec it returned. |
| `scripts/` | Snapshot of the Python that builds overlays. Runtime copies live in `tools/`. |
| `data/never_cases.v1.json` | Stems that must never appear again. |
| `data/grain_bindings.v1.json` | Reviewed Cambridge → NCERT unit lists. |
| `data/preserve_uids.v1.json` | Gold q1 and spectroscopy. Do not overwrite. |
| `schema/` | `unlock_recipe.v1`, `hint_proof.v1`. |

Run the live tools, not the snapshot, unless you are auditing this package:

```
python3 tools/lbs_compile.py snapshot
python3 tools/lbs_compile.py plan --scope electrochem
python3 tools/lbs_astra_corpus.py
python3 tools/join_lbs.py
```

Join order: Astra overlays, then spectroscopy, then gold. Gold `9701_m16_qp_12:q1` and the spectroscopy bank win.

Learner runtime is `js/paper.js` and `js/app.js`. Mix-up type names stay off the student paper.

## Rules that do not bend

1. Frozen exam.v1 is read-only. Pedagogy is overlay.
2. The public map and live V15 are not rewritten from this harness.
3. Do not dump the comprehensive NCERT map into a model.
4. Do not reprint the clicked option as the hint.
5. Do not show the original key on the hint.
6. Public UI says **AI**. Not a vendor name.

## What “done” means

A complete packed question has five-click tags, a key when one was extracted, a hint for every wrong letter when a key exists, and modify seeds for the teacher. Structural JSON is not quality. If the join cannot name a hinge and a gate, leave a gap.

The electrochem thinking-prod (Cl in HClO; S in SO₂) is the quality bar. A physics T/F that restates a Class 9 sound-wave hinge for a Doppler item is not.

## If you are new here

Read `harness/00_PRECEDENCE.md`, then `15_SLOTS.md`. Then this file. Then `isogen/ISO_GENERATION_PROTOCOL.md` §0 and `astra-lbs/82_LBS_COMPILER.md`. Stop. Build only what those pages allow.
