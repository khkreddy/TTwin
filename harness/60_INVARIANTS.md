# 60 · Instructional invariants (student-facing)

Source: IIP-2.0 (Hendrick–Kirschner). Purpose: prevent **false positives for learning**.

A system is educational only if it cannot report progress unless durable, transferable cognitive change has occurred. These are failure-prevention laws, not best practices.

Current ship: MCQ paper + row-select + score + feedback. Absent: isomorph families, delayed re-probe scheduler, full prerequisite DAG, constructed-response grading; phy/bio mx empty; maths stems dark.

If an invariant cannot be enforced, **say so** (DEGRADE HONESTLY or DEFER / DARK). Do not simulate it with copy.

| Id | Law | Status | TTwin now | Waits for |
|---|---|---|---|---|
| I1 | Skill-only success | ENFORCE NOW | Credit only on unaided scored five-ID items in the 20,792-stem pool. Take mode has no AI path. | Maths stems |
| I2 | No assisted credit | ENFORCE NOW | Take mode has no hints; all student AI gated on Finish; Modify-touched items are CANDIDATE, credit-excluded | — |
| I3 | Generative error correction | DEGRADE HONESTLY | After feedback, the student must produce the correction (re-answer / notebook). No mastery weight. Do not show the key before they try again. No constructed-response grading. | Open-response (Phy-500) |
| I4 | Anti-guessing | DEGRADE HONESTLY | MCQ correct = weak evidence; row-select stronger where present; one sitting never grants mastery | Constructed response, isomorphs |
| I5 | No immediate mastery | ENFORCE NOW | Same-session ceiling is EVIDENCED / PROGRESS_EVIDENCE | — |
| I6 | No identical-item mastery | ENFORCE NOW | Re-probe needs a different `item_uid`. With families DARK, no mastery claims at all | Isomorph families |
| I7 | Delayed confirmation | DEFER | Hold PENDING_DELAY in the schema; no scheduler exists; banner-level honesty only | Scheduler |
| I8 | Interleaved exit | DEFER | Default seed interleaves when the selector spans units; no spiral exit engine | Profile-driven assembly |
| I9 | No unguided discovery (novice) | ENFORCE NOW | UNCALIBRATED skills: lesson digest then test; student never gets bare map; no “explore” surface | — |
| I10 | Step-locked complexity | DEFER | No difficulty metadata admitted; harness bans inventing difficulty labels. Order by pack/grade tags where present is display, not a gate. | Full difficulty tags + profile |
| I11 | Detectability | ENFORCE NOW | Chosen vs key on every item after Finish — a lookup | — |
| I12 | Localisability | ENFORCE NOW (partial) | Chem: hinge. Phy/bio: chapter, and say so. Five-ID tags always. | Phy/bio hinge map |
| I13 | Interpretability | DEGRADE HONESTLY | Chem: ≤1 CANDIDATE mx on the chosen distractor, not printed as a ledger. Else Mastery / LoK / unclassified. `null` analysis → “no verified notes”. Never invent mx. | Validated mx beyond chem; analysis coverage |
| I14 | Actionability | ENFORCE NOW | Every miss: re-answer, lesson link, or later different-item re-probe. Vague encouragement banned. | — |
| I15 | High-threshold gates | ENFORCE NOW | CONFIRMED / FAMILY_MASTERY needs multiple unassisted items across sessions. Until families exist, mastery gates are maximally high by absence. AI does not set thresholds. | Families + scheduler |
| I16 | Active spirals | DEFER | Teacher can seed mixed papers. No auto-spiral. | I7 + I8 infrastructure |
| I17 | Expert decomposition | ENFORCE NOW (lookup) + DEGRADE | Post-Finish: stored solution by deterministic lookup; T-SOLVE rationale + per-option why is the decomposition slice; T-BRIEF carries it to the teacher. No interactive step-scaffold engine. | Worked-step scaffold surface |
| I18 | Transfer | DARK | No transfer claims. ISO-GEN CANDIDATEs cannot evidence transfer. LADDER / TRAP / STRUCTURE stay dark. | Isomorph families, attested trap keys |
| I19 | Mathemathantic detection | DEGRADE HONESTLY | Dark pools show status, not fake papers. Chosen-distractor patterns visible to the teacher via per-option analysis. No detector model. | Trap-key attestation; maths stems |
| I20 | No progress through error | ENFORCE NOW | Errors append error events only. Ban “you learned from this mistake”. Ledger never advances on error. | — |

Telemetry that would prove each invariant, and the tripwire when it is violated, live in `99_FAILURE_MODES.md`. If an invariant cannot be answered in engineering terms, the system is instructional theatre.
