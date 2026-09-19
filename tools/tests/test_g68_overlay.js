#!/usr/bin/env node
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const ROOT = path.resolve(__dirname, "../..");
const packer = require("../pack_g68_candidates.js");

const packed = packer.pack();
if (packed.n < 100) throw new Error("pack too small " + packed.n);
const items = JSON.parse(fs.readFileSync(packer.OUT_PACK, "utf8"));
const nav = JSON.parse(fs.readFileSync(packer.OUT_NAV, "utf8"));
if (items.length !== nav.length) throw new Error("pack/nav length");
if (items.length !== packed.n) throw new Error("count");
items.forEach((it) => {
  if (it.serve_eligible) throw new Error("serve_eligible " + it.uid);
  if (it.pack !== "middle_6_8") throw new Error("pack " + it.uid);
  if (it.subject !== "science") throw new Error("subject " + it.uid);
  if (!String(it.uid).startsWith("candidate:")) throw new Error("uid " + it.uid);
  if (!String(it.node || "").startsWith("S")) throw new Error("node " + it.uid);
});
nav.forEach((r) => {
  if (!r.subtopic_label || /^[A-Z]\d+(\/|$)/.test(r.subtopic_label)) {
    throw new Error("code label " + r.uid + " " + r.subtopic_label);
  }
  if (!String(r.ncert_family || "").startsWith("science/")) throw new Error("ncert_family " + r.uid);
});

const catalog = JSON.parse(fs.readFileSync(path.join(ROOT, "data/subjects.json"), "utf8"));
const sci = catalog.subjects.find((s) => s.id === "science");
if (!sci.candidate_overlay) throw new Error("missing overlay");
if (sci.candidate_overlay.questions.indexOf("data/questions/") === 0) throw new Error("overlay in live pool");
if (sci.packs[0].n !== 109) throw new Error("live n");
if (sci.packs.length !== 1) throw new Error("extra pack");
const junior = JSON.parse(fs.readFileSync(path.join(ROOT, "data/questions/science-junior.json"), "utf8"));
if (junior.length !== 109) throw new Error("junior " + junior.length);
if (fs.existsSync(path.join(ROOT, "data/questions/science-middle_6_8-candidate.json"))) {
  throw new Error("candidate leaked into data/questions");
}

const src = fs.readFileSync(path.join(ROOT, "js/rag.js"), "utf8");
const sandbox = { console };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(src, sandbox);
const rag = sandbox.TTwinRag;
const all = rag.assemble({ pack: "middle_6_8", subject: "science" }, nav, {});
if (all.question_uids.length !== items.length) throw new Error("assemble all " + all.question_uids.length);
const s1 = rag.assemble({ pack: "middle_6_8", subject: "science", nodes: ["S1"] }, nav, {});
if (s1.question_uids.length < 10) throw new Error("S1 empty");
const fam = rag.assemble({
  pack: "middle_6_8",
  subject: "science",
  families: ["science/grade_06/ch_01/H001"],
}, nav, {});
if (!fam.question_uids.length) throw new Error("family empty");
const grokNav = nav.filter((r) => r.author === "grok");
const grokItems = items.filter((it) => it.author === "grok");
if (grokNav.length < 1) throw new Error("no grok nav");
if (grokNav.length !== grokItems.length) throw new Error("grok nav/items");
const force = items.find((it) => it.uid === "candidate:g68:science:grade_08:ch_05:H001:a3");
if (force) {
  const t = (force.tables || []).find((x) => x && x.is_option_table);
  if (!t || !t.rows || t.rows.length < 4) throw new Error("force table rows");
  if (/^Row\s*1$/i.test(String((force.options || {}).A || ""))) throw new Error("force still Row 1");
}
const live = rag.assemble({ pack: "middle_6_8", subject: "science" }, junior.map((it) => ({
  uid: it.uid, subject: it.subject, pack: it.pack, node: it.node, ncert_family: (it.hinges && it.hinges.primary) || "",
})), {});
if (live.question_uids.length !== 109) throw new Error("live assemble " + live.question_uids.length);

console.log("g68_overlay_ok", packed.n, "S1", s1.question_uids.length, "family", fam.question_uids.length);
