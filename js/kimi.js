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
{"pack":"igcse_9_10"|"senior_11_12_as_a"|"olympiad_iit"|null,
 "subject":"${subj}",
 "nodes":[],
 "families":[],
 "unit_id":null,
 "maps":["ncert","cambridge"],
 "related_lower_grain":false}
Rules:
- pack A = grades 9-10 / IGCSE; pack B = grades 11-12 / AS-A / senior; pack C = olympiad/IIT.
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

  function modifySys(subject) {
    const lab = subjectLabel(subject);
    return `You modify ONE existing multiple-choice ${lab} item from a teacher's instruction.
This is ISO-GEN on an existing item: the stem AND all four options must stay a coherent item after the change. Text-only items are in scope. If a figure exists and the change affects it, rewrite the TikZ too.
Return ONLY JSON:
{"stem":"...","options":{"A":"...","B":"...","C":"...","D":"..."},"correct":"A"|"B"|"C"|"D",
 "rationale":"one sentence","tikz":null,"tikz_unchanged":true,"note":null}
Laws:
- Honour the teacher's requested change (numbers, species, figure, mix-up, year group, wording).
- Always return a complete stem and complete A, B, C, D. Do not leave an old option that no longer matches the new stem.
- correct is the letter of the new right answer. Recalculate it; do not keep the old key if the item changed.
- If the teacher did not mention the figure and the change does not require it: tikz_unchanged true and tikz null.
- If the figure must change: tikz_unchanged false and tikz a complete tikzpicture source. Use circuitikz as tikzpicture (never nest circuitikz). Split a drawing and a pgfplots axis into two tikzpictures. No at=/anchor= on a split axis.
- If the item is text-only, keep tikz_unchanged true.
- If options are the figure itself (options_are_figure), rewrite TikZ so A–D still match; options text may stay A–D letters.
- Do not print SMILES, hinge ids, node codes, examiner comments, or mix-up labels on the learner item.
- Do not invent a published mark scheme. The correct letter is your authored key for this session.
- Keep the same language and exam register as the source item unless asked to change it.`;
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
    const subject = ctx.subject || "chemistry";
    const onTick = ctx.onTick;
    const slim = {
      teacher_prompt: prompt,
      subject,
      uid: item.uid || item.item_uid || null,
      stem: item.stem || item.stem_lead || "",
      options: item.options || {},
      statements: item.statements || [],
      equations: item.equations || [],
      tables: item.tables || [],
      options_are_figure: !!item.options_are_figure,
      has_figure: !!(item.tikz && String(item.tikz).trim()),
      tikz: item.tikz || "",
      tikz_packages: item.tikz_packages || [],
    };
    const content = await chat([
      { role: "system", content: modifySys(subject) },
      { role: "user", content: JSON.stringify(slim) },
    ], { reasoning_effort: "low", max_tokens: 4096, timeout_ms: 90000, onTick });
    const out = extractJson(content);
    const opts = out.options || {};
    const next = {
      stem: out.stem || slim.stem,
      options: {
        A: opts.A != null ? opts.A : (slim.options.A || ""),
        B: opts.B != null ? opts.B : (slim.options.B || ""),
        C: opts.C != null ? opts.C : (slim.options.C || ""),
        D: opts.D != null ? opts.D : (slim.options.D || ""),
      },
      correct: String(out.correct || "").trim().toUpperCase().slice(0, 1),
      rationale: out.rationale || "",
      note: out.note || null,
      tikz_unchanged: out.tikz_unchanged !== false && (out.tikz == null || out.tikz === ""),
    };
    if (!/^[A-D]$/.test(next.correct)) next.correct = item.correct || null;
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

  g.TTwinKimi = {
    getKey, setKey, getProxy, setProxy, endpoint, chat,
    inferSelector, inferIsoIntent, authorItem, modifyItem, inferKeys, gradePaper,
    lessonProse, mapJournalNote, extractJson, MODEL,
  };
})(window);
