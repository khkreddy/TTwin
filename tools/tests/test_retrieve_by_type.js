#!/usr/bin/env node
"use strict";
/* Drive the shipped TTwinRag.assemble / itemMatches path, not a copy. */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../..");
const ragSrc = fs.readFileSync(path.join(ROOT, "js/rag.js"), "utf8");
if (/\bmodule\.exports\b|\brequire\s*\(/.test(ragSrc)) {
  throw new Error("rag.js must load in a window global with no Node module/require");
}

const sandbox = { console };
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(ragSrc, sandbox);
const TTwinRag = sandbox.TTwinRag;
if (!TTwinRag || typeof TTwinRag.assemble !== "function") {
  throw new Error("TTwinRag.assemble missing after loading js/rag.js");
}

const mixed = [
  { uid: "a-mcq", subject: "chemistry", pack: "igcse_9_10", node: "chem:C1", chapter_id: "cam:0620:1", subtopic_id: "cam:0620:1", item_type: "mcq", status: "tagged" },
  { uid: "b-struct", subject: "chemistry", pack: "igcse_9_10", node: "chem:C1", chapter_id: "cam:0620:1", subtopic_id: "cam:0620:1", item_type: "structured", status: "tagged" },
  { uid: "c-open", subject: "chemistry", pack: "igcse_9_10", node: "chem:C1", chapter_id: "cam:0620:1", subtopic_id: "cam:0620:1", item_type: "open_response", status: "tagged" },
  { uid: "d-mcq-phy", subject: "physics", pack: "igcse_9_10", node: "phy:P1", chapter_id: "cam:0625:1", subtopic_id: "cam:0625:1", item_type: "mcq", status: "tagged" },
];
const table = { subject: "chemistry", ncert: [], cambridge: [], aliases: {} };
const packed = {
  "a-mcq": { uid: "a-mcq", item_type: "mcq" },
  "b-struct": { uid: "b-struct", item_type: "structured" },
  "c-open": { uid: "c-open", item_type: "open_response" },
  "d-mcq-phy": { uid: "d-mcq-phy", item_type: "mcq" },
};

function assertType(selType) {
  const r = TTwinRag.assemble(
    { subject: "chemistry", pack: "igcse_9_10", item_type: selType },
    mixed,
    table
  );
  if (!r.question_uids.length) throw new Error("empty retrieve for " + selType);
  for (const uid of r.question_uids) {
    const it = packed[uid];
    if (!it || it.item_type !== selType) {
      throw new Error("leaked " + uid + " type " + (it && it.item_type) + " want " + selType);
    }
  }
  return r.question_uids;
}

const structured = assertType("structured");
const mcq = assertType("mcq");
const open = assertType("open_response");
if (structured.join() !== "b-struct") throw new Error("structured set " + structured);
if (mcq.join() !== "a-mcq") throw new Error("mcq set " + mcq);
if (open.join() !== "c-open") throw new Error("open set " + open);

const noType = TTwinRag.assemble(
  { subject: "chemistry", pack: "igcse_9_10" },
  mixed,
  table
);
if (noType.question_uids.length !== 3) {
  throw new Error("untyped retrieve should keep pack/node MCQ+written, got " + noType.question_uids);
}

const parsed = TTwinRag.parsePromptDeterministic("structured questions on chemical energetics at senior level", {
  subject: "chemistry",
  aliases: { "chemical energetics": { pack: "senior_11_12_as_a", nodes: ["chem:C6"] } },
});
if (parsed.item_type !== "structured") {
  throw new Error("parsePromptDeterministic item_type " + parsed.item_type);
}

const navPath = path.join(ROOT, "data/nav/chemistry.json");
if (fs.existsSync(navPath)) {
  const nav = JSON.parse(fs.readFileSync(navPath, "utf8"));
  const live = TTwinRag.assemble(
    { subject: "chemistry", pack: "igcse_9_10", item_type: "structured" },
    nav,
    table
  );
  if (!live.question_uids.length) throw new Error("live chemistry structured retrieve empty");
  const by = Object.fromEntries(nav.map((r) => [r.uid, r]));
  for (const uid of live.question_uids) {
    if ((by[uid] || {}).item_type !== "structured") {
      throw new Error("live leak " + uid + " " + (by[uid] && by[uid].item_type));
    }
  }
  const liveMcq = TTwinRag.assemble(
    { subject: "chemistry", pack: "igcse_9_10", item_type: "mcq" },
    nav,
    table
  );
  if (!liveMcq.question_uids.length) throw new Error("live chemistry mcq retrieve empty");
  for (const uid of liveMcq.question_uids) {
    if ((by[uid] || {}).item_type !== "mcq") throw new Error("live mcq leak " + uid);
  }
  console.log("live_chemistry", { structured: live.question_uids.length, mcq: liveMcq.question_uids.length });
}

console.log("retrieve_by_type_ok", {
  structured,
  mcq,
  open_response: open,
  untyped: noType.question_uids,
  parsed_item_type: parsed.item_type,
});
