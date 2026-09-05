# 15 · Legal AI slots

Seven legal slots: **six teacher, one student**. The live AI module exports nine named functions over those seven. Two folds. Any exported function beyond the nine named below is **FORBIDDEN until classified** against this file.

Sampling for author / modify / first-write / grade: temperature **1** only, low reasoning effort, 4096 completion tokens, 90s abort. Design brainstorms may use 32000. Empty response = the ask exceeded budget. **Never retry by enlarging the packet.** Temperature 1 means acceptance is deterministic (schema + closed-set validation); the prose is not.

Public copy names the synthesis layer **AI**. Harness text refers to **slot ids**.

## Registry

| Slot | Persona | Live function | Class | Trigger |
|---|---|---|---|---|
| **T-SEL** | Teacher | selector compiler | LEGAL | Deterministic alias parse is empty or ambiguous |
| **T-UNIT** | Teacher | ISO intent restatement ⊕ journal bind | LEGAL (fold, k-param) | ISO-GEN intent (k=1); journal note bind (k=1–4) |
| **T-AUTHOR** | Teacher | CANDIDATE author | LEGAL | Teacher-initiated ISO-GEN after T-UNIT |
| **T-MOD** | Teacher | whole-item Modify | LEGAL | Teacher edit instruction on one assembled item |
| **T-SOLVE** | Teacher | first-write solution analysis | LEGAL; bare-letter inference is **FOLD-INTO**, forbidden as standalone | Assemble/Finish hits unknown `item_uid × sha` |
| **T-BRIEF** | Teacher | lesson prose | LEGAL | Teacher toggles AI on a built digest |
| **S-FEED** | Student | post-score feedback | LEGAL — **sole student slot** | Finish event, and only Finish |

### Folds

- **Bare-letter key inference → T-SOLVE.** One cognitive act: the key letter is entailed by the per-option why. Two separate calls over the same items can disagree. A key that contradicts its own rationale is unauditable (I11/I13). The letter is a *field* of `awm.solution_analysis.v1`, never a separate opinion. Agents must not call standalone key inference as an entry point. (Go-live pin: remove that entry point in code.)
- **Journal mapping → T-UNIT.** Same act as ISO intent: ground free text against a closed, deterministically pre-filtered candidate list. Difference is arity (k≤4 vs k=1). The note body is always teacher-authored; AI returns bindings only; bindings are CANDIDATE until the teacher saves.

## Packets and outputs (summary)

Full field caps: `40_PACKETS.md`.

| Slot | Packet | Output | Must not invent | Fail-closed |
|---|---|---|---|---|
| T-SEL | prompt ≤2k; closed nodes id+label only | selector JSON (`pack`, `subject`, `nodes`, …) or `{error, ask}` | uids, counts, items, nodes outside the list | Discard; show deterministic result + “AI could not refine” |
| T-UNIT | free text ≤2k; candidate units ≤64 after chapter/subject filter | restated intent + `unit_ids[1..k]` | hinges for phy/bio, units outside list, the note body | Abstain → teacher picks from the filtered list |
| T-AUTHOR | chem: `hinge_pack`; phy/bio: chapter + explicit `mx: []` | one CANDIDATE MCQ, `serve_eligible: false`, `owner_ratified: false` | mx ids, VALIDATED stamp, second items, SMILES/hinge codes on the stem | Schema fail → discard, log, no silent retry |
| T-MOD | one item, learner-whitelist fields + instruction ≤1k | whole item (stem + A–D; TikZ only if needed), session namespace, key UNVERIFIED | new freeze uid, pool membership, partial-item edits | Invalid → keep original item |
| T-SOLVE | ≤8 items: stem ≤900 chars + options + option-table + capped map slice | `awm.solution_analysis.v1` write-once at uid×sha; honesty: not a published mark scheme | key without rationale, refs not in the slice, official mark-scheme authority | Those items unscorable + banner; teacher may hand-key |
| T-BRIEF | three already-typeset packs (map / enrichment / journal), total cap | Zinsser prose | facts, hinges, citations, frequency claims outside the packs | Show the three packs raw; prose is garnish |
| S-FEED | scored paper + evaluability slice; **mx/ledger stripped at builder** | `{overall, per_item[], next_steps[]}` | ledger print, frequency claims, keys for items outside the paper, criterion before Finish, new items | Deterministic score table still ships + “AI feedback unavailable” |

## Census pin

Before go-live, grep the AI module. Every exported function beyond the nine named in the design pass (selector, ISO intent, author, modify, bare-letter keys, analyze, lesson prose, journal bind, grade) is FORBIDDEN until classified here. The old “four teacher + one student” undercount is why this pin exists.
