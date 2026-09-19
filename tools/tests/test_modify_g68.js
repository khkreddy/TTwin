#!/usr/bin/env node
"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "../..");
const g68 = require("../modify_g68.js");

const K = g68.loadKimi();
const science = JSON.parse(fs.readFileSync(path.join(ROOT, "data/maps/science.json"), "utf8"));
const junior = JSON.parse(fs.readFileSync(path.join(ROOT, "data/questions/science-junior.json"), "utf8"));
const unit = science.units.find((u) => u.unit_id === "science/grade_06/ch_08/H005");
if (!unit) throw new Error("missing named unit");
const source = junior.find((it) => it.uid === "physics_8a_rjb_exe14") || junior.find((it) => (it.stem || "").length > 40 && it.hinges && it.hinges.primary);
if (!source) throw new Error("missing packed source");

const packet = g68.compileUnit(K, unit, source, science, {});
if (packet.schema !== "modify_packet.v1") throw new Error("schema");
if (packet.slot !== "T-MOD") throw new Error("slot");
if (JSON.stringify(packet).length > 16000) throw new Error("cap");
if (!g68.packetHasPedagogy(packet)) throw new Error("pedagogy");
if ((packet.intelligence.mx || []).length < 1) throw new Error("mx from named gap");
if (!packet.intelligence.enrichment) throw new Error("NCERT enrichment");
if (packet.intelligence.packed_tags.pack !== "middle_6_8") throw new Error("pack");
if (packet.intelligence.packed_tags.subject !== "science") throw new Error("subject");
if (packet.spec.variation_class !== "V1" && packet.spec.variation_class !== "V3" && packet.spec.variation_class !== "V4") {
  throw new Error("variation " + packet.spec.variation_class);
}
if (String(JSON.stringify(packet)).indexOf("CHEMISTRY_MAP_COMBINED") >= 0) throw new Error("map dump");

const igcse = {
  uid: "0620_m18_qp_12:q1",
  subject: "chemistry",
  pack: "secondary_9_10",
  node: "chem:C4",
  chapter_id: "cam:0620:1",
  subtopic_id: "IGCSE:0620.1.2.1",
  item_type: "mcq",
  stem: "Four physical changes are listed. In which changes do the particles move further apart?",
  options: { A: "melting and condensing", B: "freezing and condensing", C: "melting and evaporating", D: "condensing and freezing" },
  hinges: { primary: "IGCSE:0620.1.2.1" },
  assessment: {
    mcq_key: "C",
    modify_seeds: [{ instruction: "Change the listed changes; keep the particle-spacing decision." }],
    examiner_comment: { present: false },
  },
};
const p2 = g68.compileUnit(K, unit, igcse, science, {});
if (p2.intelligence.join_status !== "UNBOUND") throw new Error("IGCSE must be UNBOUND");
if (p2.intelligence.hinge !== null) throw new Error("UNBOUND hinge null");
if (!(p2.intelligence.mx || []).length) throw new Error("target mx");
if (p2.spec.fidelity_mode === "BLOCKED") throw new Error("C4 to S2 should bridge");
if (p2.spec.variation_class !== "V4") throw new Error("expected V4");
if (p2.spec.figure.mode !== "preserve") throw new Error("H005 no-figure hinge stays preserve");

const eco = science.units.find((u) => u.unit_id === "science/grade_08/ch_12/H008");
const pEco = g68.compileUnit(K, eco, igcse, science, {});
if (pEco.spec.figure.mode !== "add") throw new Error("feeding-diagram hinge with no source tikz must add");
if (!pEco.spec.figure.tikz_required) throw new Error("add requires tikz");

const circuit = science.units.find((u) => u.unit_id === "science/grade_07/ch_03/H007");
const circuitSrc = Object.assign({}, igcse, {
  uid: "0625_m18_qp_12:q1",
  subject: "physics",
  pack: "secondary_9_10",
  node: "phy:P2",
  stem: "Which circuit shows a lamp in series with a cell and a switch?",
  tikz: "\\begin{tikzpicture}\\draw (0,0) -- (1,0);\\end{tikzpicture}",
  hinges: { primary: "IGCSE:0625.4.2.1" },
});
const pCir = g68.compileUnit(K, circuit, circuitSrc, science, {});
if (pCir.spec.figure.mode !== "rewrite") throw new Error("circuit-diagram hinge with source tikz must rewrite");

