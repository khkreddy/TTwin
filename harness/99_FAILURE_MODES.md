# 99 · Failure modes

| Mode | What it looks like | Tripwire | Law |
|---|---|---|---|
| False learning | Same-item retest credited; hints counted; same-session mastery | Ledger rejects those transitions | I2, I5, I6 |
| Context-dump retry | Empty AI → bigger packet resubmitted | Packet caps; one attempt only | P-LLM-CLOG |
| Map dump | V15 / 523-mx catalog pasted into a prompt | Packet cap; fail closed | P-LLM-CLOG, P-HINGE-UID-PACK |
| Freeze rewrite | Write to exam.v1 / L20 / V15 / public map sha | Sha write-gate; overlay only | P-FROZEN-REWRITE |
| Vendor leak | Vendor or model slug on github.io | String lint; slot-id references only | `95_STRINGS.md` |
| CANDIDATE as frequency | “Common mix-up”, “most students” | Phrase lint; badge unverified | Law 7 |
| Key without rationale | Bare letters reaching scoring | Standalone key inference forbidden; letter is a field of analysis | I11, I13; T-SOLVE fold |
| Scoring without honesty | Key with no generated-analysis label | Render-time label | Honesty protocol |
| Unscorable silence | No-key items silently marked wrong | Exclusion + banner is the only path | Kernel scoring |
| LoK/mx conflation | Guessing named as a mechanism corruption | Diagnosis engine requires stored mx | Three-state law |
| Mx fabrication | AI emits mx ids not in the slice | Copy-only validation | P-ZERO-IS-A-RESULT |
| Gap-fill | Zero mx treated as a hole to author into | `mx: []` marker; T-AUTHOR banned from inventing mx | P-ZERO-IS-A-RESULT |
| Hinge inflation | Chapter list presented as hinge map | Phy/bio labeled chapter list; diagnosis Mastery/LoK/unclassified | P-SYLLABUS-INTERIM |
| Anti-narration leak | Feedback before Finish donates the criterion | Evaluability slice only after score; no pre-Finish student slot | I2, I11–I14 |
| Phantom pool | MathNet / Phy-500 / Pack C shown as live papers | Builder gated on stem count | Corpus honesty |
| Cross-subject graft | Chem mx invented for physics | Empty mx renders empty | P-SYLLABUS-INTERIM |
| Journal forgery | AI writes the teacher note | Journal write = teacher only | T-UNIT fold |
| Session leak | Modified item persisted into the pool | `session/` has no write-to-store path | P-ITEM-MODIFY-WHOLE |
| Write-after-write | Solution analysis overwritten | Write-once at uid × sha | P-SOLUTION-ANALYSIS |
| Forked state | Persona writes outside its namespace | Single-writer per namespace | Precedence 3 |
| Self-certify | Agent sets `owner_ratified` | Flag has no agent-writable path | Author ≠ checker |
| Silent-dark | Dark store surfaced as live paper | Store whitelist; assemble refuses | `91_DARK.md` |
| Wiki at inference | Wiki pages in an agent packet | Forbidden; skills only | P-WIKI-AT-TRAIN |
