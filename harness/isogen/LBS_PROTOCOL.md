# Learn-by-Solving Protocol

**Version 1.2 · 2026-08-10 · Learning charter added (§0a, verbatim from the
three-expert-panel-signed ISO-GEN v1.3 layer — Kimi YES R2+R3, Codex YES R4;
`reports/isogen_v3/ISOGEN_V13_SYNTHESIS.md` §A governs).**

**Version 1.1 · 2026-08-09 · Kimi review folded (LbS-P1–P8 verbatim, §9).** Builds on: the enriched corpus (66k items with
`question_intelligence`, solution paths, anchored failure paths), `CMS_PROTOCOL.md`
(retrieval, grades), `ISO_GENERATION_PROTOCOL.md` v1.1 (generation), the evidence-first
ASSEMBLER precedent (author = pedagogy, engine = mechanics, invents nothing), and the
LamportEngine LbS runtime (typed solution graphs → synthesized hints).

## 0a. The learning charter (v1.2; owner's central question answered)

**A warranted learning claim is a DIRECTED, EARNED, envelope-indexed,
horizon-tested change in the system's evidence-supported model of the learner —
never a directly observed change in the learner.** Five fail-closed clauses:
DIRECTED (distance-to-target decreases on the contract's `intended_transition`;
movement toward a misconception profile is REGRESSION) · EARNED
(contamination-free, learner-generated evidence; attribution vocabulary only
`intervention_linked`, or `caused_by` under a registered causal design; tainted
work never satisfies an unaided mastery claim) · TRANSFERABLE within the
family's registered envelope (confirmed radicals/incidentals only) · PERSISTENT
over the declared `persistence_horizon` (current minimum one week; before the
re-probe the clause is NOT_RUN and blocks) · CHECKABLE (every clause carries a
truth-table status; sub-floor movement is UNVERIFIED).

**The only learner-claim vocabulary LbS emits:** `PROGRESS_EVIDENCE →
SESSION_MASTERY → FAMILY_MASTERY → STABLE_FAMILY_MASTERY@delay →
COMPOSED_MASTERY (optional, by declared grain)`. Within-session evidence
supports performance claims only; family-transfer and horizon-persistence sit
above it; there is no undifferentiated `LEARNED` boolean. Response events and
learner-state posteriors remain separate records. The isomorph family is the
measurement apparatus for the TRANSFER clause — LbS consumes what ISO-GEN v1.3
certifies (`PASS_PRETEST` instruments), and learner evidence outranks every
design-time prediction.

## 0. First principles

1. **A hint is a question where the gate is a move; where the gate is a fact or a
   choice, the system tells, then questions** (amended per LbS-P1 — the universal form
   was false for declarative prerequisites and representation/decomposition choices: no
   question's solving produces a fact you lack, and a smaller question either
   presupposes the frame or donates it).
2. **A complex problem is a sequence of difficulty gates.** Its stored solution path
   (steps with claims and warrants) is a chain of moves; its derived failure paths
   (Grade A/B attested or Grade E hypothesised, anchored at steps) are the *known ways
   each gate defeats a learner*. Difficulty is not a scalar — it is the specific gate
   the learner cannot yet pass.
3. **Diagnosis is a lookup wherever the metadata exists.** A chosen wrong option with a
   mapped misconception names the trap; the trap's anchor step names the gate; the gate
   names the unlock question. No model call, full audit trail.
4. **Mastery is demonstrated on an isomorph, never on the same item.** Re-solving a
   problem you were just walked through proves memory. Solving its
   `FAITHFUL_TRANSFER` unaided proves the move. The iso protocol is the exit-ticket
   factory.
5. **Expertise is structure perception.** Experts categorise problems by governing
   principle, novices by surface (Chi/Feltovich/Glaser — the basis of the structural
   atlas). The corpus's structural edges make that perceptual training *servable*:
   surface-diverse, structure-identical sets exist as data, not intention.
6. **Every learner response is evidence, appended, never laundered** (P8 discipline:
   `selected_option` is never converted into an attested path; learner state is a
   compatibility set, not a scalar; grades gate what inference is allowed).

## 1. The three manifestations, one machinery

All three modes are the same engine — serve → attempt → diagnose → route — pointed at
different targets:

| mode | target | the set served | exit evidence |
|---|---|---|---|
| **LADDER** | master a concept via a complex problem | the problem + its per-step unlock questions | solve a faithful isomorph unaided |
| **TRAP** | recognise and defeat one misconception | the family's transfer set (same Mx, disjoint topics) | predict-the-trap on a novel family member |
| **STRUCTURE** | expert-like perception of deep structure | surface-diverse items joined by structural edges | classify + solve a far-transfer item (shared structure, alien surface) |

