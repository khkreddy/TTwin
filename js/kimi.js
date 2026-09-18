(function (g) {
  const KEY = "ttwin.kimi.key";
  const PROXY = "ttwin.kimi.proxy";
  const MODEL = "kimi-k3";

  function getKey() { return localStorage.getItem(KEY) || ""; }
  function setKey(v) { if (v) localStorage.setItem(KEY, v); else localStorage.removeItem(KEY); }
  function getProxy() { return localStorage.getItem(PROXY) || ""; }
  function setProxy(v) { if (v) localStorage.setItem(PROXY, v.trim()); else localStorage.removeItem(PROXY); }

  function endpoint() {
    const p = getProxy();
    if (p) return p.replace(/\/$/, "");
    if (location.protocol === "http:" && location.hostname === "127.0.0.1") return "/kimi";
    return "https://api.moonshot.ai/v1/chat/completions";
  }

  async function chat(messages, extra) {
    extra = extra || {};
    const key = getKey();
    if (!key) throw new Error("No AI API key. Open Settings and paste a key. It stays in this browser.");
    const url = endpoint();
    const timeoutMs = extra.timeout_ms || 0;
    const onTick = extra.onTick;
    const bodyExtra = Object.assign({}, extra);
    delete bodyExtra.timeout_ms;
    delete bodyExtra.onTick;
    const body = Object.assign({
      model: MODEL,
      temperature: 1,
      messages,
    }, bodyExtra);
    const headers = { "Content-Type": "application/json" };
    if (url.endsWith("/kimi") || getProxy()) headers["X-Kimi-Key"] = key;
    else headers.Authorization = "Bearer " + key;
    const ctrl = new AbortController();
    const t0 = Date.now();
    let tickTimer = null;
    let abortTimer = null;
    if (onTick) {
      onTick(0);
      tickTimer = setInterval(() => onTick(Math.round((Date.now() - t0) / 1000)), 1000);
    }
    if (timeoutMs) abortTimer = setTimeout(() => ctrl.abort(), timeoutMs);
    let r, txt;
    try {
      r = await fetch(url, { method: "POST", headers, body: JSON.stringify(body), signal: ctrl.signal });
      txt = await r.text();
    } catch (e) {
      if (e && e.name === "AbortError") {
        throw new Error("AI timed out after " + Math.round((timeoutMs || 0) / 1000) + "s. Try a shorter prompt, or run python3 tools/serve.py and set the proxy.");
      }
      throw e;
    } finally {
      if (tickTimer) clearInterval(tickTimer);
      if (abortTimer) clearTimeout(abortTimer);
    }
    let data;
    try { data = JSON.parse(txt); } catch (e) {
      throw new Error("AI response was not JSON (" + r.status + "). If this is GitHub Pages, set a local proxy in Settings (python3 tools/serve.py).");
    }
    if (!r.ok) throw new Error((data.error && (data.error.message || data.error)) || txt.slice(0, 240));
    const content = (((data.choices || [])[0] || {}).message || {}).content || "";
    if (!String(content).trim()) throw new Error("Empty AI response.");
    return content;
  }

  function extractJson(s) {
    const t = String(s || "").trim();
    const fence = t.match(/```(?:json)?\s*([\s\S]*?)```/);
    const raw = fence ? fence[1] : t;
    const start = raw.indexOf("{");
    const end = raw.lastIndexOf("}");
    if (start < 0 || end <= start) throw new Error("AI did not return JSON.");
    return JSON.parse(raw.slice(start, end + 1));
  }

  function selectorSys(subject) {
    const subj = subject || "chemistry";
    return `You are Kimi-k3, selector compiler for TeacherTwin RAG.
Return ONLY a JSON object. No prose.
The JSON schema:
{"pack":"middle_6_8"|"secondary_9_10"|"senior_11_12"|"olympiad_iit"|null,
 "subject":"${subj}",
 "nodes":[],
 "families":[],
 "unit_id":null,
 "maps":["ncert","cambridge"],
 "related_lower_grain":false}
Rules:
- pack middle_6_8 = grades 6-8; secondary_9_10 = grades 9-10; senior_11_12 = grades 11-12; olympiad_iit = Olympiad/IIT practice. Origin of a question does not decide pack.
- subject is "${subj}". Do not switch subject.
- nodes must be from the closed list you are given.
- Do not emit question uids.
- Do not dump hinges or mx.
- Unknown topic → {"error":"unknown_phrase","ask":"..."}.
- A specific hinge id in the prompt goes in unit_id.`;
  }

  async function inferSelector(prompt, nodes, subject) {
    const list = (nodes || []).map((n) => n.id || n).join(", ");
    const content = await chat([
      { role: "system", content: selectorSys(subject) },
      { role: "user", content: "Closed nodes: " + list + "\n\nTeacher prompt:\n" + prompt },
    ]);
    return extractJson(content);
  }

  function subjectLabel(subject) {
    const s = String(subject || "chemistry").toLowerCase();
    return ({ chemistry: "chemistry", physics: "physics", biology: "biology", maths: "mathematics" })[s] || s;
  }
  function bareNode(n) {
    return String(n || "").replace(/^(chem|phy|bio|math):/, "");
  }
  function isoScopeSys(subject) {
    const lab = subjectLabel(subject);
    return `A ${lab} teacher described an idea for a new question. They do not know system ids, hinge codes, or node lists. Their language is often fuzzy.
Restate their intent in teacher language, then name the map nodes the idea belongs to.
Return ONLY JSON:
{"intent":"one sentence, teacher language",
 "grade":"SECONDARY"|"SENIOR_SECONDARY"|null,
 "nodes":[],
 "ask":null}
Rules:
- nodes must be copied from the closed node list (id field only). 1–3 nodes.
- Prefer the most specific node (a hub over its parent origin when the idea is that hub).
- grade: SECONDARY = grades 9–10; SENIOR_SECONDARY = grades 11–12 / AS–A / senior / class 11 or 12. Infer from the idea's demand if they did not say a year group. If still unclear, null.
- If the idea is too vague to place: nodes [], ask one clarifying question in teacher language.
- Never put node ids, unit_ids, or file paths in intent or ask.`;
  }
  function isoPickSys(interim) {
    const what = interim
      ? "ONE NCERT syllabus chapter a new question should sit in. This is a published chapter list, not a complete hinge map."
      : "ONE NCERT hinge a new question should test.";
    return `You pick the ${what}
The teacher idea is already restated. The list is already narrowed to that topic.
Return ONLY JSON:
{"primary":{"unit_id":"...","why":"one clause in teacher language"},
 "related":[{"unit_id":"...","why":"..."}],
 "ask":null}
Rules:
- unit_id must be copied from the supplied list. Do not invent ids.
- related: 0–2 extras only if the idea truly spans them.
- why is for the teacher: no unit_ids, no node codes.
- If none fit: primary null, ask one clarifying question in teacher language.`;
  }

  function underNode(hNode, want) {
    const a = bareNode(hNode);
    const b = bareNode(want);
    if (!a || !b) return false;
    return a === b || a.startsWith(b + "/") || b.startsWith(a + "/");
  }

  function slimMech(m) {
    if (!m) return null;
    if (typeof m === "string") return m;
    return {
      law: m.law || null,
      causal_direction: m.causal_direction || null,
      boundary_conditions: (m.boundary_conditions || []).slice(0, 4),
    };
  }

  async function inferIsoIntent(prompt, hinges, nodes, aliasHint, ctx) {
    ctx = ctx || {};
    const subject = ctx.subject || "chemistry";
    const interim = ctx.mapStatus === "syllabus_interim";
    const nodeList = (nodes || []).map((n) => ({
      id: bareNode(n.id || n),
      title: n.title || "",
      mechanism: n.mechanism || "",
    }));
    const chapters = Array.from(new Set(
      (hinges || []).map((h) => h.chapter_title).filter((t) => t && String(t).indexOf("science/") !== 0)
    )).sort();
    const hintNodes = (aliasHint && aliasHint.nodes) || [];
    const hint = aliasHint && (hintNodes.length || aliasHint.pack || aliasHint.grade_band)
      ? { nodes: hintNodes, pack: aliasHint.pack || null, grade_band: aliasHint.grade_band || null }
      : null;
    const scope = extractJson(await chat([
      { role: "system", content: isoScopeSys(subject) },
      { role: "user", content: JSON.stringify({ teacher_idea: prompt, subject, nodes: nodeList, chapters, alias_hint: hint }) },
    ]));
    const wantNodes = (scope.nodes || []).map((n) => bareNode(n)).filter(Boolean);
    if (scope.ask && !wantNodes.length) {
      return { intent: scope.intent || null, grade: scope.grade || null, primary: null, related: [], ask: scope.ask };
    }
    if (!wantNodes.length) {
      return {
        intent: scope.intent || prompt,
        grade: scope.grade || null,
        primary: null,
        related: [],
        ask: scope.ask || "Which topic is this, and what should the student have to decide?",
      };
    }
    let pool = (hinges || []).filter((h) => wantNodes.some((n) => underNode(h.node, n)));
    if (scope.grade) {
      const graded = pool.filter((h) => !h.grade_band || h.grade_band === scope.grade);
      if (graded.length) pool = graded;
    }
    if (!pool.length) {
      return {
        intent: scope.intent || prompt,
        grade: scope.grade || null,
        primary: null,
        related: [],
        ask: "I can see the topic but not a precise hinge. What must the student decide?",
      };
    }
    if (pool.length === 1) {
      return {
        intent: scope.intent || prompt,
        grade: scope.grade || pool[0].grade_band || null,
        primary: { unit_id: pool[0].unit_id, why: "this is the matching decision for that idea" },
        related: [],
        ask: null,
      };
    }
    const catalog = pool.map((h) => ({
      unit_id: h.unit_id,
      chapter: h.chapter_title || h.chapter,
      grade: h.grade_band === "SENIOR_SECONDARY" ? "grades 11-12" : "grades 9-10",
      hinge: h.decision_hinge,
    }));
    const pick = extractJson(await chat([
      { role: "system", content: isoPickSys(interim) },
      { role: "user", content: JSON.stringify({
        teacher_idea: prompt,
        intent: scope.intent,
        grade: scope.grade,
        subject,
        map_status: ctx.mapStatus || null,
        hinges: catalog,
      }) },
    ]));
    const allowed = new Set(pool.map((h) => h.unit_id));
    const primaryId = pick.primary && pick.primary.unit_id;
    if (!primaryId || !allowed.has(primaryId)) {
      return {
        intent: scope.intent || prompt,
        grade: scope.grade || null,
        primary: null,
        related: [],
        ask: pick.ask || "Which decision should the student make? Add a bit more about the situation.",
      };
    }
    const related = (pick.related || [])
      .filter((x) => x && allowed.has(x.unit_id) && x.unit_id !== primaryId)
      .slice(0, 2);
    return {
      intent: scope.intent || prompt,
      grade: scope.grade || null,
      primary: { unit_id: primaryId, why: pick.primary.why || null },
      related,
      ask: null,
    };
  }

  function isoAuthorSys(subject, interim) {
    const lab = subjectLabel(subject);
    const specLine = interim
      ? "The specification is the published NCERT chapter. Mx is empty; do not invent a mix-up ledger. Write realizable distractors from the chapter."
      : "The specification is the hinge pack. Do not invent a different mechanism. Status of mx is CANDIDATE; do not stamp VALIDATED.";
    return `You author ONE new multiple-choice ${lab} item.
The teacher described an idea in ordinary language. You have already mapped that idea to a curriculum unit.
Return ONLY JSON:
{"stem":"...","options":{"A":"...","B":"...","C":"...","D":"..."},"correct":"A"|"B"|"C"|"D",
 "rationale":"one sentence","mx_targeted":"confusion_type or null","tikz":null}
Laws:
- Honour the teacher's framing (level, context, quantities) without leaving the unit.
- ${specLine}
- Do not copy enrichment verbatim as the stem.
- Distractors should be realizable wrong outputs, not "student is confused".
- Do not print SMILES, hinge ids, or node codes in the stem or options.
- No examiner comments.
- tikz is null unless the item needs a simple TikZ figure. If present it must be a complete tikzpicture (circuitikz as tikzpicture plus the circuitikz package, never nested).`;
  }

  async function authorItem(pack, teacherIntent, ctx) {
    ctx = ctx || {};
    const st = pack.statement || {};
    const slim = {
      teacher_intent: teacherIntent || null,
      subject: ctx.subject || "chemistry",
      map_status: ctx.mapStatus || null,
      decision_hinge: st.decision_hinge,
      mechanism: slimMech(st.mechanism),
      chapter: st.chapter_title || st.chapter,
      grade: st.grade_band,
      mx: (st.mx || []).slice(0, 4).map((m) => ({
        type: m.type, cwo: m.cwo, status: m.status,
      })),
      enrichment: ((pack.enrichment && pack.enrichment.items) || []).slice(0, 3).map((e) => ({
        type: e.type, statement: e.statement,
      })),
    };
    const content = await chat([
      { role: "system", content: isoAuthorSys(ctx.subject, ctx.mapStatus === "syllabus_interim") },
      { role: "user", content: JSON.stringify(slim) },
    ], { reasoning_effort: "low", max_tokens: 4096, timeout_ms: 90000 });
    return extractJson(content);
  }

  function clip(s, n) {
    s = String(s == null ? "" : s);
    return s.length <= n ? s : s.slice(0, n);
  }
  function packedItemType(item) {
    if (item && item.options_are_figure) return "options_are_figure";
    const t = item && item.item_type;
    const key = item && item.assessment && item.assessment.mcq_key;
    const multi = (item && item.assessment && item.assessment.one_or_more) ||
      (typeof key === "string" && key.length > 1);
    if (t === "three_statement") return "three_statement";
    if (t === "structured") return "structured_parts";
    if (t === "open_response") return "open_response";
    if (t === "mcq_table") return "option_table";
    if (multi) return "one_or_more";
    return "single_mcq";
  }
  function sourceKey(item) {
    const a = item && item.assessment;
    const k = a && a.mcq_key;
    if (typeof k === "string" && k.length > 1) {
      return { kind: "letter_set", letters: k.split("").filter((c) => /[A-F]/.test(c)) };
    }
    if (typeof k === "string" && /^[A-F]$/.test(k)) return { kind: "single_letter", letter: k };
    return null;
  }
  function findMapUnit(map, unitId) {
    if (!unitId || !map) return null;
    const rows = Array.isArray(map) ? map : (map.units || map.items || []);
    for (let i = 0; i < rows.length; i++) {
      if (rows[i] && rows[i].unit_id === unitId) return rows[i];
    }
    return null;
  }
  function findMapNode(map, nodeId) {
    if (!nodeId || !map || Array.isArray(map)) return null;
    const rows = map.nodes || [];
    for (let i = 0; i < rows.length; i++) {
      if (rows[i] && rows[i].id === nodeId) return rows[i];
    }
    return null;
  }
  function nodeLabel(map, nodeId) {
    const n = findMapNode(map, nodeId);
    return (n && n.title) || "";
  }
  function sheafHomeOf(map, nodeId) {
    const n = findMapNode(map, nodeId);
    if (n && n.sheaf_home) return n.sheaf_home;
    const parent = nodeId && String(nodeId).split("/")[0];
    if (parent && parent !== nodeId) {
      const p = findMapNode(map, parent);
      if (p && p.sheaf_home) return p.sheaf_home;
    }
    return null;
  }
  function sheafFamily(sheaf) {
    const s = String(sheaf || "");
    if (s === "C2" || s.indexOf("C2") === 0) return ["C1", "C2", "C3", "C4", "C5"];
    if (s === "P1" || s.indexOf("P1") === 0) return ["P1"];
    if (s === "P2" || s.indexOf("P2") === 0) return ["P2"];
    if (s === "L1" || s.indexOf("L1") === 0) return ["L1", "Q1", "Q2", "Q3", "Q8"];
    if (s === "B5" || s.indexOf("B5") === 0) return ["B5", "B2", "B4"];
    if (s === "B3" || s.indexOf("B3") === 0) return ["B3", "Q8"];
    return s ? [s] : [];
  }
  function hasModifyBridge(item, sourceUnit, targetUnit, map) {
    if (!targetUnit) return true;
    if (sourceUnit && sourceUnit.unit_id === targetUnit.unit_id) return true;
    if (sourceUnit && sourceUnit.chapter && sourceUnit.chapter === targetUnit.chapter) return true;
    const srcNode = bareNode(item && item.node);
    const tgtNode = String(targetUnit.node || "");
    const tgtParent = String(targetUnit.node_parent || tgtNode.split("/")[0] || "");
    if (srcNode && tgtNode && (srcNode === tgtNode || srcNode === tgtParent)) return true;
    if (srcNode && tgtParent && srcNode.startsWith(tgtParent + "/")) return true;
    if (item && item.subject === "science" && sourceUnit && targetUnit
        && (sourceUnit.node === targetUnit.node || sourceUnit.node_parent === targetUnit.node_parent)) {
      return true;
    }
    const sheaf = sheafHomeOf(map, tgtNode) || sheafHomeOf(map, tgtParent);
    if (sheaf && srcNode) {
      const s = bareNode(srcNode);
      if (s === sheaf || s.startsWith(String(sheaf) + "/")) return true;
      const fam = sheafFamily(sheaf);
      for (let i = 0; i < fam.length; i++) {
        if (s === fam[i] || s.startsWith(fam[i] + "/")) return true;
      }
    }
    return false;
  }
  function compileModifyVariation(item, ctx, sourceUnit, targetUnit) {
    if (ctx.variation_class) return ctx.variation_class;
    const fig = ctx.figure || {};
    if (fig.mode === "rewrite") return "V5";
    if (targetUnit && sourceUnit && targetUnit.unit_id !== sourceUnit.unit_id) {
      const srcSub = (item && item.subject) || "";
      const tgtSub = targetUnit.subject || "";
      if (srcSub && tgtSub && srcSub !== tgtSub) return "V4";
      return "V3";
    }
    if (targetUnit && !sourceUnit) {
      const srcSub = (item && item.subject) || "";
      if (srcSub && srcSub !== (targetUnit.subject || "science")) return "V4";
      return "V3";
    }
    return "V1";
  }
  function compileModifyFidelity(item, ctx, sourceUnit, targetUnit, variation) {
    if (ctx.fidelity_mode) return ctx.fidelity_mode;
    if ((variation === "V3" || variation === "V4") && targetUnit
        && !hasModifyBridge(item, sourceUnit, targetUnit, ctx.map)) {
      return "BLOCKED";
    }
    return "FAITHFUL_TRANSFER";
  }
  function unitEnrichmentText(unit, ctx) {
    let enrichText = "";
    const serves = unit && unit.unit_id;
    (ctx.enrichment || []).forEach((e) => {
      const ids = e.serves || e.serves_statement_ids || [];
      if (serves && ids.indexOf(serves) >= 0 && e.statement) {
        enrichText += (enrichText ? " " : "") + e.statement;
      }
    });
    if (enrichText) return clip(enrichText, 1500);
    if (!unit) return null;
    const bits = [];
    const mech = unit.mechanism;
    if (mech && typeof mech === "string") bits.push(mech);
    if (mech && mech.law) bits.push(mech.law);
    if (mech && mech.causal_direction) bits.push(mech.causal_direction);
    const ped = unit.pedagogy || {};
    if (ped.mastery_signal) bits.push(ped.mastery_signal);
    if (ped.lok_folk) bits.push(ped.lok_folk);
    const joined = bits.filter(Boolean).join(" ");
    return joined ? clip(joined, 1500) : null;
  }
  function validPack(p) {
    return p === "middle_6_8" || p === "secondary_9_10" || p === "senior_11_12" || p === "olympiad_iit" ? p : null;
  }
  function assembleModifyPacket(item, instruction, ctx) {
    ctx = ctx || {};
    const itype = packedItemType(item);
    const primary = item && item.hinges && item.hinges.primary;
    const sourceUnit = findMapUnit(ctx.map, primary);
    const targetUnit = ctx.target_unit_id ? findMapUnit(ctx.map, ctx.target_unit_id) : null;
    const intelUnit = targetUnit || sourceUnit;
    const bound = !!(sourceUnit && sourceUnit.unit_id);
    const opts = item.options || {};
    const options = ["A", "B", "C", "D", "E", "F"].filter((k) => opts[k] != null && String(opts[k]).trim() !== "")
      .map((k) => ({ id: k, text: clip(opts[k], 1000) }));
    const statements = (item.statements || []).slice(0, 5).map((s, i) => ({
      id: String((s && s.n) || i + 1),
      text: clip((s && s.text) != null ? s.text : s, 1000),
    }));
    const parts = (item.parts || []).slice(0, 8).map((p, i) => ({
      id: String((p && p.id) || i + 1),
      text: clip((p && p.stem) || "", 2000),
      marks: typeof (p && p.marks) === "number" ? p.marks : 0,
    }));
    const mxRows = ((intelUnit && intelUnit.mx) || []).slice(0, 4).map((m) => ({
      mx_type: clip(m.type || m.mx_type, 60),
      name: clip(m.name || m.type || m.mx_type || "", 120),
      teacher_note: clip(m.cwo || m.canonical_wrong_output || m.note || "", 300),
    }));
    const lbs = item.assessment && item.assessment.learn_by_solve;
    let lbsRecipe = null;
    if (lbs && lbs.wrong) {
      const gates = Object.keys(lbs.wrong).slice(0, 6).map((L) => {
        const rec = lbs.wrong[L] || {};
        return clip((rec.mx_type || rec.pathway || L), 120);
      });
      lbsRecipe = {
        unit: clip((intelUnit && intelUnit.unit_id) || primary || "", 120),
        gate_names: gates,
        hint_skeleton: clip("", 500),
        retry_plan: "retry original unaided",
      };
    }
    const seeds = ((item.assessment && item.assessment.modify_seeds) || []).slice(0, 4)
      .map((s) => clip(typeof s === "string" ? s : (s && (s.text || s.instruction)) || "", 500))
      .filter(Boolean);
    const variation = compileModifyVariation(item, ctx, sourceUnit, targetUnit);
    const fidelity = compileModifyFidelity(item, ctx, sourceUnit, targetUnit, variation);
    const fig = ctx.figure || {};
    const figMode = fig.mode || "preserve";
    const labels = [];
    if (intelUnit) {
      const t1 = nodeLabel(ctx.map, intelUnit.node);
      const t2 = nodeLabel(ctx.map, intelUnit.node_parent || (intelUnit.node && String(intelUnit.node).split("/")[0]));
      if (t1) labels.push(clip(t1, 120));
      if (t2 && t2 !== t1) labels.push(clip(t2, 120));
    }
    const hingeUnit = bound ? (intelUnit || sourceUnit) : null;
    const pack = validPack(ctx.pack) || validPack(item && item.pack) || "secondary_9_10";
    const subject = (ctx.subject || (item && item.subject) || "").slice(0, 40) || "science";
    const topic = (intelUnit && (nodeLabel(ctx.map, intelUnit.node) || intelUnit.chapter_title)) || "";
    const level = intelUnit && intelUnit.grade != null ? ("grade " + intelUnit.grade) : (intelUnit && intelUnit.grade_band) || "";
    const srcTikz = clip(Array.isArray(item.tikz) ? item.tikz.join("\n") : (item.tikz || ""), 6000);
    const packet = {
      schema: "modify_packet.v1",
      packet_id: "session:" + (item.uid || item.item_uid || "item"),
      slot: "T-MOD",
      created_at: new Date().toISOString(),
      source: {
        item_ref: "session:" + (item.uid || item.item_uid || "item"),
        item_type: itype,
        stem: clip(item.stem || item.stem_lead || "", 4000),
        options: options,
        statements: statements,
        parts: parts,
        equations: (item.equations || []).slice(0, 6).map((e) => clip(typeof e === "string" ? e : JSON.stringify(e), 1000)),
        tables: (item.tables || []).slice(0, 6).map((t) => clip(JSON.stringify(t), 1000)),
        tikz: srcTikz,
        key: sourceKey(item),
      },
      intelligence: {
        join_status: bound ? "BOUND" : "UNBOUND",
        hinge: hingeUnit ? {
          primary: clip(hingeUnit.unit_id || primary || "", 120),
          unit_id: clip(hingeUnit.unit_id || "", 120),
          title: clip(hingeUnit.decision_hinge || hingeUnit.chapter_title || hingeUnit.chapter || "", 240),
          node_labels: labels.slice(0, 8),
        } : null,
        packed_tags: {
          pack: pack,
          subject: subject,
          level: clip(level, 40),
          topic: clip(topic, 120),
          paper_hint: clip(ctx.paper_hint || "", 60),
        },
        mx: mxRows,
        enrichment: unitEnrichmentText(intelUnit, ctx),
        lbs_recipe: lbsRecipe,
        modify_seeds: seeds,
      },
      spec: {
        instruction: clip(instruction || "", 1000),
        variation_class: variation,
        fidelity_mode: fidelity,
        target_item_type: ctx.target_item_type || "preserve",
        format: { n_options: Math.max(2, Math.min(6, options.length || 4)) },
        figure: { mode: figMode, tikz_required: !!fig.tikz_required },
      },
      caps: { hard_total_chars: 16000, tightened_from: "40_PACKETS" },
      assembly: {
        builder: "assembleModifyPacket",
        trimmed: [],
        slim_map_ref: clip(ctx.slim_map_ref || "S.map", 80),
      },
    };
    const order = ["enrichment", "lbs_recipe", "mx_notes", "node_labels", "enrichment_drop"];
    while (JSON.stringify(packet).length > 16000 && order.length) {
      const step = order.shift();
      packet.assembly.trimmed.push(step);
      if (step === "enrichment") {
        packet.intelligence.enrichment = packet.intelligence.enrichment
          ? clip(packet.intelligence.enrichment, 400) : null;
      } else if (step === "lbs_recipe") {
        packet.intelligence.lbs_recipe = null;
      } else if (step === "mx_notes") {
        packet.intelligence.mx = (packet.intelligence.mx || []).map((m) => ({
          mx_type: m.mx_type, name: m.name,
        }));
      } else if (step === "node_labels" && packet.intelligence.hinge) {
        packet.intelligence.hinge.node_labels = [];
      } else if (step === "enrichment_drop") {
        packet.intelligence.enrichment = null;
      }
    }
    return packet;
  }
  function modifySys() {
    return `You design ONE replacement exam item inside the compiled modify_packet.v1 bundle. Specification exists before the item. You do not free-write.
Return ONLY modify_result.v1 JSON:
{"status":"OK"|"REFUSED","refusal_reason":null,"item_type":"...","stem":"...","options":[{"id":"A","text":"..."}],"statements":[],"parts":[],"equations":[],"tables":[],"tikz":null,"answer":{"kind":"single_letter"|"letter_set"|"statement_pattern"|"part_answers"|"rubric","letter":"A","letters":null},"teacher":{"proposed_key_status":"UNVERIFIED","key_rationale":"...","variation_applied":"V1","fidelity_selfcheck":"FAITHFUL_TRANSFER","mx_links":[],"figure_note":null}}
Laws:
- Honor spec.instruction, spec.variation_class, spec.fidelity_mode, spec.target_item_type, spec.figure.
- If target_item_type is preserve, keep source.item_type.
- Do not coerce to four-option MCQ. one_or_more uses answer.letters (e.g. ["B","C"]). structured_parts uses parts[]. open_response uses rubric kind, no letter.
- Recalculate the key. Do not copy source.key unless the change cannot affect it.
- Learner fields (stem, options, statements, parts, tables, tikz) must not contain mx_type names, mix-up labels, examiner comments, SMILES strings, hinge ids, node codes, or the word CANDIDATE.
- If intelligence.join_status is UNBOUND, teacher block must not name a map title or hinge.
- TikZ: at most one visual. Rewrite only if spec.figure.mode is rewrite or add. Never invent a figure when source has none unless mode is add and you supply complete tikzpicture. Use circuitikz as tikzpicture (never nest). Split drawing and pgfplots axis into two tikzpictures if needed.
- If you cannot meet the spec: status REFUSED and a refusal_reason. Do not drift.
- Public copy is an exam item, not a published mark scheme. Keep the source language and register unless asked to change it.`;
  }
  function bannedInLearner(text, packet) {
    const blob = String(text || "").toLowerCase();
    if (/\bcandidate\b/.test(blob)) return "CANDIDATE";
    if (/\b(kimi|moonshot|openai|anthropic|chatgpt|claude|astra)\b/.test(blob)) return "vendor";
    const mx = (packet.intelligence && packet.intelligence.mx) || [];
    for (let i = 0; i < mx.length; i++) {
      const t = mx[i] && mx[i].mx_type;
      const n = mx[i] && mx[i].name;
      if (t && t.length > 3 && blob.indexOf(String(t).toLowerCase()) >= 0) return "mx_type";
      if (n && n.length > 6 && blob.indexOf(String(n).toLowerCase()) >= 0) return "mx_name";
    }
    if (/smiles\s*[:=]/i.test(blob) || /\bSMILES\b/.test(String(text || ""))) return "SMILES";
    return null;
  }
  function learnerBlob(out) {
    const opts = (out.options || []).map((o) => (o && (o.text || "")) + " " + ((o && o.tikz) || ""));
    const parts = (out.parts || []).map((p) => (p && p.text) || "");
    const stmts = (out.statements || []).map((s) => (s && s.text) || "");
    return [out.stem, opts.join("\n"), parts.join("\n"), stmts.join("\n"),
      (out.tables || []).join("\n"), out.tikz || ""].join("\n");
  }
  function optionIds(out) {
    return (out.options || []).map((o) => o && o.id).filter(Boolean);
  }
  function isBlankGridTable(t) {
    const s = typeof t === "string" ? t : JSON.stringify(t || "");
    if (!/<table/i.test(s)) return false;
    const cells = s.match(/<t[dh]\b[^>]*>[\s\S]*?<\/t[dh]>/gi) || [];
    if (cells.length < 8) return false;
    let empty = 0;
    for (let i = 0; i < cells.length; i++) {
      const inner = cells[i].replace(/<[^>]+>/g, "").replace(/&nbsp;/g, " ").trim();
      if (inner.length <= 1) empty++;
    }
    return empty / cells.length > 0.7;
  }
  function mentionsFigure(text) {
    return /figure|diagram|shown above|shown below|as shown|the graph|the circuit|the apparatus/i.test(String(text || ""));
  }
  function joinCodeHit(text) {
    const s = String(text || "");
    return /science\/grade_\d+|IGCSE:|AS_A:|[SPCBMLQ]\d+\/H-[A-Z0-9-]+|\b(?:chem|phy|bio|math):[A-Z]/.test(s);
  }
  function validateModifyResult(out, packet, item) {
    if (!out) return { ok: false, gate: "G1" };
    if (out.status === "REFUSED") {
      return { ok: false, gate: out.refusal_reason ? "REFUSED" : "G1" };
    }
    if (out.status !== "OK") return { ok: false, gate: "G1" };
    if (!out.item_type || !out.stem || !out.answer || !out.teacher) return { ok: false, gate: "G1" };
    if (out.schema && out.schema !== "modify_result.v1") return { ok: false, gate: "G1" };
    if (out.teacher.proposed_key_status && out.teacher.proposed_key_status !== "UNVERIFIED") {
      return { ok: false, gate: "G1" };
    }
    const want = (packet.spec && packet.spec.target_item_type) || "preserve";
    const preserved = (packet.source && packet.source.item_type) || packedItemType(item);
    const itype = out.item_type;
    if (want === "preserve") {
      if (itype !== preserved) return { ok: false, gate: "G2" };
    } else if (itype !== want) {
      return { ok: false, gate: "G2" };
    }
    const ids = optionIds(out);
    const ans = out.answer || {};
    if (itype === "single_mcq") {
      if (ans.kind !== "single_letter" || !ans.letter || ids.indexOf(ans.letter) < 0) return { ok: false, gate: "G2" };
      if (ids.filter((x) => x === ans.letter).length !== 1) return { ok: false, gate: "G2" };
    }
    if (itype === "one_or_more") {
      const L = ans.letters || [];
      const uniq = [];
      for (let i = 0; i < L.length; i++) if (uniq.indexOf(L[i]) < 0) uniq.push(L[i]);
      if (ans.kind !== "letter_set" || uniq.length < 2) return { ok: false, gate: "G2" };
      for (let i = 0; i < uniq.length; i++) if (ids.indexOf(uniq[i]) < 0) return { ok: false, gate: "G2" };
    }
    if (itype === "three_statement") {
      const stmts = out.statements || [];
      if (stmts.length < 2) return { ok: false, gate: "G2" };
      if (ans.kind === "statement_pattern") {
        if (!ans.pattern || ans.pattern.length !== stmts.length) return { ok: false, gate: "G2" };
      } else if (ans.kind === "single_letter") {
        if (!ans.letter || ids.indexOf(ans.letter) < 0) return { ok: false, gate: "G2" };
      } else {
        return { ok: false, gate: "G2" };
      }
    }
    if (itype === "structured_parts") {
      const parts = out.parts || [];
      const pa = ans.part_answers || [];
      if (!parts.length || ans.kind !== "part_answers") return { ok: false, gate: "G2" };
      for (let i = 0; i < parts.length; i++) {
        const pid = parts[i] && parts[i].id;
        const hit = pa.filter((x) => x && x.part_id === pid && String(x.answer || "").trim());
        if (!hit.length) return { ok: false, gate: "G2" };
        const mk = parts[i].marks;
        if (mk != null && (mk < 0 || mk > 20 || mk !== Math.floor(mk))) return { ok: false, gate: "G2" };
      }
    }
    if (itype === "open_response") {
      if (ans.kind !== "rubric" || !ans.rubric || !ans.rubric.length) return { ok: false, gate: "G2" };
      if (ans.letter || (ans.letters && ans.letters.length)) return { ok: false, gate: "G2" };
    }
    if (itype === "option_table" || itype === "options_are_figure") {
      if (!ids.length) return { ok: false, gate: "G2" };
      if (itype === "options_are_figure") {
        const withFig = (out.options || []).filter((o) => o && o.tikz);
        if (!withFig.length && !out.tikz) return { ok: false, gate: "G2" };
      }
    }
    const figMode = (packet.spec && packet.spec.figure && packet.spec.figure.mode) || "preserve";
    const srcTikz = (packet.source && packet.source.tikz) || "";
    const outTikz = out.tikz || "";
    const hasTikz = String(outTikz).trim() !== "";
    const learnerFig = mentionsFigure(out.stem) || (out.parts || []).some((p) => mentionsFigure(p && p.text));
    if (hasTikz !== learnerFig) return { ok: false, gate: "G3" };
    const nVisual = (hasTikz ? 1 : 0) + (out.options || []).filter((o) => o && o.tikz).length;
    if (nVisual > 1) return { ok: false, gate: "G3" };
    if ((out.tables || []).some(isBlankGridTable) && hasTikz) return { ok: false, gate: "G3" };
    if (!String(srcTikz).trim() && figMode !== "add" && hasTikz) return { ok: false, gate: "G3" };
    if (figMode === "remove" && hasTikz) return { ok: false, gate: "G3" };
    const learner = learnerBlob(out);
    const ban = bannedInLearner(learner, packet);
    if (ban) return { ok: false, gate: "G4" };
    const dumped = JSON.stringify(out);
    if (/exam\.v1/.test(dumped)) return { ok: false, gate: "G5" };
    if (out.uid && !/^session:|^candidate:/.test(String(out.uid))) return { ok: false, gate: "G5" };
    if (ans.kind === "single_letter") {
      if (!ans.letter || ids.indexOf(ans.letter) < 0) return { ok: false, gate: "G6" };
    }
    if (ans.kind === "letter_set") {
      const L = ans.letters || [];
      const seen = {};
      for (let i = 0; i < L.length; i++) {
        if (seen[L[i]] || ids.indexOf(L[i]) < 0) return { ok: false, gate: "G6" };
        seen[L[i]] = true;
      }
    }
    if (ans.kind === "statement_pattern") {
      if (!ans.pattern || ans.pattern.length !== (out.statements || []).length) return { ok: false, gate: "G6" };
    }
    const applied = out.teacher && out.teacher.variation_applied;
    if (applied !== (packet.spec && packet.spec.variation_class)) return { ok: false, gate: "G7" };
    const join = packet.intelligence && packet.intelligence.join_status;
    if (joinCodeHit(learner)) return { ok: false, gate: "G8" };
    if (join === "UNBOUND") {
      const teach = JSON.stringify(out.teacher || "");
      if (joinCodeHit(teach)) return { ok: false, gate: "G8" };
      const title = packet.intelligence.hinge && packet.intelligence.hinge.title;
      if (title && teach.toLowerCase().indexOf(String(title).toLowerCase()) >= 0) return { ok: false, gate: "G8" };
    }
    return { ok: true };
  }
  function applyModifyOutcome(out, packet, item) {
    if (!out) return { ok: false, gate: "G1", keepOriginal: true };
    if (packet && packet.spec && packet.spec.fidelity_mode === "BLOCKED") {
      return { ok: false, gate: "BLOCKED", keepOriginal: true };
    }
    const gate = validateModifyResult(out, packet, item);
    if (!gate.ok) return { ok: false, gate: gate.gate, keepOriginal: true };
    return { ok: true, gate: null, keepOriginal: false };
  }

  function inferPkgs(code, prev) {
    const pkgs = {};
    (prev || []).forEach((p) => { if (p) pkgs[p] = true; });
    const t = String(code || "");
    if (/circuitikz/.test(t) || /to\[/.test(t)) pkgs.circuitikz = true;
    if (/\\begin\{axis\}/.test(t) || /pgfplots/.test(t)) pkgs.pgfplots = true;
    if (/chemfig/.test(t)) pkgs.chemfig = true;
    const out = Object.keys(pkgs);
    if (out.indexOf("tikz") < 0) out.unshift("tikz");
    return out;
  }

  async function modifyItem(item, prompt, ctx) {
    ctx = ctx || {};
    const onTick = ctx.onTick;
    const packet = assembleModifyPacket(item, prompt, ctx);
    if (packet.spec.fidelity_mode === "BLOCKED") {
      const err = new Error("Modify blocked (no bridge). Original item kept.");
      err.gate = "BLOCKED";
      err.keepOriginal = true;
      err.packet = packet;
      throw err;
    }
    const content = await chat([
      { role: "system", content: modifySys() },
      { role: "user", content: JSON.stringify(packet) },
    ], { reasoning_effort: "low", max_tokens: 4096, timeout_ms: 90000, onTick });
    const out = extractJson(content);
    const gate = applyModifyOutcome(out, packet, item);
    if (!gate.ok) {
      const err = new Error("Modify refused (" + gate.gate + "). Original item kept.");
      err.gate = gate.gate;
      err.keepOriginal = true;
      err.packet = packet;
      err.result = out;
      throw err;
    }
    const optList = out.options || [];
    const options = {};
    optList.forEach((o) => { if (o && o.id) options[o.id] = o.text || ""; });
    const mcqLike = out.item_type === "single_mcq" || out.item_type === "one_or_more"
      || out.item_type === "option_table" || out.item_type === "options_are_figure"
      || out.item_type === "three_statement";
    if (!optList.length && mcqLike) {
      const src = item.options || {};
      ["A", "B", "C", "D"].forEach((k) => { if (src[k] != null) options[k] = src[k]; });
    }
    let correct = null;
    if (out.answer && out.answer.kind === "letter_set" && Array.isArray(out.answer.letters)) {
      correct = out.answer.letters.join("");
    } else if (out.answer && out.answer.letter) {
      correct = String(out.answer.letter).trim().toUpperCase().slice(0, 1);
    }
    const tikzUnchanged = out.tikz == null || out.tikz === "" || out.tikz === (item.tikz || "");
    const next = {
      stem: out.stem || item.stem,
      options: options,
      statements: out.statements || item.statements,
      parts: out.parts || item.parts,
      correct: correct,
      rationale: (out.teacher && out.teacher.key_rationale) || "",
      note: (out.teacher && out.teacher.figure_note) || null,
      item_type: out.item_type || item.item_type,
      join_status: packet.intelligence.join_status,
      tikz_unchanged: tikzUnchanged,
      packet: packet,
      result: out,
      serve_eligible: false,
      key_status: "UNVERIFIED",
    };
    if (next.tikz_unchanged) {
      next.tikz = item.tikz || "";
      next.tikz_packages = item.tikz_packages || [];
    } else {
      next.tikz = out.tikz || "";
      next.tikz_packages = inferPkgs(next.tikz, item.tikz_packages);
    }
    return next;
  }

  function keysSys(subject) {
    const lab = subjectLabel(subject);
    return `You infer the most likely correct letter for each ${lab} multiple-choice item.
These are demonstration exam-style items. There is NO published mark scheme in the payload. Say so in honesty.
Return ONLY JSON:
{"honesty":"not a published mark scheme",
 "keys":[{"uid":"...","correct":"A"|"B"|"C"|"D","confidence":"high"|"medium"|"low","why":"one clause"}]}
Rules:
- uid must be copied from the list.
- correct is your best letter. If you cannot tell, still pick and set confidence low.
- Do not invent extra items. Do not print stems.`;
  }

  async function inferKeys(items, ctx) {
    ctx = ctx || {};
    const payload = {
      subject: ctx.subject || "chemistry",
      items: (items || []).map((it) => ({
        uid: it.uid || it.item_uid,
        stem: String(it.stem || it.stem_lead || "").slice(0, 800),
        options: it.options || {},
        options_are_figure: !!it.options_are_figure,
      })),
    };
    const content = await chat([
      { role: "system", content: keysSys(ctx.subject) },
      { role: "user", content: JSON.stringify(payload) },
    ], { reasoning_effort: "low", max_tokens: 4096, timeout_ms: 90000, onTick: ctx.onTick });
    return extractJson(content);
  }

  function gradeSys(subject) {
    const lab = subjectLabel(subject);
    return `You write short feedback for a ${lab} student who just sat a multiple-choice paper.
Return ONLY JSON:
{"overall":"one short paragraph to the student",
 "per_item":[{"uid":"...","verdict":"right"|"wrong"|"blank","why":"one clause","teach":"one clause"}],
 "next_steps":["concrete action 1","concrete action 2","concrete action 3"]}
Rules:
- Speak to the student, not the teacher.
- Use only the supplied stems, options, keys, and chosen letters. Do not invent a syllabus anecdote.
- For wrong answers, say what the chosen option would mean and what the key decides instead.
- For right answers, one short confirmation or skip with empty teach.
- next_steps: 2–4 actions the student can do today.
- Do not name models, files, or internal ids other than question numbers if helpful.
- Keys may be AI-inferred, not a published mark scheme; do not claim official marks.`;
  }

  async function gradePaper(items, responses, score, ctx) {
    ctx = ctx || {};
    const payload = {
      subject: ctx.subject || "chemistry",
      honesty: score && score.honesty,
      score: score && { n: score.n, right: score.right, blank: score.blank, nokey: score.nokey },
      items: (items || []).map((it, i) => ({
        n: i + 1,
        uid: it.uid || it.item_uid,
        stem: String(it.stem || it.stem_lead || "").slice(0, 500),
        options: it.options || {},
        correct: it.correct || null,
        chosen: (responses && responses[it.uid || it.item_uid]) || null,
      })),
    };
    const content = await chat([
      { role: "system", content: gradeSys(ctx.subject) },
      { role: "user", content: JSON.stringify(payload) },
    ], { reasoning_effort: "low", max_tokens: 4096, timeout_ms: 90000, onTick: ctx.onTick });
    return extractJson(content);
  }

  const LESSON_SYS = `You write a teacher briefing in the manner of William Zinsser (On Writing Well).
Short sentences. Concrete verbs. No clutter, no throat-clearing, no jargon for its own sake.
The reader is a chemistry teacher with twenty minutes before class.
Return plain prose, not JSON.

You receive three packs. Use all of them that are present:
1. map — NCERT hinges (decision, mechanism, CANDIDATE mx).
2. enrichment — classroom evidence with citations.
3. teacher_overlay — this teacher's own journal notes already mapped to those hinges.

Order:
1. What the student must decide (the hinge). One short paragraph.
2. Where they usually go wrong. Only from supplied mx. Mark CANDIDATE as unverified.
3. What to do in class today. Three to six numbered actions.
4. What to leave out.

Rules:
- Use only the supplied packs. Do not invent facts, hinges, or citations.
- If a citation URL is null, do not invent a DOI or link.
- Weave overlay notes in as the teacher's prior, not as published evidence.
- Do not name models, file paths, or internal ids except hinge unit_id if it helps the teacher find the topic.
- 350–500 words.`;

  async function lessonProse(digest) {
    return chat([
      { role: "system", content: LESSON_SYS },
      { role: "user", content: JSON.stringify(digest) },
    ]);
  }

  function journalSys(subject, interim) {
    const lab = subjectLabel(subject);
    const unit = interim ? "NCERT syllabus chapters" : "NCERT hinges";
    return `You map a teacher's note onto ${lab} ${unit}.
Return ONLY JSON:
{"bindings":[{"unit_id":"...","node":"...","why":"one short clause"}]}
Rules:
- unit_id must be copied from the supplied list.
- 1 to 4 bindings. If none fit: {"bindings":[],"ask":"what topic or chapter?"}.
- Do not invent units. Do not dump mx or write a lesson.`;
  }

  async function mapJournalNote(text, hinges, ctx) {
    ctx = ctx || {};
    const catalog = (hinges || []).slice(0, 523).map((h) => ({
      unit_id: h.unit_id,
      node: h.node || h.node_id,
      hinge: h.decision_hinge,
      chapter: h.chapter_title || h.chapter,
    }));
    const content = await chat([
      { role: "system", content: journalSys(ctx.subject, ctx.mapStatus === "syllabus_interim") },
      { role: "user", content: JSON.stringify({ note: text, hinges: catalog }) },
    ]);
    return extractJson(content);
  }

  function analyzeSys(subject) {
    const lab = subjectLabel(subject);
    return `You write a teacher answer-key analysis for ${lab} multiple-choice items.
There is NO published mark scheme. Say so in honesty.
Return ONLY JSON:
{"items":[{"item_uid":"...","correct":"A"|"B"|"C"|"D",
  "rationale":"one short paragraph for the key",
  "map":{"unit_ids":[],"nodes":[],"chapter_title":null,"decision":"one clause"},
  "options":{
    "A":{"role":"key"|"distractor","why":"one clause","mx":[{"type":null,"cwo":null}],"enrichment":[{"item_id":null,"statement":null}]},
    "B":{"role":"key"|"distractor","why":"one clause","mx":[],"enrichment":[]},
    "C":{"role":"key"|"distractor","why":"one clause","mx":[],"enrichment":[]},
    "D":{"role":"key"|"distractor","why":"one clause","mx":[],"enrichment":[]}
  }}]}
Laws:
- item_uid must be copied from the payload.
- correct is your best letter. Recalculate from stem and options.
- Map unit_ids and nodes must be copied from the supplied map slice. Do not invent ids.
- Mix-up (mx) rows must be copied from the supplied mx list (type + cwo). Status is CANDIDATE / unverified. If none fit, mx [].
- Enrichment statements must be copied from the supplied enrichment. If none fit, enrichment [].
- Do not dump the map. Do not write examiner comments onto a learner stem.
- honesty is always: not a published mark scheme.`;
  }

  async function analyzeSolutions(items, slices, ctx) {
    ctx = ctx || {};
    const payload = {
      subject: ctx.subject || "chemistry",
      map_status: ctx.mapStatus || null,
      honesty: "not a published mark scheme",
      items: (items || []).map((it) => {
        const uid = it.uid || it.item_uid;
        const sl = (slices && slices[uid]) || {};
        const tab = ((it.tables || []).find((t) => t && t.is_option_table)) || null;
        return {
          item_uid: uid,
          stem: String(it.stem || it.stem_lead || "").slice(0, 900),
          options: it.options || {},
          option_table: tab ? { headers: tab.headers || [], rows: tab.rows || [], caption: tab.caption || "" } : null,
          node: it.node || null,
          chapter_label: it.chapter_label || null,
          map: sl.units || [],
          mx: sl.mx || [],
          enrichment: sl.enrichment || [],
        };
      }),
    };
    const content = await chat([
      { role: "system", content: analyzeSys(ctx.subject) },
      { role: "user", content: JSON.stringify(payload) },
    ], { reasoning_effort: "low", max_tokens: 4096, timeout_ms: 90000, onTick: ctx.onTick });
    const out = extractJson(content);
    return out.items || [];
  }

  g.TTwinKimi = {
    getKey, setKey, getProxy, setProxy, endpoint, chat,
    inferSelector, inferIsoIntent, authorItem, modifyItem, assembleModifyPacket, inferKeys, gradePaper,
    analyzeSolutions, lessonProse, mapJournalNote, extractJson, MODEL,
    validateModifyResult, applyModifyOutcome, findMapUnit, hasModifyBridge,
  };
})(window);
