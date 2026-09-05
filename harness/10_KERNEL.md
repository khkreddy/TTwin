# 10 · Shared kernel

Owns every deterministic path and all state. Teacher and Student call it; they do not bypass it.

## Owns

- `assemble(selector)` — aliases compile without a model. `provider_calls: 0`.
- Joins: Cambridge `chapter_id` / `subtopic_id`. Chemistry NCERT join is **node × grade_band** via `data/projection.json`, not a rewrite of tags.
- `hinge_pack(unit_id)` — this hinge’s mechanism + CANDIDATE mx + ≤8 enrichment (`serves_statement_ids`). String equality on `unit_id`. Never `resolve_node` dump.
- Seeded paper builder (`mulberry32` on seed). Seed is recorded on the paper.
- Learner display overlay: grammatical stems, option tables as tables, TikZJax, no nested `circuitikz`, split stacked figures.
- Learner field whitelist: stem, options/option-table, figures (TikZ), equations, statements, tables. **Banned on learner copy:** mx, examiner comments, crop paths, SMILES, mix-up ledgers, answer keys.
- Scoring: chosen letter/row vs stored analysis key. Honesty label required.
- Solution lookup: `item_uid × item_sha256` in `data/solutions/index.json` (plus browser overlay). Cache hit → zero provider calls.
- Claim ledger (see `70_LEDGER.md`).
- Packet budgets (`40_PACKETS.md`). Overflow fails closed.

## Does not own

- Fuzzy restatement, ISO-GEN authoring, first-write analysis, lesson prose, post-score feedback — those are the five AI slots.

## Identity

Census uniqueness is `item_uid`. Five-ID tags: `pack`, `subject`, `big_idea_id`, `chapter_id`, `subtopic_id`.
