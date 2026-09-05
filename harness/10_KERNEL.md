# 10 · Shared kernel

Owns every deterministic path and all state. Teacher and Student call it; they do not bypass it.

## Owns

- **Store whitelist for live papers.** Items with stem + structured A–D (or option-table rows). Measured 2026-09-05: **20,792** of 22,091 tagged nav rows. Chemistry 8,965 · biology 7,221 · physics 4,606. Maths Pack C (792 tagged, 0 stems) is registered, not whitelisted. `assemble` refuses non-whitelisted stores as live papers.
- **Identity.** Census uniqueness is `item_uid` (paper:question form, e.g. `9702_m18_qp_12:q23`). Five-ID **tags** (not the uid) are `pack`, `subject`, `big_idea_id`, `chapter_id`, `subtopic_id`. Overlay namespaces: `journal/`, `session/`, `candidate/` — never colliding with freeze uids. Solutions keyed `item_uid × item_sha256`. AI never mints uids; the kernel assigns.
- **`assemble(selector)`.** Aliases compile without a model. `provider_calls: 0`. Cambridge `chapter_id` / `subtopic_id` stay on the question. Chemistry NCERT join is **node × grade_band** via `data/projection.json`, not a rewrite of tags. A question tagged at a higher node is retrieved by any descendant selector.
- **`hinge_pack(unit_id)`.** Schema `awm.hinge_pack.v1`. This hinge’s statement (decision, mechanism, CANDIDATE mx, mx_na) + ≤8 enrichment where `unit_id` is in `serves_statement_ids`. Join is **string equality** on `unit_id` (`science/grade_11/chem_ch_106/H001`). Never embedding. Never `primary_node_id`. Never `resolve_node` dump.
- **Prompt parse.** Deterministic alias table first. AI selector only on empty/ambiguous parse.
- **Seeded paper builder.** `mulberry32` on the seed. Seed is recorded on the paper. Paper is fixed from that moment; Modify is the only mutation, and only before Take begins.
- **Learner display overlay** at pack time (`tools/learner_display.py`). Grammatical stems, option tables as tables, TikZJax, no nested `circuitikz`, split stacked figures. See P-LEARNER-DISPLAY.
- **Learner field whitelist.** Stem, options / option-table, figures (TikZ), equations, statements, tables. **Banned on learner copy:** mx ledger, examiner comments, crop paths, printed SMILES strings, mix-up ledgers, answer keys. SMILES may be packed for the drawer; they are never printed as text.
- **Scoring.** Chosen letter or table-row vs stored analysis key. Key precedence: stored analysis → Modify session key → first-write analysis (UNVERIFIED). No key → item excluded from the denominator with a banner, never silently zero-marked. Honesty label required.
- **Solution lookup.** `item_uid × item_sha256` in `data/solutions/index.json` plus browser overlay. Cache hit → zero provider calls. Write-once; a second opinion is a new sha, not an overwrite.
- **Claim ledger** (`70_LEDGER.md`). Single writer per namespace.
- **Packet builder + slot validator.** Schema shape, closed-set membership, copy-only refs, banned-phrase screen, learner-field screen. Overflow truncates and logs; the agent never “includes a bit more.”

## Does not own

The seven AI slots in `15_SLOTS.md`. Those are the only synthesis paths.

## Refuses

Model calls inside kernel code. Freeze writes. Persisting `session/` into the live pool. Emitting banned fields to the learner copy. Scoring without a key. Retrying an empty AI response with a bigger packet. Serving a non-whitelisted store as a live paper. Inventing phy/bio hinges or mx.
