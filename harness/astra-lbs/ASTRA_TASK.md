# TASK FOR GPT-6 ASTRA — proof-carrying LBS hint compiler

You are GPT-6 Astra. Design a **system**, not a prompt loop.

Do **not** propose calling an LLM once per wrong option of ~21,124 MCQs (~63k calls). That is forbidden.

Design a **Lamport-style structured-proof compiler** that uses TeacherTwin's **existing intelligence** (curriculum map, enrichment map, packed tags, Mx V2 library, ISO-GEN LBS protocol) as the floor. An LLM may be used only inside a **bounded, whitelist-projected slot** whose inputs are already compiled from that intelligence. Pedagogy the intelligence already holds must not be re-invented by the model (`bundle_breaches`).

Return:

1. Architecture (compiler, not generator).
2. Proof obligations and fail-closed gaps.
3. Exact data structures and joins (string equality / existing projection — no embeddings over the 46 MB source map).
4. Deterministic pipeline (numbered steps, no model).
5. Bounded LLM slot(s): when, packet, output schema, what it must not invent.
6. Instantiation: how a packed exam item + wrong letter becomes a hint **without** a model call, given the compiled library.
7. Concrete Python modules/scripts to add under `/home/harik/TTwin/tools/` and overlay schema.
8. Tests and owner-check gate (electrochemistry first; do not scale chapters until a human checks a packed sample).
9. How gold success cases would be *replayed* as proofs, and how NEVER failure cases would be *rejected* by a gate (not by taste).

Write as an implementable engineering spec. Include a compact JSON schema for `unlock_recipe.v1` and `hint_proof.v1`. Include a sketch of `tools/lbs_compile.py` (functions + control flow, not 2000 lines of filler).

---

## 0. Objective (owner)

A student sitting a Cambridge-style MCQ who picks a **wrong letter** must get a **hint that is a different, simpler question**. The hint tests the **intermediate step or mix-up (Mx)** that produced that letter. After the hint, they **retry the original** unaided. The original key is never shown on the hint. Mix-up type names stay off the learner paper.

This is Learn-by-solve (LBS) under ISO-GEN + IIP:

- Specification exists **before** the hint item.
- Diagnosis is a **lookup** wherever metadata exists (wrong option → misconception / intermediate gate → unlock question). No model call at runtime.
- I2: hint does not credit the original.
- I3: student produces the original answer after the explanation, not before.
- I20: needing a hint is not progress.

We already have ~21k packed MCQs with five-click tags. We must overlay `assessment.learn_by_solve.wrong[letter].followup` at **pack time**. Frozen exam.v1 is read-only. Live CHEMISTRY_MAP_V15.json is not rewritten. The ~46 MB comprehensive NCERT map is **never dumped into an LLM**.

---

## 1. Existing intelligence (the floor)

### Packed item (ttwin.question.v1)

Identity: `uid` e.g. `9701_m16_qp_12:q1`.

Five-click tags (not the uid): `pack`, `subject`, `big_idea_id` / `node` (chemistry hub e.g. `chem:C5/H-REDOX`), `chapter_id` (Cambridge e.g. `cam:9701:6`), `subtopic_id` (e.g. `AS_A:9701.6.1`).

Learner body: stem, options A–D, statements[], equations[], figures.

Assessment: `mcq_key` when extracted; examiner comments only if present (never invent).

Join to NCERT map is **not** `unit_id` on the packed item. Packed chemistry uses Cambridge ids. Map units use NCERT `unit_id` like `science/grade_11/chem_ch_207/H001`. TTwin `data/projection.json` already has `ncert`, `cambridge`, `ncert_by_node_band`, `grain`. Kernel `hinge_pack(unit_id)` joins enrichment by **string equality** on `unit_id`. Never embedding. Never dump `resolve_node`.

### Curriculum map (`data/maps/chemistry.json`, schema ttwin.map.v1)

523 units. Each unit:

- `unit_id`, `node` (e.g. `C5/H-REDOX`), `grade_band`, `chapter`, `chapter_title`
- `decision_hinge` (the construct)
- `mechanism`: `law`, `causal_direction`, `boundary_conditions`, `steps[]` (`step_id`, `step`)
- `cognitive_operation`
- `mx[]`: `{id, type, cwo, status}` where `type` ∈ Mx V2 seven:
  `term_substitution | condition_omission | relationship_reversal | scope_error | surface_feature_capture | mechanism_conflation | operation_confusion`
  `cwo` = canonical wrong output (a concrete wrong claim)
  status is usually `CANDIDATE` (not VALIDATED)
- `pedagogy`: `mastery_signal`, `lok_folk`, `gaming_pockets`, `facets`, `anti_narration`

Honesty: derived from NCERT comprehensive map; 46 MB blob is not in Pages.