## 2. LADDER — solving a complex problem through hint-questions

### 2.1 The decomposition object

For complex problem `P` with solution path `s1..sn`:

- each step `si` has: claim, warrant, (where enriched) anchored failure paths with
  confusion_type + misconception statement + what-it-produces;
- each step defines an **unlock slot** carrying a `gate_type ∈ {move_execution,
  representation_choice, decomposition, declarative_prerequisite, perceptual}`
  (LbS-P1). `unlock_pool` assembly serves `move_execution` only; choice/decomposition
  gates route to WORKED-CONTRAST with the selection stated, then a selection-training
  pair; declarative gates route to a stating item — told, then used.

### 2.2 Filling unlock slots — RAG first, generation second

Deterministic assembly (`unlock_pool(P, si)`):
1. corpus items whose family matches a failure path anchored at `si`, at a lower
   difficulty rung (difficulty-ladder edges) — *the trap-specific unlock*;
2. corpus items sharing the step's construct at rung-1 (same-construct /
   same-method edges) — *the move-specific unlock*;
3. if the pool is thin → a **tutorial_bridge bundle** enters the iso generation queue:
   source = `P` + the step; operators = `SPECIALIZE` / `DECOMPOSE_RECOMBINE` /
   `REPARAMETERIZE`; the Baumanns posing goal "reformulate for problem solving — pose a
   simpler, adjacent, or auxiliary problem to unlock the source solution" is exactly
   this product. Generated unlocks inherit family ids and pass the full v1.1 gate
   stack before serving.

### 2.3 The session state machine

```
SERVE P  (at the learner's frontier: family + rung from their open-path profile)
  ├─ correct, unaided ............... harvest evidence; exit or raise rung
  ├─ wrong option, Mx-mapped ........ anchor step known → UNLOCK(si, trap-specific)
  ├─ wrong option, unmapped ......... UNLOCK by binary probe (below)
  └─ stall / no answer .............. BINARY PROBE: serve step-check questions at
                                      midpoints of the path until the failing gate
                                      is bracketed → UNLOCK(si)

UNLOCK(si):
  q1 := pool item (trap-specific if diagnosis named one, else move-specific)
  ├─ solved → return to P, re-attempt from si
  ├─ failed with mapped Mx → remediation rung (CI ladder where aliased,
  │       else the family's remediation_hint) rendered AS A QUESTION → q2 (parameter
  │       variant of q1)
  └─ failed k=2 times → WORKED-CONTRAST: show the step done correctly and done
          corrupted (from the failure path's expr pair), ask the learner to identify
          and repair the corruption — still a question, the last rung before telling.

EXIT: serve P' = FAITHFUL_TRANSFER isomorph of P (first-exposure, always).
  Unaided success on P' records `session_mastery` ONLY — it tests execution under
  maximal priming, with the method named by context. `family_mastery` (LbS-P4, amended per IIP I5/I7 — contradiction C-02 adjudicated:
  the governing IIP forbids same-session mastery) requires a second unaided success on
  a surface-distinct member in a **later session**, inside a mixed queue of ≥2
  families. An intervening different-family item in the same session may record
  `family_mastery_candidate`, never `family_mastery`. The claim becomes `stable` only
  after the LbS-P8 re-probe at ≥1 week. The two
  labels are never conflated. Success on P after hints is progress, never mastery.

PRE-DIAGNOSIS (LbS-P2, runs before any UNLOCK or probe): a wrong response first
triggers a stem-restitution check — the learner lists the givens and the target.
Divergence routes to a comprehension item about the STEM, never to the solution path,
and logs `off_path_evidence`. If binary probing brackets no gate (all step-checks pass
yet P failed), log `off_path_evidence`, make NO learner-state update, re-serve P once;
a second failure exits `unclassified`. Off-path evidence never accrues to item
calibration or to move evidence — this is the branch for the measured 20.2% of real
errors that live before the solution path, and without it the engine would write false
gate evidence into an append-only store and contaminate calibration for every future
learner.

TERMINAL (LbS-P1): failure after WORKED-CONTRAST records `incomplete at si
(gate_type)`, demotes one rung in the family, and exits P — no mastery-eligible exit
item for this family in the session. No state machine node is undefined.
```

Hint-depth per session is the learning-curve signal: mastery shows as decreasing
unlock depth across successive problems of the same family/rung.

## 3. TRAP — training against a named misconception

Input: one canonical family (Grade A/B attested preferred; the 3,161 practisable
families). The set: `practice_set(mx, transfer=True)` — same trap, disjoint topics, so
the *trap* is the only constant the learner can learn.

