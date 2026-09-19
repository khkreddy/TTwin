#!/usr/bin/env node
"use strict";
/**
 * grade_g68_quality.js — deterministic quality grading for G6–8 CANDIDATE items.
 * Rubric: harness/modify/QUALITY_RUBRIC_G68.md (v1, written before mass inspection).
 * Reads candidate/{science,math}-middle_6_8/items/*.json, applies rubric checks, and
 * writes candidate/<tray>/quality.json as { uid: {tier, score, reasons[] } }.
 * The packer merges quality.json into packed items + nav rows for UI filtering.
 * Never writes data/questions/.
 * Usage: node tools/grade_g68_quality.js | --gold
 */
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..");

/* Learner-text regexes. Each MUST hold gold-corpus FP = 0 (see --gold). */
const G14_RE = /\bis what (creates|produces)\b/i;
// Learner-safe whitelist: vendor names, harness identifiers, and mx type tokens.
// NB: "CANDIDATE", "closed formula", "triangular numbers" were removed — they false-positive
// on the gold corpus (verified 0 FP for the set below via --gold). G16 covers grade-6 vocab separately.
const WHITELIST_RE = /\b(Moonshot|Grok|Kimi|modify_g68|mx_option_map|condition_omission|relationship_reversal|scope_error|mechanism_conflation)\b/i;
const FIGURE_REF_RE = /\b(the|this)\s+(figure|diagram|graph|circuit|food\s*web|ray\s*diagram|apparatus|picture(s)?\s+(below|shown))\b|\bas shown\b|\bshown (in|below)\b/i;
const HINGE_WANTS_FIGURE_RE = /(figure|diagram|circuit|food webs?|ray|graph|apparatus)/i;
const CRIT = "critical", MOD = "moderate";

function readJson(p) { return JSON.parse(fs.readFileSync(p, "utf8")); }
function fileExists(p) { try { fs.accessSync(p); return true; } catch (e) { return false; } }
function trunc(s, n) { s = String(s == null ? "" : s); return s.length > n ? s.slice(0, n - 1) + "…" : s; }

function optionEntries(it) {
  const out = [];
  const opts = it.options || {};
  if (opts && typeof opts === "object" && !Array.isArray(opts)) {
    Object.keys(opts).forEach((L) => out.push({ id: L, text: opts[L] }));
  } else if (Array.isArray(opts)) {
    opts.forEach((o) => { if (o && o.id) out.push({ id: o.id, text: o.text || "" }); });
  }
  (it.parts || []).forEach((p) => {
    (p && p.options || []).forEach((o) => { if (o && typeof o === "object" && o.id) out.push({ id: o.id, text: o.text || "" }); });
  });
  return out;
}
function keyLetters(it) {
  const k = it.assessment && it.assessment.mcq_key;
  if (typeof k !== "string" || !k) return [];
  return k.split("").filter((c) => /[A-Z]/.test(c));
}
function planNullLetters(doc) {
  const plan = (doc.build_logic && doc.build_logic.option_plan) || {};
  return Object.keys(plan).filter((k) => /^[A-D]$/.test(k) && plan[k] == null);
}
function looksLikeCode(s) {
  const t = String(s || "").trim();
  if (!t) return true;
  return /^(chem|phy|bio|math|sci):/i.test(t) || /^(cam:|IGCSE:|AS_A:)/i.test(t) || /^[A-Z]\d+(\/|$)/.test(t) || /\//.test(t);
}
function loadResults(resultsDir) {
  const byFile = {};
  if (!fileExists(resultsDir)) return byFile;
  fs.readdirSync(resultsDir).filter((f) => f.endsWith(".json")).forEach((f) => {
    try { byFile[f] = readJson(path.join(resultsDir, f)); } catch (e) {}
  });
  return byFile;
}

