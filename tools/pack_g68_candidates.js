#!/usr/bin/env node
"use strict";
/**
 * Pack Science 6–8 CANDIDATE items into one questions file + one nav file
 * so Browse / Test maker can load them. Does not write data/questions/.
 */
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..");
const IS_MATH = process.argv.indexOf("--maths") >= 0 || process.env.TTWIN_G68_SUBJECT === "maths";
const TRAY = IS_MATH ? "math-middle_6_8" : "science-middle_6_8";
const SUBJ = IS_MATH ? "maths" : "science";
const SRC = path.join(ROOT, "candidate", TRAY, "items");
const OUT_PACK = path.join(ROOT, "candidate", TRAY, "pack.json");
const OUT_NAV = path.join(ROOT, "candidate", TRAY, "nav.json");
const SCIENCE = path.join(ROOT, "data", "maps", IS_MATH ? "maths.json" : "science.json");
const QUALITY = path.join(ROOT, "candidate", TRAY, "quality.json");
let QUALITY_MAP = null;
function readQuality(p) {
  try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch (e) { return null; }
}

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}
function looksLikeCode(s) {
  const t = String(s || "").trim();
  if (!t) return true;
  return /^(chem|phy|bio|math|sci):/i.test(t) ||
    /^(cam:|IGCSE:|AS_A:)/i.test(t) ||
    /^[A-Z]\d+(\/|$)/.test(t);
}
function hingeLabel(unit, chapter) {
  const hinge = String((unit && unit.decision_hinge) || "").trim();
  const ch = String(chapter || (unit && unit.chapter_title) || "").trim();
  let lab = hinge || ch;
  if (lab.length > 90) lab = lab.slice(0, 87).replace(/\s+\S*$/, "") + "…";
  if (!lab || looksLikeCode(lab)) lab = ch || "Science decision";
  return lab;
}
function flatten(doc, unit) {
  const it = Object.assign({}, doc.item || {});
  if (!it.uid) return null;
  it.lifecycle = "CANDIDATE";
  it.serve_eligible = false;
  it.complete_exam = false;
  it.owner_ratified = false;
  it.subject = SUBJ;
  it.pack = "middle_6_8";
  if (doc.variation_class) it.variation_class = doc.variation_class;
  if (doc.join_status) it.join_status = doc.join_status;
  if (doc.target_unit_id) it.target_unit_id = doc.target_unit_id;
  if (doc.source_ref) it.source_ref = doc.source_ref;
  if (doc.build_logic || doc.mx_option_map) it.author = "grok";
  if (Array.isArray(it.tables)) {
    it.tables = it.tables.map((t) => {
      if (typeof t !== "string") return t;
      try { return JSON.parse(t); } catch (e) { return t; }
    });
  }
  const chapter = it.chapter_label || (unit && unit.chapter_title) || "";
  if (chapter && !it.chapter_label) it.chapter_label = chapter;
  if (QUALITY_MAP && it.uid && QUALITY_MAP[it.uid]) it.quality = QUALITY_MAP[it.uid];
  return it;
}
function navRow(it, unit) {
  const chapter = it.chapter_label || (unit && unit.chapter_title) || "";
  const subLab = hingeLabel(unit, chapter);
  return {
    uid: it.uid,
    subject: SUBJ,
    pack: "middle_6_8",
    grade_band: "MIDDLE",
    node: it.node,
    chapter_id: it.chapter_id || (unit && unit.chapter) || "",
    chapter_label: chapter,
    subtopic_id: it.subtopic_id || (it.hinges && it.hinges.primary) || "",
    subtopic_label: subLab,
    complete_exam: false,
    cam_family: null,
    ncert_family: (it.hinges && it.hinges.primary) || it.subtopic_id || "",
    item_type: it.item_type || "mcq",
    lifecycle: "CANDIDATE",
    author: it.author || null,
    quality_tier: (it.quality && it.quality.tier) || null,
  };
}
function pack() {
  const science = readJson(SCIENCE);
  QUALITY_MAP = readQuality(QUALITY);
  const byId = {};
  (science.units || []).forEach((u) => { if (u.unit_id) byId[u.unit_id] = u; });
  const files = fs.readdirSync(SRC).filter((f) => f.endsWith(".json")).sort();
  const items = [];
  const nav = [];
  files.forEach((f) => {
    let doc;
    try { doc = readJson(path.join(SRC, f)); } catch (e) { return; }
    const unit = byId[doc.target_unit_id] || byId[doc.item && doc.item.subtopic_id];
    const it = flatten(doc, unit);
    if (!it) return;
    if (it.serve_eligible) it.serve_eligible = false;
    items.push(it);
    nav.push(navRow(it, unit));
  });
  fs.writeFileSync(OUT_PACK, JSON.stringify(items) + "\n", "utf8");
  fs.writeFileSync(OUT_NAV, JSON.stringify(nav) + "\n", "utf8");
  return { n: items.length, pack: path.relative(ROOT, OUT_PACK), nav: path.relative(ROOT, OUT_NAV) };
}

module.exports = { pack, flatten, navRow, OUT_PACK, OUT_NAV, ROOT };

if (require.main === module) {
  const r = pack();
  console.log(JSON.stringify(r));
}
