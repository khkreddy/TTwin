> **Provenance.** Moonshot `kimi-k3` (Kimi K3 Max) · 2026-09-18 · 715 s · prompt 3,121 / completion 18,037 tokens · temperature 1. Briefs: `/tmp/kimi_pack_plan/{SYS,USER}.md`. **CANDIDATE — not applied.** Owner approval required before any pack, vocab, map, or question write.

# TTwin Re-Alignment: Four Demand Packs on the Five Final Maps

**Status:** CANDIDATE
**Auditor:** Kimi K3 Max
**Date:** 2026-09-18
**Repo:** /home/harik/TTwin · khkreddy/TTwin main @ c62efef · 86,320 live questions
**Scope:** Audit of Grok four-pack draft; plan to align packs, vocab, questions, LBS/ISO-GEN with the five FINAL maps. Nothing applied.

---

## 1. Verdict on the Grok draft

Clause by clause. "Keep" means adopt as written; "amend" means adopt with the stated correction; "reject" means strike.

| # | Grok clause | Verdict | Reason |
|---|---|---|---|
| 1 | Four packs | **Keep** | Matches owner intent 1. |
| 2 | Vocab = map titles | **Keep** | Correct, and it is what kills the live vocab defect (vocab M4 = Calculus vs map M4 = Euclidean geometry). Pin: titles come from the five final maps, not from current vocab files. |
| 3 | Pack-scoped menus | **Keep** | Required. Current `nodeOptions()` dumps all `vocab.ideas`; this must die. |
| 4 | Middle = Maths + combined Science; 9+ = chem/phy/bio/maths | **Keep** | Matches the maps: science.json is the 6–8 spine; Q/C/P maps start at 9. See §5. |
| 5 | Dump all extra banks into olympiad because `practice_tier=advanced` | **Reject** | This is the **"all MathNet → olympiad" error**. It classifies by provenance, which owner intent forbids twice (origin must not decide pack; every question lands by demand). MathNet contains grade-9 algebra; AIME contains senior-level items; JEE contains single-hinge grade-12 items. Bulk-routing 25k+ items by source tag is the brute-force smell TTwin exists to avoid. Pack is computed from bound hinges + demand (§4). |
| 6 | Biology ids L1–L9 | **Reject** | This is the **L1–L9 vs Q1–Q9 error**. The final BIOLOGY_MAP.json numbers its origins **Q1–Q9**. L* exists only in the broken live slim projection (mixed L*/Q*, node=UNRESOLVED). Adopting L1–L9 would bless the broken consumer and fork the id space. The projection gets rebuilt from the map; L* is deleted, not propagated. |
| 7 | Hide B-shelves as big ideas | **Amend** | Correct that B* are shelves, not top-level big ideas (B2 alone holds 308 maths statements). But "hide" must not mean "lose": shelves resurface in the Olympiad pack as the extension section (§6) and in internal tooling. Note PHYSICS_MAP B1/B2/B4 have empty titles — one minimal patch (§12). |
| 8 | Phase 1 = UI filter only | **Reject** | A cosmetic filter over the wrong ontology doubles migration debt: menus would still render vocab titles against map-tagged questions. Phase 1 must pin the maps and regenerate the projections; the UI filter rides on corrected data (§11). |

Net: 4 keep, 1 amend, 3 reject. The draft's skeleton (four packs, map titles, scoped menus, subject split) is right. Its two data errors (L1–L9, source-bulk olympiad) and its sequencing error (UI-first) are not cosmetic; each would bake a second wrong ontology into the product.

---

## 2. First principles

Five principles bind everything below.