function gradeItem(doc, unit, result) {
  const it = doc.item || {};
  const asm = it.assessment || {};
  const reasons = [];
  const flags = [];
  let crit = 0, mod = 0;
  const bad = (sev, msg, flag) => { reasons.push(msg); if (flag) flags.push(flag); if (sev === CRIT) crit++; else if (sev === MOD) mod++; };
  const good = (msg) => reasons.push(msg);
  const note = (msg, flag) => { reasons.push(msg); if (flag) flags.push(flag); };

  const itemType = it.item_type || "mcq";
  const isThreeStmt = itemType === "three_statement";
  const isStructured = itemType === "structured";
  const isMcqFamily = ["mcq", "mcq_diagram", "mcq_table", "three_statement"].indexOf(itemType) >= 0;
  const entries = optionEntries(it);
  const optIds = entries.map((e) => e.id);
  const key = keyLetters(it);
  const keySet = {}; key.forEach((L) => { keySet[L] = true; });
  const wrongEntries = entries.filter((e) => !keySet[e.id]);
  const statements = Array.isArray(it.statements) ? it.statements : [];
  const hasTikz = !!String(it.tikz || "").trim();
  const hasFigure = hasTikz || !!it.options_are_figure || (it.tables || []).length > 0;
  const stem = String(it.stem || "");
  const learnerText = [stem]
    .concat((it.parts || []).map((p) => String((p && p.text) || "")))
    .concat(entries.map((e) => e.text))
    .concat(statements.map((s) => String((s && s.text) || s))).join("\n");

  if (!stem.trim()) bad(CRIT, "Broken structure: the stem is empty.", "structure_broken");
  if (isMcqFamily && !isThreeStmt && entries.length < 2)
    bad(CRIT, "Broken structure: MCQ-family item has fewer than two options.", "structure_broken");

  if (isThreeStmt) {
    const hasPattern = statements.length > 0 && !entries.length;
    if (!key.length && !hasPattern) {
      const resHas = result && result.answer && (result.answer.kind === "statement_pattern" || result.answer.kind === "part_answers");
      if (!resHas) bad(CRIT, "Key missing: three-statement item has no key and no statement pattern anywhere.", "key_missing");
    }
  } else if (isMcqFamily && !key.length) {
    bad(CRIT, "Key missing: MCQ item has no assessment.mcq_key.", "key_missing");
  }
  if (isStructured && !(result && result.answer && result.answer.kind === "part_answers"))
    bad(CRIT, "Key missing: structured item has no part_answers in results.", "key_missing");
  key.forEach((L) => {
    if (optIds.length && optIds.indexOf(L) < 0)
      bad(CRIT, "Key invalid: key letter " + L + " is not present among the options.", "key_invalid");
  });
  if (new Set(key).size !== key.length)
    bad(CRIT, "Key invalid: one_or_more key letters are not distinct.", "key_invalid");

  const mxMap = doc.mx_option_map || {};
  key.forEach((L) => {
    if (mxMap[L] && mxMap[L] !== "UNRESOLVED")
      bad(CRIT, "Mix-up bound to the key: mx_option_map names key letter " + L + " as a wrong-option mix-up.", "mx_on_key");
  });

  const nulls = planNullLetters(doc);
  if (nulls.length && key.length) {
    const nk = key.slice().sort().join(""), nl = nulls.slice().sort().join("");
    if (nk !== nl)
      bad(CRIT, "Plan/key mismatch: the build plan marked {" + nl + "} as correct but the item key is " + nk + " (R0 donor-key artefact).", "plan_key_mismatch");
  }

  wrongEntries.forEach((e) => {
    if (G14_RE.test(e.text))
      bad(CRIT, "Reverse-causation artefact: option " + e.id + " reads \"" + trunc(e.text, 70) + "\".", "g14_reverse_causation");
  });

  if (FIGURE_REF_RE.test(learnerText) && !hasFigure)
    bad(CRIT, "Figure referenced but missing: the stem/parts refer to a figure/diagram yet none is present.", "figure_ref_without_figure");

  if (WHITELIST_RE.test(learnerText)) {
    const m = learnerText.match(WHITELIST_RE);
    bad(CRIT, "Whitelist leak: learner-facing text contains the term \"" + (m && m[0]) + "\".", "whitelist_leak");
  }

  if (isStructured && result && result.answer && result.answer.kind === "part_answers")
    note("Harness note: the part answers live only in results/*.json; the packed item cannot be auto-marked (a known resultToCandidate packing gap, §5.2).", "key_not_packed");
  if (isThreeStmt && !key.length && result && result.answer && result.answer.kind === "statement_pattern")
    note("Harness note: the true/false pattern lives only in results/*.json; the packed item cannot be auto-marked (a known packing gap, §5.2).", "key_not_packed");
  if (looksLikeCode(it.chapter_label))
    note("Harness note: chapter label is a machine path (" + trunc(it.chapter_label, 40) + ") instead of a teacher-facing title (map data gap, §5.4).", "chapter_label_code");
  if (hasTikz && !FIGURE_REF_RE.test(learnerText))
    bad(MOD, "Figure without reference: a figure is present but the stem/parts never refer to it.", "tikz_without_reference");
  if (!hasFigure && unit && HINGE_WANTS_FIGURE_RE.test(String(unit.decision_hinge || "")))
    bad(MOD, "Missing figure: the map hinge calls for a figure/diagram but the item has none.", "hinge_figure_missing");
  const oneOrMore = !!asm.one_or_more;
  if (oneOrMore && key.length < 2) bad(MOD, "one_or_more declared but the key has fewer than two letters.", "one_or_more_short_key");
  if (!oneOrMore && key.length > 1) bad(MOD, "Multi-letter key (" + key.join("") + ") without the one_or_more flag.", "multi_key_single_flag");

  if (/\b(Meera|Meena)\b/.test(learnerText)) note("Note: uses a Kimi-era recurring character name (Meera/Meena).", "meera_meena");
  if (hasTikz && itemType === "mcq") note("Note: has a drawn figure but item_type stayed mcq, so the 'MCQ diagram' filter misses it.", "item_type_not_promoted");
  const attempt = (String(it.uid || "").match(/:(a\d+)$/) || [])[1];
  if (doc.variation_class === "V1" && attempt && attempt !== "a1" && attempt !== "a2")
    note("Note: variation_class is V1 on attempt " + attempt + " (the V1–V8 ladder was not executed).", "variation_ladder");
  if (!doc.build_logic && !doc.mx_option_map) note("Note: Kimi-era a1/a2 item (no build_logic provenance).", "kimia12");

  if (!crit && !mod) {
    if (key.length || (result && result.answer)) good("Keyable: a key or answer pattern is available.");
    if (entries.length && Object.keys(mxMap).some((L) => !keySet[L] && mxMap[L] && mxMap[L] !== "UNRESOLVED"))
      good("Distractors are mix-up bound (mx_option_map on wrong letters).");
    if (hasFigure) good("Figure present and referenced.");
    good("No known generator artefact detected (clean against G9–G16-era defects).");
  }

  let score = Math.max(0, 100 - crit * 40 - mod * 15);
  let tier = "top";
  if (crit > 0 || score < 60) tier = "low";
  else if (mod > 0 || score < 85) tier = "medium";
  return { tier: tier, score: score, reasons: reasons, flags: flags };
}