**Gap you must handle:** some units have **empty** `mechanism.steps`. Fail closed for those units rather than inventing steps.

Example unit (truncated): `science/grade_11/chem_ch_207/H001`

- hinge: "Decide whether a reaction is redox by checking that oxidation and reduction occur together, not as isolated events."
- mx term_substitution cwo: "In Zn + CuSO4 → ZnSO4 + Cu, Cu²⁺ is oxidised (it gained electrons) and Zn is reduced."
- mx condition_omission cwo: "Zn → Zn²⁺ + 2e⁻ is a redox reaction."
- mx scope_error cwo: "2Na + Cl2 → 2NaCl is not a redox reaction — no oxygen is involved."
- mx surface_feature_capture cwo: "AgNO3 + NaCl → AgCl + NaNO3 is redox because a white precipitate appeared."
- mx mechanism_conflation cwo: "HCl + NaOH → NaCl + H2O is a redox reaction because a proton is transferred..."

H-REDOX has 29 units across several NCERT chapters (Redox Reactions, Coordination Compounds, Hydrocarbons, …). A Cambridge Electrochemistry item tagged `chem:C5/H-REDOX` + `cam:9701:6` is **not** automatically H004 coordination-entity OS. Token-overlap matching of hinge words into the stem is how the current overlay picked the wrong grain. Your join must be tighter.

### Enrichment (`data/enrichment/chemistry.json`, 543 items)

Types: activity, phenomenon, teaching_caution, representation, misconception, student_difficulty, probe, assessment, …

Roles: `activity_source`, `explanation_source`, `caution`, `assessment_source`, `misconception_distractor_seed`.

Each has `statement`, `node`, `serves[]` (list of `unit_id`), `readiness`, `citation`.

Join: `unit_id` ∈ `serves`. Only ~9 items currently sit on H-REDOX / H-ECHEM nodes. Thin enrichment is a **proof gap**, not a license to free-write.

### Mx V2 (seven types)

Used for teacher-key `mx_type` and T-MOD `modify_seeds`. Never printed on the learner paper.

### ISO-GEN LBS protocol (normative)

`awm_build/protocols/LBS_PROTOCOL.md` + `ISO_GENERATION_PROTOCOL.md` + TTwin `harness/80_ISOGEN.md`, `81_LBS.md`.

LBS first principles:

1. A hint is a question where the gate is a **move**; where the gate is a fact or a choice, the system **tells, then questions**.
2. A complex problem is a sequence of **difficulty gates**. Stored solution path = chain of moves; failure paths = known ways each gate defeats a learner.
3. **Diagnosis is a lookup** wherever metadata exists. Wrong option with mapped Mx names the trap; trap's anchor step names the gate; gate names the unlock question. **No model call, full audit trail.**
4. Mastery is on an isomorph, never the same item (I18 transfer is currently DARK on TTwin — do not claim family mastery).
5. Unlock pool assembly (RAG first, generation second):
   - corpus items whose family matches a failure path at a **lower rung**
   - corpus items sharing the step's construct at rung-1
   - if thin → tutorial_bridge **queued** as ISO-GEN (SPECIALIZE / DECOMPOSE_RECOMBINE / REPARAMETERIZE), **not** a silent LLM paraphrase of the option

ISO-GEN: specification-before-item; deterministic bundle assembly; LLM is poser/examiner on a **hashed bundle**, never on raw intelligence files. Author ≠ checker. Fail-closed gates G0–G6.

### Lamport engine (frozen L20 — do not rewrite)

Location: `/home/harik/raw/LamportEngine`. Frozen. New work is a **new TTwin pack-time overlay**, not a rewrite of L20.

Doctrine: an item is a **theorem**; the prompt bundle is its **structured proof** — named leaf/derived steps; each leaf is a **hash-bound element-level citation** into owned intelligence; derived steps are replayable rules; proof gaps **fail closed**.

The LLM receives ONLY a **strict-whitelist projection** (never the intelligence files) and may add **SURFACE** only. Any pedagogical element it introduces that the intelligence already holds is a failure (`bundle_breaches`). `gold/register/design_dna` are selection priors, not proof leaves.

Proof schema (already implemented): `Citation`, `LeafBy`, `DerivedBy` (rule_id + execution_sha256), `ProofStep`, `ProofGap`.

Author-may-not-add: target_state, misconception, distractor_mapping, discrimination_point, format, DoK, figure, remediation_route, elevation_pattern, synthesis_hinge, subject_fact_outside_grounding_payload.

Surface slots: stem_wording, grounded_scenario_instantiation, option_wording_from_locked_recipe, worked_solution_wording, feedback_wording_from_locked_remediation.

