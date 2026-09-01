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
    const key = getKey();
    if (!key) throw new Error("No AI API key. Open Settings and paste a key. It stays in this browser.");
    const url = endpoint();
    const body = Object.assign({
      model: MODEL,
      temperature: 1,
      messages,
    }, extra || {});
    const headers = { "Content-Type": "application/json" };
    if (url.endsWith("/kimi") || getProxy()) headers["X-Kimi-Key"] = key;
    else headers.Authorization = "Bearer " + key;
    const r = await fetch(url, { method: "POST", headers, body: JSON.stringify(body) });
    const txt = await r.text();
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

  const SELECTOR_SYS = `You are Kimi-k3, selector compiler for TeacherTwin NCERT chemistry RAG.
Return ONLY a JSON object. No prose.
The JSON schema:
{"pack":"igcse_9_10"|"senior_11_12_as_a"|null,
 "subject":"chemistry",
 "nodes":["chem:C6",...],
 "families":[],
 "unit_id":null,
 "maps":["ncert","cambridge"],
 "related_lower_grain":false}
Rules:
- pack A = grades 9-10 / IGCSE; pack B = grades 11-12 / AS-A / senior.
- nodes must be from the closed chem: list you are given.
- Do not emit question uids.
- Do not dump hinges or mx.
- Unknown topic → {"error":"unknown_phrase","ask":"..."}.
- Cross-hinge (acids AND equilibrium AND buffers) puts multiple nodes and families pH-buffer.
- A specific hinge id in the prompt goes in unit_id.`;

  async function inferSelector(prompt, nodes) {
    const list = (nodes || []).map((n) => n.id || n).join(", ");
    const content = await chat([
      { role: "system", content: SELECTOR_SYS },
      { role: "user", content: "Closed nodes: " + list + "\n\nTeacher prompt:\n" + prompt },
    ]);
    return extractJson(content);
  }

  const ISO_SCOPE_SYS = `A chemistry teacher described an idea for a new question. They do not know system ids, hinge codes, or node lists. Their language is often fuzzy.
Restate their intent in teacher language, then name the map nodes the idea belongs to.
Return ONLY JSON:
{"intent":"one sentence, teacher language",
 "grade":"SECONDARY"|"SENIOR_SECONDARY"|null,
 "nodes":["C6"],
 "ask":null}
Rules:
- nodes must be copied from the closed node list (id field only). 1–3 nodes.
- Prefer the most specific node (a hub over its parent origin when the idea is that hub).
- grade: SECONDARY = grades 9–10; SENIOR_SECONDARY = grades 11–12 / AS–A / senior / class 11 or 12. Infer from the idea's demand if they did not say a year group. If still unclear, null.
- If the idea is too vague to place: nodes [], ask one clarifying question in teacher language.
- Never put node ids, unit_ids, or file paths in intent or ask.`;

  const ISO_PICK_SYS = `You pick the ONE NCERT hinge a new question should test.
The teacher idea is already restated. The hinge list is already narrowed to that topic.
Return ONLY JSON:
{"primary":{"unit_id":"...","why":"one clause in teacher language"},
 "related":[{"unit_id":"...","why":"..."}],
 "ask":null}
Rules:
- unit_id must be copied from the supplied list. Do not invent ids.
- related: 0–2 extras only if the idea truly spans them.
- why is for the teacher: no unit_ids, no node codes.
- If none fit: primary null, ask one clarifying question in teacher language.`;

  function underNode(hNode, want) {
    const a = String(hNode || "").replace(/^chem:/, "");
    const b = String(want || "").replace(/^chem:/, "");
    if (!a || !b) return false;
    return a === b || a.startsWith(b + "/");
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

  async function inferIsoIntent(prompt, hinges, nodes, aliasHint) {
    const nodeList = (nodes || []).map((n) => ({
      id: String(n.id || n).replace(/^chem:/, ""),
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
      { role: "system", content: ISO_SCOPE_SYS },
      { role: "user", content: JSON.stringify({ teacher_idea: prompt, nodes: nodeList, chapters, alias_hint: hint }) },
    ]));
    const wantNodes = (scope.nodes || []).map((n) => String(n).replace(/^chem:/, "")).filter(Boolean);
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
      { role: "system", content: ISO_PICK_SYS },
      { role: "user", content: JSON.stringify({
        teacher_idea: prompt,
        intent: scope.intent,
        grade: scope.grade,
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

  const ISO_SYS = `You author ONE new multiple-choice chemistry item.
The teacher described an idea in ordinary language. You have already mapped that idea to a hinge pack (mechanism, decision hinge, CANDIDATE mx, enrichment).
Return ONLY JSON:
{"stem":"...","options":{"A":"...","B":"...","C":"...","D":"..."},"correct":"A"|"B"|"C"|"D",
 "rationale":"one sentence","mx_targeted":"confusion_type or null"}
Laws:
- Honour the teacher's framing (level, context, species) without leaving the hinge.
- The specification is the hinge pack. Do not invent a different mechanism.
- Do not copy enrichment verbatim as the stem.
- Distractors should be realizable wrong outputs, not "student is confused".
- Status of mx is CANDIDATE; do not stamp VALIDATED.
- Do not print SMILES, hinge ids, or node codes in the stem or options.
- No examiner comments.`;

  async function authorItem(pack, teacherIntent) {
    const st = pack.statement || {};
    const slim = {
      teacher_intent: teacherIntent || null,
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
      { role: "system", content: ISO_SYS },
      { role: "user", content: JSON.stringify(slim) },
    ]);
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

  const JOURNAL_SYS = `You map a teacher's note onto NCERT chemistry hinges.
Return ONLY JSON:
{"bindings":[{"unit_id":"science/grade_11/chem_ch_105/H009","node":"C6","why":"one short clause"}]}
Rules:
- unit_id must be copied from the supplied hinge list.
- 1 to 4 bindings. If none fit: {"bindings":[],"ask":"what topic or chapter?"}.
- Do not invent hinges. Do not dump mx or write a lesson.`;

  async function mapJournalNote(text, hinges) {
    const catalog = (hinges || []).slice(0, 523).map((h) => ({
      unit_id: h.unit_id,
      node: h.node,
      hinge: h.decision_hinge,
    }));
    const content = await chat([
      { role: "system", content: JOURNAL_SYS },
      { role: "user", content: JSON.stringify({ note: text, hinges: catalog }) },
    ]);
    return extractJson(content);
  }

  g.TTwinKimi = {
    getKey, setKey, getProxy, setProxy, endpoint, chat,
    inferSelector, inferIsoIntent, authorItem, lessonProse, mapJournalNote, extractJson, MODEL,
  };
})(window);
