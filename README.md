# TeacherTwin — NCERT chemistry showcase

Static GitHub Pages instrument for the NCERT chemistry **comprehensive map**, **enrichment layer**, and the **tagged question bank** (Cursor Wave 3.5: Cambridge coordinates kept, RAG join via projection + ancestor closure).

Live site (after one Settings click): **https://khkreddy.github.io/TTwin/**

Enable Pages: GitHub → **khkreddy/TTwin** → **Settings → Pages → Build and deployment**. Source **Deploy from a branch**. Branch **main**, folder **/ (root)**. Save. Wait a minute.

## What it tests

| Surface | What happens |
|---|---|
| **Browse** | Pack → node → Cambridge chapter → subtopic. Questions and hinge packs. |
| **Prompt retrieve** | “Chemical energetics at senior level” compiles to a selector (aliases, no model). Fuzzy prompts use **Kimi K3**. Retrieve is deterministic (`provider_calls: 0`). |
| **Lesson planner** | Teacher digest from enrichment (caution / mx / difficulty / sequencing) with ChemEd X citations. Optional Kimi prose; null URLs must not become invented DOIs. |
| **Test maker** | N + seed → paper. Learner sheet has no mx, no examiner comments, no crops. |
| **ISO-GEN** | New MCQ from `hinge_pack(unit_id)` via Kimi. CANDIDATE, `serve_eligible=false`. Does **not** rewrite frozen Lamport-20. |
| **Map** | 523 NCERT hinges with mechanism, CANDIDATE mx, mastery / LoK / gaming pockets from the comprehensive map. |

Join law: a hinge `unit_id` pulls map mx + enrichment (`serves_statement_ids`). Questions keep `cam:9701:5` / `AS_A:9701.x.y`. Cross-map retrieve is `node × grade_band` via the projection table. A question tagged at a higher node is retrieved by any descendant selector.

## Run locally

```bash
python3 tools/serve.py
# http://127.0.0.1:8766/
```

The local server also proxies `POST /kimi` to Moonshot (`X-Kimi-Key`). GitHub Pages cannot hold a secret; paste a key under **Settings**. If the browser blocks CORS to `api.moonshot.ai`, point the proxy URL at this local `/kimi`.

Rebuild derived JSON from the live AWM tree (does not rewrite frozen exam / V15 / public map):

```bash
python3 tools/build_data.py
```

## Data (derived, committed)

Under `data/`: nodes, 523 hinges (slim pedagogy + mx), 543 enrichment items, projection table, tagged chemistry nav rows, typeset stems for complete-exam MCQs.

Not in this repo: the 46 MB comprehensive map blob, live V15, frozen exam.jsonl, API keys.

## Kimi K3

- Model: `kimi-k3`
- Endpoint: `https://api.moonshot.ai/v1/chat/completions`
- Roles: selector compiler, ISO-GEN author, lesson prose
- Temperature 1. Selector output is JSON only — never item uids.

## License

MIT. See `LICENSE`.