1. **The map is the sheaf.** One conceptual spine per subject. Slim maps, vocab, nav, enrichment, question metadata are projections and consumers. When a consumer disagrees with a final map, the consumer is wrong.
2. **Pack is demand, not provenance.** A pack answers "what does this item demand of a student?" Never "where did this item come from?" Source tags (MathNet, JEE, Cambridge, RJB) are evidence the binder may weigh; they are never the classifier.
3. **The hinge is the join.** Every question binds to statement `unit_id`(s) on a final map. Node, chapter, subtopic, pack, menu placement, LBS recipe, ISO-GEN family — all derive from that one join. A question without a hinge is unfinished inventory, not content.
4. **Board is a view.** NCERT, Cambridge, CISCE are layers already on the statements (`syllabus`, `board`, `grade_band`). A board profile is a filter and a label router over the same spine. Never a fork, never a pack name.
5. **The LLM is the one-time binder.** Spend the model once per question to bind hinges, against a closed candidate set drawn from the map. After that, every downstream artefact — menu, LBS option, ISO-GEN variant — is a deterministic join. Zero per-task model calls.

---

## 3. Authority: how the pieces relate

**Authority (source of truth):** the five final maps — `science.json`, `MATHEMATICS_MAP.json`, `CHEMISTRY_MAP_COMBINED.json`, `PHYSICS_MAP.json`, `BIOLOGY_MAP.json`. They own: node ids and titles, big-idea structure, statement `unit_id`s, `decision_hinge`, `mechanism`, `mx[]`, syllabus/board layers, grade occupancy.

**Consumers (regenerable projections):**

| Consumer | Current state | Disposition |
|---|---|---|
| Live slim maps | biology.json broken (UNRESOLVED, L*/Q* mix) | Regenerate all four as projections of the finals. Biology first. |
| Vocab files | Maths vocab is a rival ontology (M4 = Calculus) | Replace wholesale with projected titles. Do not patch. |
| Nav / menus | Dump all vocab | Rebuild as map queries filtered by pack (§10). |
| Questions (86,320) | No hinge field; node + family codes only | Additive schema change; bind hinges; re-derive node/chapter/subtopic/pack. Keep old codes as provenance. |
| Enrichment | chemistry n=543; maths/physics/biology empty | Revalidate chemistry against the combined map. Backfill the other three **per statement** (unit_id-keyed), not per question, so one enrichment row serves every bound question. |

**The consumer pin.** Add `data/maps/MANIFEST.json`: five entries {file, sha256, schema version, map version}. Every consumer (slim generator, vocab generator, UI tree endpoint, retrieve, LBS compiler, ISO-GEN) resolves maps through the manifest. Regeneration is allowed only from pinned inputs, and outputs carry the pin hash. This is the single lever that keeps "live slim maps and vocab may be wrong" from recurring.

**Not rewritten:** frozen exam.v1. Live chemistry hinge sentences. The only map patch I propose is titling PHYSICS_MAP B1/B2/B4 shelves (§12) — titles only, no statement touched. Astra's earlier APPROVE_WITH_FIXES on science.json: confirm the fixes landed before pinning (Phase 0 gate).

---

## 4. The four packs

| Pack id (internal) | Teacher label | Band |
|---|---|---|
| `middle_6_8` | Middle School · Grades 6–8 | 6–8 |
| `secondary_9_10` | Secondary · Grades 9–10 | 9–10 |
| `senior_11_12` | Senior Secondary · Grades 11–12 | 11–12 |
| `olympiad_iit` | Olympiad / IIT Practice | extended |

No letters, no board names. The label is year-group + demand.

**Membership rule (deterministic, runs after hinge binding):**

1. Let `h_p` = primary hinge (a statement `unit_id`). Read `grade_band` off **that statement** — not the hub span. A hub like ACIDBASE spans 10–12, but each statement under it carries its own band.
2. Base tier `t` = band of `h_p` bucketed: 6–8 → middle; 9–10 → secondary; 11–12 → senior.
3. Escalation to olympiad, one-directional, when the binder's demand signature fires: (a) primary or supporting hinge lives only on a B-shelf (concept outside the senior spine), **or** (b) advanced multi-hinge synthesis — ≥3 bound hinges chained across nodes, or mx-chain depth beyond the statement's own mx — with corroborating evidence (contest format, multi-stage derivation). Provenance (JEE Advanced, AIME) is logged as evidence, never sufficient alone.
4. Exactly one pack by construction: single primary hinge gives one base tier; escalation only moves upward; no ties.
5. No candidate statement on any final map → `unbound` quarantine for owner review (map gap or item defect). Quarantine is a pre-pack state, not a fifth pack.