TTwin kernel **refuses model calls**. Legal AI slots are listed in `harness/15_SLOTS.md` (T-SEL, T-UNIT, T-AUTHOR, T-MOD, T-SOLVE, T-BRIEF, S-FEED). If you need a new pack-time compile slot, **name it, classify it, and keep it out of kernel runtime**. Runtime student-take is deterministic lookup of the overlay.

### Runtime already shipped (keep)

`js/paper.js` + `js/app.js`: wrong letter → hint (formats: single_mcq, true_false, multi_mcq, assertion_reason, match, fill_blank) → submit → **auto-return** to original with letter cleared + `why` of the hint. No "Original question: the key is".

---

## 2. History of hint development (failure vs success)

### Failure class F0 — taxonomy stamp (rejected)

Constructor always: follow-up key A; stems like "What did they drop?"; solve "The keyed choice is C: …". Irrelevant to the item. Owner: "template questions irrelevant to the question and the option."

### Failure class F1 — wrapper shape (rejected)

Catch-all stems counted as complete: "Which check is required?" → "fit this requirement" → "what this question is asking for" → "What is true of … in the situation the stem describes?" Structural JSON presence ≠ quality. `lbs_quality.is_wrapper_shape` now fails these.

### Failure class F2 — restating original A–D / leaking the key (rejected)

Follow-up reshuffled original key vs wrong clauses. Numeric follow-up leaked keyed value. I2/I3 violation.

### Failure class F3 — reprint of the clicked option (owner NEVER, recorded)

These were served. They must never be generated again. They restate text the student just read. They are not a task.

**NEVER `9701_m17_qp_12:q33` option C:**

> Option C is "2 and 3 only are correct". The numbered statement "The oxidation number of chlorine in a compound is negative." belongs in the correct 1 / 2 / 3 combination.

Parent item: which statements are *always* correct? (1) OS in a compound sum to 0 (2) Na in a salt is positive (3) Cl in a compound is negative. Key B = 1 and 2 only. Gate: statement 3 is not always true. Unlock: **calculate OS of Cl in HClO** (+1).

**NEVER `9701_m18_qp_12:q18` option B:**

> This option is "X: −2; Y: +4; Z: +6" and assigns "Y: +4". What oxidation number should that species actually have here?

Parent: sulfur burns → X (SO2, S +4); oxidised → Y (SO3, S +6); Y + water → Z (H2SO4, S +6). "That species" is unnamed. Unlock: **named species** SO2 or SO3 and its OS.

Banned stem shapes: `Option C is "2 and 3 only…"`, `belongs in the correct 1 / 2 / 3 combination`, `This option is "X: −2; Y: +4…"`, `What oxidation number should that species actually have here?`

### Failure class F4 — brute per-item LLM (forbidden by this task)

Would "work" locally and destroy audit, cost, and ISO-GEN specification-before-item. Also cannot dump the 46 MB map into the model.

### Success class S1 — gold `9701_m16_qp_12:q1` (owner approved)

Stem: "Which compound contains two different elements with identical oxidation states?" A HClO (key) · B Mg(OH)2 · C Na2SO4 · D NH4Cl.

Wrong B (scope_error): follow-up "Mg(OH)2 has two hydroxide groups. In each OH, what are the oxidation states of O and H?" Options include "O is −2 and H is +1…". Why: repeating OH twice is not two different elements sharing a state.

Wrong C (operation_confusion): "In Na2SO4, Na is +1 and O is −2. What is the oxidation state of S?" Key +6.

Wrong D (term_substitution): "What is the oxidation state of chlorine in NH4Cl?" Key −1 (chloride, not +1 as in HClO).

Pattern: **named species from that option**, **one missing calculation**, **does not reprint A–D of the parent**, **does not leak parent key A**.

### Success class S2 — spectroscopy overlay (hand)

e.g. `9701_s18_qp_11:q30`: follow-ups name Propanal C=O / carboxylic acid canyon / ester pair — diagnostic of **that option's spectrum**, not a reshuffle of the original.

### Success class S3 — thinking-prod after NEVER (electrochem overlay, partial)

q33 C now: fill-blank "In HClO, the oxidation number of chlorine is [[Cl]]" key +1.

q18 B now: "In SO2, the oxidation number of sulfur is [[S]]" key +4.

These are still **hand/heuristic templates** (`tools/lbs_electrochem.py`), not a proof-carrying join to map units. They are the quality bar for **surface**, not the architecture.

### Current constructor (`tools/lbs_construct.py`)

`unique_diff` on option clauses → mx_type heuristic → template follow-up. Completeness census 21124/21124 is **structural**, not electrochem-quality. Do not treat it as the target architecture.

---

## 3. Hard constraints