const c = g68.census(science, junior);
if (c.science_units !== 391) throw new Error("units " + c.science_units);
if (c.junior_live !== 109) throw new Error("junior " + c.junior_live);
if (c.uncovered < 0) throw new Error("uncovered negative " + c.uncovered);
const sumUnc = Object.keys(c.by_node).reduce((n, k) => n + c.by_node[k].uncovered, 0);
if (c.uncovered !== sumUnc) throw new Error("uncovered mismatch");
if (g68.variationForAttempt(2) !== "V1") throw new Error("a2 V1");
if (g68.variationForAttempt(3) !== "V6") throw new Error("a3 V6");
if (g68.variationForAttempt(4) !== "V5") throw new Error("a4 V5");
if (c.uncovered === 0) {
  const deep = g68.deepenUnits(science);
  if (deep.length) {
    const withCand = deep.find((u) => g68.maxAttempt(u.unit_id) >= 1);
    if (!withCand) throw new Error("deepen missing candidate units");
    if (g68.nextAttempt(withCand.unit_id) < 2) throw new Error("next attempt after first fill");
    const failedFirst = deep.find((u) => g68.attemptFailed(u.unit_id, g68.nextAttempt(u.unit_id)));
    const fresh = deep.find((u) => g68.maxAttempt(u.unit_id) === 1 && !g68.attemptFailed(u.unit_id, 2));
    if (failedFirst && fresh && deep.indexOf(failedFirst) < deep.indexOf(fresh)) {
      throw new Error("fail-closed a2 must sort after fresh a2 gaps");
    }
  }
}

const circ = g68.sanitizeTikz("\\begin{circuitikz}\\draw (0,0) to[battery1] (1,0);\\end{circuitikz}");
if (!circ.ok || circ.tikz.indexOf("tikzpicture") < 0) throw new Error("sanitize circuitikz");
if (circ.packages.indexOf("circuitikz") < 0) throw new Error("circuitikz package");
if (g68.liveItemType("one_or_more") !== "mcq") throw new Error("one_or_more maps to mcq");
if (g68.liveItemType("assertion_reason") !== "structured") throw new Error("assertion_reason maps to structured");
const fakeMcq = {
  item_type: "single_mcq",
  stem: "Which change moves particles further apart?",
  options: [{ id: "A", text: "melting only" }, { id: "B", text: "freezing" }, { id: "C", text: "melting and evaporating" }, { id: "D", text: "condensing" }],
  answer: { kind: "single_letter", letter: "C" },
  mx_option_map: { A: "condition_omission", B: "scope_error", D: "UNRESOLVED" },
  teacher: { proposed_key_status: "UNVERIFIED", variation_applied: p2.spec.variation_class, fidelity_selfcheck: "FAITHFUL_TRANSFER" },
};
const g9ok = g68.gateG9(fakeMcq, p2);
if (!g9ok.ok) throw new Error("G9 should pass two distinct mx");
const g9fail = g68.gateG9(Object.assign({}, fakeMcq, { mx_option_map: { A: "UNRESOLVED", B: "UNRESOLVED", D: "UNRESOLVED" } }), p2);
if (g9fail.ok || g9fail.gate !== "G9") throw new Error("G9 fail closed");
const cand = g68.resultToCandidate(Object.assign({ status: "OK", schema: "modify_result.v1" }, fakeMcq, {
  item_type: "one_or_more",
  answer: { kind: "letter_set", letters: ["B", "C"] },
}), p2, igcse, unit, 9);
if (cand.item.item_type !== "mcq") throw new Error("live type");
if (!cand.item.assessment.one_or_more) throw new Error("one_or_more flag");
if (cand.item.assessment.mcq_key !== "BC") throw new Error("mcq_key BC");
if (cand.item.assessment.proposed_key_status !== "UNVERIFIED") throw new Error("stay UNVERIFIED");
if (!cand.build_logic) throw new Error("build_logic");
if (JSON.stringify(cand.item).indexOf("build_logic") >= 0) throw new Error("build_logic leaked into learner item");

