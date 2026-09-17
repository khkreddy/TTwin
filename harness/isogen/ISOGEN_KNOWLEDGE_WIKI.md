# ISO-GEN Knowledge Wiki — what worked, what failed, and why

**Standing owner directive (2026-08-10):** maintain this as a persistent, growing
wiki of ISO-GEN knowledge. **Maintenance rule:** every generation run, every owner
review, and every discovered audit gap appends a dated entry. Working patterns get
stable IDs `WP-n`, failure patterns `FP-n`; protocol text, examiner briefs, and
calibration fixtures reference these IDs. Entries are never deleted — a superseded
entry is marked superseded with a pointer. Owner findings outrank machine audits
(§4 is the authoritative signal).

Companion documents: `ISO_GENERATION_PROTOCOL.md` v1.4 (the binding rules distilled
from this knowledge) · `reports/isogen_v2/` + `reports/isogen_v3/` (derivation records) ·
`cms/iso_test/` (the E8 ten) · `cms/lbs_demo/` (the 48, NOT DEPLOYABLE) ·
`cms/isogen_v2_fable/` (the structural-isomorph ten, owner-accepted 2026-08-11).

> **Before authoring or reviewing any figure-bearing item, read [§13 Figure
> fidelity](#13--figure-fidelity--the-standing-checklist-owner-directed-2026-08-11).**
> It is the standing checklist — label rules L1–L7, typography rules T1–T6, and the three
> inspection passes — and it applies to the whole corpus, not only to ISO-GEN output.
> Sections 1–12 are the evidence it was distilled from; §13 is what you actually apply.

---

## 1. Patterns that WORK (WP)

### WP-1 · Transformation anchored to an attested source bundle
Every E8 item was a transformation of one attested exam item whose invariants,
manipulables, misconception, and difficulty evidence rode in the bundle. Fidelity
had a referent at every step. (All ten keys verified; owner verdict GOOD.)

### WP-2 · Machine-addressable representation relations in figure items
The two good E8 figures specified RELATIONS, not just values: ISO06 (spring graph)
recorded axes, zero intercept, line through (0,0)→(4,8), calibration 3.0 N → 6.0 cm;
ISO07 (puck) recorded equal mass, equal speed magnitudes, signed +6.0/−6.0 m/s
directions. The audit could inspect the same primitives a solver needs. This — not
"transformation vs de novo" — is what separated the good figures from FIG01.

### WP-3 · Formulation-work items (owner-endorsed 2026-08-10)
E8 spring item (V5_figure): gives unloaded length 14.0 cm, loaded length 20.0 cm at
3.0 N, shows the graph, asks **which quantity is on the vertical axis** — options
{measured length / original length / sum / difference}, key = difference. The
student must CONSTRUCT extension = measured − original; no option is reachable by
recall or cue. Owner: "a good question because the student has to work out the
formulation." Generalization: ask for the RELATION the representation encodes, not
a value readable off it.

### WP-4 · Solve-before-key, blind-solve two-phase
The author solves the source blind before seeing its stored answer (phase-1 bundle
carries no key), and solves the generated target independently before keying.
Caught mis-bindings in E8; now protocol G1/P5.

### WP-5 · Examiner solves AS THE MISCONCEIVING STUDENT
The one E8 defect that any structural check missed was caught by the examiner
simulating the misconception and checking whether that belief actually produces the
named distractor (re-mapped 1 of 10). Architecture generalized in v1.2 §E: the
examiner derives corruptions from the examiner bundle, blind of the author mapping.

### WP-6 · Metadata born with the item
The `question_intelligence` block (misconception per distractor, locus, provenance,
invariants preserved) written in the same act as the item — never annotated
afterwards. Owner: the ten's "language and meta data overall is better." v1.2
sharpens: thinking-path metadata is a pre-deployment PREDICTION until response
evidence supports it.

### WP-7 · Representation-translation as the cognitive task
The item gives some representations and demands another; the demanded translation
is the work (spring item: graph+values → formulation; puck item: figure alone
carries the velocities, prose deliberately does not). Now the core of v1.2 §B/§C.

### WP-8 · Refuse-then-sign adversarial protocol development
Design → adversary attacks with quotes → pins folded verbatim → re-audit → sign.
ISO-GEN v2 took 3 rounds (16 pins + 4 integration blockers, all real). The refusals
found defects the author (Fable) could not see in its own draft — including a
contradiction that would have gutted the capacity halt rule.

---

## 2. Patterns that FAIL (FP)

### FP-1 · Invariant giveaway in the option set — **owner-caught 2026-08-10**
**Exemplar:** LAD01-H2 (LbS ladder; the dropped-ball item — note: it sits in the
48-item LbS set, not the E8 ten). "A bead is dropped from rest. At 3.0 s … which
completed row is consistent?" Options:
A: speed 29.4, **acceleration 9.8** (KEY) · B: 9.8 / 29.4 · C: 29.4 / 0 · D: 9.8 / 0.
**Only the key carries acceleration 9.8.** A student who knows only "g stays
constant" — a fact the item's own Tell had just donated — picks A with zero
calculation; the speed cell does no diagnostic work. Owner: "this is a bad
pattern."
**Rule:** when an option row spans multiple dimensions, every dimension a student
can know WITHOUT the target computation must be homogeneous across ≥2 options
(here: ≥2 options sharing acceleration 9.8, differing in speed), so the invariant
eliminates at most part of the set and the computed dimension separates the rest.
**Protocol home:** v1.2 §B.6 gaming pockets (the cheap route "constant-g recall"
needs a closure contrast) + §E surface-cue failure; PRISM F1-5/U8. **Add to
examiner seeded-defect fixtures.**

### FP-2 · De-novo depiction without a semantic contract (FIG01, five defects)
A standing wave drawn from prose: (a) "open-open" pipe drawn CLOSED at both ends
(stroked rectangle = end walls contradicting the boundary condition); (b)
longitudinal displacement rendered as an unlabeled transverse curve fused with the
apparatus (graph/apparatus category error); (c) node crossings at 0° tangency and
±43° corners at antinodes — the slope structure of sin(nπx/L) exactly inverted
(measured from the Bézier control points); (d) accessibility title donates the node
count; (e) dropdown reveals λ on a wrong attempt, contaminating the frequency
response. All VALUES were correct — which is why the value-agreement audit passed.
**Fix:** v1.2 §C (verified canonical state + semantic contract + typed scenes) and
§D G9 (split blind-checklist inspection, functional-geometry predicates, leak scan,
fail-closed).

### FP-3 · Text-redundant figure (FIG02)
Every parameter and the topology restated in the stem; the item solvable without
reading the figure; a pedantic wire trace even read as a short. A figure that
contributes no matrix-required field is decoration. **Fix:** G9.3 evidence
contribution over the representation package.

### FP-4 · Figure-geometry contradiction with the key (FIG03-I2)
Label said 37°, intended key 53°, but the drawn ray ran ~37° to the NORMAL and the
arc endpoint missed the ray — making a second option independently defensible.
Arithmetic and geometry derived separately instead of from one solved state.
**Fix:** v1.2 §C.1 canonical state as single authority; G9.1 ray/arc/normal
predicates.

### FP-5 · Prompt/interaction donates the mapping (FIG04)
The interaction prompt handed the student the definition-to-arrow mapping; I2's
dropdown returned the same letter the final MCQ asked for. A second control that
repeats the evidence operation is the SAME field, and a donated mapping is not
evidence. **Fix:** §B.4 field-signature normalization; §G interaction contract.

### FP-6 · Over-telling hints (LAD01-H2, LAD02-H2, LAD03-H3, LAD04-H1)
The "Tell" resolves the very field the item then elicits (LAD01-H2's Tell donates
constant-g, then asks which row has constant g — compounding FP-1). A hint may
route; it may never be an answer key. **Fix:** LbS harm pin + v1.2 §G taint
(revealing a relation taints downstream fields transitively).

### FP-7 · Reveal-policy contamination (the dropdown experiment)
Server showed the correct wavelength after a wrong dropdown attempt, then unlocked
the frequency options — later correctness cannot show independent translation.
Owner verdict: the figure+dropdown experiment failed. **Fix:** §G executable
interaction graph; contaminated fields diagnostic-ineligible; interactive figures
deferred until a family passes held-out G9 calibration.

### FP-8 · Accessibility text as answer channel (FIG01-I2 title)
"…with five internal displacement nodes" — a screen-reader user receives the count
sighted users must derive; equivalence violated in the other direction too when alt
text withholds evidence. **Fix:** §C.3/§D representation-package rule.

### FP-9 · Mega-batch attention dilution
52 items in one run produced the 48; ten items with one bundle each produced the
good set. Throughput pressure converts quality work into shortcuts. **Fix:** v1.2
§H capped pilot 12–18, split cards, halt conditions, telemetry.

### FP-10 · Value-agreement-only audit (the audit gap that let FIG01 through)
The audit verified node positions, arithmetic, IDs, SVG well-formedness — labels,
not meaning. Machine 48/48 closure was read as deployability; the owner's eye
refuted it. **Fix:** G9.2 blind domain checklist; §I positive execution receipts;
this wiki's §4 owner-review log as the standing calibration signal.

### FP-11 · Parameter-clone confirmation (paired FIG items)
FIG01-I1/I2 etc. were parameter variants of the SAME operation; two such items
cannot corroborate a learner model. **Fix:** §H meaningful independence (different
normalized evidence operation + different witness).

### FP-12 · Surface-cue distractor (TRP01-P1)
Only option B contained the phrase "swaps the labels" — keyword-matchable without
running the model. **Fix:** §E surface-cue fail; distractors rebuilt target-native.

### FP-13 · Delegated translation alters mathematics (T1; policy 2026-08-10)
Delegation of translation to a smaller local model altered 11 math tokens (caught
by the protected-token check). Owner rule: Codex translates in its own reasoning;
the deterministic guard stays. (Corpus-side, but recorded here because generated
items inherit corpus text quality.)

---

## 3. Design laws distilled (binding form lives in the protocol)

1. **Three-layer law:** backbone fidelity ≠ representation fidelity ≠ served
   interaction validity; all three verdicts required; release = AND (v1.2 §A/§I).
2. **Referent principle:** every generated artifact needs a referent it can be
   checked against; for representations that referent is a semantic contract
   derived from ONE verified canonical solved state — never author prose (§C).
3. **Ancestry is not truth:** a semantically thin state makes every pane
   consistently wrong; the state itself must be verified against a registered
   domain schema (Attack 3, §C.1).
4. **Format is an evidence channel:** chosen LAST, as the cheapest channel whose
   diagnostic ceiling covers the required claim; never for variety (§B).
5. **Options are engineered per-dimension:** every dimension knowable without the
   target computation must be non-identifying across the option set (FP-1).
6. **The examiner is a checker, not a monitor:** independent artifacts, blind
   derivation, positive execution receipts; self-certification is worthless
   ([[teachertwin-checker-not-monitor]] doctrine, proven again by FIG01).
7. **Owner review outranks machine closure** — and each owner finding becomes a
   named pattern + seeded fixture here, so the machine gate learns it.

## 4. Owner review log (authoritative)

- **2026-08-09 · E8 ten:** GOOD — "the diagrams came out faithful to the question
  and the language and meta data overall is better."
- **2026-08-10 · LbS 48:** "all poor quality and cant be deployed"; the
  figure+dropdown experiment "is a failure at this stage"; "the figure for waves is
  wrong." → set demoted (DEPLOY_STATUS.md), ISO-GEN v2 commissioned.
- **2026-08-10 · LAD01-H2 (ball at 3 s):** "the major flaw is that only one option
  is having acceleration as 9.8. any student who knows the g stays constant will
  pick that option without any calculations. this is a bad pattern." → FP-1.
- **2026-08-10 · E8 spring item:** "a good question because student has to work
  out the formulation." → WP-3.

## 5. Run history

| run | date | scale | machine result | owner verdict |
|---|---|---|---|---|
| E8 iso test (`cms/iso_test/`) | 2026-08-09 | 10 items, all 8 variation classes | 10/10 keys, 1 adjudicated re-map | **GOOD** |
| LbS demo (`cms/lbs_demo/`) | 2026-08-09/10 | 52 planned → 48 released | 40/48 R0 accept → 48/48 after revisions | **NOT DEPLOYABLE** (machine closure ≠ deployability) |
| v2 capped pilot | pending | 12–18 items | — | — (gated by v1.2 §H telemetry) |

## 6. Standing TODO for the next pilot

- Seed FP-1 (invariant giveaway) and FP-12 (surface cue) into examiner calibration
  fixtures alongside the G9 figure fixtures.
- Register the first physics figure family (graph-type, ISO06-shaped) with schema +
  held-out mutations before any figure item enters the pilot.
- Re-run the spring/WP-3 pattern deliberately: at least 2 pilot items whose demand
  is "state the relation the representation encodes."
- Kimi counter-sign of v1.2 when its rate limit clears.

*Append below this line; never rewrite history.*

---

## 2026-08-10 · v1.3 panel round (appended per maintenance rule)

- **WP-9 · Three-expert refuse-then-sign panel (NETFLIX process).** Independent
  positions → cross-attack → synthesis → counter-sign converged in 4 rounds with
  zero unresolved disagreements. The refusals carried the value: Kimi killed a
  degenerate selection order and an unsigned movement clause; Codex killed
  namespace collisions, gold contamination, and pin compression. Divergences were
  resolved by argument quality, not authority — including an expert withdrawing
  its own pin after independently verifying the opposing argument.
- **FP-14 · Compressed pin carriage.** Summarizing an expert's pins in a
  synthesis silently weakens them; carriage requires verbatim incorporation with
  the synthesis as integration layer only. (Codex R2 refusal; now §0.5 pattern.)
- **FP-15 · Level confusion in vocabulary reuse.** Reusing a judge-card
  permission name (CERTIFY) as an item-level consequence created a contradiction
  that survived two rounds; enforcement fields must live at the level they
  govern (serve_eligible / family_founder_eligible). (Codex R3.)
- Charter, tournament, derivation-DAG, judge-qualification: see protocol v1.3
  layer; run history table gains: v1.3 panel (4 rounds, YES/YES, 2026-08-10).

### FP-16 · Transliterated figure code — gate-passing, purpose-failing (2026-08-11)
Converting the first 26 mathnet figures SVG→TikZ mechanically produced code that
compiled, was non-blank, held every geometric constraint, and matched the accepted
render to <2% MAE — yet defeats isomorph generation. All 26 carried SVG pixel-space
scaffolding (`PX_W`, `PX_H`, `VB_X`, `CANVAS_W`) mixed into the semantic parameters;
all 26 wrapped every parameter in an obfuscated alias (`\def\PFAFIFPFH{\csname
PX_W\endcsname}`) that no human or agent can read; and derived positions were frozen
as literals (`C1=100, C2=200, CY1=50`) rather than computed from `BOX_X`/`R`/`GRID`,
so changing the semantic parameter would leave the drawing stale — the protocol's own
"change a number and the diagram silently contradicts the new stem" failure.
**Rule:** author TikZ in the problem's coordinates with readable, commented macros
(phy500 style `\def\HR{1.6} % hoop radius r`); compute derived geometry with
`\pgfmathsetmacro`; and pass the new **isomorph-readiness gate** — perturb a semantic
parameter, recompile, and require the drawing to follow coherently with no hand edit.
Sibling of FP-2 (FIG01): the gates were satisfied and the artifact still failed the
job it existed to do.

## 2026-08-11 · gold-set parametric-TikZ proof run

### WP-10 · Mutate → constrain → compile → independently read

The gold encodings supported their intended ISO-GEN use when mutation was treated
as one witnessed chain: change named source parameters, retain and re-evaluate every
source constraint, compile the changed TikZ to a fresh self-contained SVG, then make
the external examiner cite the load-bearing labels, directions, topology, and
dimension referents it actually used. Across 44 realized variants from 20 distinct
stored-answer sources, TikZ changed 44/44, validator gates passed 44/44, and 336/336
candidate-level constraint evaluations held. Kimi independently reproduced the
physics key, worked path, distractor mechanism, and figure reading for 44/44.

### WP-11 · Accessibility checked against a frozen blind figure read

A text alternative was compared with Kimi's content-addressed phase-1 figure
interpretation, not with the author key. The checker separately required equivalent
load-bearing evidence, no contradiction, and no answer leak. This caught omissions
and over-telling that the correct SVG could not catch. Four fresh non-clone
challengers replaced candidates that could not legally receive another repair;
every final tournament had exactly two admitted candidates and none was
UNCONTESTED.

### FP-17 · Distractor-letter drift after option permutation

Thirteen of the first 40 candidates had correct keys, correct solutions, correct
figures, and plausible misconception logic, but the named misconception still
pointed to its pre-permutation option letter. Kimi rejected all 13. A one-field
metadata repair passed fresh comparison, but this failure rate is too high for
scale. **Rule:** option permutation must atomically transform option text, key,
named misconception target, and replay witness; then execute the misconception to
the named option.

### FP-18 · Accessibility omission and result donation

The first P215 alternative omitted its figure-only 3 m and 4 m labels; the first
P259 alternative said charge signs were shown without identifying the positive
plate; the first P234 alternative described the cancelled/resultant field instead
of only the two visible arrows. These are opposite representation-package failures:
withholding evidence and donating the inference. A sibling disagreement on the P234
phrase was treated as UNVERIFIED, never averaged. **Rule:** accessibility evidence
must be independently compared to a frozen blind visual interpretation, with
equivalence and leak checks both required.

### FP-19 · Numeric mutation leaves prose metadata stale

Kimi explicitly found inherited note/consistency prose with old values in P082,
P197, P248, and P295 even though the bound parameters, TikZ, constraints, stem, and
solution agreed. **Rule:** free-text parameter notes are generated from the final
parameter state or removed; they are never copied blindly into a variant.

### FP-20 · Hollow constraints and fixed-answer manifolds

Validator diagnostics named source parameters that do not drive drawing marks and
constraints resting only on undrawn answer-check values (notably P008, P025, P082,
P089, P092, P197, P215, P315, and P355), plus slack sign/range checks in P234 and
P299. Several contracts also permit new input tuples only along a baked fixed-answer
manifold. **Rule:** lint and quarantine constraint-free/undrawn parameters; type
constraints as visual invariant, physical invariant, or target-lock so mutation
diversity is not overstated.

### Run record

- Artifacts: `cms/isogen_gold/generated_items.jsonl`, `GENERATION_LOG.md`, and
  `ISOGEN_GOLD_REPORT.md`.
- Scope: gold set only; 20 stored-answer sources and 20 physics topics; no MathNet.
- Realization: 40 initial candidates + 4 fresh challengers = 44; 40 admitted after
  all three scoped fidelity verdicts; 4 rejected before tournament; 20 winners +
  20 admitted runner-ups; 0 UNCONTESTED.
- External examination telemetry: 161 recorded uncapped Kimi-k3 responses,
  229,095 input tokens, 430,052 output tokens, known cost $7.1381; one malformed
  schema response and one stalled worker were excluded until clean retries passed.
- Machine verdict: qualified proof-of-function for parametric mutation/rendering;
  owner verdict pending. Items remain `REQUIRE_HUMAN_ADJUDICATION` and
  `serve_eligible=false`; do not scale to 5,066 until owner review and FP-17–FP-20
  controls are closed.

---

## 7 · Structural editing of encoded figures (owner directive, 2026-08-11)

**The defect being corrected.** The phy500 ISO-GEN set was judged *superficial*: 26 of
40 candidates were `V5_figure`, 14 `V1_parameter`, and **every one changed only
NUMBERS**. Median A/B stem similarity was 0.98. Parametric TikZ was treated as a
number-substitution device, which is the least of what it enables.

**What an encoded figure actually permits.** Once the figure is code with named
parameters and machine-checkable constraints, four *structural* edit classes open up
that a raster never allowed. They are ordered by how much new reasoning they demand:

| class | edit | example | what the student must newly do |
|---|---|---|---|
| **V1 · parameter** | change values | r = 1.6 → 1.4 | nothing new — same solution path (the shallow class) |
| **V9 · component insertion** | ADD an element to the drawing | a second resistor in the circuit; a cevian, tangent or midpoint in the geometry; a second pulley | handle a term/branch that did not exist; the solution path GROWS a step |
| **V10 · topological rearrangement** | change how elements CONNECT | series → parallel; move the load between two nodes; swap which vertices a segment joins; move a mass above vs below the pivot | re-derive the governing relation; the old formula silently fails |
| **V11 · representation transfer** | same structure, different representation family | circuit → its I–V graph; geometry → coordinates; apparatus → energy-bar chart; algebraic → graphical | translate between representations — the transfer the multi-representation framework exists to test |
| **V12 · inverse/goal swap** | make a given the unknown | "find R given I" → "find the R that makes I = 2 A" | run the relation backwards; often exposes whether it was understood or memorised |

**Why V9–V12 are the point.** V1 produces an item a student who memorised the first
one can answer. V9–V12 produce items that require the same *construct* but a
different *derivation* — which is the definition of an isomorph that measures
transfer rather than recall (see the learning charter: transfer is what distinguishes
learned from memorised).

**The constraint system is what makes structural editing safe.** Inserting a resistor
or a cevian changes what must hold. The rule: **every structural edit must come with
its own new constraint**, and every inherited constraint must be re-evaluated against
the new configuration. If adding a component leaves the constraint set unchanged, the
component is decorative and the edit is fake.

**Multi-representation transfer (V11), operationally.** Use the translation graph from
`reports/knowledge_handover_multirepresentation_physics_agent.md` §7.1/§7.3: each
representation has a semantic payload and a known misuse, and each edge is a
translation the learner can be asked to perform in either direction. A V11 isomorph
gives one representation and demands another — the demanded translation IS the item.

**Honest limits.** V10 and V11 can change the construct, not just the surface. When
that happens the honest label is `GENERATIVE_EXTENSION`, not `FAITHFUL_TRANSFER`
(protocol §1 mode grammar) — the item is still valuable, but it must not be sold as a
parallel form of the original. Check the backbone tests before labelling.


### Iteration 2 — Fable-authored set, 2026-08-11 (`cms/isogen_v2_fable/`)

First set built under the §7 structural taxonomy. **10 items from 7 source problems
across phy500 circuits and MathNet geometry**, distributed deliberately away from the
shallow classes:

| class | n | example |
|---|---:|---|
| V9 component insertion | 3 | a third series resistor (answer moves E·r/(R+2r) → E·r/(2R+3r), and the ideal-meter limit moves E/2 → E/3) |
| V10 topological rearrangement | 3 | the same two resistors re-wired series → parallel: meter loading VANISHES, so the source formula gives a wrong r-dependent answer |
| V11 representation transfer | 2 | a circuit given as its I–V characteristic — emf from the intercept, internal resistance from the slope |
| V12 inverse / goal swap | 2 | derive the general relation AD² = 2·r·AC, then invert it for AD = r → AC = r/2 |

**V1 parameter items: zero.** Contrast with iteration 1: 40/40 were number changes.

**What made these pass the "not superficial" test.** Every item was required to answer
*what must the student newly do?* — and the answer had to be a changed derivation, not
a changed arithmetic. Three worked examples of the standard:
- inserting a resistor moves the **limit**, so a memorised E/2 is wrong;
- rearranging series→parallel makes the loading error **disappear**, so the memorised
  formula is wrong in kind, not in value;
- re-attaching cevians from AB to BC turns an elegant 30° into **2·arctan(√3/9) =
  21.79°**, verified numerically — the pattern-matcher is wrong by 8°.

**Every structural edit carries a NEW constraint** (§7 rule): a fourth branch adds
`NBRANCH == 4`, a parallel pair adds `SHARED_TOP == 1 and SHARED_BOTTOM == 1`, the
inverse item adds the FIGURE-TO-ANSWER assertion `abs(LAD - R) < 1e-9`. An edit that
leaves the constraint set unchanged is decorative and was rejected.

**Iteration lessons for the next round.**
1. *Source figures already carry structural parameters worth mining.* P281 exposes
   `NLEFT`/`NRIGHT` — the resistor COUNT per side — so component insertion was
   directly drawable. Grep the corpus for count-like parameters before authoring.
2. *Verify numerically before claiming an item is different.* The cevian item was
   authored on the belief that 30° would break; it does — but only checking produced
   the exact 2·arctan(√3/9). Two draft answers were wrong until computed.
3. *V10 and V11 usually change the construct*, so they are honestly
   `GENERATIVE_EXTENSION`, not `FAITHFUL_TRANSFER`. 8 of these 10 are labelled so.
4. *Figures now compiled — gap closed.* All 10 varied TikZ figures compile under
   tectonic and clear `validator.py` (**10/10 render_gate PASS**), each carrying its own
   re-derived constraint set. Two of my own constraints were caught as **vacuous** by the
   300-draw perturbation check (`... or True`, and `abs((RX-LX)-(RX-LX))<1e-9`), which is
   exactly what that check is for — an author writing his own constraints will write
   tautologies, and only a mechanical check finds them.

**Review surface.** `/isogen2` in the review app (`webapp/isogen_v2_review.py`) renders
each pair side by side: original stem + source figure + stored answer, isomorph stem +
compiled figure + answer + worked solution, and a BUILD LOGIC panel showing what moved
in the figure code, the new constraint the edit introduced, every constraint re-evaluated
against the new configuration, the render-gate verdict, and the blind-verifier result.
One source (`mathnet_00a0`) stored TikZ but had never been rendered; `build_source_svgs.py`
compiles those once into a cache so the app needs no LaTeX at request time.

**Gotchas hit while compiling (circuitikz).** `rmeter*` is only defined inside a
`circuitikz` environment, not a bare `tikzpicture` — the error surfaces as
`I do not know the key '/tikz/rmeter*'`. And `to[C=$C_2=2C_1$]` breaks the key parser on
the nested `=`; write `to[C,l=$C_2$]` and put the relation in a separate label node.

---

## 8. The invariant audit — the test that caught two bad items

Every phy500 record declares, in `generation.isomorph_seed`, two lists: **invariants**
("must survive for a variant to remain the same question") and **manipulables** ("free
to vary", including named *structural* ones). Until this iteration ISO-GEN never read
them. Auditing the v2 set against them rejected 2 of 10 items that had already passed
every mechanical gate — compiled figure, non-vacuous constraints, blind-solvable.

### FP-21 · A topological rearrangement can *destroy* the construct instead of testing it

Both rejected items were V10 edits that removed the very effect the source assesses.

| item | the edit | why it failed |
|---|---|---|
| IG2-003 draft | series divider → parallel | P281 invariant #1: *"the meter's resistance must be comparable, or the loading effect vanishes and the question is empty."* Wiring in parallel makes the reading `E` regardless of `r` — the loading effect is gone, so nothing is being assessed. |
| IG2-006 draft | switch opened to isolate C2 | P259 invariant #4: *"the energy loss is independent of the resistance."* With nothing to redistribute into, no energy is dissipated at all; "energy lost" degenerated into a bookkeeping choice about which capacitor you look at. |

**The rule this yields:** *a structural edit must leave the construct's mechanism
running.* Changing the topology so the effect no longer occurs produces a **contrast
item** — pedagogically useful for testing when a formula applies, but it is not an
isomorph and must never be served as one. §7 now requires an `invariant_audit` on every
structural edit, marking each declared invariant `PRESERVED` / `DELIBERATELY_VARIED`
(only when the source's own manipulables sanction it) / `BROKEN` — and any `BROKEN`
blocks release as an isomorph.

The replacements keep the mechanism and change the topology:
- **IG2-003** → a **bridge**: two dividers in parallel, meter across the midpoints. The
  meter still loads what it measures, but now loads a Thévenin resistance the student
  must compute first. `V = E·r/(7R + 6r)`, ideal limit `E/6`. All five invariants hold
  (the asymmetry is a *sanctioned manipulable*, named in the source record).
- **IG2-006** → the partner capacitance becomes a **series pair** `C2 = C3 = 2C1`, so
  `C_s = C1`. Charge conservation, common final potential, and R-independent loss all
  survive; the new demand is reducing the pair first. `V_f = V0/2`, loss `C1V0²/4`, and
  reading the pair as parallel gives the diagnostic wrong answer `V0/5`.

### FP-22 · A telegraphing stem

The IG2-003 draft ended *"…and explain why the answer differs in kind from the series
case."* That sentence announces the discrimination the item exists to test. Same family
as the g-constant flaw in the owner's original review: **never let the stem assert the
insight the student is supposed to supply.**

### WP-12 · Stored figures must carry their own package requirements

All ten figures compiled during authoring and none could be recompiled from the stored
record: `circuitikz` was passed at validation time and never persisted, so `to[R=$R$]`
failed with `I do not know the key '/tikz/R'`. For a system whose premise is *"ISO-GEN
alters the code to get a new variant,"* a figure block that cannot be rebuilt from
itself is not encoded at all. Every figure now stores `tikz_libraries` and
`extra_packages`, and `repair_and_replace.py` recompiles each one **from its stored
block alone** — 10/10 PASS, self-contained.

---

## 9. FP-23 · The render gate cannot see what the figure SAYS — you must look

All ten v2 figures held `render_gate: PASS` — compiled, non-blank, ≥60px, every geometric
constraint satisfied, no vacuous constraints. Then I opened the ten PNGs. **Seven were
defective**, in four distinct ways that no mechanical gate can detect:

| item | defect | why the gate missed it |
|---|---|---|
| IG2-001, IG2-002 | **the voltmeter was not drawn at all** — the loading effect the item is entirely about was invisible, and the student could not see which resistor was measured | nothing was geometrically wrong; the missing element simply had no constraint |
| IG2-001, IG2-002 | printed `ℰ = 12 V` while the stem works symbolically in `E` | a literal in a label is not a geometric quantity |
| IG2-005 | **printed `P(0, −2√3)` beside P — the answer to part (a)** | the answer was in a text node, not a coordinate |
| IG2-010 | drawn at `AC = r/2`, **the answer to part (b)**, pinned there by two constraints | the constraints were *satisfied*; they were satisfied at the answer |
| IG2-004, IG2-010 | carried H, E, M, N and the source's right-angle MHN — construction from the *source's proof*, unreferenced by the new stem | extra correct geometry is still correct geometry |
| IG2-009 | an orphan `θ` on a dashed median the stem never mentions; positioned so it reads as the **half**-angle | a label's meaning is not a constraint |
| IG2-008 | axes so disproportionate the plot was a tall ribbon | aspect ratio is not a gate criterion |

**The rule:** `render_gate: PASS` certifies that a figure is *well-formed*, never that it
is *the right figure for this stem*. Author and checker must both open the image. Two
mandatory checks, neither mechanisable today:

1. **Every element the stem names is drawn, and nothing else is.** Inherited construction
   from the source's proof is not neutral — it asserts a different argument.
2. **The figure must not contain its own answer.** This is L-ISO-1's converse. As well as
   deleting constraints that pin the SOURCE's answer, add constraints that *forbid*
   pinning the NEW one — IG2-010 now carries `abs(CX - R/2) > 0.15*R` with the reason
   recorded, so the drawing can never drift back onto the answer.

Marking is subject to the same test: mark what the stem **gives** (the right angle at C,
the tick marks asserting a trisection) and never what the student must **supply** (the
right angle at D, which is the Thales step part (a) exists to demand).

---

## 10. FP-24 · Inlined SVGs collide, and the figure you inspect is not the figure served

Owner review: *"the circuit diagrams when rendered as figures has some text not clear."*
Every PNG I had inspected was correct. The defect was in the **page**, not the figures.

`pdftocairo -svg` renders each glyph as a path in `<defs>` and names them `glyph-0-0`,
`glyph-0-1`, … **in every file it writes**. Clip paths are numbered the same way. Inline
twenty such figures into one HTML document and every `<use href="#glyph-0-0">` resolves
to the **first** definition on the page — so each figure after the first silently draws
letters borrowed from an earlier figure. An `R` renders as a `V`, a `b` as a `c`.

Measured on the v2 page: **31 glyph IDs were defined by more than one figure**;
`glyph-0-0` by all ten. The fix is to prefix every `id`, every `href="#…"` and every
`url(#…)` per figure so each SVG closes over its own defs — 248 IDs, 0 duplicated after.

**This was not confined to ISO-GEN.** `render.py:sanitize_svg` is the shared inliner
behind the whole corpus browse surface and had the same defect, so *any* page showing
more than one encoded figure was affected. Fixed there too.

**The rule:** inspecting a PNG proves the *figure* is right; it says nothing about what
the *page* draws. Check the served HTML — count duplicate `id`s and dangling `#`
references — as a separate gate.

## 11. FP-25 · A stem may not defer to something the figure cannot say

IG2-007's stem read *"taking the cell polarities from the figure"* while the figure used
circuitikz's `battery1`, whose long and short plates are not distinguishable at render
size. The sign of every branch current — and therefore the question's third part, which
cell is being charged — was undetermined. **If the stem defers to the figure for a fact,
that fact must be unmissable in the figure.** Both cells are now drawn plate by plate
with explicit `+` and `−` terminals, and a constraint (`PLA > PSH`) holds the positive
plate longer than the negative one.

Two smaller instances of the same class, both found only by looking:
- **A label struck by a rule.** IG2-005's `E` and `F` sat on the x-axis with a 2pt drop,
  so the axis cut through both letters. Points that lie *on* an axis need their labels
  moved clear of it, not merely offset from the point.
- **A wire that goes nowhere.** IG2-003's rails ran two units past the last divider,
  reading as a fifth connection. Constraint now requires `XD <= XR`.

## 12. FP-26 · Build-logic prose is unverified text and drifts

IG2-009's recorded `edit` claimed *"the source joins C to the trisection points of AB."*
The source does no such thing: it places F on BC with CF = AD and joins **F** to the
trisection points, then asks for a **sum of two angles**. The item was sound and its
answer correct; the *description of what was changed* was wrong — and that description is
the whole justification for calling something an isomorph. Every gate in the stack
examines figures, constraints and answers; **nothing checks the prose.** Re-read each
`edit` and `why_not_superficial` against the source stem before release.

*(Separately: the source figure for `mathnet_00a0` labels angles `1, 2, 3` — its
solution's decomposition — while its stem asks for `∠CDF + ∠CEF`, and never draws DC or
CE. A corpus-side defect, logged, not introduced here.)*

---

## 13 · FIGURE FIDELITY — the standing checklist (owner-directed, 2026-08-11)

**Scope: every figure-bearing item in the corpus, not only ISO-GEN output.** These rules
generalize the label check and the typography check the owner asked for after reviewing
the v2 set. They apply equally to newly authored figures, to encoded corpus figures
(MathNet, phy500, chemistry SMILES/TikZ), and to any page that displays them.

The organising fact: **compilation and constraint evaluation certify that a figure is
well-formed, never that it is the right figure, and never that the page draws it
correctly.** Three distinct artefacts exist and they fail independently —

| artefact | what it proves | what it cannot show |
|---|---|---|
| the TikZ/SVG **source** | constraints hold; nothing is vacuous | whether it depicts *this* stem |
| the compiled **image** | it renders, is not blank, is legible | whether the browser will draw it |
| the **served page** | what a reader actually sees | — this is the only one that matters |

*Inspect the last one.* A defect found only at the served page (FP-24) passed every gate
above it.

### 13.1 Label fidelity — the figure must say exactly what the stem says

| # | rule | why it fails silently |
|---|---|---|
| L1 | **Completeness.** Every identifier the stem names is drawn. | A missing element is not a geometry error; no constraint references it. The v2 set shipped two voltmeter items *with no voltmeter drawn* — the effect under assessment was invisible. |
| L2 | **Exclusivity.** Nothing the stem does not name is drawn. | Extra construction is still *correct* geometry, so every check passes. Inherited points from the SOURCE's proof are the common case, and they assert a different argument than the one being asked. |
| L3 | **Denotation.** Names attach to the objects the stem describes, in the stated order and position ("D nearer B", "E between A and F"). | A figure can satisfy every metric constraint with two labels transposed. |
| L4 | **Marks state givens, never the insight.** Mark the right angle the stem *gives*; never the one the student must *supply*. | Marking the Thales angle in "show that AD² = 2r·AC" hands over the whole first step, and no gate distinguishes a given from a deduction. |
| L5 | **No answer in the figure.** Not printed as text, and not *drawn at* the answer configuration. | Both v2 breaches were invisible to the gates: one printed `P(0, −2√3)` beside P while part (a) asked for it; the other was *pinned by its own satisfied constraints* to the part-(b) answer. For an inverse item, add a constraint that FORBIDS the answer configuration and record why. |
| L6 | **Register agreement.** A symbolic stem gets a symbolic figure. | `ℰ = 12 V` printed against a stem working in `E` is a contradiction the compiler is happy with. |
| L7 | **Deference is a promise.** If the stem says to read something *off the figure*, that fact must be unmissable at served size. | See T4 — the found case compiled perfectly and left the question unanswerable. |

**Mechanical assist, not a substitute:** diff the identifiers drawn in the figure against
those named in the stem. It reliably catches L1/L2 candidates but is noisy (prose capitals,
symbol conventions like a meter drawn `V`), so it *shortlists* — a human still applies
L3–L7 by reading the two side by side.

### 13.2 Typography and rendering — what the reader actually sees

| # | rule | why it fails silently |
|---|---|---|
| T1 | **Namespace every inlined SVG.** Prefix each `id`, `href="#…"` and `url(#…)` per figure. | `pdftocairo` names glyphs `glyph-0-0`, `glyph-0-1`, … in *every* file it writes. Two figures on one page and each `<use>` binds to the first definition in the document: figures after the first draw letters borrowed from an earlier figure. Each figure is valid alone — the bug exists only in the composition. |
| T2 | **A label on a point that lies ON a rule must clear the rule**, not merely offset from the point. | A 2pt drop below a point sitting on an axis puts the axis through the letter. |
| T3 | **Nothing extends past what it connects.** | A rail or construction line running beyond its last element reads as a connection that does not exist. |
| T4 | **Meaning carried by size needs a redundant textual marker.** | circuitikz `battery1` distinguishes polarity by plate *length*; at render size the difference vanishes. Draw the element explicitly and add `+` / `−`, then hold it with a constraint (`PLA > PSH`). |
| T5 | **Independently scaled axes must be declared**, with every quantity read from labelled values rather than measured. | A plot whose axes carry different units is not wrong, but a figure that looks like a tall ribbon invites measurement off the paper. |
| T6 | **Check labels against each other and against drawn elements**, not only against the geometry. | Collision is a typographic property; no geometric constraint expresses it. |

### 13.3 The three passes, and what each can catch

1. **Mechanical** — compile from the *stored record alone*; evaluate every constraint;
   perturbation-test for vacuity; diff drawn identifiers against stem identifiers.
   *Catches:* malformed figures, stale constraints, missing package declarations.
2. **Visual** — open the rendered image. Non-negotiable, non-mechanisable, and where
   7 of 10 v2 defects were found.
   *Catches:* L1–L6, T2–T6.
3. **Served** — fetch the actual HTML and assert **zero duplicated `id` attributes and
   zero dangling `#` references**.
   *Catches:* T1, which the first two passes cannot see by construction.

### 13.4 Two invalidation rules

- **A figure edit voids every blind verification run against the earlier code.** A
  verification is a statement about a specific figure, not about an item. Clear and
  re-run; do not carry results forward. (Evidence that this matters: after the v2
  figures were repaired, a blind solver that had returned a bare `r` against the
  cluttered figure returned `HK = r` against the clean one, and an item confirmed
  *after* its printed answer was removed — which is the only way to know the solver
  derived it rather than read it.)
- **Prose is unverified.** `edit`, `why_not_superficial` and any "what changed" field are
  the justification for the whole artefact and **no gate examines them** (FP-26). Re-read
  each against the source stem before release; a false rationale is a blocking defect
  because it makes the item unauditable by anyone else.

### 13.5 The executable half

`corpus_intelligence/awm_corpus/figure_encoding_v1/tools/figure_fidelity.py` runs the
machine-checkable subset and prints, every time, the list of checks it did **not**
perform — so a clean run is never mistaken for a clean figure.

```
figure_fidelity.py all <items.jsonl> --served <page-or-url>
```

- `labels` — the L1/L2 shortlist (drawn identifiers vs stem identifiers). **Advisory,
  never blocking:** house style capitalises words for emphasis ("THREE equal resistors"),
  and those runs are shape-identical to point-name runs (`ABC`, `DAE`), so the emphasis
  vocabulary is listed rather than inferred and the tool still shortlists rather than
  rules.
- `served` — T1, and **blocking**: non-zero exit on any duplicated `id` or dangling `#`
  reference.

Verified against a negative control before it was trusted: four figures inlined without
namespacing report **16 duplicated ids, exit 1**; the same figures through the fixed
inliner report **0 duplicated, 0 dangling, exit 0**. A gate that cannot fail is not a
gate — the same discipline the constraint vacuity check exists to enforce.

### 13.6 Where these bind

Protocol `ISO_GENERATION_PROTOCOL.md`: **G-EYES** (13.1, 13.2 by inspection), **G-SERVED**
(13.3 pass 3), **G-DEFER** (L7/T4), **G-PROSE** (13.4), **G-SELF** (compile from the
stored record), **G-TIDY** (answer form). Evidence: FP-23 (gates cannot see meaning),
FP-24 (SVG collision), FP-25 (deference), FP-26 (prose drift), WP-12 (self-contained
figures).

---

## 14 · v2 run record — verification standing (2026-08-11)

### What was checked, and what it showed

| check | result |
|---|---|
| figures compiled from the stored block alone | **10/10 PASS** |
| figures inspected by eye (G-EYES) | 10/10 — **7 repaired in the first pass (§9), 4 more in the owner-prompted second pass (§10–11)** |
| answers re-derived and **asserted** quantity by quantity (sympy, no model) | **30/30 quantities across 10 items match; 0 mismatches** (`independent_check.py` — it now fails the run on a mismatch rather than printing both for eyeballing) |
| served page checked for glyph-ID collisions | 248 IDs, **0 duplicated**, 372 references, **0 dangling** |
| blind solve (stem + TikZ only, no image, no solution) | 9/10 machine-CONFIRMED; IG2-007 outstanding on provider latency, not on a defect |
| independent closed form | IG2-009 authored `2·arctan(√3/9)`; GLM returned `arccos(13/14)` and Kimi `\cos^{-1}\frac{13}{14}` — all three evaluate to 21.78679° |
| invariant audit against `isomorph_seed` | 32 invariants over 6 items; 2 items rejected and replaced, 1 re-parameterised, 1 (IG2-008) admitted with 2 BROKEN and an honest `audit_note` |

**The two checks answer different questions and must both run.** The sympy
re-derivation asks *is the answer right?*; the blind solve asks *does the figure carry
its information?* IG2-005 is the case that shows why: it was CONFIRMED blind **after**
the printed `P(0, −2√3)` was removed, which is the only way to know the solver derived
the point rather than read it. Conversely IG2-007 is unverified blind but its answer is
exact — provider latency is not evidence about an item.

**A figure edit voids every blind verification run against the earlier code.** Seven
figures were repaired in §9, so all nine prior verifications were cleared and re-run
rather than carried forward. The improvement was visible: IG2-004 returned a bare `r`
against the cluttered figure and `HK = r` against the clean one.

### 14.1 Comparator lessons — the checker needs checking too

- Two correct solvers reach the same angle by different routes, so string comparison
  reports a false disagreement. The comparator now evaluates closed forms in both
  radians and degrees and matches within 0.2%, requiring at least one side to come from
  an *evaluated expression* so two loose integers cannot agree by accident.
- Solvers answer in LaTeX freely. `\cos^{-1}\left(\frac{13}{14}\right)` needs
  de-LaTeXing, and the substitutions are order-dependent: `\frac{\sqrt{3}}{9}` only
  resolves after the inner `\sqrt` is gone, and `2\arctan(x)` must have its implicit `*`
  restored *before* the `arc`→`a` rewrite, or the digit glues to the name and kills the
  word boundary both that rewrite and the scanner depend on.
- Parentheses in these expressions nest arbitrarily deep; match them by counting, not by
  regex. A one-level-nesting regex silently evaluated `acos(13/14)` as `cos(13/14)` —
  0.599 rad instead of 0.380 — and would have reported a disagreement between two
  identical answers.

**Iteration 2 lesson L-ISO-1 — inherited FIGURE-TO-ANSWER constraints pin the SOURCE's
answer and must be REPLACED, not kept.** Compiling the inverse item (IG2-010) failed
because it carried the source's `abs(LAD - 2*sqrt(3)*R/3) < 1e-6`, which encodes the
answer for AC = 2r/3. The variant has AC = r/2 and AD = r, so the inherited constraint
correctly rejected the new drawing. **The constraint system caught an authoring error
that no amount of visual inspection would have** — the figure looked perfectly fine.
Rule for every variation that changes the answer: enumerate the source's
FIGURE-TO-ANSWER constraints, delete each one, and derive its replacement from the new
answer. Constraints that merely assert configuration (D on the circle, CD perpendicular
to AB) are inherited unchanged.

---

## 15 · v3 run — diagnostic probes (2026-08-12)

Ten items built under protocol v2.0. Everything below is generally applicable and belongs
to the standing checklist, not to this run.

### WP-13 · Under a constraint substitution, the parent's own answer is the best trap

When the governing law of one element is changed, the highest-value distractor is not an
invented number — it is **the answer the OLD law gives**, because that is the answer a
learner reaches by doing exactly what the parent taught. Three of the v3 items have this
property and it is worth engineering for deliberately:

| item | old-law answer | key |
|---|---|---|
| IG3-01 | 5.45 V — P281's own formula `E r/(R+2r)` | 4.00 V |
| IG3-02 | 9 W for all three circuits — a three-way tie | 12 / 27 / 9 W |
| IG3-03 | 50 m — P145's printed answer | 54 m |

**Pin the old-law value with its own figure-to-answer constraint.** If a drawn parameter
drifts, the trap silently stops being the parent's answer and the item loses the very
separation it was built for, while every other gate still reports PASS. The constraint in
IG3-01 asserts `E·r/(R+2r) = 5.4545…` for exactly this reason: it guards a number that
appears nowhere in the item's own answer.

Standing disposition when the old law is executed (protocol §6): output equals the key ⇒
`LAW_DECORATIVE`, fail · output expressible ⇒ it MUST appear as a distractor · output
inexpressible ⇒ record `OLD_LAW_NOT_EXPRESSIBLE` with the receipt and bind the nearest
attested corruption instead.

### WP-14 · Cross-execute every corruption before authoring, and repair by re-parameterising

Run every named corruption through SymPy at design time and assert pairwise separation of
all outputs, key included, at ≥2% of the larger magnitude on the **displayed** value. In
this run that found a real collision: IG3-04's "hanging mass included in the normal force"
and "assumed equal masses" both produced μ* = 1, so two different beliefs would have
written the same script and the item could not have told them apart.

**The repair is to re-parameterise the item until the values separate — never to delete the
colliding corruption.** Deleting hides the collision; the learner still holds the belief and
still writes the answer, and the item now reads it as something else.

Related: this is also how you discover that a distractor is not producible at all. Two
candidate errors for IG3-03 ("uses the loop radius in I = ⅖mρ²") turn out to give exactly
the key, because ρ cancels — they are undetectable, and listing them would have been
decoration.

### FP-27 · A `circuitikz` label containing `=` breaks the key-value parser

`to[R=$R = 150\ \Omega$]` fails with *Extra }, or forgotten $*. The option list is parsed as
key=value, so the second `=` ends the label. **Brace it: `to[R={$R = 150\,\Omega$}]`.**
This cost four of ten figures a compile in this run and is invisible until you read the
TeX log, because the item's own gate reports only "did not compile".

### FP-28 · `arc (180:-180:R)` does not centre where you expect

`\draw (x-R,0) arc (180:-180:R);` puts the centre at `(x, 0)`, so a loop drawn this way
sits **half below** the datum it was supposed to rest on. The v3 rollercoaster loop was
drawn buried in the ground and every mechanical gate passed it. When an object must rest on
a line, draw it as `\draw (x, R) circle (R);` and let the geometry state the contact
explicitly.

### FP-29 · A quantity parameter the drawing never prints is not a figure parameter

If `RVAL = 150` exists in the parameter block but no `\RVAL` appears in the TikZ, then a
figure-to-answer constraint written over it tests the *record*, not the *picture* — and the
picture can contradict the stem freely. Either bind the quantity into a printed label
(`$R = \RVAL\ \Omega$`) or move it out of the figure block, where it belongs to the stem.
The vacuity gate must therefore check two things, not one: every parameter is referenced by
the drawing, **and** every constraint references at least one parameter that is.

### FP-30 · An annotation that exists only to satisfy a gate is a smell

Three parameters were added to IG3-02 to count elements per panel, and the only way to make
them "used" was a caption reading *panel (a) holds 1 element X, (b) holds 2, (c) holds 0* —
information the reader can see, phrased as if they could not. **If the only reason a
parameter exists is to be referenced, delete the parameter.** A gate satisfied by adding
words to the page has not been satisfied.

### FP-31 · The figure may not name what the stem does not, and a symbol may not mean two things

IG3-06 labelled the rod's contacts `A` and `B` although its stem never refers to them, and
`B` was simultaneously the magnetic field. Both are G-EYES completeness-and-exclusivity
failures and neither is visible to any mechanical check. Standing rule: **every symbol on
the figure is either used by the stem or deleted, and no glyph carries two referents on one
page.**

### FP-32 · A guard parameter must never be rendered

IG3-09 carried `AMPL = 0.289` purely to assert that the graph's axis runs far beyond the
amplitude the question asks for. The caption written to "use" it printed
*(> 0.289 m)* — **the figure printed its own answer.** Guard parameters exist for placement
arithmetic and constraint evaluation only; if a guard needs to be referenced by the
drawing, reference it in a `\pgfmathsetmacro` that computes a ratio, never in a node.

### FP-33 · The G-EYES base rate is close to 100%, and repair takes rounds

| run | mechanical gates | human inspection, first build |
|---|---|---|
| v2 (2026-08-11) | 10/10 PASS | 7/10 defective |
| v3 (2026-08-12) | 10/10 PASS | **10/10 defective**, 3 critically |

The v3 criticals were an **open circuit** (a wire drawn through an element box and never
reaching the next node), a **turntable drawn as disconnected fragments**, and a figure that
**printed its own answer**. Four inspection-and-repair rounds were needed to clear the set.

Plan for this. A figure set is not "built" when it compiles; it is built when someone has
looked at every rendered image at serve size and can state what each one asserts. Budget
three to four rounds and treat the first pass as a draft. `render_gate: PASS` certifies
well-formedness and predicts nothing about correctness — that is now measured twice.

### FP-34 · `pdftocairo` SVG dimensions may carry no unit

The header is `width="266.59"` on this toolchain, not `width="266.59pt"`. A dimension check
regexing for `pt` silently fails to match, `min_dimension_ok` stays false, and ten
perfectly good figures report FAIL with an empty log — which reads as a compile failure and
sends you debugging the wrong thing. Match the unit optionally.

---

## 16 · v4 run — twelve items across four subjects (2026-08-12)

### WP-15 · The corpus that actually supports diagnostic generation is `v1/`, not the benchmarks

`awm_corpus/v1/` carries per-option `role` + `why`, `isomorph_seed` invariants and
manipulables, a solution path and a derived answer, for **10,631 physics · 11,384 chemistry
· 11,501 biology** records. `math_v1` adds **5,811** (of 22,917 — 17,106 are BLOCKED on
corrupted stems). That `option_intent[X].why` field IS the misconception-mapped distractor
data; it is the MCQ analogue of phy500's `common_errors[].wrong_result`.

**SUPERChem-500 is not a generation source and must never become one.** It carries
`no_training_export: true` and the benchmark canary, and it has no `isomorph_seed` — so it
is both contractually and mechanically bundle-ineligible. Check the canary before treating
any 500-item collection as a parent pool.

### WP-16 · `chemfig` is the chemistry figure encoding, and SMILES is its data channel

`chemfig` compiles under tectonic. Structures are written as `\chemfig{HO-CH_2-CH(-[6]OH)-CHO}`
and the SMILES string is stored beside each as the machine-readable channel. Note two gaps:
`rdkit` is not installed, and this chemfig version has no `\smiles{}` macro, so the drawing
is hand-encoded and *checked against* the SMILES rather than *generated from* it. At scale,
install rdkit so the render derives from the SMILES; until then, make the blind examiner
check the correspondence explicitly — it did, and confirmed agreement.

### WP-17 · A distribution figure must be plotted from its equation, never traced

The Boltzmann item plots `sqrt(E)exp(-E/T)` normalised to unit area. That normalisation
*forces* the physics: peak position `E = T/2` moves right with temperature, peak height goes
as `1/T` so the hotter curve is lower, and the areas stay equal. A hand-drawn version is
where the classic misconception lives — raising the peak with temperature — and a figure
that got it wrong would teach the very error the item exists to detect. Bind the shape
constraints (`TB > TA`, peak positions, `1/T` heights) as machine-checked geometric
constraints, not as drawing notes.

### FP-35 · Kimi returns NOTHING when the job is too big for its token budget

Asked for three complete item records in one call, Kimi-k3 consumed all 32,000 output tokens
on reasoning and returned **zero characters** — a silent failure that costs a full call
($0.51) and reports success. **The fix is to split the job, not to raise the cap:** a larger
budget buys more reasoning, not more answer. One item per call delivered all three, each
complete. The standing rule "no meaningful token cap" is necessary but not sufficient —
also size the ASK to the budget.

### WP-18 · The second author catches leaks the first author cannot see

Fable drafted the osmosis item with two curves — walled cells and wall-free protoplasts —
and Kimi independently specified **one curve only**, because plotting the protoplast trace
prints the answer to the question being asked. Kimi's spec went further and enumerated
forbidden strings (`turgid`, `equilibrium`, `burst`, `lysis`, `protoplast`) that would leak
the reasoning even without a second curve.

Generalisable: **when a figure shows a comparison, ask whether the comparison IS the answer.**
If it is, draw only the control and let the stem name the other case. A `must_not_show` list
belongs in every figure spec, and it should name strings as well as shapes.

### WP-19 · Honest witness coverage below 1.0 is a sign of a working process

Kimi returned 0.6 witness coverage on all three biology items and named the pairs it could
not separate. Fable's own items reported 0.78 and 0.86 where pairs genuinely collided. A set
in which every item claims 1.00 is either trivial or unexamined — the separation matrix is
only worth having if it is allowed to say `NOT_SEPARATED`.

### FP-36 · An attribution collision is repaired by re-parameterising, and it recurs

The codominance item's "complete dominance" belief and its "probability not compounded"
belief both produced N = 11 at a 5% threshold. Tightening to 1% separated them to 17 and 51.
This is the second run in which cross-executing every corruption at design time found a
collision that no other gate would have caught (v3 found one in the turntable item). Treat
the pairwise-separation assertion as mandatory, not as a nicety.

---

## 17 · The external JEE-Advanced audit and the v2.1 layer (2026-08-13)

An external examiner audit of the v2 and v4 sets
(`reports/ISOGEN_AI_EXPLAINABLE_IITJEE_ADVANCED_AUDIT.md`, 58 sections) landed with two
REJECT-grade findings — both verified independently, both repaired and re-verified the
same day. The protocol response is the v2.1 layer (engineered with Kimi-k3,
`reports/isogen_v21_calibration/`). Every entry below is the generally applicable form.

### FP-37 · Generation depth is not student difficulty — and the error runs both ways

The depth ladder classifies the EDIT; difficulty is a property of the SHORTEST valid
solution a prepared candidate can find. Ten of the audit's twenty-two verdicts turned on
this gap, in BOTH directions: D4a/D4b items whose shortest solutions are two standard
relations (IG4-P2), reagent recall (IG4-C1) or one equality of exponents (IG4-C2) — and a
D2 topology edit (IG2-003) the audit rated Advanced-candidate because no memorised
template covers it. Two independent fields from now on: `depth_class` (provenance) and
`difficulty_band` (blind examiner, shortest solution, UNCALIBRATED). Never infer either
from the other; a mismatch triggers a second blind solve, not a ban.

### FP-38 · Coupling multiplies hidden assumptions — the flagship was invalid

IG4-P3, the set's most ambitious item, assumed q = CBℓv at every instant. That requires
NEGLIGIBLE SELF-INDUCTANCE, never stated. Verified before repair: with L > 0 the reduced
ODE is mLq''' + (m/C + B²ℓ²)q' = FBℓ — oscillatory current, non-constant acceleration;
the stored key is strictly the L→0 limit. Every domain coupling imports the idealisations
of BOTH domains, so D5 items need MORE closure scrutiny than single-domain items, not
less. "The intended textbook approximation is obvious" is not a defence. Audit effort
must scale with ambition.

### FP-39 · A repair can create the next defect

IG4-C3's first blind solve flagged an unstated Kp convention. The repair added "taking
the standard pressure as 1 atm" — dimensionless-K language — onto a key reported in atm,
creating F-CONVENTION-MIXED, which the external audit then caught. The repair satisfied
the finding and broke the item, because there was no contract to regress against.
Standing rule (v2.1 §9): repairs edit the model contract FIRST, then the stem; the full
battery re-runs. Satisfying the finding is not finishing the repair.

### FP-40 · An approximation stated as motivation does not license exact notation

IG4-P1 said ρ ≪ R (motivation) and answered "the least value" with exact multiples of R.
Motivation and licence are different speech acts. The stem must instruct the neglect
("neglect ρ compared with R in the centre-of-mass geometry") or define the symbol so the
answer is exact. Same family, second tier caught on re-verification: "negligible
resistance" licenses approximately-zero heat; exactly-zero needs "treat these
idealisations as exact".

### FP-41 · The item record is not the student item — the projection must be TESTED

IG4-C1's rendered figure printed the raw SMILES under each structure: the record's
machine-readable channel leaked into the student layer. `student_visible` is now a
DEFINED projection with a denial list, and G-SELF recompiles both renders — "never
render" that is not tested is a wish. (General form of FP-32, the guard parameter that
printed the answer.)

### FP-42 · A gate that is not executed is decoration

IG4-C2's Boltzmann figure is decorative — the stem supplies the equation and every
number. v1.2 G9.3 ALREADY fails text-redundant representations; the build recorded the
figure block as passing without running that check. Recurring system failure (OCR
zero-violations; P9): not missing rules, unexecuted ones. A gate whose verdict can be
asserted without a receipt eventually will be — bind every gate to an artifact that
cannot exist unless the check ran (v2.1: figure_role's reads_figure receipt).

### FP-43 · A scaffold can hand over the discriminating step — in either direction

IG4-M3 part (a) derives the mixture expression part (b)'s inverse needs, reducing the
intended reconstruction to algebra. Counterfactual test: delete the earlier part — does
the later part's demand change? Dispositions: restructure, declare TEACHING_SEQUENCE (no
band), or accept the examiner-rated band. The reverse rule also binds: later parts must
not become unanswerable because an earlier numerical answer was missed.

### FP-44 · Combination language conflates elements — "right" keys can be wrong

"V₀/2 across every element pair" (IG2-006) was true of the series combination and false
of each element (V₀/4 each). Network-equivalent language must enumerate per-component
values; "across the combination" is banned unless each element's value also appears.

### FP-45 · The orphan datum

IG2-004 carried AC = 2r/3 — inherited from the parent, used by nothing, diagnostic of
nothing. Every stem datum now needs a ledger entry: a solution step, a corruption input,
or the independence ask itself ("show HK is independent of the position of C" — the
audit's elegant disposition turns the red herring into the point). Otherwise deleted.

### FP-46 · Rules that matter need local teeth

The k≥2 tournament mandate existed from v1.3 and two builds shipped single-candidate:
a globally scoped rule had no local enforcement point. v2.1 attaches it to the claim it
protects — no band ≥ ADVANCED without ≥3-candidate tournament provenance — and leaves
practice bands cheap. Attach every rule that matters to the claim that needs it.

### FP-47 · Node dump or mx catalog as the chemistry bundle (owner 2026-09-01)

`resolve_node("C7")` and `item_meta.map_mx_ids` (p50≈80) are not a hinge. They clog
the author (FP-9 / `P-LLM-CLOG`) and skip the enrichment layer that actually
attests classroom errors the derived list missed (hollow 1s, `Mg2O2` on the zero
`g9/ch_09/H013`, buffer mole-excess, sealed-balloon buoyancy, …). Remedy is
`hinge_pack(unit_id)`, not a bigger prompt.

### WP-20 · An external audit is the residual loop running pre-administration

The v2.0 residual/patch machinery is dormant until learners respond, but an external
expert audit produces the same artifact: findings no internal gate predicted, each
becoming a named code, a wiki entry, and where mechanizable a seeded fixture (four were
seeded from this audit). Schedule external audits as instruments, not events.

### WP-21 · Elegance is a tournament criterion, not a gate

IG2-010 (clean identity, inverse use) vs IG2-009 (correct but ugly 2·tan⁻¹(√3/9) when
cos∠DAE = 13/14 was available). The target quantity is a design choice; "the quantity
whose exact form reveals structure" is a comparison a tournament can execute.
TARGET_INELEGANT is a flag that loses ties — a failure code would make it a gate, which
it must never be (adjudicated, v2.1 §8).

### WP-22 · One examiner call, many gates

The blind solve the pipeline already pays for was extended with a structured schema —
shortest solution, alternate interpretations, stated-vs-assumed idealisations, shortcut
checklist, scaffold check, band. Five audit gates absorbed into one existing call; first
execution matched all four keys AND surfaced a second closure tier the first pass missed.
Pay for isolation once; spend it everywhere.

### WP-23 · The old-law dual solve is the system's most reliable distractor source

Confirmed across physics (point mass vs rolling), chemistry (NaBH4 vs LiAlH4), and
biology (viability renormalisation; walled vs wall-free): solve under both laws, bank the
old answer as the trap when expressible. Mandatory at G-LAW; the audit independently
endorsed it as the strongest pattern in the sets.

### WP-24 · Contract before stem

Items whose idealisations, conventions and approximation order were written down before
the stem had somewhere to regress repairs against; the one item repaired WITHOUT a
contract (C3) is the one whose repair created a defect. Authoring order is a validity
instrument, not a style preference.

### WP-25 · Natural checks are drift alarms

Ideal-meter limits, mass cancellations, tidy node potentials and clean coefficients
caught contradictions that mechanical gates missed, in both this audit and the v3 build.
An item with no limit, special case, or symmetry check is unfinished — and the check
belongs in the answer, where the student earns it.

### WP-26 · Chemistry author/examiner bundle is `hinge_pack(unit_id)` (owner 2026-09-01)

When the topic is a curriculum hinge, load **that hinge** from both layers by
`unit_id` string equality: map statement (mechanism, derived mx, `mx_na`) plus
enrichment rows whose `serves_statement_ids` contain the UID, plus ChemEd X
witness mx not on the derived list. Packet, then LLM. Do not dump a node, do not
copy `map_mx_ids` onto the item, do not invent distractors while 24 attested
witnesses sit unwired (`mx_refs` = 1/543 on the NCERT hinge enrichment). Consumer:
`reports/paper/src/hinge_pack.py`. WikiSkill: `P-HINGE-UID-PACK`,
`P-ENRICHMENT-WITNESS-MX`. Frozen L20 engine not rewritten; new runs read the pack.

This is WP-1 (attested bundle) at curriculum grain: the referent is the hinge, not
a chapter blob.

---

## 2026-09-01 · Hinge packet as the chemistry bundle (owner)

Audit gap, not a generation run. Derived mx and ChemEd X enrichment for NCERT chemistry
are both keyed by hinge `unit_id`; no ISO-GEN consumer loaded both. Added **WP-26**
(load `hinge_pack(unit_id)`) and **FP-47** (node dump / mx catalog is not a bundle).
L20 tray/engine hashes unchanged. WikiSkill patterns `P-HINGE-UID-PACK` and
`P-ENRICHMENT-WITNESS-MX`.
