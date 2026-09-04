/* Solution-analysis sub-layer of the question bank.
   First write is an LLM analysis keyed by item_uid + item_sha256.
   Later assemblies retrieve it deterministically. Not printed on the learner paper. */
(function (g) {
  const PACK = "data/solutions/index.json";
  const LOCAL_KEY = "ttwin.solutions.v1";
  const S = { packed: {}, local: {}, booted: false };

  function loadLocal() {
    try { return JSON.parse(localStorage.getItem(LOCAL_KEY) || "{}"); }
    catch (e) { return {}; }
  }
  function saveLocal() {
    try { localStorage.setItem(LOCAL_KEY, JSON.stringify(S.local)); }
    catch (e) { /* quota */ }
  }
  async function boot() {
    if (S.booted) return S;
    S.local = loadLocal();
    try {
      const r = await fetch(PACK);
      if (r.ok) {
        const doc = await r.json();
        S.packed = (doc && doc.by_uid) || {};
      }
    } catch (e) { S.packed = {}; }
    S.booted = true;
    return S;
  }
  function canonical(item) {
    const tab = ((item && item.tables) || []).find((t) => t && t.is_option_table) || null;
    return JSON.stringify({
      stem: item && (item.stem || item.stem_lead) || "",
      options: (item && item.options) || {},
      table: tab ? { headers: tab.headers || [], rows: tab.rows || [], row_labels: tab.row_labels || [] } : null,
    });
  }
  async function fingerprint(item) {
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonical(item)));
    return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
  }
  function pick(store, uid, sha) {
    const rec = store && store[uid];
    if (!rec) return null;
    if (sha && rec.item_sha256 && rec.item_sha256 !== sha) return null;
    return rec;
  }
  function get(uid, sha) {
    if (g.TTwinRag && TTwinRag.solutionOf) {
      return TTwinRag.solutionOf(uid, sha, S.local) || TTwinRag.solutionOf(uid, sha, S.packed);
    }
    return pick(S.local, uid, sha) || pick(S.packed, uid, sha);
  }
  function allNew() {
    return Object.keys(S.local).map((k) => S.local[k]);
  }
  async function put(rec) {
    if (!rec || !rec.item_uid) return rec;
    S.local[rec.item_uid] = rec;
    saveLocal();
    const proxy = (g.TTwinKimi && TTwinKimi.getProxy && TTwinKimi.getProxy()) || "";
    const local = location.protocol === "http:" && (location.hostname === "127.0.0.1" || location.hostname === "localhost");
    if (!local && !proxy) return rec;
    try {
      await fetch((proxy ? proxy.replace(/\/kimi\/?$/, "") : "") + "/solution", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(rec),
      });
    } catch (e) { /* Pages cannot write; localStorage still holds it. */ }
    return rec;
  }
  function exportJsonl() {
    return allNew().map((r) => JSON.stringify(r)).join("\n") + (allNew().length ? "\n" : "");
  }

  g.TTwinSolutions = { boot, fingerprint, get, put, exportJsonl, allNew, canonical };
})(window);
