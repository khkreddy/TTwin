# Isomorphic Transformation & New-Item Generation Protocol

**Version 1.3 · 2026-08-10 · LEARNING-PURPOSE + TOURNAMENT LAYER (three-expert panel Fable·Codex·Kimi, NETFLIX-style; Kimi SIGN: YES R2+R3, Codex SIGN: YES R4; full derivation in `reports/isogen_v3/`) — v1.2 and v1.1 text survive only where not amended by the v1.3 layer at the end of this document; the stricter applicable rule controls.**

**Version 1.2 · 2026-08-10 · REPRESENTATION-FIRST LAYER (owner-directed refinement; Codex adversarial R1→R3 SIGN: YES; Kimi counter-sign pending 429 clearance) — v1.1 text survives only where not amended by the v1.2 layer at the end of this document; the stricter applicable rule controls.**

**Version 1.1 · 2026-08-09 · SIGNED-PENDING (Kimi P1–P11 folded verbatim; P12 tracked annex) · consolidates:** the tested E8 pipeline
(`cms/iso_test/`, 10 items, 10/10 keys, 1 adjudicated re-map), the Baumanns-based
*Agent Protocol for Isomorphic Problem Posing* (normative annex at
`reports/Agent_Protocol_for_Isomorphic_Problem_Posing.md`), `CMS_PROTOCOL.md` (this
document supersedes its §6b), and the patent draft's controlling mechanisms
(specification-before-item, fail-closed gating, whitelist projection, compiled
diagnostic manifest, different-family conformance).

## 0. Why generation exists in this system

Generation is **demand-driven, never decorative**. The demand signal is deterministic:
`bank gaps` lists every canonical misconception with too few items to practise
(currently 2,024 of 14,069 families below 3 members), and every request the RAG cannot
fill abstains with a reason — that abstention is the generation queue's input. A
generated item exists to close a named gap: a misconception family, a difficulty rung,
a representation variant, or a cross-topic transfer set.

The unique position (patent-documented): the **specification exists before the item**.
Our corpus already stores, per source item, the invariants and manipulables
(`isomorph_seed`), the attested misconception with its plain-language mechanism
(`question_intelligence`), the family identity (registry v2.2), difficulty evidence
with denominator class, structural edges (30,019) and cross-curriculum remediation
aliases. Generation compiles from this; it never free-writes.

## 1. The product grammar: mode × variation

Every generated item carries TWO labels, decided at different times:

**Variation class (V1–V8)** — the transformation *axis*, chosen at bundle time
(deterministic): parameter / structural / cross-topic / cross-subject / figure /
inverse-flip / representation / composite. (E8-tested, all eight.)

**Fidelity mode** — the honesty *label*, decided at release (validated, not asserted):

| mode | meaning | rule |
|---|---|---|
| `FAITHFUL_TRANSFER` | backbone, construct, difficulty preserved | no new load-bearing relation |
| `DIFFICULTY_TUNED_ISOMORPH` | backbone intact, difficulty deliberately moved | delta declared on the difficulty vector |
| `GENERATIVE_EXTENSION` | backbone active + new load-bearing condition | never sold as a parallel form |
| `SOURCE_INSPIRED` | influenced, not backbone-bound | never enters a parallel set |
| `BLOCKED` | failed a hard gate | retained with coded reason |

Mode boundary rule (Baumanns, binding): **any new load-bearing condition
automatically reclassifies to extension.** Every addition is tagged
`REALIZATION_ONLY` / `NONCORE_SUPPORT` / `NEW_CORE`, and `NEW_CORE` triggers the
reclassification mechanically.

## 2. The deterministic layer (no model call, ever)

RAG-only, exact, auditable — this is the CMS working as compiler:

1. **Target selection** — from the gap report or an abstained request:
   (family × difficulty rung × representation) holes, ranked by member deficit.
2. **Bundle assembly** (`awm_engine/iso_bundle.py`, extended): source item chosen from
   family members (grade-preferred); the bundle carries —
   - `isomorph_seed` invariants + manipulables (the condition-ledger seed);
   - the canonical Mx entry: statement, confusion_type, `why_option_follows`
     (the wrong-reasoning graph seed);
   - facility + denominator class (the difficulty-vector baseline);
   - structural edges of the source (analogue candidates for cross-* classes);
   - transfer-pattern guidance from the structural atlas (V4);
   - CI remediation alias where one exists.
   The bundle is content-hashed; the hash rides in the released item's provenance.
3. **Projection discipline** — the author receives the bundle and ONLY the bundle.
   (Enforcement today: instruction + logged compliance; OS-level no-read remains a
   [CONCEIVED] embodiment, stated exactly as the patent draft states it.)
4. **Structural release checks** — schema validity; option-set integrity; exactly one
   key; figure-stem numeric agreement (exact parse); mode-boundary check (a `NEW_CORE`
   tag present ⇒ label must be extension); duplicate-hash check against the corpus.
5. **Admission + indexing** — released items enter the corpus via CMS §2 with
   provenance `isomorphic_generation`, join the registry (mapped Mx ids provisional),
   and the RAG indexes them immediately. The gap report recomputes.

## 3. The LLM layer (creativity and synthesis, two families)

**Family 1 — the poser** (currently Codex). Runs the Baumanns cycle inside the
guardrail:
- *Situation analysis*: solve the source blind (before reading its stored answer);
  build the condition ledger (givens, hidden constraints, goal form, representation
  cues, scaffolds) on top of the bundle's seeds.
- *Backbone selection*: smallest load-bearing subgraph; passes the four tests
  (deletion / path / counterfactual / cue). Topic, formula or vocabulary is never a
  backbone.
- *Posing*: ≥3 candidates where feasible (close transfer · representation-shifted ·
  extension-contrast), each with a quick solution sketch; select before rendering.
- *Target-native construction*: derive from target-domain principles — never noun
  substitution into the source solution; figures via semantic spec → self-contained
  SVG; distractors ENGINEERED target-native (each names what it catches, mapped to a
  misconception mechanism, not copied numerically).
- *Independent solve* of the target, edge cases, all options computed.
- *Synchronous metadata*: the `question_intelligence` block is written in the same act
  — inherited + mapped canonical ids, locus, plain-language misconception per
  distractor, provenance with role mapping and invariants-preserved list.

**Family 2 — the examiner** (currently Kimi). Blind of the author's reasoning:
- solves the item independently; checks the key;
- **solves as the misconceiving student** — would that belief actually produce the
  named distractor? (The ISO08 check: the one error class nothing structural catches;
  it re-mapped 1 of our first 10.)
- invariant preservation, well-posedness (a subtle second answer is a FAIL),
  structural-vs-surface judgement for V3/V4, figure load-bearing + agreement for V5,
  difficulty-delta plausibility for the named learner.

**Adjudication** — disagreements are adjudicated case-by-case on the record (both
directions: the checker has been wrong before), folded as events, never averaged.

## 4. Hard gates (fail-closed; no averaging; every failure coded)

Every gate is annotated with its executor class — **D** (deterministic code), **M2**
(second model family over an independent artifact), **H** (human adjudication) — and
the artifacts it consumes. Standing rule (Kimi, folded): **no model gate may consume
only author-produced artifacts.** The one gate that caught a real defect in E8 was the
one where the examiner produced an independent artifact (G5); that architecture is now
generalised, not admired.

- **G0 provenance [D]** — bundle hash, source status, **and the phase-interlock (P5)**.
- **G1 source understood [D+M2]** — enforced by *two-phase bundle release* (P5, verbatim):
  > Phase 1 contains stem, seed invariants/manipulables, representation cues — no key,
  > no Mx entry, no facility. The deterministic layer releases phase 2 only on receipt
  > of a blind-solve artifact whose hash enters the manifest. A manifest lacking the
  > phase-1→phase-2 interlock fails G0.
