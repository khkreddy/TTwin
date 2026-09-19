# Science 6–8 Modify examples (Grok ingest)

Library for agents. Grok-authored CANDIDATEs only. Do not copy Kimi a1/a2 as templates for Mx maps; do copy their **option parallelism**.

## Good

### Force as interaction — `candidate:g68:science:grade_08:ch_05:H001:a3`

Owner: this item is good; **option C is a good distractor**.

- Hinge: a force is a push or pull **between two objects**.
- A (key): kick — push between foot and ball.
- B: ball applies a force to itself (not a pair).
- **C: pull acts only on the wagon** — still the interaction idea, not units.
- D: leaf falls with no objects interacting.

Do not replace C with pascal/newtons. That is a second hinge.

### Length conversion — `…ch_05:H003:a3` (after fix)

Four options, same frame: `2 m = 2 cm.` / `200 cm.` / `0.02 cm.` / `20 cm.` No mix-up recipe in the text.

## Bad (must fail G10–G12)

### Stem list not covered — `…ch_01:H001:a3`

Stem numbers activities 1–4. Options only mention 1, 2, 3. Activity 4 is a dead alternative. **G10**.

### Nested multi-tier encoding — `…ch_01:H001:a4`

Intended two-tier MCQ (choose, then reason). Illegal: A/B/C pasted inside `parts[i].text`, outer options empty, `mcq_key` null. Legal two-tier: `structured_parts` with **first-class** `part.options[]` and a letter answer on part (i); part (ii) is reason text only. **G11**.

### Mix-up recipe in the option

`2 m = 0.02 cm, by reversing the 100s` — author talk, not a learner claim.

### Extra objects / second idea

Reddish bowls not in the stem. Kelvin when the stem is °C/°F. Pascal when the stem is force-as-pair.

## Legal multi-tier MCQ

Part (i): `options: [{id:A,text:...},{id:B,...}]`, answer letter.  
Part (ii): reason, no nested A–D list in the text.
