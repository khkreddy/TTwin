# ttwin.question.v1

Contract for every object in `data/questions/*.json`. JSON Schema: `ttwin.question.v1.json`.

A **complete TTwin question** is self-contained: five-click tags, learner stem/options/figures, extracted answer key, examiner comments when they exist, learn-by-solve follow-ups for every wrong MCQ option when a key exists, and Mx-library modify seeds for T-MOD. Overlay at pack time; frozen exam.v1 is not rewritten.

## Split

| Layer | Fields | Who sees it |
|---|---|---|
| Learner | `uid`, five-ID tags, `stem`, `options`, `statements`, `equations`, `tables`, `structures`, `tikz` / `figure_src` | Student paper |
| Student-take overlay | follow-up *question text* after a wrong letter (from `assessment.learn_by_solve`) | Student after a miss; no mx_type |
| `assessment` | `mcq_key`, `mark_scheme`, `examiner_comment`, `learn_by_solve`, `modify_seeds`, honesty enums | Teacher sheet / Finish scoring only |

A renderer that walks top-level learner fields never prints the key.

## Assessment rules

- `assessment` is **always** present.
- `key_source`: `cambridge_extract` (published MS extract) · `olympiad_gold` (JEE gold letter, not a Cambridge MS) · `none`.
- `key_status`: copy of extract availability. Finish treats anything other than `available` as **unscored**, never wrong.
- If extract `ms_text` is exactly `A`/`B`/`C`/`D` → `mcq_key` and `mark_scheme: null`.
- Otherwise if `ms_text` is non-empty prose → `mark_scheme.text` (verbatim) and `mcq_key: null`.
- No extracted key → `key_source: "none"`, `key_status: "not_applicable"`, both key fields null.
- Examiner comment envelope is always present: `{present: false}` or `{present: true, text, comment_sha256?}`. Text is verbatim. Never invent or summarise.
- `learn_by_solve` (keyed MCQ only): hinge `solve` + `wrong[letter]` with V2 `mx_type`, `pathway`, and a follow-up `{stem, options, key, why}`. Not fabricated for items with no `mcq_key`.
- `modify_seeds`: T-MOD instruction stubs from those mx rows. Session-only; no new freeze uid.
- Mix-up type names are never printed on the learner paper.
- There is no top-level `correct` field.

## Join

`uid` = testmaker uid with `tm:` stripped = examiner_join `uid`. Frozen exam.v1 is not rewritten. Mix-up catalogs stay off this schema.

## Homes (build-time only)

- Learner body: exam pack / chem_joined (already packed).
- `ms_text` / examiner comments: `awm_build/data/corpus_intelligence/awm_corpus/testmaker_v1/index/questions.jsonl`.
- Comment sha: `awm_build/data/awm_product/generated/examiner_join/items.jsonl`.