**The key gate (LbS-P5 — the harm pin, replaces "Grade A/B preferred"):** stages 2
and 3 serve ONLY families whose `named_option`/`why_option_follows` are Grade A/B
attested, or confirmed by observed response distributions (the predicted trap option is
the modal first-attempt error across ≥2 members and ≥30 observations). D/E-only
families are restricted to stage 1, where they accumulate confirmation evidence. Until
the adjudicator SLA exists, the why-component is constrained selection over the stored
why plus sibling-family whys of the same confusion_type — never free text. **A
hypothesis about an item may route a hint; it may never be an answer key.** Without
this gate the system would mark a learner with a CORRECT model of the error wrong
against a machine hypothesis and remediate them toward a phantom — the one defect that
manufactures misunderstanding rather than merely underperforming.

Progression ladder (each stage is still solving):
1. **Solve** family members; wrong-option choices matching the family's named option
   are direct evidence the trap is open.
2. **Predict the trap**: serve a new member; the task is "which option would a solver
   holding [no statement shown] pick — and why?" — answer key is the stored
   `named_option` + `why_option_follows`. The learner articulates the trap by
   predicting its behaviour, not by reciting it.
3. **Spot it cold**: a mixed set where only some members carry this trap; the task is
   to flag which. Distractor sets for this task come from sibling families of the same
   confusion_type (deterministic assembly).

Exit: stage-2/3 performance on members never seen, from topics never practised.
Where the family has a CI alias, its remediation ladder's rungs (verbal →
worked_contrast, routed by confusion_type) supply the between-stage interventions —
rendered as questions.

## 4. STRUCTURE — expert perception beneath the surface

Input: a structural relation, not a topic. Sets assembled from:
- `same-method-different-physics` edges (physics-500, 1,224 edges, validated rule);
- cross-subject family members (63 pairs) and the transfer atlas patterns
  (baseline-correction, out-and-back, total-vs-change, exponential-state,
  scope-boundary);
- `same-structure-different-topic` edges (the 31 shipped at 93.3% measured precision —
  small by design; the iso queue's V3/V4 classes GROW this set on demand, which is the
  deliberate synergy: generation exists to make structure-training sets servable).

Tasks, in order of demand:
1. **Solve the pair** (two surface-alien, structure-identical items in sequence);
2. **Match**: "which previously solved problem does this new one resemble *in how it is
   solved*?" — options are prior items; key is the stored edge; wrong-answer analysis
   distinguishes surface-matching (picked the same-topic decoy) from structure-matching;
3. **Name the move**: closed vocabulary (the 26 method_tags on p500; the transfer-atlas
   pattern names corpus-wide) as the option set — "what removes the nuisance here?
   ratio / difference / conservation / …";
4. **Far transfer**: a member of the same structural family from a subject the learner
   has not practised (the strongest available evidence of structure perception).

The decoys in task 2/3 are engineered deterministically: same-topic-different-structure
items (the surface trap) versus same-structure-different-topic (the target) — both
exist as typed edges, so the *discrimination* between surface and structure is the
thing scored.

**Scope and edge validation (LbS-P6):** STRUCTURE v1 serves tasks 1–3 within physics
(the validated 1,224-edge set + 26-tag vocabulary) and tasks 1–2 on the 63
cross-subject pairs under a `limited pool` label; task 4 serves only gate-passed V3/V4
members, and its absence is reported as scope, never learner failure. **No edge from
the 31-edge cross-topic set is used as a scored key until individually human-reviewed**
(at n=31, review is cheaper than the validation study was; 93.3% precision means ~2
wrong keys that would train surface-matching — the exact perception this mode exists to
destroy). A generated structure member's serving key is the EDGE; edges carry their own
validation grade — passing the item gates does not establish the relation.

## 5. What is deterministic and what calls a model

**Deterministic (the session engine, no model call):**
routing and diagnosis via mapped options → anchor steps; unlock-pool assembly;
binary-probe scheduling; set assembly for all three modes incl. decoy engineering;
progression gates; hint-depth bookkeeping; mastery events; evidence logging
(append-only session trace, replayable); grade labelling on everything served.

**Model, through the iso protocol only (gated, asynchronous):**
generating missing unlock questions (tutorial_bridge), missing isomorph exit tickets,
missing structure-set members (V3/V4). Never generated mid-session; the queue fills
between sessions and every generated item passes the v1.1 gates first.

**Model, per interaction (narrow):**
free-text response adjudication where the item format demands it (math CR); a
different-family model, verdict logged with the response. MCQ modes need none.

### Engine completeness rules (LbS-P7, verbatim)

