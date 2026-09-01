(function () {
  const S = {
    meta: null, nodes: [], hinges: [], enrichment: [], projection: null, nav: [],
    stems: {}, loadedPacks: {},
  };

  const ROUTES = [
    ["home", "Home"],
    ["browse", "Browse"],
    ["prompt", "Prompt"],
    ["lesson", "Lesson"],
    ["paper", "Test maker"],
    ["isogen", "ISO-GEN"],
    ["map", "Map"],
    ["settings", "Settings"],
  ];

  function $(id) { return document.getElementById(id); }
  function esc(s) { return TTwinPaper.esc(s); }

  async function jget(path) {
    const r = await fetch(path);
    if (!r.ok) throw new Error("failed " + path);
    return r.json();
  }

  async function boot() {
    $("app").innerHTML = "<p class='muted'>Loading NCERT chemistry pack…</p>";
    try {
      const [meta, nodes, hinges, enrichment, projection, nav] = await Promise.all([
        jget("data/meta.json"),
        jget("data/nodes.json"),
        jget("data/hinges.json"),
        jget("data/enrichment.json"),
        jget("data/projection.json"),
        jget("data/nav.json"),
      ]);
      S.meta = meta; S.nodes = nodes; S.hinges = hinges;
      S.enrichment = enrichment; S.projection = projection; S.nav = nav;
      route();
    } catch (e) {
      $("app").innerHTML = "<div class='notice err'>Could not load data: " + esc(e.message) + "</div>";
    }
  }

  async function ensurePack(pack) {
    const file = pack === "senior_11_12_as_a" ? "data/questions-senior.json"
      : pack === "olympiad_iit" ? "data/questions-olympiad.json"
      : "data/questions-igcse.json";
    if (S.loadedPacks[file]) return;
    try {
      const rows = await jget(file);
      rows.forEach((r) => { S.stems[r.uid] = r; });
      S.loadedPacks[file] = true;
    } catch (e) {
      S.loadedPacks[file] = "missing";
    }
  }

  function navHTML() {
    const hash = (location.hash || "#home").slice(1).split("/")[0] || "home";
    return "<nav class='top'>" +
      "<a class='brand' href='#home'>TWIN</a>" +
      ROUTES.map(([id, lab]) =>
        "<a href='#" + id + "' class='" + (hash === id ? "active" : "") + "'>" + lab + "</a>"
      ).join("") +
      "</nav>";
  }

  function statsBar() {
    const m = S.meta || {};
    return "<div class='banner'>" +
      "<span class='stat'><b>" + (m.n_nodes || 0) + "</b> nodes</span>" +
      "<span class='stat'><b>" + (m.n_hinges || 0) + "</b> NCERT hinges</span>" +
      "<span class='stat'><b>" + (m.n_enrichment || 0) + "</b> enrichment</span>" +
      "<span class='stat'><b>" + (m.n_questions || 0) + "</b> tagged questions</span>" +
      "<span class='stat'><b>" + (m.n_stems || 0) + "</b> typeset stems</span>" +
      "</div>";
  }

  function nodeOptions(selected) {
    return S.nodes.map((n) => {
      const id = "chem:" + n.id;
      return "<option value='" + esc(id) + "'" + (selected === id ? " selected" : "") + ">" +
        esc(n.id + " — " + (n.title || "")) + "</option>";
    }).join("");
  }

  function unique(arr) {
    return Array.from(new Set(arr.filter(Boolean))).sort();
  }

  function renderHome() {
    const m = S.meta || {};
    $("hero").classList.remove("hidden");
    $("hero-inner").innerHTML =
      "<p class='kicker'>TeacherTwin · NCERT chemistry</p>" +
      "<h1>One hinge is enough to assemble the packet.</h1>" +
      "<p class='sub'>Map, enrichment, and the tagged question bank are separate homes. " +
      "A teacher request becomes a selector. Retrieve is deterministic. AI infers fuzzy prompts and authors ISO-GEN candidates from hinge packs — never from the 46&nbsp;MB map.</p>";
    $("app").innerHTML = statsBar() +
      "<div class='claim'>" + esc(m.honesty || "") + "</div>" +
      "<div class='grid'>" +
      card("#browse", "Browse", "Pack → node → chapter → subtopic. Questions render as exam items with figures.") +
      card("#prompt", "Prompt retrieve", "“Chemical energetics at senior level” → selector → questions + hinge packs.") +
      card("#lesson", "Lesson planner", "Teacher digest from the enrichment layer, optional AI prose.") +
      card("#paper", "Test maker", "Set N, seed, and a selector. Same inputs, same paper.") +
      card("#isogen", "ISO-GEN", "New MCQ from a hinge pack. CANDIDATE. Frozen L20 is not rewritten.") +
      card("#map", "Map explorer", "523 NCERT hinges, mx, mastery, LoK, gaming pockets.") +
      "</div>" +
      "<p class='muted'>AI is optional (Settings). Browse, retrieve, and papers work without it.</p>";
  }

  function card(href, title, body) {
    return "<a class='card' href='" + href + "' style='text-decoration:none;color:inherit'><h2>" +
      esc(title) + "</h2><p>" + esc(body) + "</p></a>";
  }

  function filtersHTML(prefix) {
    return "<div class='card'><div class='row'>" +
      "<div><label>Pack</label><select id='" + prefix + "-pack'>" +
      "<option value='igcse_9_10'>A · Grades 9–10 / IGCSE</option>" +
      "<option value='senior_11_12_as_a'>B · Grades 11–12 / AS–A</option>" +
      "</select></div>" +
      "<div><label>Big idea (map node)</label><select id='" + prefix + "-node'><option value=''>any</option>" +
      nodeOptions() + "</select></div>" +
      "<div><label>Chapter</label><select id='" + prefix + "-ch'><option value=''>any</option></select></div>" +
      "<div><label>Subtopic</label><select id='" + prefix + "-sub'><option value=''>any</option></select></div>" +
      "</div></div>";
  }

  function fillChapters(prefix) {
    const pack = $(prefix + "-pack").value;
    const node = $(prefix + "-node").value;
    const rows = S.nav.filter((r) => r.pack === pack && (!node || TTwinRag.nodesComparable(r.node, node)));
    const ch = unique(rows.map((r) => r.chapter_id + "||" + (r.chapter_label || "")));
    const sel = $(prefix + "-ch");
    const keep = sel.value;
    sel.innerHTML = "<option value=''>any</option>" + ch.map((x) => {
      const [id, lab] = x.split("||");
      return "<option value='" + esc(id) + "'>" + esc(id + " · " + lab) + "</option>";
    }).join("");
    if (keep && [...sel.options].some((o) => o.value === keep)) sel.value = keep;
    fillSubs(prefix);
  }
  function fillSubs(prefix) {
    const pack = $(prefix + "-pack").value;
    const node = $(prefix + "-node").value;
    const ch = $(prefix + "-ch").value;
    const rows = S.nav.filter((r) => r.pack === pack &&
      (!node || TTwinRag.nodesComparable(r.node, node)) &&
      (!ch || r.chapter_id === ch));
    const subs = unique(rows.map((r) => r.subtopic_id + "||" + (r.subtopic_label || "")));
    const sel = $(prefix + "-sub");
    const keep = sel.value;
    sel.innerHTML = "<option value=''>any</option>" + subs.map((x) => {
      const [id, lab] = x.split("||");
      return "<option value='" + esc(id) + "'>" + esc((lab || id)) + "</option>";
    }).join("");
    if (keep && [...sel.options].some((o) => o.value === keep)) sel.value = keep;
  }
  function selectorFromFilters(prefix) {
    const sel = {
      pack: $(prefix + "-pack").value,
      subject: "chemistry",
      maps: ["ncert", "cambridge"],
    };
    const node = $(prefix + "-node").value;
    if (node) sel.nodes = [node];
    const ch = $(prefix + "-ch").value;
    if (ch) sel.families = [ch];
    const sub = $(prefix + "-sub").value;
    if (sub) sel.families = [sub];
    return sel;
  }
  function bindFilters(prefix, onchange) {
    ["pack", "node", "ch"].forEach((id) => {
      $(prefix + "-" + id).addEventListener("change", () => { fillChapters(prefix); onchange(); });
    });
    $(prefix + "-sub").addEventListener("change", onchange);
    fillChapters(prefix);
  }

  function renderBrowse() {
    $("hero").classList.add("hidden");
    $("app").innerHTML = "<p class='kicker'>Browse</p><h1>Five-click retrieve</h1>" +
      "<p class='sub'>Pack and node are map language. Chapter and subtopic are the Cambridge coordinates already on the tagged corpus.</p>" +
      filtersHTML("br") + "<div id='br-out'></div>";
    const go = async () => {
      const sel = selectorFromFilters("br");
      const r = TTwinRag.assemble(sel, S.nav, S.projection);
      const uids = r.question_uids.slice(0, 8);
      const items = await itemsForUids(uids);
      $("br-out").innerHTML =
        "<div class='banner'><span class='stat'><b>" + r.receipt.n_questions + "</b> questions</span>" +
        "<span class='stat'><b>" + r.receipt.n_hinge_unit_ids_before_cap + "</b> hinges</span>" +
        "<span class='stat'>preview <b>" + items.length + "</b></span></div>" +
        TTwinPaper.paperHTML({ title: "Question preview", subtitle: (sel.nodes || []).join(" ") }, items) +
        (r.question_uids.length > 8 ? "<p class='muted no-print'>Showing 8 of " + r.question_uids.length + ". Use Test maker for a full paper.</p>" : "");
      TTwinPaper.mount($("br-out"));
    };
    bindFilters("br", () => { go(); });
    $("br-pack").value = "senior_11_12_as_a";
    $("br-node").value = "chem:C6";
    fillChapters("br");
    go();
  }

  function renderPrompt() {
    $("hero").classList.add("hidden");
    $("app").innerHTML = "<p class='kicker'>Prompt retrieve</p><h1>Teacher language → packets</h1>" +
      "<p class='sub'>Aliases compile without a model (“chemical energetics at senior level”). Fuzzy prompts can use AI to emit a selector JSON. Retrieve itself never calls a provider.</p>" +
      "<div class='card'><label>Teacher prompt</label>" +
      "<textarea id='pr-text'>chemical energetics at senior level</textarea>" +
      "<p style='margin-top:10px'><button id='pr-go' type='button'>Retrieve</button> " +
      "<button class='sec' id='pr-kimi' type='button'>Infer selector with AI</button></p>" +
      "<pre class='dump' id='pr-sel'></pre></div><div id='pr-out'></div>";
    function show(sel, via) {
      $("pr-sel").textContent = (via ? via + "\n" : "") + JSON.stringify(sel, null, 2);
      const r = TTwinRag.assemble(sel, S.nav, S.projection);
      S.lastRetrieve = { sel, r };
      const by = Object.fromEntries(S.nav.map((x) => [x.uid, x]));
      $("pr-out").innerHTML =
        "<div class='banner'><span class='stat'><b>" + r.receipt.n_questions + "</b> questions</span>" +
        "<span class='stat'><b>" + r.hinge_unit_ids.length + "</b> hinge packs</span>" +
        "<span class='stat'>provider_calls <b>0</b></span></div>" +
        "<div class='split'><div class='card'><h2>Questions</h2>" +
        r.question_uids.slice(0, 25).map((u) => {
          const it = by[u] || {};
          return "<div class='q'><span class='uid'>" + esc(u) + "</span> " +
            "<span class='tag'>" + esc(it.subtopic_label || it.chapter_id || "") + "</span></div>";
        }).join("") + "</div><div class='card'><h2>Hinges</h2>" +
        r.hinge_unit_ids.map((u) => "<div class='q'><span class='uid'>" + esc(u) + "</span></div>").join("") +
        "</div></div>" +
        "<p><button class='sec' id='pr-paper' type='button'>Send to test maker</button> " +
        "<button class='sec' id='pr-lesson' type='button'>Send to lesson planner</button></p>";
      $("pr-paper").onclick = () => { S.carry = { sel, r }; location.hash = "paper"; };
      $("pr-lesson").onclick = () => { S.carry = { sel, r }; location.hash = "lesson"; };
    }
    $("pr-go").onclick = () => {
      const sel = TTwinRag.parsePromptDeterministic($("pr-text").value, S.projection);
      show(sel, "deterministic alias compile");
    };
    $("pr-kimi").onclick = async () => {
      $("pr-kimi").disabled = true;
      try {
        const sel = await TTwinKimi.inferSelector($("pr-text").value, S.nodes.map((n) => ({ id: "chem:" + n.id })));
        if (sel.error) throw new Error(sel.ask || sel.error);
        show(sel, "AI selector");
      } catch (e) {
        $("pr-out").innerHTML = "<div class='notice err'>" + esc(e.message) + "</div>";
      }
      $("pr-kimi").disabled = false;
    };
    $("pr-go").click();
  }

  function digestFromSelector(sel, r) {
    const unitIds = (r && r.hinge_unit_ids) || [];
    const nodes = sel.nodes || [];
    let rows = S.enrichment.filter((e) => {
      if (unitIds.length && (e.serves || []).some((u) => unitIds.includes(u))) return true;
      if (nodes.some((n) => TTwinRag.nodesComparable(e.node, n))) return true;
      return false;
    });
    const rank = { teaching_caution: 0, misconception: 1, student_difficulty: 2, sequencing_insight: 3 };
    rows.sort((a, b) => (rank[a.type] ?? 9) - (rank[b.type] ?? 9) || String(a.item_id).localeCompare(b.item_id));
    rows = rows.slice(0, 12);
    return {
      schema: "awm.teacher_digest.v1",
      selector: sel,
      n_returned: rows.length,
      rows: rows.map((e) => ({
        item_id: e.item_id,
        evidence_type: e.type,
        statement: e.statement,
        classroom_readiness: e.readiness,
        attested: e.attested,
        citation: e.citation,
        node: e.node,
      })),
    };
  }

  function renderLesson() {
    $("hero").classList.add("hidden");
    const preset = (S.carry && S.carry.sel) || TTwinRag.parsePromptDeterministic("chemical energetics at senior level", S.projection);
    $("app").innerHTML = "<p class='kicker'>Lesson planner</p><h1>Digest from the enrichment layer</h1>" +
      "<p class='sub'>Planning types first (caution, misconception, difficulty, sequencing). Citations from ChemEd X documents. AI may write prose from this view; it must not invent URLs.</p>" +
      filtersHTML("ls") +
      "<p><button id='ls-go' type='button'>Build digest</button> " +
      "<button class='sec' id='ls-kimi' type='button'>AI prose</button></p>" +
      "<div id='ls-out'></div>";
    if (preset.pack) $("ls-pack").value = preset.pack;
    if (preset.nodes && preset.nodes[0]) $("ls-node").value = preset.nodes[0];
    function go() {
      const sel = selectorFromFilters("ls");
      const r = TTwinRag.assemble(sel, S.nav, S.projection);
      const d = digestFromSelector(sel, r);
      S.lastDigest = d;
      $("ls-out").innerHTML = "<div class='card'><h2>Deterministic digest</h2>" +
        "<p class='muted'>" + d.n_returned + " enrichment rows · node " + esc((sel.nodes || []).join(", ")) + "</p>" +
        d.rows.map((row) => "<div class='q'><span class='tag'>" + esc(row.evidence_type || "") + "</span>" +
          (row.attested ? "<span class='tag'>attested</span>" : "") +
          "<p>" + esc(row.statement || "") + "</p>" +
          (row.citation && row.citation.url
            ? "<p class='muted'><a href='" + esc(row.citation.url) + "' target='_blank' rel='noopener'>" +
              esc(row.citation.title || row.citation.url) + "</a></p>"
            : "<p class='muted'>No public URL (local PDF) — do not invent a DOI.</p>") +
          "</div>").join("") +
        "</div><div id='ls-prose'></div>";
    }
    bindFilters("ls", () => {});
    $("ls-go").onclick = go;
    $("ls-kimi").onclick = async () => {
      if (!S.lastDigest) go();
      $("ls-kimi").disabled = true;
      try {
        const prose = await TTwinKimi.lessonProse(S.lastDigest);
        $("ls-prose").innerHTML = "<div class='card'><h2>AI lesson prose</h2><p>" +
          esc(prose).replace(/\n\n/g, "</p><p>").replace(/\n/g, "<br>") + "</p></div>";
      } catch (e) {
        $("ls-prose").innerHTML = "<div class='notice err'>" + esc(e.message) + "</div>";
      }
      $("ls-kimi").disabled = false;
    };
    go();
  }

  async function itemsForUids(uids) {
    const need = { igcse_9_10: false, senior_11_12_as_a: false };
    uids.forEach((u) => {
      const row = S.nav.find((r) => r.uid === u);
      if (row) need[row.pack] = true;
    });
    if (need.igcse_9_10) await ensurePack("igcse_9_10");
    if (need.senior_11_12_as_a) await ensurePack("senior_11_12_as_a");
    return uids.map((u) => S.stems[u] || S.nav.find((r) => r.uid === u) || { uid: u });
  }

  function renderPaper() {
    $("hero").classList.add("hidden");
    $("app").innerHTML = "<p class='kicker'>Test maker</p><h1>Assemble a question paper</h1>" +
      "<p class='sub'>Dropdown selector or a carried prompt retrieve. Shuffle is mulberry32 on the seed. Learner paper has no mx, no examiner comments, no crops.</p>" +
      filtersHTML("tm") +
      "<div class='card'><div class='row'>" +
      "<div><label>N questions</label><input id='tm-n' type='number' min='1' max='40' value='10'></div>" +
      "<div><label>Seed (empty = uid order)</label><input id='tm-seed' placeholder='optional'></div>" +
      "<div><label>Jump to uid</label><input id='tm-jump' placeholder='9701_m16_qp_12:q5'></div>" +
      "<div><label>Title</label><input id='tm-title' value='Chemistry paper'></div>" +
      "</div><p style='margin-top:10px'><button id='tm-go' type='button'>Make paper</button> " +
      "<button class='sec no-print' onclick='window.print()'>Print</button></p></div>" +
      "<div id='tm-out'></div>";
    bindFilters("tm", () => {});
    if (S.carry && S.carry.sel && S.carry.sel.pack) {
      $("tm-pack").value = S.carry.sel.pack;
      if (S.carry.sel.nodes && S.carry.sel.nodes[0]) $("tm-node").value = S.carry.sel.nodes[0];
      fillChapters("tm");
    }
    $("tm-go").onclick = async () => {
      const jump = ($("tm-jump").value || "").trim();
      const sel = selectorFromFilters("tm");
      const r = TTwinRag.assemble(sel, S.nav, S.projection);
      const n = Math.max(1, Math.min(40, Number($("tm-n").value || 10)));
      const seed = $("tm-seed").value;
      const ordered = jump ? [jump] : TTwinRag.seededShuffle(r.question_uids, seed).slice(0, n);
      const items = await itemsForUids(ordered);
      $("tm-out").innerHTML = TTwinPaper.paperHTML({
        title: $("tm-title").value,
        subtitle: (sel.nodes || []).join(" ") + " · " + (sel.pack || ""),
        seed,
      }, items);
      TTwinPaper.mount($("tm-out"));
    };
  }

  function shaHex(str) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(str)).then((buf) =>
      Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("")
    );
  }

  function renderIsogen() {
    $("hero").classList.add("hidden");
    $("app").innerHTML = "<p class='kicker'>ISO-GEN</p><h1>Author from a hinge pack</h1>" +
      "<p class='sub'>The frozen Lamport-20 engine is not rewritten. This tray authors a CANDIDATE item from <code>hinge_pack(unit_id)</code> using AI. Specification exists before the stem. Nothing enters the live exam pool.</p>" +
      "<div class='card'><label>Teacher prompt or hinge id</label>" +
      "<textarea id='iso-text'>science/grade_11/chem_ch_105/H009</textarea>" +
      "<p><button id='iso-pack' type='button'>Load hinge pack</button> " +
      "<button class='sec' id='iso-go' type='button'>Author with AI</button></p></div>" +
      "<div id='iso-out'></div>";
    $("iso-pack").onclick = () => {
      const text = $("iso-text").value.trim();
      let unit = (text.match(/science\/grade_\d+\/[^\s]+\/H\d+/) || [])[0];
      if (!unit) {
        const sel = TTwinRag.parsePromptDeterministic(text, S.projection);
        const r = TTwinRag.assemble(sel, S.nav, S.projection);
        unit = r.hinge_unit_ids.find((u) => u.startsWith("science/")) || r.hinge_unit_ids[0];
      }
      if (!unit) { $("iso-out").innerHTML = "<div class='notice err'>No hinge resolved.</div>"; return; }
      const pack = TTwinRag.hingePack(unit, S.hinges, S.enrichment);
      S.lastPack = pack;
      const st = pack.statement || {};
      $("iso-out").innerHTML = "<div class='card'><h2>Specification · " + esc(unit) + "</h2>" +
        "<p>" + esc(st.decision_hinge || "") + "</p>" +
        "<p class='muted'>" + esc(st.mechanism || "") + "</p>" +
        "<h3 class='muted'>CANDIDATE mx</h3>" +
        (st.mx || []).map((m) => "<div class='mx'><b>" + esc(m.type || "") + "</b> " + esc(m.cwo || "") + "</div>").join("") +
        "<h3 class='muted'>Enrichment (" + pack.enrichment.n_in_packet + ")</h3>" +
        (pack.enrichment.items || []).map((e) => "<div class='q'>" + esc(e.statement || "") + "</div>").join("") +
        "</div><div id='iso-item'></div>";
    };
    $("iso-go").onclick = async () => {
      if (!S.lastPack) $("iso-pack").click();
      if (!S.lastPack) return;
      $("iso-go").disabled = true;
      try {
        const specHash = await shaHex(JSON.stringify(S.lastPack.statement));
        const item = await TTwinKimi.authorItem(S.lastPack);
        const ev = {
          schema: "ttwin.isogen.candidate.v1",
          serve_eligible: false,
          owner_ratified: false,
          unit_id: S.lastPack.unit_id,
          spec_sha256: specHash,
          item,
          model: TTwinKimi.MODEL,
          utc: new Date().toISOString(),
        };
        const tray = JSON.parse(localStorage.getItem("ttwin.isogen.tray") || "[]");
        tray.unshift(ev);
        localStorage.setItem("ttwin.isogen.tray", JSON.stringify(tray.slice(0, 20)));
        $("iso-item").innerHTML = "<div class='notice'>CANDIDATE · serve_eligible=false · spec " + specHash.slice(0, 12) + "…</div>" +
          TTwinPaper.itemHTML({ uid: "isogen:" + specHash.slice(0, 8), stem: item.stem, options: item.options }, 0) +
          "<p class='muted'>Correct " + esc(item.correct) + " · " + esc(item.rationale || "") + "</p>";
        TTwinPaper.mount($("iso-item"));
      } catch (e) {
        $("iso-item").innerHTML = "<div class='notice err'>" + esc(e.message) + "</div>";
      }
      $("iso-go").disabled = false;
    };
  }

  function renderMap() {
    $("hero").classList.add("hidden");
    $("app").innerHTML = "<p class='kicker'>NCERT comprehensive map</p><h1>Hinges, mx, pedagogy</h1>" +
      "<p class='sub'>523 NCERT statements. Big idea is a layer above the hinge. Pedagogy is joined from chapter intelligence; mx are CANDIDATE (v2).</p>" +
      "<div class='card'><div class='row'><div><label>Node</label><select id='mp-node'>" + nodeOptions() +
      "</select></div><div><label>Band</label><select id='mp-band'>" +
      "<option value=''>any</option><option value='SECONDARY'>Secondary</option>" +
      "<option value='SENIOR_SECONDARY' selected>Senior secondary</option></select></div></div></div>" +
      "<div id='mp-out'></div>";
    const go = () => {
      const node = $("mp-node").value;
      const band = $("mp-band").value;
      const rows = S.hinges.filter((h) => TTwinRag.nodesComparable("chem:" + h.node, node) && (!band || h.grade_band === band));
      $("mp-out").innerHTML = "<p class='muted'>" + rows.length + " hinges</p>" + rows.map((h) => {
        const ped = h.pedagogy || {};
        return "<div class='card' style='margin:10px 0'><div class='uid'>" + esc(h.unit_id) +
          " · " + esc(h.chapter_title || h.chapter) + "</div>" +
          "<p><b>" + esc(h.decision_hinge || "") + "</b></p>" +
          "<p class='muted'>" + esc(h.mechanism || "") + "</p>" +
          (ped.mastery_signal ? "<p><span class='tag'>mastery</span> " + esc(ped.mastery_signal) + "</p>" : "") +
          (ped.lok_folk ? "<p><span class='tag'>LoK</span> " + esc(ped.lok_folk) + "</p>" : "") +
          (h.mx || []).map((m) => "<div class='mx'><b>" + esc(m.type) + "</b> " + esc(m.cwo || "") + "</div>").join("") +
          "</div>";
      }).join("");
    };
    $("mp-node").value = "chem:C6";
    $("mp-node").onchange = go;
    $("mp-band").onchange = go;
    go();
  }

  function renderSettings() {
    $("hero").classList.add("hidden");
    $("app").innerHTML = "<p class='kicker'>Settings</p><h1>AI</h1>" +
      "<div class='card'><p>The key is stored in <code>localStorage</code> on this machine only. Browse and papers work without it.</p>" +
      "<label>AI API key</label><input id='st-key' type='password' placeholder='sk-…' value='" + esc(TTwinKimi.getKey()) + "'>" +
      "<label>Proxy URL (optional)</label><input id='st-proxy' placeholder='leave blank for direct API, or /kimi on local serve.py' value='" + esc(TTwinKimi.getProxy()) + "'>" +
      "<p class='muted'>GitHub Pages cannot keep a secret. For AI features on github.io paste a key (CORS may block) or run <code>python3 tools/serve.py</code> and set the proxy to that origin + <code>/kimi</code>.</p>" +
      "<p><button id='st-save' type='button'>Save</button> <button class='sec' id='st-clear' type='button'>Clear key</button></p>" +
      "<p class='muted' id='st-ep'></p></div>";
    $("st-ep").textContent = "Active endpoint: " + TTwinKimi.endpoint();
    $("st-save").onclick = () => {
      TTwinKimi.setKey($("st-key").value.trim());
      TTwinKimi.setProxy($("st-proxy").value.trim());
      $("st-ep").textContent = "Saved. Endpoint: " + TTwinKimi.endpoint();
    };
    $("st-clear").onclick = () => { TTwinKimi.setKey(""); $("st-key").value = ""; };
  }

  const VIEWS = {
    home: renderHome,
    browse: renderBrowse,
    prompt: renderPrompt,
    lesson: renderLesson,
    paper: renderPaper,
    isogen: renderIsogen,
    map: renderMap,
    settings: renderSettings,
  };

  function route() {
    document.getElementById("navhost").innerHTML = navHTML();
    const name = (location.hash || "#home").slice(1).split("/")[0] || "home";
    (VIEWS[name] || renderHome)();
    window.scrollTo(0, 0);
  }

  window.addEventListener("hashchange", route);
  boot();
})();