**Worked example A — a MathNet quadratic that is Secondary.**
Item (MathNet corpus): "α and β are roots of x² − 5x + 6 = 0. Find α² + β²." Candidate set: EQUATION-hub and M2 statements on quadratics (NCERT_SECONDARY layer, plus the IGCSE core algebra graft). Binder picks primary = the grade-9 quadratics statement (`math/grade_09/…`, EQUATION hub), supporting = symmetric-function arithmetic. Demand: single hinge, band 9–10, no synthesis. **Pack: `secondary_9_10`.** That it arrived via a competition bank is irrelevant; a weak student meets this item in grade 9.

**Worked example B — two electrochemistry items on the same hinge, different packs.**
Both items bind primary to `C5/H-ECHEM` (span 10–12).
- Item 1: "Calculate EMF of Zn|Zn²⁺(0.1M)||Cu²⁺(1M)|Cu at 298 K." Single-step Nernst. Primary = grade-12 Nernst statement. One hinge. **Pack: `senior_11_12`.**
- Item 2 (JEE Advanced): concentration cell where EMF must be chained through ΔG = −nFE, an equilibrium constant, and a gas-volume stoichiometry step. Primary = the same H-ECHEM statement; supporting = H-STOICH (C1) + thermodynamics (C6). Three hinges chained across three nodes. Demand signature fires. **Pack: `olympiad_iit`.**

Same hinge, same node (C5), same menu neighbourhood — different pack, because pack is demand. The teacher browsing Senior Secondary sees item 1 under the electrochemistry hinge; the Olympiad teacher sees item 2 under the same hinge flagged as synthesis. That is the TTwin distinction: the hinge join carries the intelligence, the pack carries the demand.

---

## 5. Subject model: 6–8 vs 9+

- **Middle School (6–8): two subjects.** *Mathematics* (M-origins, band-filtered) and *Science* — one combined subject whose spine is `science.json` (S1–S6 origins + 16 grains, 391 units; grades 6/7/8 = 129/119/143). There is no separate chemistry/physics/biology at 6–8, because no final map supports one. The current split of junior science items across biology/physics files with S* nodes is a storage accident; the subject is Science.
- **Secondary and Senior (9–12): four subjects.** Mathematics (M1–M8), Chemistry (C1–C8 + hubs), Physics (P1–P8 + hubs), Biology (Q1–Q9 + hubs). The Q/C/P maps start at grade 9 (C1–C5 span 9–12; P-spans begin at 9; Q-map is grades 9–12).
- **Olympiad:** the senior spine, all four subjects, plus shelf extensions (§6).
- science.json is the 6–8 spine only. Do not stretch it to 9–10; the discipline maps take over at 9.

---

## 6. Teacher-facing trees, copied from the final maps

Labels are node titles verbatim; ids stay internal. **Visibility rule:** an origin or hub is visible in a pack iff at least one statement under it has `grade_band` intersecting the pack band on **any** layer — NCERT span **or** Cambridge core/supplement/AS/A **or** CISCE (ICSE/ISC). This is how P8 (NCERT span empty) and P4 circuits (NCERT 12) legitimately appear in Secondary via the Cambridge layer. Marks below: ✓ = NCERT span; (CAM)/(CISCE) = visible via that layer, verify exact occupancy during projection.

### 6.1 Middle School · Grades 6–8