> (a) empty unlock pool ⇒ immediate WORKED-CONTRAST plus queued generation; the same
> item is never served twice within one attempt chain; (b) a failure path opens in
> learner state only on a second corroborating observation (two mapped clicks on
> distinct items, or one mapped click plus failure of its trap-specific unlock);
> single-click openings are provisional and expire at session end; (c) rung promotion
> requires two consecutive unaided successes; (d) initial placement is the family's
> lowest rung with fast-forward on unaided success; (e) three consecutive failed
> unlocks in a session demote the frontier and change family; (f) every item offers an
> explicit "I don't know," routing to probe without entering diagnosis; (g) exit items
> must be first-exposure, and a family whose unseen transfer pool falls below two
> ceases issuing exit claims until replenished.

**Shortcut contamination (LbS-P3):** for families with an attested option-shortcut
failure path, an unaided-correct MCQ response is progress evidence only; mastery
eligibility requires a constructed justification or a "which statement justifies this
step" follow-up.

**Retention (LbS-P8):** every `family_mastery` and trap-defeat entry carries a
scheduled re-probe at ≥1 week; a failed re-probe reopens the family. No mastery or
defeat claim is reported as stable before its re-probe.

## 6. Learner state and evidence (inherited, not reinvented)

- Learner state = **compatibility set over open failure paths and unproved moves**
  (AWM v1 doctrine: never a scalar). LADDER updates gates; TRAP updates families;
  STRUCTURE updates structure-recognition evidence per pattern.
- Every serve/response appends to the session trace with the set's provenance (match
  levels, grades, rule versions). Replay reconstructs any session decision.
- **Grade discipline in serving**: attested (A/B) members anchor every set; D/E
  members fill and are labelled; Grade-E derived paths may *route* hints but never
  count as learner-state evidence of the misconception (they are hypotheses about the
  item, not observations of people).
- Difficulty facility observed in sessions accrues to items (the P8/P11 calibration
  path) — LbS usage is what upgrades the corpus.

## 7. Readiness and gaps (honest)

Works today: LADDER on items with solution paths + anchored derived paths (physics-500
fully; MathNet 11,409 enriched; v1 typed items; math_deploy 2,301); TRAP on the 3,161
practisable families; STRUCTURE on physics-500 edges + cross-subject family pairs +
transfer-atlas sets.

Gaps, each with its named fill: thin unlock pools (→ tutorial_bridge queue); thin
cross-topic structure sets (→ V3/V4 queue); step-level move tags outside p500 (→ the
same closed method vocabulary applied at enrichment, future wave); free-text
adjudication throughput (math CR modes deferred until the adjudicator SLA of
ISO §6 P11(d) exists).


---

## Tightening amendments (2026-08-09, gold-sweep folds)

**Failure-ontology binding (CNS CC1 — contradiction C-01):**
> `cognitive_core/taxonomy/error_taxonomy.json` is the only authority for
> failure-coordinate vocabularies. Every unlock-slot record and learner-evidence event
> carries `failure_ontology_schema_version`, `failure_ontology_sha256`,
> `failure_ontology_status`. CAUSE (`confusion_type`), PROCESS (`block_code`), PRODUCT
> (`error_class`) are independent nullable coordinates; populate only what the
> evidence supports; association fallbacks are labelled `DEFAULT_FALLBACK`, never a
> diagnosis. An unlock slot binds `gate_type` to a canonical `block_code` +
> `move_family` + `cognitive_op` — `gate_type` is a routing class, not a second
> ontology. **The five-way gate_type crosswalk is an OWNER-REVIEWED table (named gap:
> no verified artifact supplies it; do not invent it).** Unknown or digest-mismatched
> values fail closed.

**Remediation-route microtemplates (imported from the Remediation & Consolidation
draft §9 — the route moves only; its seven-state learner model, worksheet breadth and
unfixed logs are explicitly NOT imported):**

| `route_kind` | ordered rung moves | rung exit evidence |
|---|---|---|
| `MISCONCEPTION_REPAIR` | wrong/correct contrast → localise error → explain why → learner reconstruction | one unassisted near-transfer check |
| `LOK_BUILD` | micro-reteach → explicit step decomposition → guided fill → fade | one short unassisted check |
| `PROCEDURAL_STABILISE` | concise model → partly solved step → scaffold fade | independent varied execution |
| `REPRESENTATION_REPAIR` | translate representation → visible anchors → language↔symbol map | one reconstruction task in the target representation |
| `EXTEND` | challenge → near transfer → far transfer | explanation/critique/reverse-reasoning evidence |

> A remediation microtask instantiates exactly one `route_kind` for one failure
> path/gate; records `{source_evidence_ids, hinge_id, family_id, block_code,
> route_kind, move_index, assisted, exit_item_id}`; completion is progress only; the
> later-session mastery rule applies.
