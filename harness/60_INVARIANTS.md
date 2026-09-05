# 60 · Instructional invariants (student-facing)

Source: IIP-2.0 (Hendrick–Kirschner). Purpose: prevent **false positives for learning**.

Current ship: MCQ paper + row-select + score + feedback. Absent: isomorph families, delayed re-probe scheduler, full prerequisite DAG; phy/bio mx empty; maths stems dark.

| Id | Law | Status | TTwin now | Waits for |
|---|---|---|---|---|
| I1 | Skill-only success | ENFORCE NOW | Credit only on scored five-ID items in the 20,792-stem pool | Maths stems |
| I2 | No assisted credit | ENFORCE NOW | Take mode has no hints; Modify-touched items are CANDIDATE, credit-excluded | — |
| I3 | Generative error correction | DEGRADE HONESTLY | After feedback, re-answer is allowed; no mastery weight; do not show the key before they try again | Open-response (Phy-500) |
| I4 | Anti-guessing | DEGRADE HONESTLY | MCQ correct = weak evidence; never grant mastery from one sitting | Constructed response |
| I5 | No immediate mastery | ENFORCE NOW | Same-session ceiling is EVIDENCED | — |
| I6 | No identical-item mastery | ENFORCE NOW | Re-probe needs a different `item_uid` | — |
| I7 | Delayed confirmation | DEGRADE HONESTLY | Hold PENDING_DELAY; later session with a different item may confirm | Scheduler |
| I8 | Interleaved exit | ENFORCE NOW | Default seed interleaves; blocked order stamps weaker evidence | — |
| I9 | No unguided discovery (novice) | ENFORCE NOW | UNCALIBRATED skills: lesson digest then test; student never gets bare map | — |
| I10 | Step-locked complexity | ENFORCE NOW (scoped) | Order by pack/grade tags where present | Full difficulty tags |
| I11 | Detectability | ENFORCE NOW | Chosen vs key on every item after Finish | — |
| I12 | Localisability | ENFORCE NOW | Chem: hinge; phy/bio: chapter, and say so | Phy/bio hinge map |
| I13 | Interpretability | DEGRADE HONESTLY | Chem: ≤1 CANDIDATE mx on the chosen distractor. Else Mastery / LoK / unclassified. Never invent mx | Validated mx beyond chem |
| I14 | Actionability | ENFORCE NOW | Every miss: re-answer, lesson link, or later different-item re-probe | — |
| I15 | High-threshold gates | ENFORCE NOW | CONFIRMED needs multiple unassisted items across sessions; AI does not set thresholds | — |
| I16 | Active spirals | DEGRADE HONESTLY | Teacher can seed mixed papers | Auto-spiral |
| I18 | Transfer | DEFER | No transfer claims. ISO-GEN CANDIDATEs cannot evidence transfer | Isomorph families |
| I19 | Mathemathantic detection | DEGRADE HONESTLY | Dark pools show status, not fake papers | Maths stems |
| I20 | No progress through error | ENFORCE NOW | Errors append error events only. Ban “you learned from this mistake” | — |

If an invariant cannot be enforced, **say so** (DEGRADE HONESTLY). Do not simulate it with copy.