- Freeze exam.v1 read-only. Overlay pack-time only (`join_lbs.py`).
- Do not rewrite live V15 map. Do not copy mx type names onto learner papers.
- Do not dump the comprehensive map into the LLM.
- Chemistry tagged 9472 kept. Phy/bio mx empty — do not invent phy/bio hinges.
- Unique id is `item_uid`. Five-click tags stay.
- Do not scale beyond Chemistry AS/A Electrochemistry (`cam:9701:6`, hubs H-REDOX / H-ECHEM) until the owner checks a packed sample.
- Gold q1 and spectroscopy overlays are **preserve-uids**; compiler must not overwrite them.
- Kernel: no model calls at assemble/take time.
- New legal AI slot if needed: pack-time compile of **recipes**, not per-item authoring of 21k hints.
- Fail closed on missing hinge steps, missing mx match, thin enrichment: `ProofGap`, skip overlay for that letter, do not stamp a wrapper.

---

## 4. What "proof-based hint generator" means here

For parent item P and wrong letter L, the theorem is:

> UNLOCK(P, L) is a simpler question whose construct is gate G of hinge H, whose distractors (if any) are licensed by mx M or by a named intermediate omission, and whose surface instantiates only atoms present in P or in the cited map/enrichment leaves.

Proof leaves (hash-bound citations), examples:

- packed item fields: uid, node, chapter_id, subtopic_id, stem, option L, option key, mcq_key (key used in proof, **not** projected to the author LLM)
- map unit: unit_id, decision_hinge, mechanism.law, mechanism.steps[k], mx[id].type, mx[id].cwo
- enrichment item if used: item_id, statement, serves
- projection grain used for the Cambridge↔NCERT join

Derived steps (replayable rules, no LLM):

- JOIN_UNIT: tags → candidate unit_ids
- MATCH_MX: option L vs unit.mx[].cwo (and vs mechanism steps) → mx_id or intermediate_omission@step_id
- SELECT_RECIPE: (unit_id, mx_id or step_id) → unlock_recipe
- INSTANTIATE: recipe slots filled from P (formulas, species, numbered statements) by deterministic extractors
- PROJECT_LEARNER: strip mx_type, parent key, reprint of option L
- QUALITY_GATE: not wrapper, not NEVER reprint, followup_ok, no parent key leak

LLM (if any) only:

- **Compile recipes** for a **hinge unit** (or a cluster of units sharing a decision_hinge pattern) from the whitelist projection of that unit + its mx cwo's + enrichment probes. Output = `unlock_recipe.v1` library, human-checkable, hashed, reused across all exam items that join to that unit.
- Optional **examiner** slot on a recipe (not on each exam item): would this recipe's surface, instantiated on a fixture, catch the cwo?

That is how 523 chem units × ≤7 mx becomes a **few hundred recipes**, not 63k LLM calls. Instantiation across 21k items is code.

If a recipe cannot be instantiated for an item (missing named species, empty steps), **gap**, do not call the LLM "just this once" as a back door to brute force.

---

## 5. Electrochemistry-first scope

Packed: chapter_id `cam:9701:6`, pack `senior_11_12_as_a`. ~213 keyed items. Hubs `chem:C5/H-REDOX` (AS_A:9701.6.1) and `chem:C5/H-ECHEM` (AS_A:9701.24.1).

Map: 29 H-REDOX + 24 H-ECHEM units.

Your join story must explain how `cam:9701:6` + stem about cryolite / FeC2O4 / Cl always-negative / sulfur combustion maps onto the **correct** unit (or a small candidate set), not "any H-REDOX unit with two overlapping tokens".

Preserve: `9701_m16_qp_12:q1` (gold), spectroscopy uids, and do not clobber them when joining.

---

## 6. Output format

Respond in this order:

A. **Verdict on the current constructor** (one paragraph: why it cannot be the compiler).

B. **Architecture diagram** (ASCII is fine): intelligence → join → recipe library → instantiate → overlay → runtime.

C. **Joins**, with exact fields and fail-closed rules.

D. **`unlock_recipe.v1` JSON schema** (complete enough to implement).

E. **`hint_proof.v1` JSON schema** stored next to the overlay (teacher-side; not learner).

F. **Deterministic instantiate algorithm** (pseudocode).

G. **Bounded LLM compile slot**: packet whitelist, output, gates, how many calls worst-case for chemistry (show the arithmetic).

H. **Python layout**: modules, functions, CLI (`lbs_compile.py`, `lbs_instantiate.py` or one tool with subcommands), how it plugs into existing `join_lbs.py` without rewriting freeze.

I. **Tests** that encode S1, S3, NEVER F3, and "no per-item LLM".

J. **Rollout**: electrochem only; owner check list (uids q1, q33, q18, cryolite q3, FeC2O4 q10).

K. **Honest gaps** (empty mechanism.steps, thin enrichment, Cambridge↔NCERT grain). Do not paper over them with an LLM.

Do not write a full 21k overlay. Do not invent examiner comments. Do not put mx_type on the learner follow-up stem.
