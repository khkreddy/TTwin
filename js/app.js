(function () {
  const S = {
    meta: null, catalog: null, subject: "chemistry",
    nodes: [], hinges: [], enrichment: [], projection: null,
    vocab: { ideas: [] }, nav: [],
    stems: {}, loadedPacks: {},
    map: [], mapStatus: null,
    paper: null,
  };
  const SUBJECT_KEY = "ttwin.subject";

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

  function specOf(id) {
    return (S.catalog || []).find((s) => s.id === id) || null;
  }

  async function boot() {
    $("app").innerHTML = "<p class='muted'>Loading…</p>";
    try {
      const [meta, subjects, nodes, hinges, enrichment, projection] = await Promise.all([
        jget("data/meta.json"),
        jget("data/subjects.json"),
        jget("data/nodes.json"),
        jget("data/hinges.json"),
        jget("data/enrichment.json"),
        jget("data/projection.json"),
      ]);
      S.meta = meta;
      S.catalog = subjects.subjects || [];
      S.nodes = nodes; S.hinges = hinges;
      S.enrichment = enrichment; S.projection = projection;
      const wanted = sessionStorage.getItem(SUBJECT_KEY) || subjects.default || "chemistry";
      await loadSubject(wanted);
      route();
    } catch (e) {
      $("app").innerHTML = "<div class='notice err'>Could not load data: " + esc(e.message) + "</div>";
    }
  }

  async function loadSubject(id) {
    const spec = specOf(id) || specOf("chemistry") || (S.catalog || [])[0];
    if (!spec) throw new Error("No subjects in catalog");
    S.subject = spec.id;
    try { sessionStorage.setItem(SUBJECT_KEY, spec.id); } catch (e) {}
    const jobs = [jget(spec.vocab), jget(spec.nav)];
    const loadMap = spec.map && spec.id !== "chemistry";
    if (loadMap) jobs.push(jget(spec.map));
    const got = await Promise.all(jobs);
    S.vocab = got[0] || { ideas: [] };
    S.nav = got[1] || [];
    S.stems = {};
    S.loadedPacks = {};
    S.spec = spec;
    S.mapStatus = spec.map_status || (spec.has_map ? "comprehensive" : null);
    if (spec.id === "chemistry") S.map = S.hinges;
    else if (loadMap) S.map = got[2] || [];
    else S.map = [];
    return spec;
  }

  async function ensurePack(pack) {
    const spec = S.spec || specOf(S.subject);
    const entry = ((spec && spec.packs) || []).find((p) => p.id === pack);
    const file = entry && entry.questions;
    if (!file) return;
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
    const opts = (S.catalog || []).map((s) =>
      "<option value='" + esc(s.id) + "'" + (s.id === S.subject ? " selected" : "") + ">" +
      esc(s.label) + "</option>"
    ).join("");
    return "<nav class='top'>" +
      "<a class='brand" + (hash === "home" ? " active" : "") + "' href='#home'>Teacher's Twin</a>" +
      "<label class='nav-subject-lab'>Subject <select id='nav-subject' class='nav-subject'>" + opts + "</select></label>" +
      ROUTES.map(([id, lab]) =>
        "<a href='#" + id + "' class='" + (hash === id ? "active" : "") + "'>" + lab + "</a>"
      ).join("") +
      "</nav>";
  }

  function bindNavSubject() {
    const sel = $("nav-subject");
    if (!sel) return;
    sel.value = S.subject;
    sel.onchange = async () => {
      const next = sel.value;
      if (next === S.subject) return;
      $("app").innerHTML = "<p class='muted'>Loading " + esc(next) + "…</p>";
      try {
        await loadSubject(next);
        route();
      } catch (e) {
        $("app").innerHTML = "<div class='notice err'>" + esc(e.message) + "</div>";
      }
    };
  }

  function nodeOptions(selected) {
    return (S.vocab.ideas || []).map((n) => {
      const id = n.id;
      return "<option value='" + esc(id) + "'" + (selected === id ? " selected" : "") + ">" +
        esc(id + " — " + (n.title || "")) + "</option>";
    }).join("");
  }

  function packOptions(selected) {
    const packs = (S.spec && S.spec.packs) || [];
    if (!packs.length) {
      return "<option value='igcse_9_10'>A · Grades 9–10 / IGCSE</option>";
    }
    return packs.map((p) =>
      "<option value='" + esc(p.id) + "'" + (p.id === selected ? " selected" : "") + ">" +
      esc(p.label) + " (" + p.n + ")</option>"
    ).join("");
  }

  function unique(arr) {
    return Array.from(new Set(arr.filter(Boolean))).sort();
  }

  function renderHome() {
    $("hero").classList.remove("hidden");
    const counts = (S.catalog || []).map((s) =>
      "<span class='stat'><b>" + s.n_tagged + "</b> " + esc(s.label) + "</span>"
    ).join("");
    $("hero-inner").innerHTML =
      "<p class='kicker'>A resource for teachers</p>" +
      "<h1>Teacher's Twin</h1>" +
      "<p class='sub'>A working copy of how you think. Pick a subject. You bring the idea. The twin finds the questions, the lesson, and the mix-ups.</p>";
    $("app").innerHTML =
      "<div class='banner'>" + counts + "</div>" +
      "<div class='home-lede'>" +
      "<p>Use the subject menu for chemistry, biology, physics, or mathematics. It is not tied to one syllabus. You do not need codes or a chapter list in your head.</p>" +
      "<p>The twin is organised around what the student must decide. That decision is the same whether you teach NCERT, Cambridge, or another board.</p>" +
      "<p>AI is optional. Browse, retrieve, and papers work without it. Chemistry has the NCERT hinge map. Physics and biology use the published NCERT chapter list until a complete hinge map exists. Mix-ups stay off the learner paper.</p>" +
      "</div>" +
      "<h2 class='modules-head'>What it does</h2>" +
      "<div class='modules'>" +
      card("#browse", "Browse", "Walk the question bank by idea and year group. Items typeset as they would on a paper. Figures draw on the page.") +
      card("#prompt", "Prompt", "Say what you want in ordinary language. The twin returns the matching questions and the ideas they test.") +
      card("#lesson", "Lesson", "A briefing for class: the decision the student must make, the usual mix-ups, your notes, and a short plan.") +
      card("#paper", "Test maker", "Cut a paper. Modify any item (stem, options, figure). Take it as a student. Score and feedback stay off the printed paper.") +
      card("#journal", "Journal", "Keep notes and links. They attach to the idea you were teaching and come back on the lesson.") +
      card("#isogen", "ISO-GEN", "Describe the question you want, even if the idea is fuzzy. The twin drafts a candidate. It stays out of the exam pool until you accept it.") +
      card("#map", "Map", "Chemistry: hinges, mix-ups, pedagogy. Physics and biology: the published NCERT chapter list until a complete map exists.") +
      "</div>";
  }

  function card(href, title, body) {
    return "<a class='card module' href='" + href + "'><h2>" +
      esc(title) + "</h2><p>" + esc(body) + "</p></a>";
  }

  function filtersHTML(prefix) {
    return "<div class='card'><div class='row'>" +
      "<div><label>Subject</label><select id='" + prefix + "-subject'>" +
      (S.catalog || []).map((s) =>
        "<option value='" + esc(s.id) + "'" + (s.id === S.subject ? " selected" : "") + ">" +
        esc(s.label) + "</option>"
      ).join("") +
      "</select></div>" +
      "<div><label>Pack</label><select id='" + prefix + "-pack'>" +
      packOptions() + "</select></div>" +
      "<div><label>Big idea</label><select id='" + prefix + "-node'><option value=''>any</option>" +
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
      subject: ($(prefix + "-subject") && $(prefix + "-subject").value) || S.subject,
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
    const subjEl = $(prefix + "-subject");
    if (subjEl) {
      subjEl.addEventListener("change", async () => {
        const next = subjEl.value;
        if (next !== S.subject) {
          await loadSubject(next);
          const navSel = $("nav-subject");
          if (navSel) navSel.value = next;
          $(prefix + "-pack").innerHTML = packOptions();
          $(prefix + "-node").innerHTML = "<option value=''>any</option>" + nodeOptions();
        }
        fillChapters(prefix);
        onchange();
      });
    }
    ["pack", "node", "ch"].forEach((id) => {
      $(prefix + "-" + id).addEventListener("change", () => { fillChapters(prefix); onchange(); });
    });
    $(prefix + "-sub").addEventListener("change", onchange);
    fillChapters(prefix);
  }

  function renderBrowse() {
    $("hero").classList.add("hidden");
    const spec = S.spec || specOf(S.subject);
    $("app").innerHTML = "<p class='kicker'>Browse · " + esc((spec && spec.label) || S.subject) + "</p><h1>Five-click retrieve</h1>" +
      "<p class='sub'>Subject, pack, and big idea. Chapter and subtopic are the Cambridge coordinates already on the tagged corpus.</p>" +
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
        TTwinPaper.paperHTML({ title: "Question preview", subject: (S.spec && S.spec.label) || sel.subject, subtitle: [sel.subject, (sel.nodes || []).join(" ")].join(" · ") }, items) +
        (r.question_uids.length > 8 ? "<p class='muted no-print'>Showing 8 of " + r.question_uids.length + ". Use Test maker for a full paper.</p>" : "");
      TTwinPaper.mount($("br-out"));
    };
    bindFilters("br", () => { go(); });
    if (spec && spec.default_pack) $("br-pack").value = spec.default_pack;
    if (spec && spec.default_node) $("br-node").value = spec.default_node;
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
      const table = Object.assign({}, S.projection || {}, { subject: S.subject });
      const sel = TTwinRag.parsePromptDeterministic($("pr-text").value, table);
      sel.subject = S.subject;
      show(sel, "deterministic alias compile");
    };
    $("pr-kimi").onclick = async () => {
      $("pr-kimi").disabled = true;
      try {
        const sel = await TTwinKimi.inferSelector(
          $("pr-text").value,
          (S.vocab.ideas || []).map((n) => ({ id: n.id })),
          S.subject
        );
        if (sel && !sel.subject) sel.subject = S.subject;
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
  function mapUnits() {
    if (S.map && S.map.length) return S.map;
    if (S.subject === "chemistry") return S.hinges || [];
    return [];
  }
  function isoNodes() {
    if (S.subject === "chemistry" && (S.nodes || []).length) return S.nodes;
    return S.vocab.ideas || [];
  }
  function mapPackFor(r) {
    const units = mapUnits();
    const fromRetrieve = ((r && r.hinge_unit_ids) || []).filter(Boolean).slice(0, 8);
    const ids = fromRetrieve.length
      ? fromRetrieve
      : units.filter((h) => (S.vocab.ideas || []).some((n) => TTwinRag.nodesComparable(h.node_id || h.node, n.id))).slice(0, 8).map((h) => h.unit_id);
    return ids.map((id) => {
      const h = units.find((x) => x.unit_id === id);
      if (!h) return { unit_id: id };
      return {
        unit_id: h.unit_id,
        node: h.node || h.node_id,
        chapter: h.chapter_title || h.chapter,
        decision_hinge: h.decision_hinge,
        mechanism: h.mechanism,
        mx: (h.mx || []).slice(0, 4).map((m) => ({ type: m.type, cwo: m.cwo, status: m.status })),
        pedagogy: h.pedagogy
          ? { mastery_signal: h.pedagogy.mastery_signal, lok_folk: h.pedagogy.lok_folk }
          : null,
        status: h.status || null,
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
          : "<p class='muted'>No map units in this selector cap." +
            (S.mapStatus === "syllabus_interim" ? " Physics/biology Map is the published NCERT chapter list." : "") +
            "</p>") +
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
    const need = {};
    uids.forEach((u) => {
      const row = S.nav.find((r) => r.uid === u);
      if (row && row.pack) need[row.pack] = true;
    });
    for (const pack of Object.keys(need)) await ensurePack(pack);
    return uids.map((u) => S.stems[u] || S.nav.find((r) => r.uid === u) || { uid: u });
  }

  function cloneItem(it) {
    return JSON.parse(JSON.stringify(it));
  }
  function optionLetter(lab) {
    return TTwinPaper.optionLetter(lab);
  }
  function paperOpts() {
    const p = S.paper;
    if (!p) return {};
    const student = p.mode === "student";
    return {
      showUid: !student,
      teacherTools: !student,
      interactive: student,
      reveal: !!p.result,
      responses: p.responses || {},
    };
  }
  function paintPaper() {
    const p = S.paper;
    const host = $("tm-out");
    const mode = $("tm-mode");
    const studentBox = $("tm-student");
    const finish = $("tm-finish");
    if (!host) return;
    if (!p) {
      host.innerHTML = "";
      if (mode) mode.classList.add("hidden");
      paintScore();
      return;
    }
    if (mode) mode.classList.remove("hidden");
    if (studentBox) studentBox.checked = p.mode === "student";
    if (finish) finish.classList.toggle("hidden", p.mode !== "student" || !!p.result);
    host.innerHTML = TTwinPaper.paperHTML(p.meta, p.items, paperOpts());
    TTwinPaper.mount(host);
    paintScore();
  }
  function paintScore() {
    const slot = $("tm-score");
    if (!slot) return;
    const p = S.paper;
    if (!p || !p.result) {
      slot.innerHTML = "";
      return;
    }
    const sc = p.result.score;
    const fb = p.result.feedback;
    slot.innerHTML =
      "<div class='card score-card'>" +
      "<h2>Score</h2>" +
      "<p class='score-line'><b>" + sc.right + "</b> / " + sc.n +
      (sc.blank ? " · " + sc.blank + " unanswered" : "") +
      (sc.nokey ? " · " + sc.nokey + " without a key" : "") +
      "</p>" +
      (sc.honesty ? "<p class='muted'>" + esc(sc.honesty) + "</p>" : "") +
      (fb && fb.overall ? "<p>" + esc(fb.overall) + "</p>" : "") +
      (fb && fb.next_steps && fb.next_steps.length
        ? "<h3>Next</h3><ol>" + fb.next_steps.map((s) => "<li>" + esc(s) + "</li>").join("") + "</ol>"
        : "") +
      (fb && fb.per_item
        ? "<div class='fb-items'>" + fb.per_item.map((row) =>
          "<div class='q'><span class='tag'>" + esc(row.verdict || "") + "</span> " +
          "<span class='uid'>" + esc(row.uid || "") + "</span>" +
          (row.why ? "<p>" + esc(row.why) + "</p>" : "") +
          (row.teach ? "<p class='muted'>" + esc(row.teach) + "</p>" : "") +
          "</div>").join("") + "</div>"
        : "") +
      "</div>";
  }
  function scoreItems(items, responses) {
    let right = 0, blank = 0, nokey = 0;
    items.forEach((it) => {
      const uid = it.uid || it.item_uid;
      const ch = optionLetter(responses[uid]);
      const key = optionLetter(it.correct);
      if (!ch) { blank += 1; return; }
      if (!key) { nokey += 1; return; }
      if (ch === key) right += 1;
    });
    return { n: items.length, right, blank, nokey };
  }
  function itemIndex(uid) {
    return (S.paper.items || []).findIndex((it) => (it.uid || it.item_uid) === uid);
  }
  function replaceArticle(uid) {
    const host = $("tm-out");
    if (!host || !S.paper) return;
    const i = itemIndex(uid);
    if (i < 0) return;
    const sel = "article.q[data-uid=\"" + uid.replace(/\\/g, "\\\\").replace(/"/g, "\\\"") + "\"]";
    const art = host.querySelector(sel);
    const html = TTwinPaper.itemHTML(S.paper.items[i], i, paperOpts());
    if (art) {
      art.outerHTML = html;
      const next = host.querySelector(sel);
      TTwinPaper.mount(next || host);
    } else {
      paintPaper();
    }
  }
  async function applyModify(uid, prompt, statusEl, btn) {
    const i = itemIndex(uid);
    if (i < 0) return;
    const item = S.paper.items[i];
    if (btn) btn.disabled = true;
    try {
      const edited = await TTwinKimi.modifyItem(item, prompt, {
        subject: S.subject,
        onTick: (s) => { if (statusEl) statusEl.textContent = "Rewriting stem and options… " + s + "s"; },
      });
      const next = cloneItem(item);
      next.stem = edited.stem;
      next.options = edited.options;
      next.correct = edited.correct;
      next.rationale = edited.rationale;
      next.modified = true;
      if (!edited.tikz_unchanged) {
        next.tikz = edited.tikz;
        next.tikz_packages = edited.tikz_packages;
      }
      S.paper.items[i] = next;
      if (S.paper.result) S.paper.result = null;
      replaceArticle(uid);
      paintScore();
      const art = $("tm-out") && $("tm-out").querySelector("article.q[data-uid=\"" + uid.replace(/\\/g, "\\\\").replace(/"/g, "\\\"") + "\"]");
      const st = art && art.querySelector(".q-mod-status");
      if (st) st.textContent = "Updated stem, options" + (edited.correct ? ", key " + edited.correct : "") +
        (edited.tikz_unchanged ? "." : ", and figure.");
      if (art) {
        const box = art.querySelector(".q-mod");
        if (box) box.classList.remove("hidden");
      }
    } catch (e) {
      if (statusEl) statusEl.textContent = e.message;
    }
    if (btn) btn.disabled = false;
  }
  async function finishStudent() {
    const p = S.paper;
    if (!p) return;
    const btn = $("tm-finish");
    const status = $("tm-grade-status");
    if (btn) btn.disabled = true;
    try {
      const missing = p.items.filter((it) => !optionLetter(it.correct));
      let honesty = null;
      if (missing.length) {
        if (status) status.textContent = "Inferring keys for scoring (not a published mark scheme)…";
        try {
          const inferred = await TTwinKimi.inferKeys(missing, {
            subject: S.subject,
            onTick: (s) => { if (status) status.textContent = "Inferring keys… " + s + "s"; },
          });
          honesty = (inferred && inferred.honesty) ||
            "Keys for unmodified exam items are AI-inferred. This is not a published mark scheme.";
          const by = {};
          (inferred.keys || []).forEach((row) => { if (row && row.uid) by[row.uid] = row; });
          missing.forEach((it) => {
            const row = by[it.uid] || by[it.item_uid];
            const L = optionLetter(row && row.correct);
            if (L) {
              it.correct = L;
              it.key_inferred = true;
            }
          });
        } catch (e) {
          honesty = "Could not infer keys (" + e.message + "). Score uses only items that already had a key from Modify.";
        }
      } else {
        honesty = p.items.some((it) => it.modified)
          ? "Keys come from ISO-GEN Modify on this paper. Frozen exam papers are not a mark scheme."
          : "Keys were already on these items.";
      }
      const score = Object.assign(scoreItems(p.items, p.responses || {}), { honesty });
      let feedback = null;
      try {
        if (status) status.textContent = "Writing feedback…";
        feedback = await TTwinKimi.gradePaper(p.items, p.responses || {}, score, {
          subject: S.subject,
          onTick: (s) => { if (status) status.textContent = "Writing feedback… " + s + "s"; },
        });
      } catch (e) {
        feedback = { overall: "Score is ready. Feedback was not generated: " + e.message, per_item: [], next_steps: [] };
      }
      p.result = { score, feedback };
      p.mode = "student";
      paintPaper();
    } finally {
      if (btn) btn.disabled = false;
      if (status) status.textContent = "";
    }
  }
  function bindPaperHost() {
    const host = $("tm-out");
    if (!host || host.dataset.bound) return;
    host.dataset.bound = "1";
    host.addEventListener("click", (e) => {
      const p = S.paper;
      if (!p) return;
      const opt = e.target.closest("button.opt[data-opt]");
      if (opt && p.mode === "student" && !p.result) {
        const art = opt.closest("article.q");
        const uid = art && (art.getAttribute("data-uid") || (art.id || "").replace(/^q-/, ""));
        if (!uid) return;
        p.responses[uid] = opt.getAttribute("data-opt");
        art.querySelectorAll("button.opt[data-opt]").forEach((b) => {
          const on = b.getAttribute("data-opt") === p.responses[uid];
          b.setAttribute("aria-pressed", on ? "true" : "false");
          const li = b.closest("li");
          if (li) li.classList.toggle("sel", on);
        });
        return;
      }
      const open = e.target.closest(".q-mod-open");
      if (open) {
        const art = open.closest("article.q");
        const box = art && art.querySelector(".q-mod");
        if (box) box.classList.toggle("hidden");
        return;
      }
      const revert = e.target.closest(".q-mod-revert");
      if (revert) {
        const uid = revert.getAttribute("data-uid");
        const orig = (p.originals || []).find((it) => (it.uid || it.item_uid) === uid);
        const i = itemIndex(uid);
        if (orig && i >= 0) {
          p.items[i] = cloneItem(orig);
          if (p.result) p.result = null;
          replaceArticle(uid);
          paintScore();
        }
        return;
      }
      const go = e.target.closest(".q-mod-go");
      if (go) {
        const uid = go.getAttribute("data-uid");
        const art = go.closest("article.q");
        const ta = art && art.querySelector(".q-mod-text");
        const st = art && art.querySelector(".q-mod-status");
        const prompt = ((ta && ta.value) || "").trim();
        if (!prompt) {
          if (st) st.textContent = "Say what should change. Stem and all four options will be rewritten.";
          return;
        }
        applyModify(uid, prompt, st, go);
      }
    });
  }
  function renderPaper() {
    $("hero").classList.add("hidden");
    $("app").innerHTML = "<p class='kicker'>Test maker</p><h1>Assemble a question paper</h1>" +
      "<p class='sub'>Dropdown selector or a carried prompt retrieve. Shuffle is mulberry32 on the seed. Modify rewrites the whole item (stem, options, figure if needed) with ISO-GEN — text questions included. Take as student records A–D. Learner paper has no mx, no examiner comments, no crops.</p>" +
      filtersHTML("tm") +
      "<div class='card'><div class='row'>" +
      "<div><label>N questions</label><input id='tm-n' type='number' min='1' max='40' value='10'></div>" +
      "<div><label>Seed (empty = uid order)</label><input id='tm-seed' placeholder='optional'></div>" +
      "<div><label>Jump to uid</label><input id='tm-jump' placeholder='9701_m16_qp_12:q5'></div>" +
      "<div><label>Title</label><input id='tm-title' value='" + esc((S.spec && S.spec.label) || "Subject") + " paper'></div>" +
      "</div><p style='margin-top:10px'><button id='tm-go' type='button'>Make paper</button> " +
      "<button class='sec no-print' onclick='window.print()'>Print</button></p>" +
      "<div id='tm-mode' class='tm-mode no-print hidden'>" +
      "<label class='toggle'><input id='tm-student' type='checkbox'> Take this paper as a student</label> " +
      "<button id='tm-finish' class='sec hidden' type='button'>Finish and score</button> " +
      "<span class='muted' id='tm-grade-status'></span>" +
      "<p class='muted'>Student mode hides Modify and records A–B–C–D. Score uses Modify keys where you rewrote an item; otherwise keys are AI-inferred, not a published mark scheme.</p>" +
      "</div></div>" +
      "<div id='tm-score'></div>" +
      "<div id='tm-out'></div>";
    bindFilters("tm", () => {});
    bindPaperHost();
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
      const items = (await itemsForUids(ordered)).map(cloneItem);
      S.paper = {
        meta: {
          title: $("tm-title").value,
          subject: (S.spec && S.spec.label) || sel.subject,
          subtitle: (sel.nodes || []).join(" ") + " · " + (sel.pack || ""),
          seed,
        },
        items,
        originals: items.map(cloneItem),
        mode: "teacher",
        responses: {},
        result: null,
      };
      paintPaper();
    };
    $("tm-student").onchange = () => {
      if (!S.paper) return;
      S.paper.mode = $("tm-student").checked ? "student" : "teacher";
      if (S.paper.mode === "teacher") {
        /* keep responses and result */
      }
      paintPaper();
    };
    $("tm-finish").onclick = () => finishStudent();
    if (S.paper) paintPaper();
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
          const mapped = await TTwinKimi.mapJournalNote(text, mapUnits(), { subject: S.subject, mapStatus: S.mapStatus });
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
    return (ch && ch.indexOf("science/") !== 0 ? ch : ((S.spec && S.spec.label) || "Topic")) + " · " + band;
  }
  function teacherFacing(s) {
    return String(s || "")
      .replace(/science\/grade_\d+\/[^\s,;]+\/H\d+/g, "")
      .replace(/ncert\/grade_\d+\/[^\s,;]+/g, "")
      .replace(/\bchem:[A-Z][A-Z0-9/\-]+/g, "")
      .replace(/\bphy:[A-Z][A-Z0-9/\-]+/g, "")
      .replace(/\bbio:[A-Z][A-Z0-9/\-]+/g, "")
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
        const units = mapUnits();
        if (!units.length) {
          $("iso-out").innerHTML = "<div class='notice'>ISO-GEN needs a curriculum map. Chemistry has hinges. Physics and biology use the published NCERT chapter list. Mathematics does not have a map on this tab yet.</div>";
          $("iso-go").disabled = false;
          return;
        }
        const pasted = (idea.match(/science\/grade_\d+\/[^\s]+\/H\d+|ncert\/grade_\d+\/[^\s]+/) || [])[0];
        if (pasted && units.some((h) => h.unit_id === pasted)) {
          inferred = { intent: teacherFacing(idea) || idea, primary: { unit_id: pasted, why: null }, related: [], ask: null };
        } else {
          inferred = await TTwinKimi.inferIsoIntent(
            idea,
            units,
            isoNodes(),
            TTwinRag.parsePromptDeterministic(idea, S.projection),
            { subject: S.subject, mapStatus: S.mapStatus }
          );
        }
        if (!inferred || !(inferred.primary && inferred.primary.unit_id)) {
          $("iso-out").innerHTML = "<div class='notice'>" + esc(teacherFacing((inferred && inferred.ask) || "") || "Say a bit more: topic, year group, and what the student must decide.") + "</div>";
          $("iso-go").disabled = false;
          return;
        }
        const unit = inferred.primary.unit_id;
        const h = units.find((x) => x.unit_id === unit);
        if (!h) throw new Error("That idea did not land on a curriculum unit. Try another wording.");
        const pack = TTwinRag.hingePack(unit, units, S.subject === "chemistry" ? S.enrichment : []);
        S.lastPack = pack;
        const st = pack.statement || {};
        const relatedBits = (inferred.related || []).map((x) => {
          const rh = units.find((z) => z.unit_id === x.unit_id);
          return teacherFacing((rh && (rh.decision_hinge || rh.chapter_title)) || "");
        }).filter(Boolean);
        $("iso-out").innerHTML =
          "<div class='card'><h2>What we heard</h2><p>" + esc(teacherFacing(inferred.intent || idea)) + "</p>" +
          "<p><b>The student must:</b> " + esc(st.decision_hinge || "") + "</p>" +
          "<p class='muted'>" + esc(hingePlain(h)) +
          (inferred.primary.why ? " · " + esc(teacherFacing(inferred.primary.why)) : "") + "</p>" +
          (relatedBits.length ? "<p class='muted'>Also related: " + relatedBits.map(esc).join(" · ") + "</p>" : "") +
          "<h3 class='muted'>Likely mix-ups (unverified)</h3>" +
          ((st.mx || []).length
            ? (st.mx || []).map((m) => "<div class='mx'><b>" + esc(m.type || "") + "</b> " + esc(m.cwo || "") + "</div>").join("")
            : "<p class='muted'>" + (S.mapStatus === "syllabus_interim"
              ? "Mix-ups are empty on the syllabus-interim map. They appear once a complete hinge map exists."
              : "No mix-ups on this unit.") + "</p>") +
          "</div><p class='muted'>Authoring the question from that unit…</p><div id='iso-item'></div>";
        const specHash = await shaHex(JSON.stringify(S.lastPack.statement));
        const item = await TTwinKimi.authorItem(S.lastPack, inferred.intent || idea, {
          subject: S.subject,
          mapStatus: S.mapStatus,
        });
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
    const units = mapUnits();
    if (!units.length) {
      $("app").innerHTML = "<p class='kicker'>Map</p><h1>No curriculum map for " +
        esc((S.spec && S.spec.label) || S.subject) + "</h1>" +
        "<p class='sub'>Chemistry has the 523-hinge NCERT map. Physics and biology use the published NCERT chapter list. " +
        esc((S.spec && S.spec.label) || S.subject) + " currently has a tagged question bank (" +
        ((S.spec && S.spec.n_tagged) || 0) + " items) and browse vocab only.</p>" +
        "<p><a href='#browse'>Browse " + esc((S.spec && S.spec.label) || S.subject) + " questions</a></p>";
      return;
    }
    if (S.mapStatus === "syllabus_interim") {
      const byGrade = {};
      units.forEach((h) => {
        const g = h.grade || (h.grade_band === "SECONDARY" ? "9–10" : "11–12");
        (byGrade[g] || (byGrade[g] = [])).push(h);
      });
      const grades = Object.keys(byGrade).sort();
      $("app").innerHTML = "<p class='kicker'>NCERT syllabus (interim)</p><h1>" +
        esc((S.spec && S.spec.label) || S.subject) + " chapter list</h1>" +
        "<p class='sub'>Published NCERT chapter titles. This is the map until a complete hinge/mx map exists. Mix-ups are empty. Candidate chapter intelligence is not copied here.</p>" +
        "<p class='muted'>" + units.length + " chapters</p>" +
        grades.map((g) => {
          const rows = byGrade[g];
          const label = typeof g === "number" || /^\d+$/.test(String(g)) ? "Class " + g : String(g);
          return "<div class='card' style='margin:10px 0'><h2>" + esc(label) + " · " + rows.length + "</h2>" +
            rows.map((h) => "<div class='q'><span class='uid'>" + esc(h.unit_id) + "</span> " +
              "<b>" + esc(h.chapter_title || h.chapter) + "</b>" +
              (h.node_id ? " <span class='tag'>" + esc(h.node_id) + "</span>" : "") +
              "</div>").join("") +
            "</div>";
        }).join("");
      return;
    }
    const chemVocab = (S.vocab.ideas || []).length ? S.vocab.ideas : S.nodes.map((n) => ({ id: "chem:" + n.id, title: n.title }));
    $("app").innerHTML = "<p class='kicker'>NCERT comprehensive map</p><h1>Hinges, mx, pedagogy</h1>" +
      "<p class='sub'>523 NCERT statements. Big idea is a layer above the hinge. Pedagogy is joined from chapter intelligence; mx are CANDIDATE (v2).</p>" +
      "<div class='card'><div class='row'><div><label>Node</label><select id='mp-node'>" +
      chemVocab.map((n) => "<option value='" + esc(n.id) + "'>" + esc(n.id + " — " + (n.title || "")) + "</option>").join("") +
      "</select></div><div><label>Band</label><select id='mp-band'>" +
      "<option value=''>any</option><option value='SECONDARY'>Secondary</option>" +
      "<option value='SENIOR_SECONDARY' selected>Senior secondary</option></select></div></div></div>" +
      "<div id='mp-out'></div>";
    const go = () => {
      const node = $("mp-node").value;
      const band = $("mp-band").value;
      const rows = units.filter((h) => TTwinRag.nodesComparable(h.node_id || ("chem:" + h.node), node) && (!band || h.grade_band === band));
      $("mp-out").innerHTML = "<p class='muted'>" + rows.length + " hinges</p>" + rows.map((h) => {
        const ped = h.pedagogy || {};
        return "<div class='card' style='margin:10px 0'><div class='uid'>" + esc(h.unit_id) +
          " · " + esc(h.chapter_title || h.chapter) + "</div>" +
          "<p><b>" + esc(h.decision_hinge || "") + "</b></p>" +
          "<p class='muted'>" + esc(typeof h.mechanism === "string" ? h.mechanism : "") + "</p>" +
          (ped.mastery_signal ? "<p><span class='tag'>mastery</span> " + esc(ped.mastery_signal) + "</p>" : "") +
          (ped.lok_folk ? "<p><span class='tag'>LoK</span> " + esc(ped.lok_folk) + "</p>" : "") +
          (h.mx || []).map((m) => "<div class='mx'><b>" + esc(m.type) + "</b> " + esc(m.cwo || "") + "</div>").join("") +
          "</div>";
      }).join("");
    };
    $("mp-node").value = (S.spec && S.spec.default_node) || "chem:C6";
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
    bindNavSubject();
    const name = (location.hash || "#home").slice(1).split("/")[0] || "home";
    (VIEWS[name] || renderHome)();
    window.scrollTo(0, 0);
  }

  window.addEventListener("hashchange", route);
  boot();
})();
