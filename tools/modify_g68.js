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
    if (p.tikz) sc -= 4;
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
  s += "Do not print mix-up labels, hinge codes, node codes, or the word CANDIDATE.";
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
function compileUnit(K, unit, source, science, spec) {
  spec = spec || {};
  const p0 = pedagogy(source);
  const figureMode = spec.figureMode || (p0.tikz && spec.variation_class !== "V5" ? "remove" : "preserve");
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
  return K.assembleModifyPacket(source, instruction, ctx);
}
function resultToCandidate(result, packet, source, unit, attempt) {
  const typeMap = {
    single_mcq: "mcq",
    one_or_more: "mcq",
    three_statement: "three_statement",
    structured_parts: "structured",
    open_response: "open_response",
    option_table: "mcq_table",
    options_are_figure: "mcq_diagram",
  };
  const options = {};
  (result.options || []).forEach((o) => { if (o && o.id) options[o.id] = o.text || ""; });
  let key = null;
  if (result.answer && result.answer.kind === "letter_set") key = (result.answer.letters || []).join("");
  else if (result.answer && result.answer.letter) key = result.answer.letter;
  const uid = "candidate:g68:" + String(unit.unit_id).replace(/\//g, ":") + ":a" + attempt;
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
    item: {
      uid: uid,
      subject: "science",
      pack: "middle_6_8",
      node: unit.node,
      chapter_id: unit.chapter,
      chapter_label: unit.chapter_title || null,
      subtopic_id: unit.unit_id,
      stem: result.stem,
      item_type: typeMap[result.item_type] || "mcq",
      options: options,
      statements: result.statements || [],
      parts: result.parts || [],
      equations: result.equations || [],
      tables: result.tables || [],
      tikz: result.tikz || null,
      has_figure: !!(result.tikz && String(result.tikz).trim()),
      options_are_figure: result.item_type === "options_are_figure",
      complete_exam: false,
      serve_eligible: false,
      hinges: { primary: unit.unit_id, supporting: [], binder: { method: "modify_g68_named_gap" } },
      assessment: {
        key_source: "none",
        key_status: "available",
        mcq_key: key,
        proposed_key_status: "UNVERIFIED",
        examiner_comment: { present: false },
        one_or_more: result.item_type === "one_or_more",
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
  return {
    schema: "ttwin.g68_status.v1",
    science_units: (science.units || []).length,
    junior_live: junior.length,
    live_distinct_primaries: liveCovered.size,
    candidates: cand.size,
    uncovered: (science.units || []).length - liveCovered.size - cand.size,
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
  const cand = resultToCandidate(out, packet, source, unit, attempt);
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
      const spec = {};
      if (args.variation) spec.variation_class = args.variation;
      if (args["item-type"]) spec.target_item_type = args["item-type"];
      for (let a = 1; a <= repeat; a++) {
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
  throw new Error("usage: modify_g68.js census|compile|generate [--unit ID] [--source UID] [--limit N] [--repeat N]");
}

module.exports = {
  loadKimi, compileUnit, pickSource, packetHasPedagogy, instructionFor,
  resultToCandidate, census, uncoveredUnits, pedagogy, hasPedagogy, OUT, ROOT,
};

if (require.main === module) {
  main().catch((e) => {
    console.error(e && e.stack || e);
    process.exit(1);
  });
}
