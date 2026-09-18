#!/usr/bin/env node
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const ROOT = path.resolve(__dirname, "../..");
const src = fs.readFileSync(path.join(ROOT, "js/kimi.js"), "utf8");
let fetchCalls = 0;
const sandbox = { console, Date, JSON, Array, Object, String, Math, setTimeout, clearTimeout };
sandbox.window = sandbox;
sandbox.localStorage = { getItem() { return ""; }, setItem() {}, removeItem() {} };
sandbox.fetch = function () {
  fetchCalls += 1;
  return Promise.reject(new Error("no network in test"));
};
vm.createContext(sandbox);
vm.runInContext(src, sandbox);
const K = sandbox.TTwinKimi;
if (!K || typeof K.assembleModifyPacket !== "function") {
  throw new Error("assembleModifyPacket missing");
}
if (typeof K.validateModifyResult !== "function") {
  throw new Error("validateModifyResult missing");
}

const item = {
  uid: "demo:q1",
  subject: "chemistry",
  pack: "secondary_9_10",
  node: "chem:C1",
  chapter_id: "cam:0620:1",
  subtopic_id: "IGCSE:0620.1.1",
  item_type: "mcq",
  stem: "Which particle is an atom?",
  options: { A: "H+", B: "He", C: "e-", D: "n0" },
  hinges: { primary: "science/grade_11/chem_ch_101/H016" },
  assessment: {
    mcq_key: "B",
    key_source: "cambridge_extract",
    key_status: "available",
    modify_seeds: ["Change the species but keep the same hinge."],
    examiner_comment: { present: false },
  },
};
const unbound = K.assembleModifyPacket(item, "Change He to Ne.", { subject: "chemistry", map: [], enrichment: [] });
if (unbound.schema !== "modify_packet.v1") throw new Error("schema");
if (unbound.intelligence.join_status !== "UNBOUND") throw new Error("expected UNBOUND without map hit");
if (unbound.intelligence.hinge !== null) throw new Error("UNBOUND hinge must be null");
if (unbound.source.key.letter !== "B") throw new Error("key");
if (unbound.caps.hard_total_chars !== 16000) throw new Error("caps");
if (unbound.assembly.builder !== "assembleModifyPacket") throw new Error("builder");
if (unbound.intelligence.packed_tags.node) throw new Error("packed_tags must not dump node codes");
const map = [{ unit_id: "science/grade_11/chem_ch_101/H016", decision_hinge: "Atom vs ion", node: "C1", mx: [{ type: "term_substitution", cwo: "ion named as atom" }] }];
const bound = K.assembleModifyPacket(item, "Change He to Ne.", { subject: "chemistry", map: map, enrichment: [] });
if (bound.intelligence.join_status !== "BOUND") throw new Error("expected BOUND");
if (bound.intelligence.hinge.title !== "Atom vs ion") throw new Error("hinge title");
const multi = Object.assign({}, item, { assessment: Object.assign({}, item.assessment, { mcq_key: "BC", one_or_more: true }) });
const p2 = K.assembleModifyPacket(multi, "Keep multi-correct.", { map: [], enrichment: [] });
if (p2.source.item_type !== "one_or_more") throw new Error("multi type " + p2.source.item_type);

const science = JSON.parse(fs.readFileSync(path.join(ROOT, "data/maps/science.json"), "utf8"));
if (!science.units || science.units.length < 300) throw new Error("science map missing units");
const junior = JSON.parse(fs.readFileSync(path.join(ROOT, "data/questions/science-junior.json"), "utf8"));
const jrBound = junior.find((it) => it && it.hinges && it.hinges.primary && (it.stem || "").length > 40);
if (!jrBound) throw new Error("no junior source");
const targetSibling = science.units.find((u) => u.chapter === "science/grade_06/ch_02" && u.unit_id !== jrBound.hinges.primary);
const pSci = K.assembleModifyPacket(jrBound, "Retarget to the sibling hinge using the compiled unit row.", {
  map: science,
  enrichment: [],
  subject: "science",
  pack: "middle_6_8",
  target_unit_id: targetSibling.unit_id,
  slim_map_ref: "data/maps/science.json",
});
if (pSci.schema !== "modify_packet.v1") throw new Error("science packet schema");
if (pSci.intelligence.join_status !== "BOUND") throw new Error("junior primary should BOUND on science map");
if (!pSci.intelligence.hinge || pSci.intelligence.hinge.unit_id !== targetSibling.unit_id) {
  throw new Error("BOUND packet must carry the named-gap unit row, got " + (pSci.intelligence.hinge && pSci.intelligence.hinge.unit_id));
}
if (!(pSci.intelligence.mx || []).length) throw new Error("named gap mx missing");
if (!pSci.intelligence.enrichment) throw new Error("NCERT/mechanism enrichment missing on science unit");
if (JSON.stringify(pSci).indexOf("BIOLOGY_MAP.json") >= 0) throw new Error("map dump");
if (JSON.stringify(pSci).length > 16000) throw new Error("over cap " + JSON.stringify(pSci).length);
if (pSci.spec.variation_class !== "V3" && pSci.spec.variation_class !== "V1") {
  throw new Error("compiler must set variation, got " + pSci.spec.variation_class);
}

