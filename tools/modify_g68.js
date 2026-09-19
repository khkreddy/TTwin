#!/usr/bin/env node
"use strict";
/**
 * Grades 6–8 Science CANDIDATE generator.
 * Compile modify_packet.v1 from the science map + a packed source, then one bounded
 * model call. Fail closed. Writes candidate/science-middle_6_8/ only — never the live pool.
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "candidate", "science-middle_6_8");
const BANKS = [
  "data/questions/science-junior.json",
  "data/questions/chemistry-igcse.json",
  "data/questions/chemistry-bank.json",
  "data/questions/physics-igcse.json",
  "data/questions/physics-bank.json",
  "data/questions/biology-igcse.json",
];
const KEY_FILES = [
  "/home/harik/raw/cognitive_core/kimi-api.txt",
  "/home/harik/awm_build/kimi-api.txt",
];
const SHEAF_FALLBACK = {
  S1: ["B5", "B2", "B4"],
  S2: ["C4", "C2", "C1", "C3", "C5"],
  S3: ["Q1", "Q3", "Q2", "Q8", "L1"],
  S4: ["P1"],
  S5: ["P2"],
  S6: ["B3", "Q8"],
};
const LIVE_ITEM_TYPES = ["mcq", "mcq_diagram", "mcq_table", "three_statement", "structured", "open_response"];
const FORMAT_MAP = {
  single_mcq: "mcq",
  one_or_more: "mcq",
  three_statement: "three_statement",
  structured_parts: "structured",
  open_response: "open_response",
  option_table: "mcq_table",
  options_are_figure: "mcq_diagram",
  statement_reason: "structured",
  two_part: "structured",
  assertion_reason: "structured",
  select_all: "mcq",
  mcq: "mcq",
  mcq_diagram: "mcq_diagram",
  mcq_table: "mcq_table",
  structured: "structured",
};
const VISUAL_HINGE = /figure|diagram|circuit|food web|ray|graph|apparatus/i;

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}
function writeJson(p, obj) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(obj, null, 2) + "\n", "utf8");
}
function bareNode(n) {
  return String(n || "").replace(/^(chem|phy|bio|math):/, "");
}
function safeUnit(id) {
  return String(id || "").replace(/\//g, "_");
}
function loadKimi() {
  const src = fs.readFileSync(path.join(ROOT, "js/kimi.js"), "utf8");
  const sandbox = {
    console, Date, JSON, Array, Object, String, Math, setTimeout, clearTimeout,
    fetch: global.fetch,
    AbortController: global.AbortController,
    AbortSignal: global.AbortSignal,
    Buffer: global.Buffer,
    URL: global.URL,
  };
  sandbox.window = sandbox;
  sandbox.location = { protocol: "https:", hostname: "cli" };
  sandbox.localStorage = {
    store: {},
    getItem(k) { return this.store[k] || ""; },
    setItem(k, v) { this.store[k] = String(v); },
    removeItem(k) { delete this.store[k]; },
  };
  vm.createContext(sandbox);
  vm.runInContext(src, sandbox);
  return sandbox.TTwinKimi;
}
function loadKey() {
  for (let i = 0; i < KEY_FILES.length; i++) {
    if (!fs.existsSync(KEY_FILES[i])) continue;
    const m = fs.readFileSync(KEY_FILES[i], "utf8").match(/sk-[A-Za-z0-9]+/);
    if (m) return m[0];
  }
  return "";
}
function sheafOf(science, unit) {
  const nodeId = unit.node;
  const parent = unit.node_parent || String(nodeId || "").split("/")[0];
  const nodes = science.nodes || [];
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].id === nodeId && nodes[i].sheaf_home) return nodes[i].sheaf_home;
  }
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].id === parent && nodes[i].sheaf_home) return nodes[i].sheaf_home;
  }
  return null;
}
function originOf(unit) {
  return unit.node_parent || String(unit.node || "S1").split("/")[0];
}
function pedagogy(it) {
  const stem = String((it && (it.stem || it.stem_lead)) || "").trim();
  const opts = (it && it.options) || {};
  let nopt = 0;
  if (opts && typeof opts === "object" && !Array.isArray(opts)) {
    Object.keys(opts).forEach((k) => { if (String(opts[k] || "").trim()) nopt++; });
  }
  const a = (it && it.assessment) || {};
  const seeds = a.modify_seeds || [];
  const tikz = it && it.tikz;
  const tikzText = Array.isArray(tikz) ? tikz.join("\n") : String(tikz || "");
  return {
    stem: stem.length,
    nopt,
    key: !!(a.mcq_key),
    seeds: Array.isArray(seeds) ? seeds.length : 0,
    tikz: tikzText.trim() !== "",
    type: it && it.item_type,
  };
}
function hasPedagogy(it) {
  const p = pedagogy(it);
  if (p.stem < 40) return false;
  if (p.nopt >= 2) return true;
  if (p.type === "open_response" || p.type === "structured") return true;
  return p.key && p.stem >= 80;
}
let _banks = null;
function loadBanks() {
  if (_banks) return _banks;
  const rows = [];
  BANKS.forEach((rel) => {
    const p = path.join(ROOT, rel);
    if (!fs.existsSync(p)) return;
    const data = readJson(p);
    (Array.isArray(data) ? data : []).forEach((it) => {
      if (it && it.uid) rows.push(it);
    });
  });
  _banks = rows;
  return rows;
}
function findByUid(uid) {
  const banks = loadBanks();
  for (let i = 0; i < banks.length; i++) if (banks[i].uid === uid) return banks[i];
  return null;
}
function pickSource(unit, science, used) {
  const banks = loadBanks();
  const sheaf = sheafOf(science, unit);
  const origin = originOf(unit);
  const fallback = SHEAF_FALLBACK[origin] || [];
  let best = null;
  let bestScore = -1;
  for (let i = 0; i < banks.length; i++) {
    const it = banks[i];
    if (used && used.has(it.uid)) continue;
    if (!hasPedagogy(it)) continue;
    const primary = it.hinges && it.hinges.primary;
    if (primary === unit.unit_id) continue;
    const p = pedagogy(it);
    let sc = 0;
    if (primary) {
      const srcUnit = (science.units || []).find((u) => u.unit_id === primary);
      if (srcUnit && srcUnit.chapter === unit.chapter) sc += p.nopt >= 2 ? 50 : 8;
      if (srcUnit && srcUnit.node === unit.node) sc += 20;
    }
    const srcBare = bareNode(it.node);
    if (srcBare && srcBare === unit.node) sc += 40;
    if (sheaf && srcBare && (srcBare === sheaf || srcBare.startsWith(sheaf + "/"))) sc += 35;
    for (let f = 0; f < fallback.length; f++) {
      if (srcBare === fallback[f] || srcBare.startsWith(fallback[f] + "/")) { sc += 25; break; }
    }
    if (it.subject === "science") sc += 10;
    if (p.nopt >= 4 && p.key) sc += 40;
    else if (p.nopt >= 2 && p.key) sc += 20;
    if (p.type === "open_response" && p.nopt < 2) sc -= 35;
    if (p.seeds) sc += 5;
    const hinge = String((unit && unit.decision_hinge) || "");
    if (p.tikz && VISUAL_HINGE.test(hinge)) sc += 6;
    if (sc > bestScore) {
      best = it;
      bestScore = sc;
    }
  }
  if (!best || bestScore < 25) return null;
  return { item: best, score: bestScore };
}
function instructionFor(unit, variation, figureMode) {
  const grade = unit.grade || 6;
  const hinge = unit.decision_hinge || "";
  const chapter = unit.chapter_title || "";
  let s = "Write one new grades " + grade + " Science question. Chapter: " + chapter + ". ";
  s += "The student must decide: " + hinge + " ";
  s += "Use an Indian school or home setting and Indian names. Keep the source language register. ";
  if (variation === "V1") s += "Change the numbers, materials, or everyday situation. Do not copy the source stem. Recalculate the key. ";
  else if (variation === "V6") s += "Inverse-flip: the original answer becomes given; the student finds what the source treated as given. Recalculate the key. Do not copy the original key. ";
  else if (variation === "V5") s += "Rewrite the figure and the stem so they agree. Exactly one visual. Recalculate the key. ";
  else s += "Retarget the source onto this Science decision. Keep the source item type. Recalculate the key. ";
  if (figureMode === "remove") s += "The new item has no figure. Do not refer to a diagram. ";
  if (figureMode === "add" || figureMode === "rewrite") {
    s += "Supply exactly one complete tikzpicture. The stem must refer to that figure. ";
  }
  s += "Do not print mix-up labels, hinge codes, node codes, or the word CANDIDATE. ";
  s += "If the stem numbers activities 1..n, every number must appear in an option (or in a structured part's first-class options). Two-tier (choose, then reason) is welcome: put A/B/C on part.options, not typed into part text.";
  return s.slice(0, 1000);
}
function packetHasPedagogy(packet) {
  const stem = (packet.source && packet.source.stem) || "";
  if (String(stem).trim().length < 20) return false;
  const intel = packet.intelligence || {};
  if (intel.join_status === "BOUND" && intel.hinge) return true;
  if ((intel.mx || []).length) return true;
  if (intel.enrichment) return true;
  if ((intel.modify_seeds || []).length) return true;
  return false;
}
function hingeWantsFigure(unit) {
  return VISUAL_HINGE.test(String((unit && unit.decision_hinge) || ""));
}
function sanitizeTikz(raw) {
  let s = Array.isArray(raw) ? raw.join("\n") : String(raw || "");
  if (!s.trim()) return { ok: false, tikz: "", packages: [] };
  s = s.replace(/\\begin\{circuitikz\}/g, "\\begin{tikzpicture}");
  s = s.replace(/\\end\{circuitikz\}/g, "\\end{tikzpicture}");
  if (!/\\begin\{tikzpicture\}/.test(s) || !/\\end\{tikzpicture\}/.test(s)) {
    return { ok: false, tikz: "", packages: [] };
  }
  const needsCirc = /to\s*\[(battery|lamp|short|nos|switch|american|european)/i.test(s);
  return { ok: true, tikz: s, packages: needsCirc ? ["circuitikz"] : [] };
}
function liveItemType(resultType) {
  return FORMAT_MAP[resultType] || null;
}
function normalizeResultTables(tables, liveType) {
  const out = [];
  (tables || []).forEach((t) => {
    let obj = t;
    if (typeof t === "string") {
      try { obj = JSON.parse(t); } catch (e) { return; }
    }
    if (!obj || typeof obj !== "object") return;
    if (liveType === "mcq_table") obj.is_option_table = true;
    if (obj.is_option_table) {
      const labs = obj.row_labels || [];
      const lettered = labs.some((L) => /^[A-D]$/i.test(String(L || "")));
      if (!lettered) obj.row_labels = (obj.rows || []).map((_, i) => String.fromCharCode(65 + i));
    }
    out.push(obj);
  });
  return out;
}
function mxIds(packet) {
  return ((packet && packet.intelligence && packet.intelligence.mx) || [])
    .map((m) => m && (m.mx_type || m.name))
    .filter(Boolean);
}
function compileMxPlan(unit, keyLetter, itemType) {
  const live = liveItemType(itemType) || itemType;
  if (live === "structured" || itemType === "structured_parts") return {};
  const mx = (unit && unit.mx) || [];
  const types = [];
  mx.forEach((m) => {
    const id = m.type || m.mx_type;
    if (id && types.indexOf(id) < 0) types.push(id);
  });
  const letters = ["A", "B", "C", "D"].filter((L) => L !== (keyLetter || "A"));
  const plan = {};
  letters.forEach((L, i) => {
    plan[L] = types[i] || "UNRESOLVED";
  });
  if (keyLetter) plan[keyLetter] = null;
  return plan;
}
function compileBuildLogic(packet, unit, source, spec, figureMode) {
  const mx = mxIds(packet);
  const targetType = (spec && spec.target_item_type) || "preserve";
  return {
    source_uid: source && source.uid,
    hinge: unit && unit.unit_id,
    item_type_target: targetType,
    figure_decision: { mode: figureMode, reason: hingeWantsFigure(unit) ? "hinge_names_visual" : "no_visual_referent" },
    mx_seeds_used: mx.slice(0, 4),
    option_plan: compileMxPlan(unit, packet && packet.source && packet.source.key && packet.source.key.letter, targetType),
    format_rationale: "preserve source skeleton; retarget hinge to " + ((unit && unit.unit_id) || ""),
  };
}
function gateG9(result, packet) {
  const live = liveItemType(result && result.item_type);
  if (live !== "mcq" && live !== "mcq_diagram" && live !== "mcq_table") return { ok: true };
  const map = (result && result.mx_option_map) || (result && result.teacher && result.teacher.mx_option_map) || {};
  const ids = optionIdsFromResult(result);
  const ans = result.answer || {};
  const keySet = {};
  if (ans.kind === "letter_set") (ans.letters || []).forEach((L) => { keySet[L] = true; });
  else if (ans.letter) keySet[ans.letter] = true;
  const allowed = mxIds(packet);
  const bound = [];
  ids.forEach((L) => {
    if (keySet[L]) return;
    const v = map[L];
    if (!v || v === "UNRESOLVED") return;
    if (allowed.indexOf(v) < 0) return;
    if (bound.indexOf(v) < 0) bound.push(v);
  });
  if (bound.length < 2) return { ok: false, gate: "G9" };
  return { ok: true };
}
function optionIdsFromResult(out) {
  return (out.options || []).map((o) => o && o.id).filter(Boolean);
}
function stemActivityNumbers(stem) {
  const s = String(stem || "");
  const re = /(?:^|\n)\s*(\d+)\s+[A-Za-z]/g;
  const set = [];
  let m;
  while ((m = re.exec(s))) {
    const n = parseInt(m[1], 10);
    if (n >= 1 && n <= 12 && set.indexOf(n) < 0) set.push(n);
  }
  return set.sort((a, b) => a - b);
}
function optionActivityNumbers(result) {
  const blob = [];
  (result.options || []).forEach((o) => blob.push(o && o.text));
  (result.parts || []).forEach((p) => {
    blob.push(p && p.text);
    ((p && p.options) || []).forEach((o) => blob.push(typeof o === "string" ? o : (o && o.text)));
  });
  const t = blob.join("\n");
  const set = [];
  const re = /Activity\s*(\d+)/gi;
  let m;
  while ((m = re.exec(t))) {
    const n = parseInt(m[1], 10);
    if (n >= 1 && n <= 12 && set.indexOf(n) < 0) set.push(n);
  }
  return set.sort((a, b) => a - b);
}
function nestedChoiceLetters(text) {
  const found = [];
  const re = /(?:^|\n)\s*([A-D])[.)]\s+\S/g;
  let m;
  while ((m = re.exec(String(text || "")))) {
    if (found.indexOf(m[1]) < 0) found.push(m[1]);
  }
  return found;
}
function gateG10(result) {
  const stem = String((result && result.stem) || "");
  const S = stemActivityNumbers(stem);
  if (S.length < 2) return { ok: true };
  const optBlob = ((result && result.options) || []).map((o) => (o && o.text) || "").join("\n");
  if (!/activity/i.test(stem) && !/activity/i.test(optBlob)) return { ok: true };
  const O = optionActivityNumbers(result);
  for (let i = 0; i < S.length; i++) {
    if (O.indexOf(S[i]) < 0) return { ok: false, gate: "G10" };
  }
  return { ok: true };
}
function gateG11(result) {
  const live = liveItemType(result && result.item_type);
  const parts = (result && result.parts) || [];
  if (live === "structured" || (result && result.item_type === "structured_parts")) {
    if (!parts.length) return { ok: false, gate: "G11" };
    for (let i = 0; i < parts.length; i++) {
      const p = parts[i] || {};
      const nested = nestedChoiceLetters(p.text);
      const hasOpts = Array.isArray(p.options) && p.options.length >= 2;
      if (nested.length >= 2 && !hasOpts) return { ok: false, gate: "G11" };
    }
  }
  return { ok: true };
}
function gateG12(result, packet) {
  const live = liveItemType(result && result.item_type);
  const plan = (packet && packet.build_logic && packet.build_logic.option_plan) || {};
  const ids = optionIdsFromResult(result);
  const planKeys = Object.keys(plan).filter((k) => plan[k] != null);
  if (live === "structured" || (result && result.item_type === "structured_parts")) {
    if (planKeys.length && !ids.length) return { ok: false, gate: "G12" };
    return { ok: true };
  }
  if (live === "mcq" || live === "mcq_diagram" || live === "mcq_table") {
    for (let i = 0; i < planKeys.length; i++) {
      if (ids.indexOf(planKeys[i]) < 0) return { ok: false, gate: "G12" };
    }
  }
  return { ok: true };
}
function ingestGates(result, packet) {
  const g9 = gateG9(result, packet);
  if (!g9.ok) return g9;
  const g10 = gateG10(result);
  if (!g10.ok) return g10;
  const g11 = gateG11(result);
  if (!g11.ok) return g11;
  return gateG12(result, packet);
}
function compileUnit(K, unit, source, science, spec) {
  spec = spec || {};
  const p0 = pedagogy(source);
  let figureMode = spec.figureMode;
  if (!figureMode) {
    if (hingeWantsFigure(unit)) figureMode = p0.tikz ? "rewrite" : "add";
    else if (p0.tikz && !hingeWantsFigure(unit)) figureMode = "remove";
    else figureMode = "preserve";
  }
  if (figureMode === "rewrite" || figureMode === "preserve" || figureMode === "add") {
    const san = sanitizeTikz(source && source.tikz);
    if ((figureMode === "rewrite" || figureMode === "preserve") && p0.tikz && !san.ok) figureMode = "remove";
  }
  const ctx = {
    map: science,
    pack: "middle_6_8",
    subject: "science",
    target_unit_id: unit.unit_id,
    slim_map_ref: "data/maps/science.json",
    target_item_type: spec.target_item_type || "preserve",
    figure: { mode: figureMode, tikz_required: figureMode === "rewrite" || figureMode === "add" },
  };
  if (spec.variation_class) ctx.variation_class = spec.variation_class;
  const probe = K.assembleModifyPacket(source, "probe", ctx);
  const variation = probe.spec.variation_class;
  const instruction = spec.instruction || instructionFor(unit, variation, figureMode);
  const packet = K.assembleModifyPacket(source, instruction, ctx);
  packet.build_logic = compileBuildLogic(packet, unit, source, spec, figureMode);
  return packet;
}
function resultToCandidate(result, packet, source, unit, attempt) {
  let live = liveItemType(result.item_type);
  if (!live || LIVE_ITEM_TYPES.indexOf(live) < 0) return { ok: false, gate: "G2", keepOriginal: true };
  const options = {};
  (result.options || []).forEach((o) => { if (o && o.id) options[o.id] = o.text || ""; });
  const tables = normalizeResultTables(result.tables, live);
  if (live === "mcq_table") {
    const t = tables.find((x) => x && x.is_option_table);
    (t && t.rows || []).forEach((row, i) => {
      const L = String.fromCharCode(65 + i);
      if (!options[L] || /^Row\s*\d+$/i.test(String(options[L]))) {
        options[L] = (row || []).map((c) => String(c == null ? "" : c).trim()).filter(Boolean).join(" — ");
      }
    });
  }
  let key = null;
  if (result.answer && result.answer.kind === "letter_set") key = (result.answer.letters || []).join("");
  else if (result.answer && result.answer.letter) key = result.answer.letter;
  const oneOrMore = result.item_type === "one_or_more" || (typeof key === "string" && key.length > 1);
  const figMode = (packet.spec && packet.spec.figure && packet.spec.figure.mode) || "preserve";
  let tikz = null;
  let packages = [];
  if (figMode !== "remove") {
    const raw = result.tikz || (figMode === "preserve" ? (source && source.tikz) : result.tikz);
    const san = sanitizeTikz(raw);
    if (san.ok) { tikz = san.tikz; packages = san.packages; }
  }
  if (live === "mcq" && tikz && source && source.item_type === "mcq_diagram") live = "mcq_diagram";
  const lbs = result.learn_by_solve || null;
  const uid = "candidate:g68:" + String(unit.unit_id).replace(/\//g, ":") + ":a" + attempt;
  const mxMap = result.mx_option_map || (result.teacher && result.teacher.mx_option_map) || {};
  const build = Object.assign({}, packet.build_logic || {}, result.build_logic || {});
  if (!build.source_uid) build.source_uid = source && source.uid;
  if (!build.hinge) build.hinge = unit.unit_id;
  return {
    schema: "ttwin.candidate.v1",
    lifecycle: "CANDIDATE",
    serve_eligible: false,
    owner_ratified: false,
    join_status: packet.intelligence.join_status,
    variation_class: packet.spec.variation_class,
    fidelity_mode: packet.spec.fidelity_mode,
    source_ref: packet.source.item_ref,
    target_unit_id: unit.unit_id,
    build_logic: build,
    mx_option_map: mxMap,
    item: {
      uid: uid,
      subject: "science",
      pack: "middle_6_8",
      node: unit.node,
      chapter_id: unit.chapter,
      chapter_label: unit.chapter_title || null,
      subtopic_id: unit.unit_id,
      stem: result.stem,
      item_type: live,
      options: options,
      statements: result.statements || [],
      parts: result.parts || [],
      equations: result.equations || [],
      tables: tables,
      tikz: tikz,
      tikz_packages: packages,
      has_figure: !!(tikz && String(tikz).trim()),
      options_are_figure: result.item_type === "options_are_figure",
      complete_exam: false,
      serve_eligible: false,
      hinges: { primary: unit.unit_id, supporting: [], binder: { method: "modify_g68_named_gap" } },
      assessment: {
        key_source: live === "structured" ? "none" : "none",
        key_status: "available",
        mcq_key: key,
        proposed_key_status: "UNVERIFIED",
        examiner_comment: { present: false },
        one_or_more: !!oneOrMore,
        learn_by_solve: lbs,
        mark_scheme: result.answer && result.answer.kind === "rubric"
          ? { text: (result.answer.rubric || []).join("\n") } : null,
      },
    },
  };
}
function existingCandidateUnits() {
  const dir = path.join(OUT, "items");
  const have = new Set();
  if (!fs.existsSync(dir)) return have;
  fs.readdirSync(dir).forEach((f) => {
    if (!f.endsWith(".json")) return;
    try {
      const doc = readJson(path.join(dir, f));
      if (doc.target_unit_id) have.add(doc.target_unit_id);
    } catch (e) { /* skip */ }
  });
  return have;
}
function grokCoveredUnits() {
  const dir = path.join(OUT, "items");
  const have = new Set();
  if (!fs.existsSync(dir)) return have;
  fs.readdirSync(dir).forEach((f) => {
    if (!f.endsWith(".json")) return;
    try {
      const doc = readJson(path.join(dir, f));
      if ((doc.build_logic || doc.mx_option_map) && doc.target_unit_id) have.add(doc.target_unit_id);
    } catch (e) { /* skip */ }
  });
  return have;
}
function mxTypeCount(unit) {
  const seen = [];
  ((unit && unit.mx) || []).forEach((m) => {
    const t = m.type || m.mx_type;
    if (t && seen.indexOf(t) < 0) seen.push(t);
  });
  return seen.length;
}
function remainingEligibleUnits(science) {
  const have = grokCoveredUnits();
  return (science.units || []).filter((u) => {
    return u.unit_id && mxTypeCount(u) >= 2 && !have.has(u.unit_id);
  });
}
function chapterKey(unit) {
  return String(unit.unit_id || "").split("/").slice(0, 3).join("/");
}
function nextUniformUnits(science, limit) {
  limit = limit || 12;
  const rem = remainingEligibleUnits(science);
  const buckets = {};
  rem.forEach((u) => {
    const k = chapterKey(u);
    if (!buckets[k]) buckets[k] = [];
    buckets[k].push(u);
  });
  const keys = Object.keys(buckets).sort();
  const out = [];
  while (out.length < limit) {
    let progressed = false;
    for (let i = 0; i < keys.length && out.length < limit; i++) {
      const ch = keys[i];
      if (buckets[ch] && buckets[ch].length) {
        out.push(buckets[ch].shift());
        progressed = true;
      }
    }
    if (!progressed) break;
  }
  return out;
}
function maxAttempt(unitId) {
  const dir = path.join(OUT, "items");
  const prefix = safeUnit(unitId) + "__a";
  let max = 0;
  if (!fs.existsSync(dir)) return 0;
  fs.readdirSync(dir).forEach((f) => {
    if (!f.startsWith(prefix) || !f.endsWith(".json")) return;
    const n = parseInt(f.slice(prefix.length, -5), 10);
    if (n) max = Math.max(max, n);
  });
  return max;
}
function nextAttempt(unitId) {
  return maxAttempt(unitId) + 1;
}
function variationForAttempt(attempt) {
  if (attempt === 2) return "V1";
  if (attempt === 3) return "V6";
  if (attempt === 4) return "V5";
  return null;
}
function attemptFailed(unitId, attempt) {
  const tag = safeUnit(unitId) + "__a" + attempt;
  if (fs.existsSync(path.join(OUT, "items", tag + ".json"))) return false;
  return fs.existsSync(path.join(OUT, "packets", tag + ".json"))
    || fs.existsSync(path.join(OUT, "results", tag + ".json"));
}
function deepenUnits(science) {
  const rows = (science.units || []).filter((u) => u.unit_id);
  rows.sort((a, b) => {
    const da = maxAttempt(a.unit_id) - maxAttempt(b.unit_id);
    if (da) return da;
    const fa = attemptFailed(a.unit_id, maxAttempt(a.unit_id) + 1) ? 1 : 0;
    const fb = attemptFailed(b.unit_id, maxAttempt(b.unit_id) + 1) ? 1 : 0;
    if (fa !== fb) return fa - fb;
    return String(a.unit_id).localeCompare(String(b.unit_id));
  });
  return rows.filter((u) => maxAttempt(u.unit_id) < 4);
}
function uncoveredUnits(science, junior) {
  const covered = new Set();
  junior.forEach((it) => {
    const p = it && it.hinges && it.hinges.primary;
    if (p) covered.add(p);
  });
  existingCandidateUnits().forEach((id) => covered.add(id));
  return (science.units || []).filter((u) => u.unit_id && !covered.has(u.unit_id));
}
function census(science, junior) {
  const liveCovered = new Set();
  junior.forEach((it) => {
    const p = it && it.hinges && it.hinges.primary;
    if (p) liveCovered.add(p);
  });
  const cand = existingCandidateUnits();
  const byNode = {};
  (science.units || []).forEach((u) => {
    const n = originOf(u);
    byNode[n] = byNode[n] || { units: 0, live: 0, candidate: 0, uncovered: 0 };
    byNode[n].units += 1;
    if (liveCovered.has(u.unit_id)) byNode[n].live += 1;
    else if (cand.has(u.unit_id)) byNode[n].candidate += 1;
    else byNode[n].uncovered += 1;
  });
  const uncoveredCount = (science.units || []).filter((u) => {
    return u.unit_id && !liveCovered.has(u.unit_id) && !cand.has(u.unit_id);
  }).length;
  return {
    schema: "ttwin.g68_status.v1",
    science_units: (science.units || []).length,
    junior_live: junior.length,
    live_distinct_primaries: liveCovered.size,
    candidates: cand.size,
    uncovered: uncoveredCount,
    by_node: byNode,
  };
}
function logLine(row) {
  fs.mkdirSync(OUT, { recursive: true });
  fs.appendFileSync(path.join(OUT, "log.jsonl"), JSON.stringify(row) + "\n", "utf8");
}
function modifySysText() {
  return `You design ONE replacement exam item inside the compiled modify_packet.v1 bundle. Specification exists before the item. You do not free-write.
Return ONLY modify_result.v1 JSON:
{"schema":"modify_result.v1","status":"OK"|"REFUSED","refusal_reason":null,"item_type":"...","stem":"...","options":[{"id":"A","text":"..."}],"statements":[],"parts":[],"equations":[],"tables":[],"tikz":null,"answer":{"kind":"single_letter"|"letter_set"|"statement_pattern"|"part_answers"|"rubric","letter":"A","letters":null},"teacher":{"proposed_key_status":"UNVERIFIED","key_rationale":"...","variation_applied":"V1","fidelity_selfcheck":"FAITHFUL_TRANSFER","mx_links":[],"figure_note":null}}
Laws:
- Honor spec.instruction, spec.variation_class, spec.fidelity_mode, spec.target_item_type, spec.figure.
- If target_item_type is preserve, keep source.item_type.
- Do not coerce to four-option MCQ. one_or_more uses answer.letters (e.g. ["B","C"]). structured_parts uses parts[]. open_response uses rubric kind, no letter.
- Recalculate the key. Do not copy source.key unless the change cannot affect it.
- Learner fields (stem, options, statements, parts, tables, tikz) must not contain mx_type names, mix-up labels, examiner comments, SMILES strings, hinge ids, node codes, or the word CANDIDATE.
- If intelligence.join_status is UNBOUND, teacher block must not name a map title or hinge code.
- TikZ: at most one visual. Rewrite only if spec.figure.mode is rewrite or add. Never invent a figure when source has none unless mode is add and you supply complete tikzpicture. Use circuitikz as tikzpicture (never nest).
- If you cannot meet the spec: status REFUSED and a refusal_reason. Do not drift.
- Public copy is an exam item, not a published mark scheme. Keep the source language and register unless asked to change it.`;
}

