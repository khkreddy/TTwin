# 00 · Precedence

When rules collide, this order wins:

1. **Freeze > overlay.** Frozen exam.v1, ISO-GEN L20, live V15, public NCERT map sha are read-only. Adaptation is overlay at pack time (`tools/learner_display.py`).
2. **Deterministic > AI.** If a join, retrieve, typeset, or lookup exists, do not call AI.
3. **Kernel > persona.** Teacher and Student are harnesses over one kernel. They must not fork state.
4. **Ledger honesty > engagement.** A claim the evidence cannot support is a defect.

## Freeze registry (do not write)

| Object | Home | Note |
|---|---|---|
| Chemistry exam.v1 | `awm_build/.../exam_json/items.jsonl` | sha `39646d1c…ffc2b9` · n=14146 · POOL_ID `chemistry_cambridge_extract_ok` |
| Exam schema | `awm.chem.exam.v1` | sha `16e34805…0f140` |
| ISO-GEN L20 | `isogen_lamport_20/generated_items.jsonl` | 20 candidates; not live pool |
| Public NCERT map | paper public json | sha `c6a6231f…1c41f14` |
| Live V15 | `CHEMISTRY_MAP_V15.json` | not dumped into prompts |
| C4 overlay | OFF | teacher overlay is journal, not a rewrite of the map |

New exam schema = new freeze. New ISO-GEN work = new run id. Session Modify is not a freeze write.

## Corpus honesty (measured 2026-09-05)

TTwin ships 22,091 five-ID tagged items; **20,792** have stems. Chemistry map 523 hinges. Phy/bio Map is NCERT chapter list (mx empty). Maths Pack C 792 tagged, 0 stems. MathNet / Phy-500 are not live papers. Catalog: `awm_build/data/question_corpus/STATUS.md`.
