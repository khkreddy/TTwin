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
if (!K || typeof K.assembleModifyPacket !== "function") {
  throw new Error("assembleModifyPacket missing");
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
const map = [{ unit_id: "science/grade_11/chem_ch_101/H016", decision_hinge: "Atom vs ion", node: "C1", mx: [{ type: "term_substitution", cwo: "ion named as atom" }] }];
const bound = K.assembleModifyPacket(item, "Change He to Ne.", { subject: "chemistry", map: map, enrichment: [] });
if (bound.intelligence.join_status !== "BOUND") throw new Error("expected BOUND");
if (bound.intelligence.hinge.title !== "Atom vs ion") throw new Error("hinge title");
const multi = Object.assign({}, item, { assessment: Object.assign({}, item.assessment, { mcq_key: "BC", one_or_more: true }) });
const p2 = K.assembleModifyPacket(multi, "Keep multi-correct.", { map: [], enrichment: [] });
if (p2.source.item_type !== "one_or_more") throw new Error("multi type " + p2.source.item_type);
console.log("modify_packet_ok", unbound.assembly.join_status, bound.assembly.join_status, p2.source.item_type);
