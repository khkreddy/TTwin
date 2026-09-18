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

const c = g68.census(science, junior);
if (c.science_units !== 391) throw new Error("units " + c.science_units);
if (c.junior_live !== 109) throw new Error("junior " + c.junior_live);

console.log("modify_g68_ok", packet.intelligence.join_status, p2.intelligence.join_status, p2.spec.variation_class, c.uncovered);