**Mathematics** (origins = big ideas):
- [ ] M1 — "Number…" (verbatim from map) — span 6–12 ✓
- [ ] M2 — verbatim — 7–12 ✓ (7–8 here)
- [ ] M3 — verbatim — 6–12 ✓
- [ ] M4 — **Euclidean geometry** — 6–12 ✓
- [ ] M5 — verbatim — 6–10+12 ✓ (6–8 here)
- [ ] M8 — verbatim — 6–12 ✓
- Hidden: M6 (9–12), M7 (10–12).
- Concepts (hubs): PLACEVALUE (7–9+12), RATIO (7–8), EQUATION (7–12), PROOF (7–10). Hidden: COUNTING, FUNCTION, TRIG, DERIVATIVE, CONDPROB.

**Science** (S1–S6, titles verbatim from `concept_tree`; 16 grains as concepts):
- [ ] S1 · S2 · S3 · S4 · S5 · S6 — six titles, all visible; each carries grade tags 6/7/8 from its units (129/119/143).

### 6.2 Secondary · Grades 9–10

**Mathematics:** M1 ✓ · M2 ✓ · M3 ✓ · M4 Euclidean geometry ✓ · M5 ✓ · M6 ✓ (9–12) · M7 ✓ (10–12; grade-10 slice) · M8 ✓. Hubs: PLACEVALUE (9) ✓ · EQUATION ✓ · COUNTING (9) ✓ · PROOF (–10) ✓ · TRIG (10–12; grade-10 slice) ✓ · RATIO — NCERT 7–8 only, visible only (CAM) if the graft occupies 9–10 — verify · FUNCTION, DERIVATIVE, CONDPROB hidden.

**Chemistry:** C1 ✓ (H-MOLE at 9) · C2 ✓ · C3 ✓ (PERIOD 10) · C4 ✓ (STOICH 10) · C5 ✓ (REDOX 10, ECHEM 10) · C6 ✓ (10) · C7 — NCERT 11, visible (CAM): IGCSE 0620 teaches this band — verify · ACIDBASE hub ✓ (10) · SOLUB hub — NCERT 11–12, (CAM) verify · C8 hidden (NCERT 12; A-level only).

**Physics:** P1 ✓ (9) · P2 ✓ (9) · P3 ✓ (9–12) · P4 — NCERT 12, visible (CAM): circuits sit in the 9–10 Cambridge layer ✓ · P5 ✓ (10) · P6 — NCERT 11, (CAM) verify · P7 — NCERT 12, (CAM) verify · P8 — NCERT ∅, visible (CAM) only — this is the canonical case the visibility rule exists for. Hubs: SHM (9) ✓ · SUPERPOSITION (10) ✓ · CIRCUITS (10 + CAM) ✓ · VECTORS, MOMENTUM — NCERT 11, (CAM) verify · INDUCTION hidden.

**Biology** (all titles verbatim):
- [ ] Q1 Cellular and molecular basis of life
- [ ] Q2 Diversity
- [ ] Q3 Structural organisation
- [ ] Q4 Control/coordination
- [ ] Q5 Bioenergetics
- [ ] Q6 Reproduction
- [ ] Q7 Inheritance
- [ ] Q8 Health/biotech
- [ ] Q9 Ecology

Visible where statement `grade_band` ∈ 9–10 on NCERT or Cambridge layers (609/648 statements to filter). Hubs MEMBRANE-TRANSPORT, BIOMOLECULES, TAXON-KEY, EXCHANGE-TRANSPORT, ATP-YIELD, MEIOSIS, DNA, IMMUNITY shown as occupied.

### 6.3 Senior Secondary · Grades 11–12