async function callModify(K, packet) {
  const content = await K.chat([
    { role: "system", content: modifySysText() },
    { role: "user", content: JSON.stringify(packet) },
  ], { reasoning_effort: "low", max_tokens: 4096, timeout_ms: 90000 });
  return K.extractJson(content);
}

async function runOne(K, unit, source, science, spec, attempt) {
  const packet = compileUnit(K, unit, source, science, spec);
  const tag = safeUnit(unit.unit_id) + "__a" + attempt;
  writeJson(path.join(OUT, "packets", tag + ".json"), packet);
  const row = {
    at: new Date().toISOString(),
    unit_id: unit.unit_id,
    node: originOf(unit),
    grain: unit.node,
    source_uid: source.uid,
    attempt,
    join_status: packet.intelligence.join_status,
    variation_class: packet.spec.variation_class,
    fidelity_mode: packet.spec.fidelity_mode,
    packet: "packets/" + tag + ".json",
  };
  if (!packetHasPedagogy(packet)) {
    row.status = "skip";
    row.gate = "empty_pedagogy";
    logLine(row);
    return row;
  }
  if (packet.spec.fidelity_mode === "BLOCKED") {
    row.status = "fail_closed";
    row.gate = "BLOCKED";
    writeJson(path.join(OUT, "results", tag + ".json"), { status: "BLOCKED", keep_original: true, packet_id: packet.packet_id });
    logLine(row);
    return row;
  }
  let out;
  try {
    out = await callModify(K, packet);
  } catch (e) {
    row.status = "fail_closed";
    row.gate = "call";
    row.error = String((e && e.message) || e).slice(0, 400);
    writeJson(path.join(OUT, "results", tag + ".json"), { status: "CALL_FAIL", error: row.error, keep_original: true });
    logLine(row);
    return row;
  }
  writeJson(path.join(OUT, "results", tag + ".json"), out);
  const gate = K.applyModifyOutcome(out, packet, source);
  if (!gate.ok) {
    row.status = "fail_closed";
    row.gate = gate.gate;
    logLine(row);
    return row;
  }
  const extra = ingestGates(out, packet);
  if (!extra.ok) {
    row.status = "fail_closed";
    row.gate = extra.gate;
    logLine(row);
    return row;
  }
  const cand = resultToCandidate(out, packet, source, unit, attempt);
  if (cand && cand.keepOriginal) {
    row.status = "fail_closed";
    row.gate = cand.gate || "G2";
    logLine(row);
    return row;
  }
  writeJson(path.join(OUT, "items", tag + ".json"), cand);
  row.status = "ok";
  row.candidate_uid = cand.item.uid;
  row.item = "items/" + tag + ".json";
  logLine(row);
  return row;
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const k = a.slice(2);
      const v = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : true;
      args[k] = v;
    } else args._.push(a);
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0] || "census";
  const science = readJson(path.join(ROOT, "data/maps/science.json"));
  const junior = readJson(path.join(ROOT, "data/questions/science-junior.json"));
  const K = loadKimi();
  if (cmd === "census") {
    const c = census(science, junior);
    writeJson(path.join(OUT, "status.json"), c);
    console.log(JSON.stringify(c, null, 2));
    return;
  }
  if (cmd === "audit-grok") {
    const dir = path.join(OUT, "results");
    const itemDir = path.join(OUT, "items");
    const rows = [];
    if (fs.existsSync(itemDir)) {
      fs.readdirSync(itemDir).filter((f) => f.endsWith(".json")).forEach((f) => {
        let doc;
        try { doc = readJson(path.join(itemDir, f)); } catch (e) { return; }
        if (!(doc.build_logic || doc.mx_option_map)) return;
        const resPath = path.join(dir, f);
        const pktPath = path.join(OUT, "packets", f);
        if (!fs.existsSync(resPath) || !fs.existsSync(pktPath)) {
          rows.push({ file: f, status: "skip", gate: "missing_result_or_packet" });
          return;
        }
        const out = readJson(resPath);
        const packet = readJson(pktPath);
        const g = ingestGates(out, packet);
        rows.push({
          file: f,
          uid: doc.item && doc.item.uid,
          status: g.ok ? "ok" : "fail_closed",
          gate: g.ok ? null : g.gate,
        });
      });
    }
    const fails = rows.filter((r) => r.status === "fail_closed");
    console.log(JSON.stringify({ n: rows.length, fail: fails.length, fails: fails }, null, 2));
    return;
  }
  if (cmd === "remaining") {
    const n = parseInt(args.limit || "48", 10);
    const units = nextUniformUnits(science, n);
    units.forEach((u) => {
      console.log([originOf(u), u.unit_id, chapterKey(u)].join("\t"));
    });
    return;
  }
  if (cmd === "ingest") {
    const unitId = args.unit;
    const sourceUid = args.source;
    const resultPath = args.result;
    const attempt = parseInt(args.attempt || "1", 10);
    if (!unitId || !sourceUid || !resultPath) throw new Error("ingest needs --unit --source --result");
    const unit = science.units.find((x) => x.unit_id === unitId);
    if (!unit) throw new Error("unknown unit " + unitId);
    const source = findByUid(sourceUid);
    if (!source) throw new Error("unknown source " + sourceUid);
    const out = readJson(resultPath);
    const spec = {};
    if (args.variation) spec.variation_class = args.variation;
    if (args["item-type"]) spec.target_item_type = args["item-type"];
    if (args.figure) spec.figureMode = String(args.figure);
    const packet = compileUnit(K, unit, source, science, spec);
    const tag = safeUnit(unit.unit_id) + "__a" + attempt;
    writeJson(path.join(OUT, "packets", tag + ".json"), packet);
    writeJson(path.join(OUT, "results", tag + ".json"), out);
    const gate = K.applyModifyOutcome(out, packet, source);
    const extra = gate.ok ? ingestGates(out, packet) : gate;
    if (!gate.ok || !extra.ok) {
      const row = { status: "fail_closed", gate: (extra && extra.gate) || gate.gate, unit_id: unitId, source_uid: sourceUid };
      logLine(row);
      console.log(JSON.stringify(row));
      return;
    }
    const cand = resultToCandidate(out, packet, source, unit, attempt);
    if (cand && cand.keepOriginal) {
      const row = { status: "fail_closed", gate: cand.gate || "G2", unit_id: unitId };
      logLine(row);
      console.log(JSON.stringify(row));
      return;
    }
    writeJson(path.join(OUT, "items", tag + ".json"), cand);
    const row = { status: "ok", unit_id: unitId, candidate_uid: cand.item.uid, item: "items/" + tag + ".json" };
    logLine(row);
    console.log(JSON.stringify(row));
    return;
  }
  if (cmd === "compile" || cmd === "generate") {
    const unitsWanted = args.unit ? String(args.unit).split(",").map((s) => s.trim()).filter(Boolean) : null;
    const repeat = parseInt(args.repeat || "1", 10);
    const limit = parseInt(args.limit || (unitsWanted ? String(unitsWanted.length * repeat) : "8"), 10);
    const used = new Set();
    let queue = [];
    if (unitsWanted) {
      unitsWanted.forEach((id) => {
        const u = science.units.find((x) => x.unit_id === id);
        if (!u) throw new Error("unknown unit " + id);
        queue.push(u);
      });
    } else {
      queue = uncoveredUnits(science, junior);
      if (!queue.length) queue = deepenUnits(science);
    }
    const rows = [];
    let n = 0;
    for (let i = 0; i < queue.length && n < limit; i++) {
      const unit = queue[i];
      let source = args.source ? findByUid(args.source) : null;
      if (args.source && !source) throw new Error("unknown source " + args.source);
      if (!source) {
        const picked = pickSource(unit, science, used);
        if (!picked) {
          rows.push({ unit_id: unit.unit_id, status: "skip", gate: "no_source" });
          continue;
        }
        source = picked.item;
      }
      used.add(source.uid);
      const start = nextAttempt(unit.unit_id);
      for (let k = 0; k < repeat; k++) {
        const a = start + k;
        const spec = {};
        if (args.variation) spec.variation_class = args.variation;
        else {
          const v = variationForAttempt(a);
          if (v) spec.variation_class = v;
        }
        if (args["item-type"]) spec.target_item_type = args["item-type"];
        if (args.figure) spec.figureMode = String(args.figure);
        if (cmd === "compile") {
          const packet = compileUnit(K, unit, source, science, spec);
          const tag = safeUnit(unit.unit_id) + "__a" + a;
          writeJson(path.join(OUT, "packets", tag + ".json"), packet);
          rows.push({
            status: packet.spec.fidelity_mode === "BLOCKED" ? "fail_closed" : "compiled",
            gate: packet.spec.fidelity_mode === "BLOCKED" ? "BLOCKED" : null,
            unit_id: unit.unit_id,
            node: originOf(unit),
            source_uid: source.uid,
            join_status: packet.intelligence.join_status,
            variation_class: packet.spec.variation_class,
            fidelity_mode: packet.spec.fidelity_mode,
            packet: "packets/" + tag + ".json",
            chars: JSON.stringify(packet).length,
            pedagogy: packetHasPedagogy(packet),
          });
        } else {
          const key = loadKey();
          if (!key) throw new Error("no API key in kimi-api.txt");
          K.setKey(key);
          rows.push(await runOne(K, unit, source, science, spec, a));
        }
        n += 1;
        if (n >= limit) break;
      }
    }
    const c = census(science, junior);
    c.last_run = {
      cmd,
      attempted: rows.length,
      ok: rows.filter((r) => r.status === "ok" || r.status === "compiled").length,
      fail_closed: rows.filter((r) => r.status === "fail_closed").length,
      skip: rows.filter((r) => r.status === "skip").length,
      by_node: rows.reduce((acc, r) => {
        const k = r.node || "?";
        acc[k] = acc[k] || { attempted: 0, ok: 0, fail_closed: 0 };
        acc[k].attempted += 1;
        if (r.status === "ok" || r.status === "compiled") acc[k].ok += 1;
        if (r.status === "fail_closed") acc[k].fail_closed += 1;
        return acc;
      }, {}),
      rows,
    };
    writeJson(path.join(OUT, "status.json"), c);
    console.log(JSON.stringify(c.last_run, null, 2));
    return;
  }
  throw new Error("usage: modify_g68.js census|remaining|compile|generate|ingest [--unit ID] [--source UID] [--limit N] [--repeat N]");
}

module.exports = {
  loadKimi, compileUnit, pickSource, packetHasPedagogy, instructionFor,
  resultToCandidate, census, uncoveredUnits, deepenUnits, nextAttempt, maxAttempt,
  variationForAttempt, attemptFailed, hingeWantsFigure, pedagogy, hasPedagogy,
  sanitizeTikz, gateG9, gateG10, gateG11, gateG12, ingestGates, liveItemType, FORMAT_MAP, LIVE_ITEM_TYPES, compileBuildLogic,
  normalizeResultTables, grokCoveredUnits, remainingEligibleUnits, nextUniformUnits, chapterKey,
  OUT, ROOT,
};

if (require.main === module) {
  main().catch((e) => {
    console.error(e && e.stack || e);
    process.exit(1);
  });
}