- **G2 backbone load-bearing [M2+D]** — (P7, verbatim):
  > G2 consumes two independently produced backbones. The examiner derives backbone and
  > condition ledger from the examiner bundle alone, before any author artifact is
  > released; agreement is computed mechanically over the mapping ledger; disagreement
  > is an adjudication event. An examiner verdict written over the author's write-up is
  > coded `SELF_CERTIFIED`. Backbone comparisons run over content-addressed nodes,
  > never over (operator, operand) pairs — that pair is non-injective in our corpus and
  > must never serve as a key anywhere in this pipeline.
- **G3 target valid [D where possible, else M2]** — (P3, verbatim):
  > G3 records a verification class per item: `MACHINE_VERIFIED` (deterministic key
  > check), `TWO_MODEL` (independent solves agree), or `ADJUDICATED`. Where the answer
  > class admits machine verification, `TWO_MODEL` is not accepted. Batch metrics
  > report the mix.
- **G4 sufficiency & ambiguity [M2]** — no plausible alternative reading yields a
  different answer; a subtle second answer is a FAIL.
- **G5 construct & distractor mechanism [M2]** — solve-as-the-misconceiving-student;
  the ISO08 gate, unchanged.
- **G6 difficulty declaration [D]** — (P8, verbatim):
  > Mode labels certify structure at release and difficulty only after calibration.
  > Every generated item enters with difficulty evidence grade E (predicted: source
  > facility + declared delta, method recorded). `FAITHFUL_TRANSFER` and
  > `DIFFICULTY_TUNED_ISOMORPH` are provisional until the item accumulates ≥30
  > responses with observed facility inside the declared band. Parallel-set membership
  > requires confirmed difficulty. Served items label facility as predicted or
  > observed. G6 certifies the declaration, not the difficulty, and says so.
- **G7 traceability [D]** — Chain of Evidence complete, content-addressed.
- **G8 mode honesty [D over M2-reproduced artifacts]** — (P1, verbatim, replacing the
  self-certified check):
  > For every condition-ledger entry the author tags `REALIZATION_ONLY` or
  > `NONCORE_SUPPORT`, the manifest must contain a counterfactual solve — the target
  > solved with that entry removed — produced by the poser and independently reproduced
  > by the examiner. The entry is reclassified `NEW_CORE` iff removing it changes the
  > key or leaves the item unsolvable under every declared solution class, as shown by
  > both counterfactual solves agreeing. The release label must agree with the
  > recomputed classification. A tag that disagrees with its own counterfactual solve
  > fails closed with code `MISTAGGED_CORE`. Author tags are evidence to this gate,
  > never input.

### Admission screens (deterministic, pre-index)

- **Near-duplicate screen** (P6, verbatim):
  > Embedding and structural similarity against the full corpus at a versioned
  > threshold; items above threshold quarantine with `NEAR_DUPLICATE` and enter
  > adjudication, never the index. Exact hash remains a separate, stronger code.
  > Threshold and version ride in the manifest.
- **Render proof** (P10, verbatim):
  > Every figure-bearing item requires a render-proof artifact at admission: the SVG
  > rasterized in CI, asserted non-blank, all text elements extracted and checked
  > against stem numerics by value (unit- and format-normalized). Parse failure
  > quarantines with `RENDER_UNVERIFIED`. No figure-bearing item is served without a
  > render proof.
- **Bundle whitelist** (P4, verbatim):
  > Bundle assembly is a closed whitelist projection. The bundle schema enumerates
  > every permitted field; assembly fails closed on any field outside the schema; the
  > schema version rides in the manifest. The same mechanism defines the examiner
  > bundle (item + seed invariants; no author artifacts). "Blind of the author's
  > reasoning" is a property of this projection, not of the prompt.
- **Seeded-defect calibration** (P9, verbatim):
  > Before any learner-facing serving, and per batch thereafter: a calibration suite of
  > items with known seeded defects — at least one per failure code, including
  > `UNDECLARED_NEW_CORE` and `MX_MISBINDING` — is run through the full stack. Per-gate
  > detection rates are published with batch metrics. A gate that cannot demonstrate
  > detection of its own codes is downgraded and its code removed from release criteria
  > until redesigned. A failure code that has never fired is not a guard.

