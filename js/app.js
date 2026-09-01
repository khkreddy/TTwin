(function () {
  const S = {
    meta: null, nodes: [], hinges: [], enrichment: [], projection: null, nav: [],
    stems: {}, loadedPacks: {},
  };

  const ROUTES = [
    ["browse", "Browse"],
    ["prompt", "Prompt"],
    ["lesson", "Lesson"],
    ["paper", "Test maker"],
    ["journal", "Journal"],
    ["isogen", "ISO-GEN"],
    ["map", "Map"],
    ["settings", "Settings"],
  ];
  const JOURNAL_KEY = "ttwin.journal.v1";

  function $(id) { return document.getElementById(id); }
  function esc(s) { return TTwinPaper.esc(s); }

  async function jget(path) {
    const r = await fetch(path);
    if (!r.ok) throw new Error("failed " + path);
    return r.json();
  }

  async function boot() {
    $("app").innerHTML = "<p class='muted'>Loading…</p>";
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
      "<a class='brand" + (hash === "home" ? " active" : "") + "' href='#home'>Teacher's Twin</a>" +
      ROUTES.map(([id, lab]) =>
        "<a href='#" + id + "' class='" + (hash === id ? "active" : "") + "'>" + lab + "</a>"
      ).join("") +
      "</nav>";
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
    $("hero").classList.remove("hidden");
    $("hero-inner").innerHTML =
      "<p class='kicker'>Chemistry for teachers</p>" +
      "<h1>Teacher's Twin</h1>" +
      "<p class='sub'>A working copy of how you think. You bring the idea. The twin finds the questions, the lesson, and the mix-ups.</p>";
    $("app").innerHTML =
      "<div class='home-lede'>" +
      "<p>This is a chemistry resource for teachers. It is not tied to one syllabus. You do not need codes or a chapter list in your head.</p>" +
      "<p>The twin is organised around what the student must decide. That decision is the same whether you teach NCERT, Cambridge, or another board.</p>" +
      "<p>AI is optional. Browse, retrieve, and papers work without it.</p>" +
      "</div>" +
      "<h2 class='modules-head'>What it does</h2>" +
      "<div class='modules'>" +
      card("#browse", "Browse", "Walk the question bank by idea and year group. Items typeset as they would on a paper. Figures draw on the page.") +
      card("#prompt", "Prompt", "Say what you want in ordinary language. The twin returns the matching questions and the ideas they test.") +
      card("#lesson", "Lesson", "A briefing for class: the decision the student must make, the usual mix-ups, your notes, and a short plan.") +
      card("#paper", "Test maker", "Cut a paper. Same settings, same paper. The learner never sees examiner talk or your notes.") +
      card("#journal", "Journal", "Keep notes and links. They attach to the idea you were teaching and come back on the lesson.") +
      card("#isogen", "ISO-GEN", "Describe the question you want, even if the idea is fuzzy. The twin drafts a candidate. It stays out of the exam pool until you accept it.") +
      card("#map", "Map", "Read the chemistry ideas themselves. What the student must decide. How it works. Where they usually go wrong.") +
      "</div>";
  }

  function card(href, title, body) {
    return "<a class='card module' href='" + href + "'><h2>" +
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

  function loadJournal() {
    try { return JSON.parse(localStorage.getItem(JOURNAL_KEY) || "[]"); }
    catch (e) { return []; }
  }
  function saveJournal(rows) {
    localStorage.setItem(JOURNAL_KEY, JSON.stringify(rows));
  }
  function mapPackFor(r) {
    const ids = ((r && r.hinge_unit_ids) || []).filter((u) => String(u).indexOf("science/") === 0).slice(0, 8);
    return ids.map((id) => {
      const h = S.hinges.find((x) => x.unit_id === id);
      if (!h) return { unit_id: id };
      return {
        unit_id: h.unit_id,
        node: h.node,
        chapter: h.chapter_title || h.chapter,
        decision_hinge: h.decision_hinge,
        mechanism: h.mechanism,
        mx: (h.mx || []).slice(0, 4).map((m) => ({ type: m.type, cwo: m.cwo, status: m.status })),
        pedagogy: h.pedagogy
          ? { mastery_signal: h.pedagogy.mastery_signal, lok_folk: h.pedagogy.lok_folk }
          : null,
      };
    });
  }
  function overlayFor(sel, r) {
    const units = new Set((r && r.hinge_unit_ids) || []);
    const nodes = (sel.nodes || []).map((n) => String(n).replace(/^chem:/, ""));
    return loadJournal().filter((note) => (note.bindings || []).some((b) =>
      units.has(b.unit_id) || nodes.indexOf(String(b.node || "").replace(/^chem:/, "")) >= 0
    ));
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
    rows = rows.slice(0, 8);
    const overlay = overlayFor(sel, r).slice(0, 8);
    return {
      schema: "awm.teacher_digest.v1",
      selector: sel,
      map: mapPackFor(r),
      enrichment: {
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
      },
      teacher_overlay: overlay.map((n) => ({
        id: n.id,
        text: n.text,
        url: n.url,
        bindings: n.bindings,
        utc: n.utc,
      })),
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
    $("app").innerHTML = "<p class='kicker'>Lesson planner</p><h1>Digest from map, enrichment, and your notes</h1>" +
      "<p class='sub'>AI prose is Zinsser-style and sees the hinge pack, enrichment, and journal overlay for this selection. Citations stay as given; null URLs stay null.</p>" +
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
      const overlay = d.teacher_overlay || [];
      const mapRows = d.map || [];
      $("ls-out").innerHTML =
        "<p class='muted'>AI pack: " + mapRows.length + " map hinges · " +
        (d.n_returned || 0) + " enrichment · " + overlay.length + " journal notes</p>" +
        (overlay.length
          ? "<div class='card'><h2>Your overlay</h2>" + overlay.map((n) =>
            "<div class='q'><p>" + esc(n.text) + "</p>" +
            (n.url ? "<p class='muted'><a href='" + esc(n.url) + "' target='_blank' rel='noopener'>" + esc(n.url) + "</a></p>" : "") +
            "<p class='muted'>" + (n.bindings || []).map((b) => esc(b.unit_id)).join(" · ") + "</p></div>"
          ).join("") + "</div>"
          : "") +
        "<div class='card'><h2>Map hinges</h2>" +
        (mapRows.length
          ? mapRows.map((h) => "<div class='q'><div class='uid'>" + esc(h.unit_id) + "</div><p>" +
            esc(h.decision_hinge || "") + "</p></div>").join("")
          : "<p class='muted'>No NCERT hinges in this selector cap.</p>") +
        "</div>" +
        "<div class='card'><h2>Enrichment</h2>" +
        "<p class='muted'>" + (d.n_returned || 0) + " rows · node " + esc((sel.nodes || []).join(", ")) + "</p>" +
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

  function renderJournal() {
    $("hero").classList.add("hidden");
    function paint() {
      const rows = loadJournal();
      $("jn-list").innerHTML = rows.length ? rows.map((n) =>
        "<div class='card' style='margin:10px 0'><p>" + esc(n.text) + "</p>" +
        (n.url ? "<p class='muted'><a href='" + esc(n.url) + "' target='_blank' rel='noopener'>" + esc(n.url) + "</a></p>" : "") +
        "<p class='muted'>" + ((n.bindings || []).length
          ? (n.bindings || []).map((b) => esc(b.unit_id) + (b.why ? " — " + esc(b.why) : "")).join("<br>")
          : "Not yet mapped to a hinge") + "</p>" +
        "<p><button class='sec' data-del='" + esc(n.id) + "' type='button'>Delete</button></p></div>"
      ).join("") : "<p class='muted'>No notes yet.</p>";
      $("jn-list").querySelectorAll("[data-del]").forEach((btn) => {
        btn.onclick = () => {
          saveJournal(loadJournal().filter((n) => n.id !== btn.getAttribute("data-del")));
          paint();
        };
      });
    }
    $("app").innerHTML = "<p class='kicker'>Journal</p><h1>Teacher overlay</h1>" +
      "<p class='sub'>Write a comment or paste a link. AI maps the note onto NCERT hinges. Those notes then appear on the Lesson tab for that hinge, and they go into the AI briefing pack.</p>" +
      "<div class='card'><label>Note</label><textarea id='jn-text' placeholder='Students keep mixing ΔH with activation energy on pathway diagrams.'></textarea>" +
      "<label>Link (optional)</label><input id='jn-url' placeholder='https://…'>" +
      "<p style='margin-top:10px'><button id='jn-save' type='button'>Save and map with AI</button> " +
      "<button class='sec' id='jn-plain' type='button'>Save without mapping</button></p></div>" +
      "<div id='jn-list'></div>";
    paint();
    async function add(mapIt) {
      const text = ($("jn-text").value || "").trim();
      if (!text) return;
      const url = ($("jn-url").value || "").trim();
      const note = {
        id: "jn-" + Date.now(),
        text, url: url || null,
        utc: new Date().toISOString(),
        bindings: [],
      };
      if (mapIt) {
        $("jn-save").disabled = true;
        try {
          const mapped = await TTwinKimi.mapJournalNote(text, S.hinges);
          note.bindings = mapped.bindings || [];
          if (mapped.ask && !note.bindings.length) note.ask = mapped.ask;
        } catch (e) {
          note.ask = e.message;
        }
        $("jn-save").disabled = false;
      }
      saveJournal([note].concat(loadJournal()));
      $("jn-text").value = "";
      $("jn-url").value = "";
      paint();
    }
    $("jn-save").onclick = () => add(true);
    $("jn-plain").onclick = () => add(false);
  }

  function hingePlain(h) {
    if (!h) return "";
    const band = h.grade_band === "SENIOR_SECONDARY" ? "Grades 11–12" : "Grades 9–10";
    const ch = h.chapter_title || "";
    return (ch && ch.indexOf("science/") !== 0 ? ch : "Chemistry") + " · " + band;
  }
  function teacherFacing(s) {
    return String(s || "")
      .replace(/science\/grade_\d+\/[^\s,;]+\/H\d+/g, "")
      .replace(/\bchem:[A-Z][A-Z0-9/\-]+/g, "")
      .replace(/\s{2,}/g, " ")
      .trim();
  }
  function renderIsogen() {
    $("hero").classList.add("hidden");
    $("app").innerHTML = "<p class='kicker'>ISO-GEN</p><h1>Start from what you want to ask</h1>" +
      "<p class='sub'>Write the idea in ordinary language — it can be fuzzy. AI infers the intent, maps it to a curriculum hinge, then authors a CANDIDATE item. You do not need codes or lists. Nothing enters the live exam pool. Frozen ISO-GEN L20 is not rewritten.</p>" +
      "<div class='card'><label>What question do you want?</label>" +
      "<textarea id='iso-text' placeholder='A senior question on reaction profiles where they mix up ΔH with activation energy.'></textarea>" +
      "<p style='margin-top:10px'><button id='iso-go' type='button'>Author question</button></p></div>" +
      "<div id='iso-out'></div>";
    $("iso-go").onclick = async () => {
      const idea = ($("iso-text").value || "").trim();
      if (!idea) {
        $("iso-out").innerHTML = "<div class='notice'>Say what you want the student to face — topic, year group if you have one, and the mix-up if you can see it.</div>";
        return;
      }
      $("iso-go").disabled = true;
      $("iso-out").innerHTML = "<p class='muted'>Reading the idea…</p>";
      try {
        let inferred = null;
        const pasted = (idea.match(/science\/grade_\d+\/[^\s]+\/H\d+/) || [])[0];
        if (pasted && S.hinges.some((h) => h.unit_id === pasted)) {
          inferred = { intent: teacherFacing(idea) || idea, primary: { unit_id: pasted, why: null }, related: [], ask: null };
        } else {
          inferred = await TTwinKimi.inferIsoIntent(
            idea,
            S.hinges,
            S.nodes,
            TTwinRag.parsePromptDeterministic(idea, S.projection)
          );
        }
        if (!inferred || !(inferred.primary && inferred.primary.unit_id)) {
          $("iso-out").innerHTML = "<div class='notice'>" + esc(teacherFacing((inferred && inferred.ask) || "") || "Say a bit more: topic, year group, and what the student must decide.") + "</div>";
          $("iso-go").disabled = false;
          return;
        }
        const unit = inferred.primary.unit_id;
        const h = S.hinges.find((x) => x.unit_id === unit);
        if (!h) throw new Error("That idea did not land on a curriculum hinge. Try another wording.");
        const pack = TTwinRag.hingePack(unit, S.hinges, S.enrichment);
        S.lastPack = pack;
        const st = pack.statement || {};
        const relatedBits = (inferred.related || []).map((x) => {
          const rh = S.hinges.find((z) => z.unit_id === x.unit_id);
          return teacherFacing((rh && rh.decision_hinge) || "");
        }).filter(Boolean);
        $("iso-out").innerHTML =
          "<div class='card'><h2>What we heard</h2><p>" + esc(teacherFacing(inferred.intent || idea)) + "</p>" +
          "<p><b>The student must:</b> " + esc(st.decision_hinge || "") + "</p>" +
          "<p class='muted'>" + esc(hingePlain(h)) +
          (inferred.primary.why ? " · " + esc(teacherFacing(inferred.primary.why)) : "") + "</p>" +
          (relatedBits.length ? "<p class='muted'>Also related: " + relatedBits.map(esc).join(" · ") + "</p>" : "") +
          "<h3 class='muted'>Likely mix-ups (unverified)</h3>" +
          (st.mx || []).map((m) => "<div class='mx'><b>" + esc(m.type || "") + "</b> " + esc(m.cwo || "") + "</div>").join("") +
          "</div><p class='muted'>Authoring the question from that hinge…</p><div id='iso-item'></div>";
        const specHash = await shaHex(JSON.stringify(S.lastPack.statement));
        const item = await TTwinKimi.authorItem(S.lastPack, inferred.intent || idea);
        const ev = {
          schema: "ttwin.isogen.candidate.v1",
          serve_eligible: false,
          owner_ratified: false,
          unit_id: S.lastPack.unit_id,
          spec_sha256: specHash,
          teacher_intent: inferred.intent || idea,
          item,
          model: TTwinKimi.MODEL,
          utc: new Date().toISOString(),
        };
        const tray = JSON.parse(localStorage.getItem("ttwin.isogen.tray") || "[]");
        tray.unshift(ev);
        localStorage.setItem("ttwin.isogen.tray", JSON.stringify(tray.slice(0, 20)));
        $("iso-item").innerHTML = "<div class='notice'>CANDIDATE · not in the live exam pool · spec " + specHash.slice(0, 12) + "…</div>" +
          TTwinPaper.itemHTML({ uid: "isogen:" + specHash.slice(0, 8), stem: item.stem, options: item.options }, 0, { showUid: false }) +
          "<p class='muted'>Correct " + esc(item.correct) + " · " + esc(item.rationale || "") + "</p>";
        TTwinPaper.mount($("iso-item"));
      } catch (e) {
        const slot = $("iso-item") || $("iso-out");
        slot.innerHTML = "<div class='notice err'>" + esc(e.message) + "</div>";
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
    journal: renderJournal,
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