- **Mathematics:** M1–M8 all visible (M5 at 12; M7 10–12). Hubs: EQUATION · COUNTING (11) · FUNCTION (11–12) · TRIG · DERIVATIVE (11–12) · CONDPROB (12) · PLACEVALUE (the +12 in its span is odd but the map is authority — verify intent) · RATIO hidden unless a Cambridge/A-level statement occupies the band.
- **Chemistry:** C1–C8 all visible (C7 at 11; C8 at 12; SOLUB 11–12; MOLE 11–12 continues). Full hub set.
- **Physics:** P1–P8 all visible (VECTORS, MOMENTUM at 11; INDUCTION at 12; P8 via CAM A-level layer — verify). Full hub set.
- **Biology:** Q1–Q9 at 11–12; all eight hubs as occupied.

### 6.4 Olympiad / IIT Practice

The Senior Secondary tree verbatim, **plus one section per subject: "Extensions"** — statements living only on B-shelves (maths B2 alone is 308 statements) and statements bearing advanced mx. Shelves are **not** big ideas; they render as extension lists with shelf titles. Blocker: PHYSICS_MAP B1/B2/B4 titles are empty — either apply the minimal title patch or keep physics Extensions hidden until patched (§12, Q3).

Numbering discipline: biology is Q1–Q9 everywhere; maths is M1–M8 from MATHEMATICS_MAP, never from vocab; no second numbering is introduced anywhere in this plan.

---

## 7. The question object: hinges as the join

**Schema (additive on ttwin.question.v1; nothing existing removed):**

```
hinges: {
  primary:    <unit_id>,            # one statement on a final map
  supporting: [<unit_id>, ...],     # 0–3, prerequisites / co-hinges
  binder: { method, model, candidate_set_hash, confidence, bound_at }
}
```

- **Primary hinge** = the decision the item tests. It drives `node`, menu placement, pack base tier, and the LBS unlock_recipe.
- **Supporting hinges** = what the item also pulls on. They drive LBS scaffolding order and ISO-GEN variant families, and feed the olympiad demand signature.

**Derived fields (recomputed, stored, never hand-set):**

| Field | Derivation |
|---|---|
| `node` | `statement(primary).node` |
| `pack` | rule in §4 |
| `chapter_id`, `subtopic_id` | board-view codes of the bound statement; default view, rerouted by the customization layer (§8). Old codes retained as provenance (`cam_family`, `ncert_family` stay). |
| `chapter_label`, `subtopic_label` | titles from map / concept_tree for the active view. Ends code-shaped labels like "M1". |

**Why this unlocks LBS and ISO-GEN with zero per-task calls.** The compiler (harness/82_LBS_COMPILER.md) needs `spec = hinge + mx/failure mode`. Today it can't get there because questions aren't bound, so LBS falls back to overlay/constructor. With `hinges.primary` set, the recipe is: `question → statement → decision_hinge + mechanism + mx[] + enrichment row (unit_id-keyed) → unlock_recipe`. ISO-GEN varies surface and mx while holding the hinge fixed. Both are joins. The one-time spend bought the join; everything after is arithmetic.

**The one-time binding job (closed candidate set, not open generation):**

1. **Deterministic fast paths first.** Cambridge-coded rows: the chemistry IGCSE example already carries `subtopic_id=IGCSE:0620.6.2` and the Cambridge graft carries `unit_id`s in `IGCSE:` space — exact join, zero model. Same for any 1:1 NCERT family code. Expected to clear Cambridge papers and most coded chemistry.
2. **Candidate generation for the rest.** Per question: statements filtered by subject + any code overlap, then top-k (k≈15) by embedding/lexical match of stem against `decision_hinge` + `mechanism` text. The candidate set is a slice of the pinned map; its hash is logged.
3. **LLM selection.** Prompt = stem + the closed candidate list. Output = one primary + ≤3 supporting unit_ids + confidence. Ids validated against the manifest; hallucinated ids reject to retry, then to quarantine.
4. **Persist + log.** Write `hinges`, append a binding_log row (uid, candidates hash, picks, confidence, method).
5. **QA.** Stratified audit sample per source × subject (n≥200 per stratum at rollout). Acceptance ≥97% primary-hinge agreement with human review; failed strata rebind with tightened candidates.