Failure codes: the Baumanns table (NOUN_SWAP, FORMULA_ONLY, COSMETIC_BACKBONE,
CUE_LEAK, CUE_OBSCURE, DEGENERATE_VALUES, UNDECLARED_NEW_CORE, GRATUITOUS_COMPLEXITY,
UNSOLVED_TARGET, REVERSED_AS_POSING, TARGET_GROUP_DRIFT, DISTRACTOR_MIMICRY,
FIGURE_TEXT_CONFLICT, SOURCE_COPY) **plus our measured ones**: `MX_MISBINDING`
(ISO08), `PARAPHRASE_MINT` (the 29k-proposal failure — new families obey the
granularity contract + singleton tripwire; explicitly extended to seed-driven family
minting), `SELF_CERTIFIED` (any gate consuming the author's own claim),
`MISTAGGED_CORE` (P1), `NEAR_DUPLICATE` (P6), `RENDER_UNVERIFIED` (P10),
`SEED_UNVERIFIED` (P12).

**Grammar instrumentation** (P2, verbatim):
> Each batch reports the joint mode × variation distribution and H(mode | V-class)
> over a rolling window. If H(mode | V) falls below threshold — mode has become
> predictable from variation class — the batch halts for grammar review. E8 (n=10)
> established key correctness only; the two-label grammar is unproven until this
> instrument demonstrates separation.

## 5. Chain of Evidence = the compiled diagnostic manifest

One record per released item (content-addressed, append-only):
bundle hash · condition ledger · backbone + mapping ledger · invariants /
anti-invariants · operator trace with per-change classification · blind solves (both
families) · gate results · mode label · difficulty vector + delta · the synchronous
`question_intelligence` block. This IS the patent's compiled manifest: every response
option bound to a learner-state interpretation or an honest `unresolved`, with
provenance to the specification.

## 6. Deployment: the user-facing pipeline

The corpus and protocols serve an interface through four frozen boundaries:

1. **Practice API** (deterministic, live today as `awm_engine.cli bank`):
   `practice_set(mx_id | learner_open_paths, band, transfer)` ·
   `cognitive_set(confusion_type, locus)` · difficulty-ladder sequencing over the
   2,226 ladder edges · every returned item carries uid, match level, evidence grade,
   facility, reasons. Sets are single-match-level; short sets state why.
2. **Item renderer** — stem + figures (real files) + options; for translated items the
   English surface with original retained; exam-ready formatting per the math-deploy
   standards.
3. **Generation queue** (this protocol): abstentions and gap entries become bundle
   jobs; released items flow back into (1) automatically. Target latency is
   asynchronous — the queue fills gaps between sessions, not mid-request.
4. **Evidence surface** — per-item cards (verbatim + computed only) and per-set
   provenance, so a teacher can audit any served set without repository access; the
   response write-back obeys P8 (selected_option is never converted to an inferred
   path in attested fields).

Learner-state inference remains Grade-A-gated (748 items) until real response data
upgrades grades — served practice is labelled by grade, never laundered.

**Pre-serve requirements** (P11, verbatim — none of §6 goes live without all four):
> (a) a recall path — quarantine by content hash, removed from index and all future
> sets, recall event and reason code appended to the manifest, recall lookups answered
> by the practice API; (b) provisional mapped Mx ids graduate only by examiner
> re-adjudication at the 500-item audit or response-data confirmation at ≥30 responses
> consistent with the predicted misconception signature; provisional ids are excluded
> from `cognitive_set` serving and flagged in analytics; (c) retrieval ranking
> deterministically prefers higher evidence grade within (family, rung,
> representation) — generated items fill holes, never displace attested members —
> rule version recorded in set provenance; (d) a named human adjudicator of record
> with a stated throughput SLA per batch.

## 6b. MathNet enablement (P12 — tracked annex, staged, no stage skips)

MathNet's 25,608 items are **bundle-ineligible by default** (no isomorph_seed) — the
correct fail-closed state, stated here so demand pressure cannot route around it by
minting 25k seeds the way 29k paraphrase families were minted. Stages, in order, no
stage begins until the prior stage's instrument reports:
1. **Schema first** — extend the seed schema for multi-solution invariants (which
   solution classes survive a variation) and figure-spec retro-extraction fields.
2. **Pilot extraction, two-family** — stratified ~300 items; extractor + independent
   re-extractor; structured fields compared mechanically; per-field agreement published.
3. **Scale extraction** only at demonstrated agreement above threshold; every derived
   seed stamped with evidence grade; unverified seeds bundle-ineligible
   (`SEED_UNVERIFIED`).
4. **Registry mapping** in adjudicated batches under the granularity contract +
   singleton tripwire; nothing auto-mints.
5. **Eligibility switch** per item, gap-driven targets only, full gate stack, E6
   sampling per batch; scale by measured gate-detection rates (P9), never backlog size.

## 7. Quality cadence

- E6-style cross-family sample per generation batch (stratified over variation
  classes); acceptance rate + adjudications on the record.
- Every 500 released items: a granularity re-audit of newly minted mapped families
  and a duplicate-hash sweep.
- Metrics portfolio (never one similarity score): blind-solve pass rate, mode-label
  accuracy vs mechanical check, ambiguity failure rate under adversarial review,
  distractor mechanism-match rate, self-rejection precision, human acceptance on
  sampled cards.


---

## Tightening amendments (2026-08-09, gold-sweep folds)

**P9 executable suite contract (harness shape imported from
`v6-hybrid/regression_gates_test.py`, verified 22/22 by the sweep; labels NOT
imported — coverage is the 21 ISO failure codes, never legacy analogy):**
> The suite manifest is versioned: `{suite_version, protocol_version, cases[]}`, each
> case `{case_id, failure_code (exact ISO enum), fixture_hash,
> seed_transform_version, expected_gate, expected_verdict, control_kind ∈
> {SEEDED_DEFECT, KNOWN_GOOD}, source_provenance}`. ≥1 SEEDED_DEFECT per ISO failure
> code and ≥1 KNOWN_GOOD per affected gate. The runner exercises the PRODUCTION audit
> stack, emits `{gate, failure_code, caught, total, rate, escaped_case_ids,
> false_positive_control_ids}`, and exits non-zero on any escape, any rejected good
> control, any missing code, or any code/gate mismatch.

**Difficulty-design vector (imported from LamportEngine ASSESSMENT_GRAIN_DESIGN §7
with its calibration report's corrections):**
> Every source and generated item records ordinal 0–3 coordinates
> `V=[H,T,S,R,E,M,C,U]` (hinge depth · transfer distance · decision depth ·
> representation transformation · response construction · misconception competitors ·
> construct-relevant computation burden · cue removal). `T` is always relative to a
> declared `instruction_reference`; without one it is `null`. **No scalar sum is
> permitted.** A declared `difficulty_delta` names the changed coordinates and proves
> the unchanged ones preserved. Numeric success bands live in the versioned PROFILE
> R7e parameter table, never in this core. Every form stays `UNCALIBRATED` until
> fixed-form response evidence satisfies G6/P8.

**LLM Task Cards (Kimi tightening pins 1–6, folded verbatim — see
`tightening/TIGHTENING_REPORT.md` for full texts):** every model call in this
protocol's pipeline carries a registered task card; cards are one-judgement or
one-artifact class with a linter at admission (checker arity = task arity); budgets
are measured per card version (p95 × 1.5, never truncate — reject); the author runs
as three staged artifact cards (A1 SOLVE / A2 MAP+POSE / A3 RENDER) with typed seams,
backward defect-report edges (max 2 returns then human), ledger-sufficiency and
selection-reason-replay seam checks; E5 matching is retrieval-then-select with
margin-rule abstention calibrated on the 29k-paraphrase registry; the examiner card
computes everything computable deterministically first and splits correctness into a
separate single-judgement card; every checker/repair/retry call is itself a
registered card before the gateway enforces.

---

## v1.2 — REPRESENTATION-FIRST LAYER (2026-08-10; governs over any weaker retained text)

**Origin:** owner verdict on generation quality (E8 ten GOOD; LbS 48 NOT
DEPLOYABLE; FIG01 waves figure physically wrong though the machine audit accepted
it) + owner directive to integrate Multiformat, Multirepresentations-in-physics,
and thinking-path-as-metadata via PRISM-style diagnosis. Derivation chain:
`reports/isogen_v2/` — CODEX_CRAWL_BRIEF → EXTRACTION + FIGURE_FAILURE_ANALYSIS +
DISCARDS (measured, quoted) → FIRST_PRINCIPLES (Fable; contains the corrected
hypothesis record) → ISOGEN_V2_DESIGN (draft 3) → Codex adversarial R1 (SIGN: NO,
16 pins) → draft 2 → fold-audit R2 (SIGN: NO, 4 integration blockers) → draft 3 →
R3 **SIGN: YES** (design-level contract; capacity/latency/coverage pending the
capped pilot). Kimi counter-sign: pending rate-limit clearance.

**The three-layer law (spine):** `backbone_fidelity ≠ representation_fidelity ≠
interaction_evidence_validity` — all three can fail independently; FIG01 passed
the first and failed the other two. A newly realized representation is a NEW
SCIENTIFIC CLAIM whose referent is a semantic contract derived from one verified
canonical solved state — never the author's prose.

The normative amendment text follows verbatim from the signed design.

### Amendments A–I (signed text)

Pins from Codex R1 are folded verbatim where they are the normative text.

#### A. §1 — three binding fidelity verdicts [Pin 1]

Every released item SHALL carry separately schema-validated `backbone_fidelity`,
`representation_fidelity`, and `interaction_evidence_validity` verdicts, each with
executor class, evidence hashes, execution receipt, and failure codes. No verdict
record may satisfy another layer; release is the logical AND of all applicable
verdicts, and `NOT_RUN` or `UNVERIFIED` is release-blocking. An author-assigned
mode label (`FAITHFUL_TRANSFER` etc.) is a claim about backbone fidelity only and
is never evidence for the other two.

#### B. §3 A2 — representation-first decomposition + diagnosis

Emitted in order before any candidate posing (card arity per §H below):

1. **Mechanism core** — smallest causal structure with boundary conditions and the
   relational backbone (preserve relationships, never nouns).
2. **Representation ledger** — for source and target: representation type,
   semantic payload, construction grammar, known misreads, translation edges (both
   directions). Hybrids whose graphical line can be mistaken for a literal
   physical path are resolved or rejected here. **Every ledger row SHALL cite the
   source or target artifact it describes** [Pin 2].
3. **State derivation** — Mastery; Mx by SYSTEMATIC CORRUPTION of the mechanism
   (omitted condition, reversed link, substituted term), never reverse-engineered
   from distractors; explicit LoK; observable predictions per representation.
4. **State × Response Field matrix** — falsifiable observable per cell. **Every
   claimed state-pair separation SHALL carry an executable or independently
   reproduced observable witness. Field labels are normalized to
   evidence-operation signatures; renamed or repeated signatures collapse to one
   field unless new separability is demonstrated** [Pin 2].
5. **Epistemic job + evidence mode**, separate from variation class.
6. **Gaming pockets + closure fields** — cheap success routes and the smallest
   field/contrast closing each.

Format binding LAST: cheapest response channel whose diagnostic ceiling covers the
claim the matrix requires; format variety is never an objective.

#### C. §3 A3 — verified canonical state and typed realization

1. **Canonical solved target state — verified, not merely present** [Pin 3]:
   before any representation contract is accepted, the target state SHALL be
   independently recomputed or validated against a **registered domain schema**
   that includes boundary class, field/quantity identity, reference/coordinate
   conventions, and applicable invariants as well as numbers. Missing required
   state dimensions are `UNVERIFIED`, not author discretion. (This is the Attack-3
   fix: a numerically rich but semantically thin state — no field identity, no
   boundary class — can make every pane consistently wrong; ancestry is not
   truth.)
2. **Typed realization boundaries** [Pin 4]: figure production SHALL use
   `canonical_scene → resolved_scene → rendered_artifact` boundaries (MCP-G10
   import); only a frozen resolved scene and declared backend/style profiles are
   renderable. Backend invention, unsupported required features, or failed
   independent parse-back/conformance blocks release. Curve realization is
   governed by the resolved scene and backend profile — exact graph-equation
   definitions or declared approximations under the tolerance policy of §D; the
   draft-1 blanket polyline rule is superseded.
3. **Per-representation semantic contract**: entities, relations, required visual
   claims (boundary-condition glyphs, axis/quantity/units declarations, phase
   statements), marks/labels, forbidden cues, verification mode per claim. Empty
   required lists on a diagnostic figure are a hard failure. **A visual
   representation and its accessibility alternative form ONE representation
   package carrying equivalent evidence without either donating the target
   answer** [Pin 9].
4. **Target-native distractors and hints** rebuilt from the corrupted mechanisms
   in the target representation; anchor sentences are never option text.

#### D. §4 — gate G9: representation fidelity (split executors, owned tolerance)

- **G9.1 functional geometry** — deterministic comparison of the rendered path
  against the resolved scene. **Item authors and renderers SHALL NOT set
  tolerance. A versioned domain-family/backend policy SHALL define exact logical
  and topological predicates separately from scale-normalized render error,
  preserve theorem/physical class, and require adaptive or error-bounded
  comparison rather than a fixed universal sample spacing or epsilon** [Pin 5].
  Topological predicates (crossing/tangency structure, traversal direction,
  extremum/node slope classes) are evaluated as predicates, not distances.
- **G9.2 domain visual grammar — two cards + reconciliation** [Pin 7]: one blind
  card derives and freezes the domain checklist from the mechanism and
  representation type BEFORE receiving the author contract or render; a different
  single-judgement card inspects the rendered artifact against that checklist.
  Checklist and author semantic contract are then reconciled claim by claim;
  every omission or disagreement produces adjudication or failure.
- **G9.3 evidence contribution** — at least one matrix-required field derivable
  only from the representation PACKAGE (visual + accessibility alternative, per
  Pin 9); text-redundant packages fail unless redundancy is a declared,
  independently approved purpose. **Modality alternatives never count as
  independent corroboration of the same evidence operation** [Pin 9].
- **G9.4 leak scan** — exact numeric/string leaks are deterministic; paraphrase,
  visual-implication, and accessibility-equivalence leaks route to an M2/H
  judgement card [Pin 6]. Titles, accessibility text, prompts, and option texts
  must not donate the target observation.
- **G9.5 fail-closed observation** — any load-bearing element the verifier could
  not directly observe is `UNVERIFIED` → fail. Inference from remaining character
  budget is forbidden.
- **Executor honesty** [Pin 6]: a gate may be marked `[D]` only when versioned
  code computes the declared predicate from typed non-authoritative inputs and
  emits a positive execution receipt. Semantic necessity, paraphrase leakage, and
  other uncovered classes route to a separate M2/H judgement or fail as
  `UNSUPPORTED`; an empty result is never proof that the check ran.
- **Calibration on classes, not fixtures** [Pin 8]: known-good controls, seeded
  defects, AND held-out mutated/adversarial variants per registered figure
  family; fixture identity and surface tokens unavailable to the production
  checker. An unregistered family, or one without demonstrated held-out
  detection, remains human-only and cannot inherit another family's calibration.

#### E. §4 G5 — blind the mechanism, not only the mapping [Pin 10]

The examiner SHALL derive the target mechanism, boundary conditions, corruptions,
and observable predictions from the EXAMINER bundle before receiving the author
mechanism or option mapping. Author and examiner artifacts are compared by
content-addressed claims; a missing or divergent condition is an adjudication
event, and the author mechanism is never the sole input to G5. Surface-cue
options (keyword-matchable without running the model) fail.

#### F. §5 — executable provenance and honest metadata [Pin 11]

Every derivation edge SHALL record transformation identifier, code/rule version,
input hashes, output hash, and successful recomputation receipt; pointer-only or
author-declared `derived_from` links do not satisfy G7. The manifest carries: the
verified canonical state + schema version; the matrix with witnesses; per-package
semantic contracts and G9 verdicts; epistemic job, evidence mode, format-ceiling
arithmetic; open pockets + closures; the diagnostic ceiling; and thinking-path
metadata — which **remains a pre-deployment prediction until shortcut replay and
later response-process evidence support it**.

#### G. §6 — interaction contract and serving provenance [Pins 12, 14]

- **The interaction contract SHALL be an executable state/dependency graph whose
  reachable reveal, assistance, retry, navigation, accessibility, and version
  branches are traversed in test. Taint propagates transitively through semantic
  prerequisites** (revealing `λ=2d` taints a downstream frequency field exactly as
  revealing λ numerically would), **and diagnostic eligibility is computed
  server-side before the interaction verdict is issued** [Pin 12].
- **Event storage SHALL use server-issued immutable item-version, field, and
  evidence-operation IDs and record the full pre-response visible set,
  assistance/reveal history, and taint ancestors. The observed field event is
  stored separately from any learner-state posterior; `fold_profile` rejects
  missing or unknown provenance and cannot clear taint across sessions** [Pin 14].
  (Draft 1's "the matrix row" phrasing was a type error — an event is a field
  observation; states are the other matrix axis.)
- Interactive-figure formats (dropdown/drag on figure) are gated per figure
  family: a family becomes eligible only after its G9 calibration (Pin 8) shows
  held-out detection, and item-level G9 + the interaction verdict still apply to
  every item. Family calibration is a precondition, never a substitute.

#### H. §7 — meaningful independence and honest capacity [Pins 13, 16]

- **A confirmation unit counts only when an examiner records a meaningful change
  in normalized evidence operation and shows a different state-separation or
  shortcut-closing witness. Format, context, representation, or field-name
  changes are cosmetic when the operation, response logic, and cheap success
  route remain the same** [Pin 13]. (Restores the Set gate's "meaningful", which
  draft 1 dropped.) Misconception diagnosis at set level needs 2 independent
  units, one separating LoK from Mx.
- **Card arity — split-card contract selected** [Pin 16, R2 blocker R1 closed]:
  the six B artifacts are six separately typed, separately budgeted cards. There
  is no composite branch. Coalescing required artifacts, exceeding calibrated
  card budgets, or truncating a load-bearing artifact **halts the batch**. (Draft
  2's per-batch composite exception is withdrawn: it contradicted the halt rule,
  had no component-level schema/receipts/truncation test, and invalidated the
  capacity arithmetic.)
- **Budget before scale** [Pin 16]: v2 SHALL begin with a capped pilot and
  publish per-card count, tokens, latency, retry/revision rate, G9 family
  coverage, and human-review queue against a named SLA. With the split-card
  contract fixed, Codex's capacity model holds unconditionally: ≥2.67× author
  work-units vs v1.1 → plan 12–18 released items per baseline-sized run, not 48.

#### I. Cross-cutting — status vocabulary, truth table, precedence [Pins 1, 6, 15; R2 blockers R2–R4 closed]

**One status vocabulary** governs every gate, layer verdict, batch denominator,
and admission decision: `PASS | FAIL | NOT_RUN | UNSUPPORTED | UNVERIFIED`.
Every result includes tool/version/input/output receipts; missing fields, empty
defaults, or zero violations without execution are not PASS. (The campaign has
already paid for this lesson once: the OCR zero-violations false-clean.)

**Closed truth table:**

1. An item is admissible only when EVERY applicable required gate is positively
   executed with status `PASS`.
2. Every other terminal status — `FAIL`, `NOT_RUN`, `UNSUPPORTED`, `UNVERIFIED`
   — blocks the layer verdict that owns the gate, and a blocked layer verdict
   blocks release. No aggregation step may exclude an applicable non-PASS result
   from the admission conjunction; "counts only positively executed gates"
   governs metrics denominators, never admission.
3. A layer verdict (`backbone_fidelity`, `representation_fidelity`,
   `interaction_evidence_validity`) is PASS only when all its applicable child
   gates are PASS; it can never be asserted directly.

**Backend scope** [closes R3]: retained P10 currently restricts release to
SVG-capable backend profiles — every served figure must have the SVG render
proof. A non-SVG MCP backend profile requires a per-backend P10 equivalent
(rasterization + parse-back + conformance) to be specified and calibrated BEFORE
that profile becomes releasable; any conversion to SVG is itself a derivation
edge needing recomputation receipts (§F).

**Precedence** [closes R4]: v1.1 text survives only where not amended or
superseded by §§A–I; where retained text and an amendment both apply, the
stricter applicable rule controls. "G0–G8 unchanged" in §3 means their
IDENTITIES and positions are unchanged; §E strengthens G5 and §F strengthens G7,
and those strengthened forms govern.

#### Imported frozen source (scope-caveated)

`PT-LMS_fresh_workspace/supplementary/Mathematical_Construction_Protocol_Agent_First_MCP_G10_v1_2_Frozen.md`
supplies the `canonical_scene → resolved_scene → rendered_artifact` architecture,
backend capability declaration + refusal, separated logical/render tolerances, and
release conjunction. Its architecture generalizes; its school-mathematics domain
library does NOT certify physics — physics figure families need their own
registered schemas and held-out calibration before any machine verdict counts.

#### Next stage gate

No batch beyond a **capped pilot (12–18 items, per §H telemetry against a named
SLA)** until the pilot publishes its numbers. Interactive-figure formats stay
deferred per §G until at least one figure family passes held-out G9 calibration.

#### Knowledge base (standing owner directive 2026-08-10)

`ISOGEN_KNOWLEDGE_WIKI.md` is the persistent, growing record of what worked
(WP-n) and what failed (FP-n), the owner review log, and run history. Every
generation run, owner review, and audit gap appends there; examiner briefs and
calibration fixtures cite WP/FP ids; owner findings outrank machine closure and
each becomes a named pattern + seeded fixture.

---

## v1.3 — LEARNING-PURPOSE + TOURNAMENT LAYER (2026-08-10; governs over any weaker retained text)

**Origin:** owner directive — tighten and focus; central question "what learning
means" for ISO-GEN and LbS; always ≥2 candidates, choose the best; recall
LamportEngine, PRISM, Lamport-style metadata; NETFLIX team-of-experts process.
**Panel record:** `reports/isogen_v3/` — FABLE_POSITION → KIMI_PANEL_R1 (ACCEPT
WITH PINS P1–P14) + CODEX_PANEL_R1 (ACCEPT WITH PINS 1–15, max effort) →
ISOGEN_V13_SYNTHESIS (4 divergence resolutions + signed pin amendments) → Kimi
SIGN: YES (R2, reconfirmed R3) → Codex refusals R2/R3 (carriage + five
integration gaps + CERTIFY level) each repaired → Codex SIGN: YES (R4).

**The normative v1.3 text is `reports/isogen_v3/ISOGEN_V13_SYNTHESIS.md` §§A–H,
including its §0.5 verbatim incorporation of both panel pin sets and the signed
pin amendments.** Summary of what it adds (the synthesis governs):

- **§A Learning charter** (also LBS_PROTOCOL §0): five fail-closed clauses —
  DIRECTED · EARNED (attribution: intervention_linked | caused_by under
  registered design only) · TRANSFERABLE-within-envelope ·
  PERSISTENT-over-horizon · CHECKABLE; claim ladder PROGRESS_EVIDENCE →
  SESSION_MASTERY → FAMILY_MASTERY → STABLE_FAMILY_MASTERY@delay →
  COMPOSED_MASTERY; grain declaration; ISO-GEN certifies instruments
  (PASS_PRETEST), never learning; the isomorph family is the transfer
  measurement apparatus; full guardrails Item Contract + CTR-001 +
  learning-purpose fields, response_format_constraints at request time.
- **§B Tournament**: k ≥ 2 universal floor (never reducible); plan_prune must
  leave ≥2 finalists; per-candidate split cards and gates; tournament_select =
  deterministic versioned selection_policy over frozen admitted manifests
  (coverage via predicted_family_coverage_delta with pinned set-function, then
  parsimony; bound-dominance; INCOMPARABLE semantics; hash tie-break);
  UNCONTESTED survivor = admitted, serve_eligible=false,
  family_founder_eligible=false, non-indexable/non-servable until a two-passer
  tournament, tripwire + re-tournament obligations; runner-up banking via
  set-level independence verdict, GOLD_S only.
- **§C Lamport derivation DAG**: a view over existing A/B/G artifacts (no
  parallel pipeline); 11-field witnessed events typed A0–A3; A1+ falsifiable
  from whitelist-projection inputs alone; format binds per candidate.
- **§D Judge qualification** (NETFLIX fold): card registry with strata, expiry,
  SHADOW/TRIAGE/BLOCK_ONLY/CERTIFY permissions; GOLD_R/E/P/S with split
  discipline; false-pass-led metrics; evidence capsules; adaptive inference
  (disagreement → UNVERIFIED → human, never averaged); failed executor loses
  permission never the requirement (supersedes the retained v1.2 §P9 sentence).
- **§E Vocabulary crosswalk**: five gate states unchanged; v1.3 supersedes
  "and admission decision" in v1.2 §I scope wording; item decisions
  PASS_PRETEST | REJECT | REQUIRE_HUMAN_ADJUDICATION (canonical; aliases
  declared); post-empirical PASS_OPERATIONAL | REVISE | QUARANTINE_FAMILY;
  UNKNOWN maps by cause; NOT_APPLICABLE = plan-level with receipt.
- **§F MLD boundary**: NOW coupling_context provenance +
  structural_downstream_reach (PREDICTED, request-stage queue prioritization
  only) + intended-vs-observed transition telemetry loop; LATER (A3_EMPIRICAL)
  modes, free-energy calibration, costate λ.
- **§G Pilot economics**: 12–18 counts fully realized CANDIDATES (≈6–9
  tournaments); full counter set; 100% human final review; judges SHADOW.

---

## v1.4 — INVARIANT AUDIT LAYER (2026-08-11; governs over any weaker retained text)

### Why this layer exists

v1.2 and v1.3 verified that a variant is *well-formed*: the figure compiles, constraints
are non-vacuous, the answer is blind-derivable, k≥2 candidates compete. The v2 build
proved that is not sufficient. Three items cleared every one of those gates and were
still wrong as isomorphs — because a structural edit can remove the very effect the
source assesses, and no mechanical gate was looking at that.

The corpus already holds the missing check. Every phy500 record declares, in
`generation.isomorph_seed`, an **invariants** list ("must survive for a variant to remain
the same question") and a **manipulables** list ("free to vary", including named
*structural* variations the author of the source explicitly sanctioned). ISO-GEN was not
reading them.

### G-INV — the invariant audit (blocking)

Every candidate carrying a structural edit (V9–V12) MUST emit an `invariant_audit`: one
row per declared source invariant, each labelled from the closed set

| status | meaning | release effect |
|---|---|---|
| `PRESERVED` | the invariant still holds in the variant | admits |
| `DELIBERATELY_VARIED` | broken **and** named in the source's own `manipulables` | admits; the note must cite which manipulable sanctions it |
| `BROKEN` | broken and NOT sanctioned | **blocks release as an isomorph** |
| `NOT_APPLICABLE` | the invariant has no image in the target representation (V11 only) | admits with a recorded note |

A candidate with any `BROKEN` row may still be admitted **to the bank** as a
`GENERATIVE_EXTENSION`, but it MUST NOT be served as a variant of its source, and it
MUST carry an `audit_note` stating plainly which invariants it drops and what that
narrows about the construct being assessed.

Where a source declares no `isomorph_seed` (all MathNet records today), the audit is
recorded as unavailable — never as passed. Silence is not a green light.

### The failure this catches: rearrangement that destroys the construct

> *A structural edit must leave the construct's mechanism running.*

Changing the topology so the assessed effect **no longer occurs** does not produce a hard
variant; it produces an empty one. Two worked cases from the v2 build:

- A voltmeter-loading item rewired series → parallel. The reading becomes `E` regardless
  of `r`: loading has vanished, so nothing is assessed. The source's own first invariant
  says so in as many words.
- A charge-redistribution item switched so one capacitor is isolated. Nothing
  redistributes, nothing dissipates, and the invariant "the energy loss is independent of
  R" becomes vacuous.

Both are legitimate **contrast items** — useful for testing *when* a formula applies — and
v1.4 recognises that as a distinct product, `CONTRAST`, which is never served as an
isomorph and must be paired with the item it contrasts against.

### G-TIDY — answers whose form carries a signal

Where a source invariant constrains the *form* of the answer (P277: "values should be
chosen so the node potential is a tidy number; an untidy answer usually means a polarity
has been read wrongly"), the variant must satisfy it. An untidy answer in such a family
is not cosmetic: it tells a correct student they have made an error. Re-parameterise
until the form is right, and additionally require that no branch/element current is zero
and that no two are equal, so that no given is inert and no two results can be confused.

### G-SELF — figures must be recompilable from the record alone

A stored figure MUST carry `tikz_libraries` and `extra_packages`. In the v2 build all ten
figures compiled at authoring time and none could be rebuilt from the stored record,
because `circuitikz` was supplied at validation and never persisted. For a system whose
premise is *"alter the code to obtain a new variant,"* a figure block that cannot be
rebuilt from itself is not encoded at all. Validation MUST recompile from the stored
block, not from the authoring context.

### G-EYES — the figure must be looked at (blocking)

`render_gate: PASS` certifies a figure is **well-formed**, never that it is **the right
figure for this stem**. In the v2 build all ten figures passed the gate and seven were
defective on inspection: two omitted the measuring instrument the item was about, two
printed their own answer, two carried construction inherited from the source's proof that
the new stem never references, and one carried an orphan symbol positioned so it read as
half the quantity asked for. None of these is detectable by compilation, constraint
evaluation, or vacuity testing.

Author and checker MUST each open the rendered image and record two judgements:

1. **Completeness and exclusivity** — every element the stem names is drawn, and nothing
   else is. Construction inherited from the source's proof is not neutral: it asserts a
   different argument.
2. **No answer leak** — the figure must not contain, print, or be drawn at its own answer.
   Where an item is an inverse (V12), add a constraint that *forbids* the drawing from
   sitting at the answer configuration, with the reason recorded. This is the converse of
   the deletion rule for inherited answer-pinning constraints: delete the ones that pin
   the SOURCE's answer, add ones that forbid pinning the NEW one.

Marking obeys the same division: mark what the stem **gives**, never what the student must
**supply**.

Any figure edit invalidates every blind verification run against the previous code. Clear
and re-run — a verification is a statement about a specific figure, not about an item.

### G-SERVED — check the page, not only the figure (blocking)

Inspecting a rendered PNG proves the *figure* is correct. It says nothing about what the
*page* draws. `pdftocairo -svg` names every glyph `glyph-0-0`, `glyph-0-1`, … in every
file it writes, and numbers clip paths the same way; inline two such figures into one
document and each `<use href="#glyph-0-0">` resolves to the first definition on the page.
Figures after the first then draw letters borrowed from an earlier figure — an `R` served
as a `V` — while every upstream gate reports PASS.

Before release, fetch the served HTML and assert: **zero duplicated `id` attributes and
zero dangling `#` references.** Any inliner must prefix every `id`, `href="#…"` and
`url(#…)` per figure so each SVG closes over its own defs.

### G-DEFER — a stem may not defer to what the figure cannot say

Where a stem instructs the student to read something *off the figure* ("taking the cell
polarities from the figure", "from the graph", "as marked"), that fact must be
unmissable at render size. A component symbol whose distinguishing feature disappears
when scaled — circuitikz `battery1`'s long and short plates are the found case — leaves
the question unanswerable while compiling cleanly. Draw the distinguishing feature
explicitly, add the sign or the label in text, and hold it with a constraint.

Related, and checked at the same time: a label attached to a point that lies **on** an
axis or rule must be moved clear of that rule, not merely offset from the point; and
rails or construction lines must not extend past the last element they connect, because
a wire going nowhere reads as a connection that does not exist.

### G-PROSE — the build logic is unverified text and must be re-read

Every other gate examines figures, constraints and answers. Nothing checks the prose, yet
the `edit` and `why_not_superficial` fields *are* the justification for calling a
candidate an isomorph. A v2 item recorded "the source joins C to the trisection points of
AB" when the source joins a different point to them and asks for a different quantity —
the item and its answer were correct, the account of what changed was not. Re-read both
fields against the source stem before release, and treat a wrong description as a
blocking defect: a variant whose rationale is false cannot be audited by anyone else.

---

## v2.0 — DIAGNOSTIC PROBE LAYER (2026-08-12; governs over any weaker retained text)

**Origin:** owner directive to revise ISO-GEN against two documents that turned out to be
the same finding from opposite directions — `reports/MDA_LESSONS_FOR_DIAGNOSTIC_ISOGEN_2026-08-12.md`
(the Model-Discovery-Agent adaptation) and `reports/iso-gen items audit.txt` (an
IIT-JEE-Advanced/Olympiad examiner's clinical audit of the v2 items: engineering
exceptional, assessment level JEE Main, three named gaps).

**Panel:** three experts, independent round 1 then adversarial cross-examination —
Fable (max thinking), Kimi-k3, Codex gpt-5.6-sol (ultra). **Kimi SIGN: YES** (conditional
on four folds, all folded). **Codex SIGN: YES.**

**The normative v2.0 text is `reports/isogen_v2_revision/ISOGEN_V2_SYNTHESIS.md` §§1–11.**
Panel record: `PANEL_BRIEF.md` · `fable_r1.md` · `kimi_r1.md` · `codex_r1.md` ·
`PANEL_BRIEF_R2.md` · `kimi_r2.md` · `codex_r2.md`.

### Why this layer exists

v1.4 verifies that a variant *preserves the construct*. It has no notion of whether the
variant *distinguishes* mastery from a named misconception from a missing prerequisite.
Every one of the ten v2 items passed every gate and none declared a single hypothesis pair
it could separate. The objective function changes from fidelity subject to gates to
expected diagnostic separation subject to the same gates, never fewer:
`argmax over x with all gates PASS of I(H; R_x | Q) / C(x)`. **Value of information ranks
admitted candidates; it never admits one.**

### What the synthesis adds (summary; the synthesis governs)

- **New gates** — `G-DQ` diagnostic query · `G-HYP` M-open hypothesis pool · `G-SIG`
  witnessed predicted response signatures · `G-SEP` state-pair separation ·
  `G-ACQ` VoI/cost strictly after admission · `G-RESIDUAL` · `G-PATCH` ·
  `G9.6 BOUNDARY-CARRIER` · `G-LAW-DELTA` / `G-OLD-OPTION` · `G-BOUND` · `G-COUPLE` ·
  `G-INVERSE` · `G-XREP` · `G-DMAP` / `G-DUNIQ` / `G-DGIVE` · `G-CI-HINGE` / `G-CI-CLAIM`.
  A fourth conjunctive release verdict, `diagnostic_design_eligibility`.
  **No gate is retired**; G5 is superseded by a strictly stronger generalisation of itself
  with its identity retained as the adjudication path.
- **The depth ladder** supersedes the flat V9–V12 list as the demand classification:
  `D0 parameter < D1 component < D2 topological < D3 inverse < D4 model judgment
  {constraint substitution · boundary interrogation} < D5 reciprocal domain coupling`.
  Representation transfer is an **orthogonal modifier**, never a rung and never a level
  claim. Only D4a/D4b/D5 (and D3 conditionally) may claim Advanced/Olympiad; D0–D2 never,
  whatever the algebra count.
- **`G-COUPLE`** = deletion-load-bearing ∧ **cross-domain dependency cycle** ∧ directional
  severing, computed on the domain-tagged equation set *before elimination*. Two problems
  in sequence are not coupled: `SEQUENTIAL_HANDOFF`.
- **Amended `NEW_CORE` trigger**: a new load-bearing **condition, governing relation,
  domain interface, or assessed goal-form**. Goal-form is tested by evidence-operation
  comparison against the parent.
- **Two products, one serving contract.** `depth_class`, `mode` and `product_role` are
  independent fields. A parallel-form request may be answered only with an attested bank
  item or a released `FAITHFUL_TRANSFER` / calibrated `DIFFICULTY_TUNED_ISOMORPH`. Any
  `GENERATIVE_EXTENSION` or `CONTRAST` in a parallel slot is refused by a deterministic
  filter — `EXTENSION_IN_PARALLEL_SLOT` — and the API returns the gap rather than
  substituting.
- **Misconception-mapped distractors** are executed corruptions with receipts, one
  mechanism per option, display-separated, FP-1 scanned, blind re-mapped. The corpus
  already holds the inputs: 453 of 500 phy500 records carry ≥2 fully mapped errors and 489
  carry an executable answer recipe. ISO-GEN had never read those fields.
- **Degraded-mode law for curriculum intelligence**: absent evidence narrows the claim, it
  never widens the licence and never waives a gate. Verified asset counts (which corrected
  the charter): only **695** typed hinges, **335 of 1,873** nodes carry objectives and none
  are maths, and **1,239 of 1,873** nodes have no aligned item.
- **`first_ingested_version_blind_pass_rate`**: freeze is a pipeline event, not an author
  declaration; < 7/10 halts the batch, 7–9/10 flags; per-card retry telemetry published
  alongside so laundering requires laundering two independent metrics.
- **`cue_dependence`** per item, from Kimi's announcement test: an item
  `ANNIHILATED_BY_ANNOUNCEMENT` may not be served with any hint that names its
  discriminating step.

### Corrections of record

The charter's own asset numbers were wrong and two of the three round-1 drafts inherited
them; Codex checked the files and was right on every count. The root agent's
"shared unknown proves coupling" test was refuted by both other panelists with the same
counterexample and replaced by the dependency-cycle test. The root agent's claim that the
ladder's top is structurally incapable of `FAITHFUL_TRANSFER` was too broad: it is the
*addition* of a law, domain interface or goal-form that makes an extension, not the rung.

---

## v2.1 — CALIBRATION & CLOSURE LAYER (2026-08-13; governs over any weaker retained text)

**Origin:** external IIT-JEE-Advanced audit of the v2 and v4 sets
(`reports/ISOGEN_AI_EXPLAINABLE_IITJEE_ADVANCED_AUDIT.md`). Both fatal findings were
independently verified before drafting: IG4-P3's `q = CBℓv` requires negligible
self-inductance (symbolically — with L > 0 the reduced ODE `mLq''' + (m/C + B²ℓ²)q' = FBℓ`
has oscillatory current, so the constant-acceleration key is strictly the L→0 limit); and
IG4-C3's convention mix was introduced by the build's own earlier repair.

**Partners:** Fable (draft, adjudication) · Kimi-k3 (engineering review, SIGN: YES).
Record: `reports/isogen_v21_calibration/` — DELTA_DRAFT → kimi_v21 → V21_SYNTHESIS (two
adjudications, both resolved to Kimi's position, on the record).

**The finding this layer answers:** the protocol conflated generation depth with student
difficulty. Depth classifies the EDIT; difficulty is a property of the SHORTEST valid
solution available to a prepared candidate. Ten of the audit's twenty-two item verdicts
turned on this gap — in both directions.

### 1. Two axes (E.1, E.3)

- `depth_class` — unchanged; generation provenance and class-gate index only.
- `difficulty_band` — from the target exam's `band_ladder` (JEE:
  `FOUNDATION | MAIN | MAIN_PLUS | ADVANCED | OLYMPIAD`), stamped by the **blind
  examiner** from the shortest valid solution it can produce, with
  `band_evidence: UNCALIBRATED | CALIBRATED` (CALIBRATED only via the sealed evaluation)
  and `band_receipt` referencing `examiner.shortest_solution`. **No receipt, no band.**
- `level_claim` / `level_claim_reason` are **RETIRED** (migration alias:
  `ADVANCED_DESIGN_CANDIDATE → band=ADVANCED, evidence=UNCALIBRATED` where no examiner
  band exists; an examiner band always supersedes the alias).
- `LEVEL_OVERCLAIM` fires when a claimed band exceeds the examiner band.
- **The v2.0 sentence "only D4a/D4b/D5 may claim Advanced; D0–D2 never" is RETIRED**
  (adjudicated supersession — the corpus falsifies it: IG2-003, a D2 edit, audits at
  Advanced-candidate level). Replacement: `depth_class ∈ {D0,D1,D2}` with band ≥ ADVANCED
  triggers `REQUIRE_HUMAN_ADJUDICATION` with a second blind solve plus a
  memorised-template search; the second band stands. High-depth/low-band needs no
  adjudication — the band governs.

### 2. Exam profile (E.2)

New top-level artifact per target: `exam_id, subjects, syllabus_topics, format_inventory,
band_ladder`. Every set declares `target_exam`. Subject ∉ profile ⇒ excluded from that
bank at build time; `target_exam: NONE` items stay buildable, never banked, never banded.

### 3. G-CONTRACT — the model contract before the stem (E.4)

Authored BEFORE the stem; **repairs edit it first**. Fields: `exact_laws, idealisations,
neglected_effects, approximation_order, parameter_domain, conventions, datum_ledger`.
Six checks:

- **C1 completeness** — all fields present; `N/A` requires justification.
- **C2 projection** — every load-bearing contract line appears in the student-facing stem
  or is standard in `exam_profile.syllabus_topics`. "Obvious to the author" is not
  standard.
- **C3 closure** — `examiner.unstated_assumptions` and `alternate_interpretations` must
  be empty or each entry absorbed into contract and stem. Closure is reconciliation
  against examiner output, never schema-fill. **D5 items enumerate the subject annex
  line-by-line** (physics: self-inductance, resistance, finite size, friction
  sufficiency, quasistatic, radiation, rigidity/pivot, ideal gas, heat loss; chemistry:
  standard state, ideality/activity, excess reagent, work-up, dominant product, constant
  pre-exponential) and list every coupling-interface relation with its enabling
  idealisations. Coupling multiplies hidden assumptions: the top of the ladder gets MORE
  closure scrutiny, not less. FAIL: `F-MODEL-UNSTATED`.
- **C4 exactness** — a non-exact `approximation_order` requires order language in the
  stem ("neglect terms of order ρ/R", "find the limiting value", …); the key never states
  an approximate result as exact; the requested quantity is defined over the stated
  regime. FAIL: `F-APPROX-AS-EXACT`.
- **C5 convention + enumeration** — one convention per quantity family across stem, key,
  units, options (`F-CONVENTION-MIXED`); the key enumerates every element the ask could
  be read to cover — "across the combination" is banned unless each element's value also
  appears (`F-ANSWER-AMBIGUOUS`).
- **C6 syllabus + datum** — `exact_laws ∪ examiner.syllabus_dependencies ⊆
  syllabus_topics ∪ stem-supplied relations` (`F-SYLLABUS-OUTSIDE`); the `datum_ledger`
  maps every stem datum to `used_in_step n | feeds_corruption X | independence_is_the_ask
  | REMOVE` (`F-DATA-IRRELEVANT`).

### 4. The examiner call, enriched not multiplied (E.5)

ONE blind call absorbs audit-G1, audit-G10, the shortcut review and the independent
examiner. Input: `student_visible` only — never the parent, edit summary, depth label,
pool, or intended solution. Output schema: `blind_answer, shortest_solution,
alternate_solutions, alternate_interpretations, unstated_assumptions,
syllabus_dependencies, shortcut_found` (checklist: units / sign / option shape /
all-of-the-above / figure measurable / special-value trivialisation / earlier-part
giveaway / memorised template / length-vs-reasoning), `scaffold_check, estimated_time,
difficulty_band, release_recommendation`. A figure repaired after a blind-solve failure
never counts as a native pass (standing). First execution 2026-08-13 on the four repaired
items: all keys matched, and the call surfaced a second closure tier — the instrument
works.

### 5. The student-facing projection (E.6)

`student_visible` is a DEFINED function of the record: the record minus `solution_path,
answer, diagnostic.*, invariant_audit, model_contract, figure.geometric_constraints`,
guard parameters, validation channels (SMILES et al.) and source comments. G-SELF
recompiles BOTH the record figure and the student render; G-EYES gains a third judgement
— nothing in the render that exists for build or validation. FAIL: `F-FIGURE-METADATA`.

### 6. figure_role, with a receipt (E.7)

`figure_role ∈ {load_bearing, supportive, none}`, receipted through `solution_path` steps
carrying `reads_figure`: load_bearing ⇒ ≥1 step cites the figure; supportive ⇒ stem
references it, no step reads it; decorative ⇒ delete or upgrade. This binds v1.2 G9.3
with the receipt it lacked — the gate existed and was not executed (IG4-C2), which is the
recurring failure this layer is built against. Figure specs gain `forbidden_entities`.

### 7. Format annex (E.8)

Per profile inventory. Multiple-correct: each option independently decidable; the correct
set must not depend on an unstated convention. Numerical: requested quantity and accepted
tolerance stated; rounding must not change uniqueness. Linked: each part answerable
without a correct earlier answer unless the format declares shared working. A positive
`scaffold_check` ⇒ restructure, declare `TEACHING_SEQUENCE` (not an exam item, no band),
or accept the examiner-rated band.

### 8. Tournament provenance binds the claim (E.9)

A band claim ≥ ADVANCED requires `tournament_provenance`: **≥3 gate-surviving candidates**
(minimal / boundary-or-inverse / coupled), each with its own examiner call, and a
selection record on the standing axes — economy, answer-form naturalness, checkability,
shortcut robustness. Practice bands may ship single-candidate: underclaiming is cheap,
overclaiming is not. (The v1.3 k≥2 universal floor stands; this raises the bar only where
a claim rides on it.) Elegance: `TARGET_INELEGANT` is a **flag** — it loses tournament
ties and reaches adjudication only for ≥ ADVANCED claims where the examiner exhibits a
cleaner natural target for the same construct. It is not a failure code (adjudicated).

### 9. Repair regression (E.11)

Any edit increments the item version and re-runs the full gate battery; if
`student_visible` changed, the examiner call re-runs. Repairs edit `model_contract`
first, then the stem, then re-derive key and distractors. **Satisfying the finding is not
finishing the repair** — the found case: the C3 repair satisfied its finding and created
`F-CONVENTION-MIXED`. Seeded fixtures (P9 standing): IG4-P3 ± the self-inductance line →
C3; IG4-C3 mixed convention → C5; IG4-P1 "least value" without order language → C4;
IG4-C1 SMILES in the student render → §5. Each must FAIL its named check; the repaired
versions must PASS all.

### 10. Verdict crosswalk — no fourth vocabulary (E.12)

`REJECT → REJECT` · `REVISE → REJECT + required_repairs` (resubmission is a new version) ·
`PRACTICE → PASS_PRETEST ∧ band < ADVANCED` · `ADVANCED_CANDIDATE → PASS_PRETEST ∧ band ≥
ADVANCED ∧ UNCALIBRATED ∧ tournament_provenance` · `CALIBRATED_ADVANCED` → sealed
evaluation only, never at build time. Audit codes retired as duplicates:
`F-DISTRACTOR-NONUNIQUE` = `AMBIGUOUS_ATTRIBUTION`; `F-DIAGNOSTIC-A0` = the standing §8
honesty rule. NOT folded from the audit, with reasons on the record: the 0–100 weighted
rubric (violates no-scalar-sum and score-is-not-a-verdict; three axes survive to the
tournament), shortest-solution difficulty as population truth (an examiner's shortest
path is a sample — bands stay UNCALIBRATED), abolition of supportive figures, the status
menagerie, universal three-candidate generation, and the 25-question prose liturgy.

### Net accounting

One new gate-artifact (G-CONTRACT, six checks) · one enriched call · three field families
in (band/evidence, exam profile, figure_role) · one retired (level_claim) · zero new
verdict vocabulary. Every audit gate has exactly one home. The count is roughly flat —
a protocol that only grows is itself a defect.

### World-model tie

`difficulty_band` is an A0 prediction of the assessment world model, calibrated by the
same sealed-evaluation machinery as diagnostic claims. Serving treats bands as labels
until calibrated; instrument divergences (recorded case: blind MAIN/MAIN_PLUS vs audit
ADVANCED on IG4-P1/P3) ride in the record for calibration to arbitrate, never averaged.
