# TeacherTwin — tagged question bank (four subjects)

Static GitHub Pages instrument for the NCERT chemistry **comprehensive map**, **enrichment layer**, and the **Cambridge-tagged question bank** across chemistry, biology, physics, and mathematics. Pick a subject from the menu. Questions keep Cambridge `chapter_id` / `subtopic_id`. Chemistry still joins NCERT hinges at query time via the projection table.

Live site (after one Settings click): **https://khkreddy.github.io/TTwin/**

Enable Pages: GitHub → **khkreddy/TTwin** → **Settings → Pages → Build and deployment**. Source **Deploy from a branch**. Branch **main**, folder **/ (root)**. Save. Wait a minute.

## What it tests

| Surface | What happens |
|---|---|
| **Browse** | Pack → node → chapter → subtopic. Questions and hinge packs. |
| **Prompt retrieve** | “Chemical energetics at senior level” compiles to a selector (aliases, no model). Fuzzy prompts can use **AI**. Retrieve is deterministic (`provider_calls: 0`). |
| **Lesson planner** | Map hinges + enrichment + journal overlay. AI prose is Zinsser-style and uses all three packs. |
| **Journal** | Teacher notes/links, mapped to hinges. They reappear on the matching lesson and go into the AI pack. |
| **Test maker** | N + seed → paper. Drawn figures compile in the browser from TikZ (no stored PNGs). Learner sheet has no mx, no examiner comments, no crops. |
| **ISO-GEN** | Teacher writes an idea (often fuzzy). AI restates intent, maps internally to a hinge pack, authors a CANDIDATE MCQ. Hinge codes stay system-facing. Frozen Lamport-20 is not rewritten. |
| **Map** | 523 NCERT hinges with mechanism, CANDIDATE mx, mastery / LoK / gaming pockets from the comprehensive map. |

Join law: a hinge `unit_id` pulls map mx + enrichment (`serves_statement_ids`). Questions keep `cam:9701:5` / `AS_A:9701.x.y`. Cross-map retrieve is `node × grade_band` via the projection table. A question tagged at a higher node is retrieved by any descendant selector.

## Run locally

```bash
python3 tools/serve.py
# http://127.0.0.1:8766/
```

The local server also proxies `POST /kimi` for AI calls. GitHub Pages cannot hold a secret; paste a key under **Settings**. If the browser blocks CORS, point the proxy URL at this local `/kimi`.

Rebuild derived JSON from the live AWM tree (does not rewrite frozen exam / V15 / public map):

```bash
python3 tools/build_data.py
```

## Data (derived, committed)

```
data/
  subjects.json              catalog (packs, counts, file paths)
  meta.json / RECEIPT.json
  vocab/{chemistry,biology,physics,maths}.json
  nav/{chemistry,biology,physics,maths}.json
  questions/{subject}-{igcse|senior|olympiad}.json
  nodes.json hinges.json enrichment.json projection.json   # chemistry map
```

Agent harnesses for the live site (Teacher Model and Student Model, instructional invariants, when not to call AI): `harness/`. Start at `harness/README.md`. Six teacher slots, one student slot (post-score feedback). Deterministic retrieve / typeset / score first.

Deploy issues and checks: `DEPLOYMENT_WIKI.md`.

Not in this repo: the 46 MB comprehensive map blob, live V15, frozen exam.jsonl, API keys, pre-rendered figure PNGs.

## License

MIT. See `LICENSE`.