Cost shape: deterministic joins first, LLM only for fuzzy banks (MathNet, SciBench, JEE, Phy-500, SUPERChem, HiCogMath, AIME, RJB). One pass, then the corpus is bound forever.

---

## 8. Board-agnostic core, later customization

The core stores every board layer on the statements (NCERT 523/558/156-style splits already exist per map). Packs are demand bands (§4). Therefore the core ships with no board in any pack name, menu, or label.

The later per-account layer is a **profile, not a fork**: `{board, syllabus}` → (a) filter statements to that board's layer when rendering trees and counts, (b) route `chapter_id`/`subtopic_id`/labels to that board's codes and titles (e.g. surface `0620.6.2`-style structure for a Cambridge teacher, NCERT chapter structure for another), (c) leave hinges, nodes, packs, mx, and enrichment untouched. Same spine, different lens. Building packs named "IGCSE" now would make that layer impossible without a second migration.

---

## 9. Corpus sanitisation

Rule zero: **no retag uses source as pack.** Every item flows: bind hinges → compute pack (§4) → re-derive node/labels (§7).

| Source bank | Binding path | Expected pack spread |
|---|---|---|
| MathNet (25,498) | LLM bind to M-statements | Mostly Secondary/Senior by demand; a minority Olympiad. The bulk-olympiad route is the rejected Grok error. |
| SciBench | LLM bind; watch for concepts beyond the spine | Senior/Olympiad; off-spine items → quarantine, owner decides map gap vs drop. |
| JEE / Phy-500 | LLM bind to P/C statements | Senior and Olympiad split by demand signature. |
| SUPERChem | LLM bind to C statements | Secondary/Senior/Olympiad by demand. |
| HiCogMath | LLM bind to M statements | By band. |
| AIME | LLM bind | Largely Olympiad, but per-item: senior-demand items go Senior. |
| Cambridge papers | Deterministic code join (fast path) | By statement band; feeds the Cambridge-layer visibility in §6. |
| RJB 6–8 | Bind to science.json + M-middle statements | Middle School. |

`question_bank` dissolves; its contents redistribute. Five packs become four.

**Relabel code-shaped labels.** Any `chapter_label`/`subtopic_label` that is a code ("M1" across junior maths) is replaced by the map title for the derived node/statement. Labels are regenerated, not hand-edited.

**Repair live slim biology.** Regenerate as a projection of BIOLOGY_MAP.json: nodes Q1–Q9; each unit's `node` taken from `statement.node` (kills UNRESOLVED); titles from the map. L* ids are deleted. If legacy joins need a bridge during migration, keep an internal alias table for one release, then drop it — question `node` is re-derived from hinges anyway, so the bridge is short-lived. Vocab biology = map titles.

**Junior science.** Items currently filed under biology/physics with S* nodes: subject = Science (combined), menus render S-node titles from concept_tree. File layout may persist internally; the model is one subject.

**Reversibility.** All retag writes are additive or regenerable; old values kept as provenance; dry-run diff report (per pack, per subject, per source) to the owner before any bulk write.

---

## 10. UI contract

1. Teacher picks a pack → subject list is fixed by pack: Middle → Mathematics, Science; Secondary/Senior/Olympiad → Mathematics, Physics, Chemistry, Biology.
2. Pack + subject → **big-idea list = pack-visible origins** of that subject per the §6 visibility rule. Label = map node title. Count = bound questions. `nodeOptions()` dumping `vocab.ideas` is removed; menus are map queries pinned to the manifest.
3. Origin → **concepts = hubs and grains** under that origin, pack-filtered.
4. Concept → **sub-concepts = chapter/hinge labels** drawn from bound statements (short hinge titles / concept_tree titles). Raw `unit_id`s never render. Codes never render.
5. Pack change rebuilds the tree from the map, not from a cached vocab file. Two teachers in different packs see the same spine at different depths — Middle is a subset, Secondary adds, Senior adds, Olympiad adds extensions (owner intent 6, enforced structurally).