const igcse = {
  uid: "0620_m18_qp_12:q1",
  subject: "chemistry",
  pack: "secondary_9_10",
  node: "chem:C4",
  chapter_id: "cam:0620:1",
  subtopic_id: "IGCSE:0620.1.2.1",
  item_type: "mcq",
  stem: "Four physical changes are listed. In which changes do the particles move further apart?",
  options: { A: "melting and condensing", B: "melting and evaporating", C: "melting and evaporating", D: "condensing and freezing" },
  hinges: { primary: "IGCSE:0620.1.2.1" },
  assessment: {
    mcq_key: "C",
    key_source: "cambridge_extract",
    key_status: "available",
    modify_seeds: [{ instruction: "Change the listed changes; keep the particle-spacing hinge." }],
    examiner_comment: { present: false },
  },
};
const states = science.units.find((u) => u.unit_id === "science/grade_06/ch_08/H005");
const pUn = K.assembleModifyPacket(igcse, "Retarget to grades 6 Science states of matter.", {
  map: science,
  enrichment: [],
  subject: "science",
  pack: "middle_6_8",
  target_unit_id: states.unit_id,
  slim_map_ref: "data/maps/science.json",
});
if (pUn.intelligence.join_status !== "UNBOUND") throw new Error("IGCSE primary must miss science map");
if (pUn.intelligence.hinge !== null) throw new Error("UNBOUND hinge must be null");
if (!(pUn.intelligence.mx || []).length) throw new Error("UNBOUND still compiles target mx");
if (!pUn.intelligence.enrichment) throw new Error("UNBOUND still compiles target NCERT enrichment");
if (pUn.intelligence.packed_tags.pack !== "middle_6_8") throw new Error("demand pack");
if (pUn.intelligence.packed_tags.subject !== "science") throw new Error("subject");
if (pUn.spec.fidelity_mode === "BLOCKED") throw new Error("C4→S2 sheaf should bridge");
if (pUn.spec.variation_class !== "V4") throw new Error("cross-subject should be V4, got " + pUn.spec.variation_class);
if (fetchCalls !== 0) throw new Error("assembly made a network call");

const blockedUnit = science.units.find((u) => u.node && String(u.node).startsWith("S1"));
const pBlock = K.assembleModifyPacket(igcse, "No bridge.", {
  map: science,
  pack: "middle_6_8",
  subject: "science",
  target_unit_id: blockedUnit.unit_id,
});
if (pBlock.spec.fidelity_mode !== "BLOCKED") throw new Error("C4→S1 must BLOCKED, got " + pBlock.spec.fidelity_mode);

const fatItem = Object.assign({}, item, {
  stem: "Which particle is an atom? ".repeat(150),
  tikz: "\\begin{tikzpicture}" + "\\fill (0,0) rectangle (1,1);".repeat(250) + "\\end{tikzpicture}",
  options: { A: "option A ".repeat(90), B: "option B ".repeat(90), C: "option C ".repeat(90), D: "option D ".repeat(90) },
});
const fat = K.assembleModifyPacket(fatItem, "Change the species. ".repeat(40), {
  map: [{
    unit_id: item.hinges.primary,
    decision_hinge: "Atom vs ion",
    node: "C1",
    mx: [
      { type: "term_substitution", cwo: "ion named as atom ".repeat(40) },
      { type: "scope_error", cwo: "too wide ".repeat(40) },
      { type: "condition_omission", cwo: "dropped ".repeat(40) },
      { type: "surface_feature_capture", cwo: "shiny ".repeat(40) },
    ],
    mechanism: { law: "L".repeat(2000), causal_direction: "C".repeat(2000) },
    pedagogy: { mastery_signal: "M".repeat(2000), lok_folk: "K".repeat(2000) },
  }],
  enrichment: [{ serves: [item.hinges.primary], statement: "E".repeat(3000) }],
});
if (JSON.stringify(fat).length > 16000) throw new Error("trim failed " + JSON.stringify(fat).length);
if (!fat.assembly.trimmed.length) throw new Error("trim order not recorded");

console.log(
  "modify_packet_ok",
  unbound.intelligence.join_status,
  bound.intelligence.join_status,
  p2.source.item_type,
  pSci.intelligence.join_status,
  pUn.intelligence.join_status,
  pUn.spec.variation_class,
  fat.assembly.trimmed.join(",")
);
