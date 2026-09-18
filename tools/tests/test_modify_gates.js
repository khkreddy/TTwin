#!/usr/bin/env node
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const ROOT = path.resolve(__dirname, "../..");
const src = fs.readFileSync(path.join(ROOT, "js/kimi.js"), "utf8");
const sandbox = { console, Date, JSON, Array, Object, String, Math, setTimeout, clearTimeout };
sandbox.window = sandbox;
sandbox.localStorage = { getItem() { return ""; }, setItem() {}, removeItem() {} };
sandbox.fetch = function () { return Promise.reject(new Error("no network in test")); };
vm.createContext(sandbox);
vm.runInContext(src, sandbox);
const K = sandbox.TTwinKimi;

const item = {
  uid: "demo:q1",
  subject: "chemistry",
  pack: "secondary_9_10",
  node: "chem:C4",
  item_type: "mcq",
  stem: "Which change moves particles further apart?",
  options: { A: "freezing", B: "condensing", C: "evaporating", D: "depositing" },
  hinges: { primary: "IGCSE:0620.1.2.1" },
  assessment: { mcq_key: "C", modify_seeds: ["Change the listed changes."], examiner_comment: { present: false } },
};
const science = JSON.parse(fs.readFileSync(path.join(ROOT, "data/maps/science.json"), "utf8"));
const unit = science.units.find((u) => u.unit_id === "science/grade_06/ch_08/H005");
const packet = K.assembleModifyPacket(item, "Retarget to grades 6 Science.", {
  map: science,
  pack: "middle_6_8",
  subject: "science",
  target_unit_id: unit.unit_id,
  variation_class: "V4",
});

function teacher(extra) {
  return Object.assign({
    proposed_key_status: "UNVERIFIED",
    key_rationale: "Evaporation moves particles further apart.",
    variation_applied: "V4",
    fidelity_selfcheck: "FAITHFUL_TRANSFER",
    mx_links: [],
    figure_note: null,
  }, extra || {});
}

const okMcq = {
  schema: "modify_result.v1",
  status: "OK",
  item_type: "single_mcq",
  stem: "Priya leaves a wet school bag in the sun. Which change lets water particles move further apart?",
  options: [
    { id: "A", text: "freezing" },
    { id: "B", text: "condensing" },
    { id: "C", text: "evaporating" },
    { id: "D", text: "depositing" },
  ],
  answer: { kind: "single_letter", letter: "C" },
  teacher: teacher(),
};
const gOk = K.validateModifyResult(okMcq, packet, item);
if (!gOk.ok) throw new Error("OK single_mcq should pass, got " + gOk.gate);

const multiPacket = K.assembleModifyPacket(
  Object.assign({}, item, { assessment: Object.assign({}, item.assessment, { mcq_key: "BC", one_or_more: true }) }),
  "Keep multi-correct.",
  { map: [], variation_class: "V1" }
);
const collapsed = {
  schema: "modify_result.v1",
  status: "OK",
  item_type: "single_mcq",
  stem: "Which are correct?",
  options: [{ id: "A", text: "w" }, { id: "B", text: "x" }, { id: "C", text: "y" }, { id: "D", text: "z" }],
  answer: { kind: "single_letter", letter: "B" },
  teacher: teacher({ variation_applied: "V1" }),
};
const gCollapse = K.validateModifyResult(collapsed, multiPacket, item);
if (gCollapse.ok || gCollapse.gate !== "G2") throw new Error("collapsed one_or_more must fail G2, got " + JSON.stringify(gCollapse));

const honestMulti = {
  schema: "modify_result.v1",
  status: "OK",
  item_type: "one_or_more",
  stem: "Which two changes move particles further apart?",
  options: [
    { id: "A", text: "freezing" },
    { id: "B", text: "melting" },
    { id: "C", text: "evaporating" },
    { id: "D", text: "condensing" },
  ],
  answer: { kind: "letter_set", letters: ["B", "C"] },
  teacher: teacher({ variation_applied: "V1" }),
};
const gMulti = K.validateModifyResult(honestMulti, multiPacket, item);
if (!gMulti.ok) throw new Error("letter_set BC should pass, got " + gMulti.gate);