const g10 = g68.gateG10({
  stem: "Which activity?\n1 Recited names.\n2 Watched dust.\n3 Copied steps.\n4 Looked up a fact.\nWhich activity best counts as doing science?",
  options: [
    { id: "A", text: "Activity 2, because he observed." },
    { id: "B", text: "Activity 3, because copying is enough." },
    { id: "C", text: "Activity 1, because you must know the answer first." },
    { id: "D", text: "Activity 2 cannot count." },
  ],
});
if (g10.ok || g10.gate !== "G10") throw new Error("listed Activity 4 omitted must fail G10");
const g11 = g68.gateG11({
  item_type: "structured_parts",
  parts: [{ id: "i", text: "Which action?\nA. Measure\nB. Guess\nC. Ignore", marks: 1 }],
});
if (g11.ok || g11.gate !== "G11") throw new Error("nested A/B/C in part text must fail G11");
const forceRes = JSON.parse(fs.readFileSync(path.join(ROOT, "candidate/science-middle_6_8/results/science_grade_08_ch_05_H001__a3.json"), "utf8"));
const forcePkt = JSON.parse(fs.readFileSync(path.join(ROOT, "candidate/science-middle_6_8/packets/science_grade_08_ch_05_H001__a3.json"), "utf8"));
const forcePktFresh = JSON.parse(JSON.stringify(forcePkt));
forcePktFresh.build_logic = forcePktFresh.build_logic || {};
forcePktFresh.build_logic.option_plan = { mx_allowlist: ["term_substitution", "condition_omission"], bind: "wrong_letters_after_result" };
const forceGates = g68.ingestGates(forceRes, forcePktFresh);
if (!forceGates.ok) throw new Error("force example must pass ingestGates " + forceGates.gate);
const forceOld = g68.gateG13(forceRes, forcePkt);
if (forceOld.ok) throw new Error("stored source-key plan B=null vs result key A must fail G13");

if (packet.build_logic.option_plan && packet.build_logic.option_plan.C === null) {
  throw new Error("compile must not null source.key letter C");
}
if (!packet.build_logic.option_plan || packet.build_logic.option_plan.bind !== "wrong_letters_after_result") {
  throw new Error("compile option_plan must defer letter bind");
}
if (JSON.stringify(packet.build_logic.option_plan).indexOf("source.key") >= 0) throw new Error("source.key leaked into plan");

const h002a3orig = {
  item_type: "single_mcq",
  stem: "Anya studies the whole-number list 1, 3, 5, 7, 9, …\n\nWhich claim correctly continues the list using its generative rule?",
  options: [
    { id: "A", text: "The next term is 10, because the list of whole numbers always grows by 1." },
    { id: "B", text: "Writing the next odd number is what creates the odd numbers in the first place." },
    { id: "C", text: "The next term is 11, because each term is 2 more than the one before." },
    { id: "D", text: "The next term needs a closed formula for triangular numbers before it can be named." },
  ],
  answer: { kind: "single_letter", letter: "C" },
  mx_option_map: { A: "condition_omission", B: "relationship_reversal", D: "scope_error" },
};
const h002pkt = {
  intelligence: { hinge: { unit_id: "math/grade_06/ch_01/H002", title: "Decide which generative rule defines a whole-number sequence and use that rule to continue the sequence." }, mx: [{ mx_type: "condition_omission" }, { mx_type: "relationship_reversal" }, { mx_type: "scope_error" }] },
  build_logic: { hinge: "math/grade_06/ch_01/H002", option_plan: { A: "condition_omission", B: "relationship_reversal", D: "scope_error", C: null } },
};
const h002gates = g68.ingestGates(h002a3orig, h002pkt);
if (h002gates.ok) throw new Error("original H002 a3 reverse-causation/jargon must fail closed");
if (["G13", "G14", "G15", "G16"].indexOf(h002gates.gate) < 0) throw new Error("H002 a3 must fail a new gate, got " + h002gates.gate);

const rewritten = {
  item_type: "single_mcq",
  stem: "Anya studies the whole-number list 1, 3, 5, 7, 9, …\n\nWhich claim correctly continues the list?",
  options: [
    { id: "A", text: "The next term is 10, because whole numbers always grow by 1." },
    { id: "B", text: "The next term is 13, because each term is 4 more than the one before." },
    { id: "C", text: "The next term is 11, because each term is 2 more than the one before." },
    { id: "D", text: "The next term is 25, because 1+3+5+7+9 = 25." },
  ],
  answer: { kind: "single_letter", letter: "C" },
  mx_option_map: { A: "condition_omission", B: "relationship_reversal", D: "scope_error" },
};
const rwPkt = {
  intelligence: { hinge: { unit_id: "math/grade_06/ch_01/H002", title: "Decide which generative rule defines a whole-number sequence." }, mx: [{ mx_type: "condition_omission" }, { mx_type: "relationship_reversal" }, { mx_type: "scope_error" }] },
  build_logic: { hinge: "math/grade_06/ch_01/H002", option_plan: { mx_allowlist: ["condition_omission", "relationship_reversal", "scope_error"], bind: "wrong_letters_after_result" } },
};
const rwGates = g68.ingestGates(rewritten, rwPkt);
if (!rwGates.ok) throw new Error("rewritten H002 a3 must pass " + rwGates.gate);
const stamped = g68.stampOptionPlan(rewritten, rwPkt);
if (stamped.C !== null) throw new Error("stamp must null the result key");
if (stamped.A !== "condition_omission" || stamped.bind !== "result") throw new Error("stamp must bind wrong letters from the result");

