# Science grades 6–8 CANDIDATE tray

These items were drafted by AI from compiled Science map intelligence and a packed source item. They are **not** in the live Science bank.

- `serve_eligible` is false. Keys are UNVERIFIED.
- Nothing here is exam-ready. A teacher must ratify before any merge into `data/questions/science-junior.json`.
- Packets and model results sit beside each item so the compile path can be inspected.
- Full subject maps are not stored here.
- `pack.json` and `nav.json` are the Browse / Test maker overlay. In the app, choose Science then **AI tray · unverified**. That overlay is not the live 109-item bank.

## CHANGELOG (Kimi K3 Max freeze 2026-09-19)

Harness edits after freeze `ttwin.g68_harness_freeze.v1`. Moonshot Test-maker, live 109, G1–G8 meanings, and `ttwin.question.v1` enum were not rewritten.

- **C1** `resultToCandidate` keeps `learn_by_solve`, `one_or_more`, multi-letter `mcq_key`, `tikz_packages`, plus candidate-top `build_logic` and `mx_option_map`. Why: analytics cannot name a knowledge state if those fields are dropped.
- **C2** `pickSource` no longer penalizes TikZ; visual hinges prefer figure sources. `compileUnit` removes a source figure only when the hinge has no visual referent. Why: corpus figures are the templates.
- **C3** `sanitizeTikz` rewrites `circuitikz` to `tikzpicture` and sets `tikz_packages: ["circuitikz"]` when bipole syntax remains. If sanitize fails, figure mode falls back to remove. Why: TikZJax cannot draw `to[battery1]` without the library. Deviation: do not rewrite bipoles to invented coordinates. `js/paper.js` also injects the circuitikz package at render time when needed.
- **C4** Gate **G9** in `tools/modify_g68.js` only (not Test-maker `validateModifyResult`): ≥2 wrong options must bind to distinct packet Mx types. Fail closed. Why: putting G9 in `js/kimi.js` would break teacher Modify with no `mx_option_map`.
- **C5** `compileUnit` attaches `packet.build_logic`. Copied to the candidate wrapper, never into learner `item`.
- **C6** Multi-select encodes as live `item_type: mcq` + `assessment.one_or_more` + `mcq_key` like `BC`. Keys stay UNVERIFIED.
- **C7** `FORMAT_MAP` sends assertion-reason / two-part / statement-reason to `structured`. Unknown types fail closed.
- **C8** this changelog.
- **C9** Browse AI tray starts at big-idea **any**, not S1, so figure items are not hidden by the default inquiry filter.

Grok authors via `node tools/modify_g68.js ingest --unit … --source … --result result.json`. No Moonshot stem writes on this path.

## Grok tray style (2026-09-19 rectification)

Learner options must not leak mix-up recipes. One hinge per item. Four options in one grammatical frame. No extra objects or city padding. `mx_option_map` is teacher-side and advisory. Do not edit Kimi a1/a2 files.