const openPacket = K.assembleModifyPacket(item, "make this open response", {
  map: science,
  target_item_type: "open_response",
  pack: "middle_6_8",
  subject: "science",
  target_unit_id: unit.unit_id,
  variation_class: "V1",
});
const openOk = {
  schema: "modify_result.v1",
  status: "OK",
  item_type: "open_response",
  stem: "Arun wets a slate and leaves it in the sun. Explain what happens to the water.",
  answer: { kind: "rubric", rubric: ["Names evaporation.", "Particles move further apart."] },
  teacher: teacher({ variation_applied: "V1" }),
};
const gOpen = K.validateModifyResult(openOk, openPacket, item);
if (!gOpen.ok) throw new Error("open_response should pass, got " + gOpen.gate);
const openLetter = Object.assign({}, openOk, { answer: { kind: "single_letter", letter: "A" } });
const gOpenFail = K.validateModifyResult(openLetter, openPacket, item);
if (gOpenFail.ok || gOpenFail.gate !== "G2") throw new Error("open_response with letter must fail G2");

const titled = Object.assign({}, okMcq, {
  teacher: teacher({ key_rationale: "Uses map title " + packet.intelligence.packed_tags.topic + " and science/grade_06/ch_08/H005." }),
});
const g8 = K.validateModifyResult(titled, packet, item);
if (g8.ok || g8.gate !== "G8") throw new Error("UNBOUND teacher map/hinge codes must fail G8, got " + JSON.stringify(g8));

const mxType = (packet.intelligence.mx[0] && packet.intelligence.mx[0].mx_type) || "condition_omission";
const mxHit = Object.assign({}, okMcq, {
  stem: "Priya avoids the " + mxType + " of forgetting sunlight.",
});
const g4 = K.validateModifyResult(mxHit, packet, item);
if (g4.ok || g4.gate !== "G4") throw new Error("mx_type in stem must fail G4, got " + JSON.stringify(g4));

const emptyOut = K.applyModifyOutcome(null, packet, item);
if (!emptyOut.keepOriginal || emptyOut.gate !== "G1") throw new Error("empty keeps source");
const refused = K.applyModifyOutcome({ status: "REFUSED", refusal_reason: "cannot honour inverse-flip", teacher: teacher() }, packet, item);
if (!refused.keepOriginal || refused.gate !== "REFUSED") throw new Error("REFUSED keeps source, got " + JSON.stringify(refused));

const freeze = Object.assign({}, okMcq, { uid: "9701_m16_qp_12:q1" });
const dumped = JSON.parse(JSON.stringify(freeze));
dumped.teacher = teacher({ key_rationale: "exam.v1 freeze" });
const g5 = K.validateModifyResult(dumped, packet, item);
if (g5.ok || g5.gate !== "G5") throw new Error("exam.v1 must fail G5, got " + JSON.stringify(g5));

const drift = Object.assign({}, okMcq, { teacher: teacher({ variation_applied: "V1" }) });
const g7 = K.validateModifyResult(drift, packet, item);
if (g7.ok || g7.gate !== "G7") throw new Error("variation drift must fail G7");

const missingLetter = Object.assign({}, okMcq, { answer: { kind: "single_letter", letter: "E" } });
const g6 = K.validateModifyResult(missingLetter, packet, item);
if (g6.ok || (g6.gate !== "G6" && g6.gate !== "G2")) throw new Error("missing letter must fail G6/G2, got " + JSON.stringify(g6));

console.log("modify_gates_ok", gOk.ok, gCollapse.gate, gMulti.ok, gOpen.ok, g8.gate, g4.gate, emptyOut.gate, refused.gate, g5.gate, g7.gate, g6.gate);
