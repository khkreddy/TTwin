#!/usr/bin/env node
"use strict";
/* Quality-grader invariants: rubric law (gold FP=0), defect detection, and pack wiring. */
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..", "..");
const G = require(path.join(ROOT, "tools", "grade_g68_quality.js"));
const P = require(path.join(ROOT, "tools", "pack_g68_candidates.js"));

function assert(cond, msg) { if (!cond) { console.error("FAIL: " + msg); process.exit(1); } }
function mkItem(over) {
  return Object.assign({
    uid: "candidate:g68:math:grade_06:ch_01:H001:a3", subject: "maths", chapter_label: "Patterns",
    stem: "Padma lists 3, 6, 9, 12. Which is the next term?", item_type: "mcq",
    options: { A: "13", B: "15 is what creates the multiples of 3.", C: "15", D: "18" },
    statements: [], parts: [], equations: [], tables: [], tikz: null,
    hinges: { primary: "math/grade_06/ch_01/H001" },
    assessment: { mcq_key: "C", one_or_more: false },
  }, over || {});
}

// 1. Gold-corpus false-positive law for the two learner-text regexes.
const banks = ["chemistry-igcse", "physics-igcse", "biology-igcse", "maths-bank", "science-junior"];
let goldN = 0, goldG14 = 0, goldWl = 0;
banks.forEach((b) => {
  const p = path.join(ROOT, "data", "questions", b + ".json");
  if (!fs.existsSync(p)) return;
  JSON.parse(fs.readFileSync(p, "utf8")).forEach((it) => {
    if (!it) return; goldN++;
    const opts = it.options || {};
    const blob = Object.keys(opts).map((k) => String((opts[k] && opts[k].text) || opts[k])).join("\n") + "\n" + String(it.stem || "");
    if (G.G14_RE.test(blob)) goldG14++;
    if (G.WHITELIST_RE.test(blob)) goldWl++;
  });
});
assert(goldN > 50000, "gold corpus loaded (" + goldN + ")");
assert(goldG14 === 0, "G14 gold FP must be 0, got " + goldG14);
assert(goldWl === 0, "whitelist gold FP must be 0, got " + goldWl);

// 2. G14 reverse-causation on a wrong option -> low.
let g = G.gradeItem({ item: mkItem() }, null, null);
assert(g.tier === "low" && g.flags.indexOf("g14_reverse_causation") >= 0, "G14 -> low");

// 3. Key on a letter not among options -> low (key_invalid).
g = G.gradeItem({ item: mkItem({ options: { A: "13", B: "x", C: "15", D: "18" }, assessment: { mcq_key: "E" } }) }, null, null);
assert(g.tier === "low" && g.flags.indexOf("key_invalid") >= 0, "key letter not present -> low");

// 4. Plan/key mismatch (R0 donor-C leftover) -> low; matching null-set must NOT fire.
g = G.gradeItem({ build_logic: { option_plan: { C: null } }, item: mkItem({ assessment: { mcq_key: "C" } }) }, null, null);
assert(g.flags.indexOf("plan_key_mismatch") < 0, "plan null C == key C must not flag mismatch");
g = G.gradeItem({ build_logic: { option_plan: { C: null } }, item: mkItem({ assessment: { mcq_key: "A" } }) }, null, null);
assert(g.tier === "low" && g.flags.indexOf("plan_key_mismatch") >= 0, "plan null C != key A -> low");

// 5. mx bound to the key letter -> low (mx_on_key).
g = G.gradeItem({ mx_option_map: { C: "scope_error" }, item: mkItem({ assessment: { mcq_key: "C" } }) }, null, null);
assert(g.tier === "low" && g.flags.indexOf("mx_on_key") >= 0, "mx on key -> low");

// 6. Clean MCQ -> top.
g = G.gradeItem({ item: mkItem({ options: { A: "13", B: "14", C: "15", D: "18" } }), mx_option_map: { A: "condition_omission" } }, null, null);
assert(g.tier === "top", "clean mcq -> top, got " + g.tier + " " + JSON.stringify(g.flags));

// 7. Systemic harness gaps are notes, not tier-movers: structured part_answers stays medium->top-safe.
const structured = mkItem({ item_type: "structured", options: {}, parts: [{ id: "i", text: "Pick.", options: [{ id: "A", text: "a" }, { id: "B", text: "b" }] }], assessment: { mcq_key: null } });
g = G.gradeItem({ item: structured }, null, { answer: { kind: "part_answers", part_answers: [{ part_id: "i", answer: "A" }] } });
assert(g.tier === "top" && g.flags.indexOf("key_not_packed") >= 0, "structured key_not_packed is a note, not a defect");

// 8. chapter_label code is a note (map data gap), does not lower tier.
g = G.gradeItem({ item: mkItem({ chapter_label: "math/grade_06/ch_01", options: { A: "13", B: "14", C: "15", D: "18" } }) }, null, null);
assert(g.tier === "top" && g.flags.indexOf("chapter_label_code") >= 0, "chapter_label_code is a note");

// 9. Packer wires quality onto item + nav.
const flat = P.flatten({ item: mkItem(), build_logic: { hinge: "math/grade_06/ch_01/H001" } }, null);
assert(flat && flat.uid, "flatten produces an item");

console.log("quality_ok", "gold_n=" + goldN, "gold_g14=" + goldG14, "gold_wl=" + goldWl);
