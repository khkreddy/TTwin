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
    if (!key) throw new Error("No Kimi API key. Open Settings and paste a Moonshot key. The key stays in this browser.");
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
      throw new Error("Kimi response was not JSON (" + r.status + "). If this is GitHub Pages, set a local proxy in Settings (python3 tools/serve.py).");
    }
    if (!r.ok) throw new Error((data.error && (data.error.message || data.error)) || txt.slice(0, 240));
    const content = (((data.choices || [])[0] || {}).message || {}).content || "";
    if (!String(content).trim()) throw new Error("Empty Kimi response.");
    return content;
  }

  function extractJson(s) {
    const t = String(s || "").trim();
    const fence = t.match(/```(?:json)?\s*([\s\S]*?)```/);
    const raw = fence ? fence[1] : t;
    const start = raw.indexOf("{");
    const end = raw.lastIndexOf("}");
    if (start < 0 || end <= start) throw new Error("Kimi did not return JSON.");
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

  const ISO_SYS = `You are Kimi-k3, ISO-GEN author for TeacherTwin.
You receive hinge_pack JSON (mechanism, decision_hinge, mx CANDIDATE, enrichment).
Author ONE new multiple-choice item that tests the decision hinge.
Return ONLY JSON:
{"stem":"...","options":{"A":"...","B":"...","C":"...","D":"..."},"correct":"A"|"B"|"C"|"D",
 "rationale":"one sentence","mx_targeted":"confusion_type or null"}
Laws:
- Specification is the hinge pack. Do not invent a different mechanism.
- Do not copy enrichment verbatim as the stem.
- Distractors should be realizable wrong outputs, not "student is confused".
- Status of mx is CANDIDATE; do not stamp VALIDATED.
- No SMILES. No examiner comments.`;

  async function authorItem(pack) {
    const slim = {
      unit_id: pack.unit_id,
      decision_hinge: pack.statement && pack.statement.decision_hinge,
      mechanism: pack.statement && pack.statement.mechanism,
      mx: ((pack.statement && pack.statement.mx) || []).slice(0, 4),
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

  const LESSON_SYS = `You are Kimi-k3 writing a teacher lesson digest.
You receive a deterministic enrichment view (citations included).
Write 350-500 words for a teacher about to teach this topic.
Use only the supplied evidence. If a URL is null, do not invent a DOI.
Label CANDIDATE misconceptions as unverified.
Return plain prose, not JSON.`;

  async function lessonProse(digest) {
    return chat([
      { role: "system", content: LESSON_SYS },
      { role: "user", content: JSON.stringify(digest) },
    ]);
  }

  g.TTwinKimi = {
    getKey, setKey, getProxy, setProxy, endpoint, chat,
    inferSelector, authorItem, lessonProse, extractJson, MODEL,
  };
})(window);