const g13src = g68.gateG13(rewritten, {
  build_logic: { option_plan: { A: "condition_omission", B: "relationship_reversal", D: "scope_error", C: null } },
});
if (!g13src.ok) throw new Error("result key C matching old source-null C must still pass G13");
const g13mismatch = g68.gateG13(Object.assign({}, rewritten, { answer: { kind: "single_letter", letter: "A" } }), {
  build_logic: { option_plan: { A: "condition_omission", B: "relationship_reversal", D: "scope_error", C: null } },
});
if (g13mismatch.ok || g13mismatch.gate !== "G13") throw new Error("plan-null C vs result key A must fail G13");

const g14hit = g68.gateG14({
  options: [
    { id: "A", text: "The next term is 11." },
    { id: "B", text: "Writing 11 is what creates the odd numbers." },
  ],
  answer: { kind: "single_letter", letter: "A" },
});
if (g14hit.ok || g14hit.gate !== "G14") throw new Error("is what creates on a distractor must fail G14");
const g14ok = g68.gateG14({
  options: [
    { id: "A", text: "Activity 4, because writing a looked-up fact in a notebook is not doing science." },
    { id: "B", text: "Activity 2, because he observed." },
  ],
  answer: { kind: "single_letter", letter: "B" },
});
if (!g14ok.ok) throw new Error("bare writing must pass G14");

const g15fail = g68.gateG15({
  stem: "Karan writes the whole-number list 4, 7, 10, 13, …\nWhich claim continues the list?",
  options: [
    { id: "A", text: "Each term is 3 more than the one before, so the next term is 16." },
    { id: "B", text: "Naming the next term is what creates the whole-number list in the first place." },
  ],
  answer: { kind: "single_letter", letter: "A" },
});
if (g15fail.ok || g15fail.gate !== "G15") throw new Error("numeric-list stem with no digit in a distractor must fail G15");
const treasure = {
  stem: "Bharat places a treasure on the number 24 on a number strip. He may jump by a fixed whole-number size from 0 and wants every jump to land exactly on 24.",
  options: [
    { id: "A", text: "The answer is 24, because that is the treasure number itself." },
    { id: "B", text: "Jump size 5 works, because repeated jumps of 5 stay on whole numbers." },
    { id: "C", text: "Jump sizes 1, 2, 3, 4, 6, 8, 12 and 24 all land exactly on 24." },
    { id: "D", text: "Jump size 24 is forced, because 24 is the largest printed mark." },
  ],
};
if (!g68.gateG15(treasure).ok) throw new Error("treasure-on-24 must pass G15 (no continue-the-list ask)");
const electron = {
  stem: "The electronic structures of atoms P and Q are shown. Atom P has electron arrangement 2,8,2. Which formula is correct?",
  options: [
    { id: "A", text: "PQ" },
    { id: "B", text: "P2Q" },
    { id: "C", text: "P2Q3" },
    { id: "D", text: "PQ2" },
  ],
};
if (!g68.gateG15(electron).ok) throw new Error("Cambridge electron-config stem must not fail G15");
const g14re = g68.gateG14({
  options: [{ id: "A", text: "Hydrogen produces water when it burns." }, { id: "B", text: "Oxygen is collected." }],
  answer: { kind: "single_letter", letter: "A" },
});
if (!g14re.ok) throw new Error("bare produces must pass G14; regex must be is what (creates|produces)");

const g16fail = g68.gateG16({
  stem: "Continue 1, 3, 5.",
  options: [{ id: "A", text: "Needs a closed formula for triangular numbers." }, { id: "B", text: "Next is 7." }],
  answer: { kind: "single_letter", letter: "B" },
}, { intelligence: { hinge: { unit_id: "math/grade_06/ch_01/H002", title: "Decide which generative rule defines a sequence." } } });
if (g16fail.ok || g16fail.gate !== "G16") throw new Error("grade 6 closed formula / triangular must fail G16");

const remElig = g68.remainingEligibleUnits(science);
const nCh = new Set(remElig.map((u) => g68.chapterKey(u))).size;
const uniform = g68.nextUniformUnits(science, Math.max(nCh * 2, 1));
if (nCh && uniform.length < nCh) throw new Error("uniform remaining too small");
const chans = uniform.slice(0, nCh).map((u) => g68.chapterKey(u));
if (nCh && new Set(chans).size !== nCh) throw new Error("uniform not round-robin by chapter");

console.log("modify_g68_ok", packet.intelligence.join_status, p2.intelligence.join_status, p2.spec.variation_class, c.uncovered);
