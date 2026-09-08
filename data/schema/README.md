# ttwin.question.v1

Contract for every object in `data/questions/*.json`. JSON Schema: `ttwin.question.v1.json`.

The shipped unit is self-contained: learner stem/options/figures **and** extracted answer key **and** examiner comments when they exist.

## Split

| Layer | Fields | Who sees it |
|---|---|---|
| Learner | `uid`, five-ID tags, `stem`, `options`, `statements`, `equations`, `tables`, `structures`, `tikz` | Student paper |
| `assessment` | `mcq_key`, `mark_scheme`, `examiner_comment`, honesty enums | Teacher sheet / Finish scoring only |

A renderer that walks top-level learner fields never prints the key.

## Assessment rules

- `assessment` is **always** present.
- `key_source`: `cambridge_extract` (published MS extract) · `olympiad_gold` (JEE gold letter, not a Cambridge MS) · `none`.
- `key_status`: copy of extract availability. Finish treats anything other than `available` as **unscored**, never wrong.
- If extract `ms_text` is exactly `A`/`B`/`C`/`D` → `mcq_key` and `mark_scheme: null`.
- Otherwise if `ms_text` is non-empty prose → `mark_scheme.text` (verbatim) and `mcq_key: null`.
- No extracted key → `key_source: "none"`, `key_status: "not_applicable"`, both key fields null.
- Examiner comment envelope is always present: `{present: false}` or `{present: true, text, comment_sha256?}`. Text is verbatim. Never invent or summarise.
- There is no top-level `correct` field.

## Join

`uid` = testmaker uid with `tm:` stripped = examiner_join `uid`. Frozen exam.v1 is not rewritten. Mix-up catalogs stay off this schema.

## Homes (build-time only)

- Learner body: exam pack / chem_joined (already packed).
- `ms_text` / examiner comments: `awm_build/data/corpus_intelligence/awm_corpus/testmaker_v1/index/questions.jsonl`.
- Comment sha: `awm_build/data/awm_product/generated/examiner_join/items.jsonl`.
