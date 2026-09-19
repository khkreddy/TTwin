# Science 6–8 Modify examples (Grok ingest)

Library for agents. **Categories are not good or bad.** A format (MCQ, two-tier, table, open response) can be brilliant if executed well. Bad examples are **badly executed items**, not whole families.

Grok-authored CANDIDATEs only. Do not copy Kimi a1/a2 as templates for Mx maps; do copy their **option parallelism**.

## Good execution

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

### Two-tier MCQ (choose, then reason)

A first-class format. Execute it as `structured_parts`:

- Part (i): short prompt + **first-class** `options[]` and a letter answer.
- Part (ii): reason text only.

The recoded `…ch_01:H001:a4` (part.options on (i), reason on (ii)) is this format done properly. Aim for that, not for dumping A/B/C into a paragraph.

## Badly executed items (not categories)

These failed because of how they were written, not because of the item type.

### Stem list incomplete — old `…ch_01:H001:a3`

Stem numbered activities 1–4; options only named 1–3. Activity 4 was a dead alternative. **G10** catches that execution. Listing activities is fine if every number is an option.

### Two-tier pasted as prose — old `…ch_01:H001:a4`

Same category as the good two-tier above. Execution: A/B/C typed into `parts[i].text`, outer options empty, `mcq_key` null. The paper could not show a real choice. **G11** rejects that paste, not two-tier MCQ.

### Mix-up recipe in the option

`2 m = 0.02 cm, by reversing the 100s` — author talk, not a learner claim.

### Extra objects / second idea

Reddish bowls not in the stem. Kelvin when the stem is °C/°F. Pascal when the stem is force-as-pair.