---

## 11. Phased work, with owner gates

| Phase | Work | Owner gate |
|---|---|---|
| 0 | Pin the five maps: manifest + hashes. Confirm Astra's science.json fixes landed. | Confirm pin. |
| 1 | **Regenerate projections**: slim maps and vocab from finals. **Biology projection first** (Q1–Q9, kill L*/UNRESOLVED); **maths vocab replacement** (M* from map; vocab-M4-Calculus ontology deleted). Physics B-shelf empty titles surfaced for patch decision. | Tick the §6 trees against the regenerated files. |
| 2 | **Schema**: additive `hinges` field; derive node/pack/labels; binding_log. Deterministic fast-path binder on coded subsets; measure join rate. | Join-rate threshold met on coded banks. |
| 3 | **Hinge-binding campaign**: LLM pass on fuzzy banks with closed candidate sets; stratified audit. | ≥97% audit agreement, per stratum. |
| 4 | **Pack remap** by §4 rule; dissolve `question_bank`; relabel code-shaped labels; dry-run diff first. | Spot-check; verify every question in exactly one pack; quarantine list reviewed. |
| 5 | UI contract (§10) on regenerated data. | Walkthrough: pack switch rebuilds trees; no codes visible. |
| 6 | LBS compiler from hinge (kill overlay fallback for bound items); ISO-GEN on bound families; **enrichment backfill** maths/physics/biology per statement. | Zero per-task model calls verified in traces. |
| Later | Board customization layer (§8). | Separate proposal. |

---

## 12. Risks and open questions

**Risks**
- R1. Binding precision on fuzzy banks. A wrong primary hinge poisons node, pack, menu, and LBS at once. Mitigation: closed candidate sets, confidence logging, stratified audit, rebind path.
- R2. Olympiad/Senior boundary disputes. The demand signature will false-positive on hard single-hinge senior items. Mitigation: escalation requires (a) or (b) in §4, never provenance alone; quarantine appeals.
- R3. PHYSICS_MAP B1/B2/B4 empty titles block the Olympiad Extensions section for physics.
- R4. Vocab replacement mid-migration can orphan menu joins. Mitigation: menus derive from maps, not vocab, after Phase 1; vocab becomes disposable.
- R5. Off-spine items (university-level SciBench concepts) expose map gaps. Quarantine keeps them out of packs until the owner rules.

**Open questions (five)**

1. **Olympiad demand signature.** Owner's preference for the escalation threshold: hinge-count/mx-chain rule as in §4, a lighter provenance-plus-one-hinge rule, or manual review of borderline items?
2. **Cross-band primaries.** Confirm pack band reads from the bound statement's own `grade_band` (not hub span), with olympiad the only upward escape. Any item family where this misplaces content?
3. **Physics shelf titles.** Approve the minimal patch (titles for B1/B2/B4 only, no statement changes), or hide physics Extensions until a later map revision?
4. **Science at 6–8.** One subject "Science" with S-origins as big ideas (my assumption), or a second browse level grouping S-nodes by discipline flavour?
5. **Enrichment backfill.** Is unit_id-keyed enrichment for maths/physics/biology a hard gate before Phase 6 LBS rollout, or may the compiler ship reading map-only intelligence (decision_hinge + mx) with enrichment joining later?

— Kimi K3 Max

---

## Root-checker notes (not Kimi)

Grok checked the auditor output against the five final maps. The plan is intact above. Two occupancy parent slips in §6.2 Chemistry (visibility rule still holds; tick against the map at Phase 1):

- Periodicity is hub `C1/H-PERIOD`, not under C3.
- Stoichiometry is hub `C5/H-STOICH`, not under C4.

Astra was not a co-auditor (OpenAI credits exhausted). Live slim maps, vocab, questions, and frozen exam.v1 were not modified in this turn.