function gradeTray(tray, subj) {
  const itemsDir = path.join(ROOT, "candidate", tray, "items");
  const resultsDir = path.join(ROOT, "candidate", tray, "results");
  const mapFile = path.join(ROOT, "data", "maps", subj + ".json");
  const units = {};
  try { (readJson(mapFile).units || []).forEach((u) => { if (u.unit_id) units[u.unit_id] = u; }); } catch (e) {}
  const results = loadResults(resultsDir);
  const files = fs.readdirSync(itemsDir).filter((f) => f.endsWith(".json")).sort();
  const out = {};
  const tally = { top: 0, medium: 0, low: 0, n: 0 };
  const flagCount = {};
  files.forEach((f) => {
    let doc; try { doc = readJson(path.join(itemsDir, f)); } catch (e) { return; }
    const unit = units[doc.target_unit_id] || units[doc.item && doc.item.subtopic_id];
    const g = gradeItem(doc, unit, results[f]);
    const uid = (doc.item && doc.item.uid) || f.replace(/\.json$/, "");
    out[uid] = g;
    tally[g.tier]++; tally.n++;
    (g.flags || []).forEach((fl) => { flagCount[fl] = (flagCount[fl] || 0) + 1; });
  });
  const qf = path.join(ROOT, "candidate", tray, "quality.json");
  fs.writeFileSync(qf, JSON.stringify(out) + "\n", "utf8");
  const sf = path.join(ROOT, "candidate", tray, "quality_summary.json");
  fs.writeFileSync(sf, JSON.stringify({ n: tally.n, tally: tally, flags: flagCount }, null, 2) + "\n", "utf8");
  return { tray: tray, file: path.relative(ROOT, qf), summary: path.relative(ROOT, sf), tally: tally, flags: flagCount };
}

/* Gold-corpus FP validation for the learner-text regexes (G14 + whitelist). */
function goldScan() {
  const banks = ["chemistry-igcse", "physics-igcse", "biology-igcse", "maths-bank", "science-junior",
    "maths-igcse", "maths-junior", "maths-senior", "maths-olympiad", "chemistry-bank", "biology-bank", "physics-bank"];
  const res = {};
  banks.forEach((b) => {
    const p = path.join(ROOT, "data", "questions", b + ".json");
    if (!fileExists(p)) return;
    let rows; try { rows = readJson(p); } catch (e) { return; }
    let g14 = 0, wl = 0, n = 0;
    (rows || []).forEach((it) => {
      if (!it) return;
      n++;
      const opts = it.options || {};
      const blob = Object.keys(opts).map((k) => String((opts[k] && opts[k].text) || opts[k])).join("\n") + "\n" + String(it.stem || "");
      if (G14_RE.test(blob)) g14++;
      if (WHITELIST_RE.test(blob)) wl++;
    });
    res[b] = { n: n, g14: g14, whitelist: wl };
  });
  console.log(JSON.stringify(res, null, 2));
}

if (require.main === module) {
  if (process.argv.indexOf("--gold") >= 0) { goldScan(); return; }
  const jobs = [["science-middle_6_8", "science"]];
  if (fileExists(path.join(ROOT, "candidate", "math-middle_6_8", "items"))) jobs.push(["math-middle_6_8", "maths"]);
  jobs.forEach(([tray, subj]) => console.log(JSON.stringify(gradeTray(tray, subj))));
}
module.exports = { gradeItem, G14_RE, WHITELIST_RE, FIGURE_REF_RE, HINGE_WANTS_FIGURE_RE, looksLikeCode };
