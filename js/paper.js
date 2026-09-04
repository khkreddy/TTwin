(function (g) {
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function chem(s) {
    return esc(s)
      .replace(/&lt;u&gt;/gi, "<u>").replace(/&lt;\/u&gt;/gi, "</u>")
      .replace(/&lt;sub&gt;/gi, "<sub>").replace(/&lt;\/sub&gt;/gi, "</sub>")
      .replace(/&lt;sup&gt;/gi, "<sup>").replace(/&lt;\/sup&gt;/gi, "</sup>");
  }
  function optionTableOf(it) {
    return ((it && it.tables) || []).find((t) => t && t.is_option_table) || null;
  }
  function tableHTML(t, opts) {
    if (!t) return "";
    opts = opts || {};
    const headers = t.headers || [];
    const rows = t.rows || [];
    const labels = t.row_labels || [];
    const showLab = labels.length > 0;
    const interactive = !!opts.interactive;
    const chosen = optionLetter(opts.chosen);
    const reveal = !!opts.reveal;
    const key = optionLetter(opts.correct);
    const showHead = headers.some((h) => String(h || "").trim());
    const thead = showHead
      ? "<thead><tr>" + (showLab ? "<th></th>" : "") +
        headers.map((h) => "<th>" + chem(h) + "</th>").join("") + "</tr></thead>"
      : "";
    const body = rows.map((row, i) => {
      const L = optionLetter(labels[i]) || "";
      const cls = [];
      if (interactive && L) cls.push("opt-row");
      if (chosen && L && chosen === L) cls.push("sel");
      if (reveal && key && L === key) cls.push("key");
      if (reveal && chosen && L && chosen === L && key && chosen !== key) cls.push("miss");
      const attrs = [];
      if (cls.length) attrs.push("class='" + cls.join(" ") + "'");
      if (interactive && L) {
        attrs.push("data-opt='" + L + "'");
        attrs.push("tabindex='0'");
        attrs.push("role='button'");
        if (chosen === L) attrs.push("aria-pressed='true'");
      }
      return "<tr" + (attrs.length ? " " + attrs.join(" ") : "") + ">" +
        (showLab ? "<th>" + chem(labels[i] || "") + "</th>" : "") +
        (row || []).map((c) => "<td>" + chem(c) + "</td>").join("") +
        "</tr>";
    }).join("");
    const cls = "exam" + (t.is_option_table ? " opt-table" : "");
    return '<div class="fig">' +
      (t.caption ? '<div class="cap">' + chem(t.caption) + "</div>" : "") +
      "<table class='" + cls + "'>" + thead + "<tbody>" + body + "</tbody></table></div>";
  }
  function eqHTML(text) {
    const raw = String(text == null ? "" : text);
    if (/→\s*\(step\s*\d+\)/i.test(raw)) {
      const parts = raw.split(/→\s*\((step\s*\d+)\)/i);
      let html = '<div class="eq">';
      for (let i = 0; i < parts.length; i++) {
        const bit = (parts[i] || "").trim();
        if (!bit) continue;
        html += i % 2 === 0 ? chem(bit) : " → ";
      }
      return html + "</div>";
    }
    return '<div class="eq">' + chem(raw) + "</div>";
  }
  function optionLetter(lab) {
    if (lab == null || lab === "") return null;
    const u = String(lab).trim().toUpperCase();
    return /^[A-D]$/.test(u) ? u : null;
  }
  function partitionStructures(it) {
    const stem = [];
    const byOpt = { A: [], B: [], C: [], D: [] };
    (it.structures || []).forEach((s) => {
      const L = optionLetter(s.label);
      if (L) byOpt[L].push(s);
      else stem.push(s);
    });
    return { stem, byOpt };
  }
  function molCard(st, showLabel) {
    const lab = showLabel && st.label ? "<div class='lab'>" + esc(st.label) + "</div>" : "";
    return "<div class='smiles-card'>" + lab +
      "<svg class='mol' data-smiles='" + esc(st.smiles) + "' width='200' height='140'></svg></div>";
  }
  function structuresHTML(it) {
    const { stem } = partitionStructures(it);
    if (!stem.length) return "";
    return "<div class='smiles-row'>" + stem.map((s) => molCard(s, true)).join("") + "</div>";
  }
  function forTikzJax(code) {
    return String(code || "")
      .replace(/\\begin\{circuitikz\}/g, "\\begin{tikzpicture}")
      .replace(/\\end\{circuitikz\}/g, "\\end{tikzpicture}");
  }
  function splitTikzBlocks(code) {
    const t = forTikzJax(code);
    const blocks = [];
    const re = /\\begin\{tikzpicture\}[\s\S]*?\\end\{tikzpicture\}/g;
    let m;
    while ((m = re.exec(t))) blocks.push(m[0]);
    return blocks.length ? blocks : (t ? [t] : []);
  }
  function figHTML(it) {
    const code = String(it.tikz || "").trim();
    if (!code) return "";
    const pkgs = (it.tikz_packages || []).filter(Boolean);
    const pkgAttr = pkgs.length
      ? " data-packages='" + esc(JSON.stringify(Object.fromEntries(pkgs.map((p) => [p, ""])))) + "'"
      : "";
    return splitTikzBlocks(code).map(function (one) {
      return (
        "<div class='fig tikz-slot'" + pkgAttr + ">" +
        "<pre class='tikz-src' hidden>" + esc(one) + "</pre>" +
        "<p class='muted tikz-wait'>Drawing figure…</p>" +
        "</div>"
      );
    }).join("");
  }
  function statementsHTML(it) {
    const s = it.statements || [];
    if (!s.length) return "";
    return "<ol class='stmts'>" + s.map((x) => {
      const n = x && x.n != null ? x.n : "";
      const t = x && x.text != null ? x.text : x;
      return "<li>" + (n !== "" ? "<span class='n'>" + esc(n) + "</span> " : "") + chem(t) + "</li>";
    }).join("") + "</ol>";
  }
  function optionInner(it, k, o, byOpt) {
    const mols = (byOpt && byOpt[k]) || [];
    if (it.tikz && it.options_are_figure) return "";
    if (mols.length) {
      return "<div class='smiles-row'>" + mols.map((s) => molCard(s, false)).join("") + "</div>";
    }
    if (o[k] != null && o[k] !== "") return "<span>" + chem(o[k]) + "</span>";
    return "";
  }
  function optionsHTML(it, opts) {
    opts = opts || {};
    if (optionTableOf(it)) return "";
    const o = it.options || {};
    let keys = ["A", "B", "C", "D"].filter((k) =>
      (o[k] != null && o[k] !== "") ||
      ((it.structures || []).some((s) => optionLetter(s.label) === k))
    );
    if (!keys.length && it.tikz && it.options_are_figure) keys = ["A", "B", "C", "D"];
    if (!keys.length) return "";
    const { byOpt } = partitionStructures(it);
    const interactive = !!opts.interactive;
    const chosen = optionLetter(opts.chosen);
    const reveal = !!opts.reveal;
    const key = optionLetter(it.correct);
    const ulClass = interactive ? "options pick" : "options";
    return "<ul class='" + ulClass + "'>" + keys.map((k) => {
      const cls = [];
      if (interactive) cls.push("pick");
      if (chosen === k) cls.push("sel");
      if (reveal && key === k) cls.push("key");
      if (reveal && chosen === k && key && chosen !== key) cls.push("miss");
      const inner = optionInner(it, k, o, byOpt);
      const lab = "<span class='lab'>" + esc(k) + "</span> ";
      const body = interactive
        ? "<button type='button' class='opt' data-opt='" + k + "'" +
          (reveal ? " disabled" : "") + (chosen === k ? " aria-pressed='true'" : "") + ">" +
          lab + inner + "</button>"
        : lab + inner;
      return "<li" + (cls.length ? " class='" + cls.join(" ") + "'" : "") + ">" + body + "</li>";
    }).join("") + "</ul>";
  }
  function toolsHTML(it, opts) {
    if (!opts || !opts.teacherTools) return "";
    const uid = it.uid || it.item_uid || "";
    return "<div class='q-tools no-print'>" +
      "<button type='button' class='sec q-mod-open' data-uid='" + esc(uid) + "'>Modify</button>" +
      (it.modified ? "<span class='tag'>modified</span>" : "") +
      "<div class='q-mod hidden'>" +
      "<label>How should this item change?</label>" +
      "<textarea class='q-mod-text' placeholder='Change the numbers, the species, the figure, or the mix-up. Stem and all four options will be rewritten to match.'></textarea>" +
      "<p><button type='button' class='q-mod-go' data-uid='" + esc(uid) + "'>Apply modify</button> " +
      "<button type='button' class='sec q-mod-revert' data-uid='" + esc(uid) + "'>Revert</button> " +
      "<span class='muted q-mod-status'></span></p></div></div>";
  }
  function itemHTML(it, i, opts) {
    opts = opts || {};
    const n = i == null ? "" : (i + 1);
    const uid = it.uid || it.item_uid || "";
    const eqs = (it.equations || []).map(eqHTML).join("");
    const chosen = opts.responses ? opts.responses[uid] : opts.chosen;
    const optOpts = {
      interactive: opts.interactive,
      chosen: chosen,
      reveal: opts.reveal,
      correct: it.correct,
    };
    const stemTables = ((it.tables || []).filter((t) => !t.is_option_table)).map((t) => tableHTML(t)).join("");
    const optTable = optionTableOf(it);
    const optTableHtml = optTable ? tableHTML(optTable, optOpts) : "";
    return (
      "<article class='q' id='q-" + esc(uid) + "' data-uid='" + esc(uid) + "'>" +
      "<div><span class='qnum'>" + esc(n) + "</span>" +
      (opts.showUid === false ? "" : "<span class='uid'>" + esc(uid) + "</span>") +
      (it.modified && opts.showUid !== false ? " <span class='tag'>modified</span>" : "") +
      "</div>" +
      "<p class='stem'>" + chem(it.stem || it.stem_lead || "(no stem — tagged only)") + "</p>" +
      eqs + stemTables + figHTML(it) + structuresHTML(it) + statementsHTML(it) +
      optTableHtml + optionsHTML(it, optOpts) +
      toolsHTML(it, opts) +
      "</article>"
    );
  }
  function analysisHTML(it, i) {
    const a = it.analysis;
    if (!a) return "";
    const n = i + 1;
    const uid = it.uid || it.item_uid || "";
    const opts = a.options || {};
    const letters = ["A", "B", "C", "D"].filter((k) => opts[k] || (it.options && it.options[k]));
    const mapBits = [];
    if (a.map && a.map.chapter_title) mapBits.push(a.map.chapter_title);
    if (a.map && a.map.decision) mapBits.push(a.map.decision);
    return "<article class='key-q'>" +
      "<div><span class='qnum'>" + esc(n) + "</span> " +
      "<span class='tag'>" + esc(a.correct || it.correct || "?") + "</span> " +
      "<span class='uid'>" + esc(uid) + "</span></div>" +
      (a.rationale ? "<p>" + esc(a.rationale) + "</p>" : "") +
      (mapBits.length ? "<p class='muted'>" + mapBits.map(esc).join(" · ") + "</p>" : "") +
      letters.map((k) => {
        const row = opts[k] || {};
        const mx = (row.mx || []).map((m) => esc((m.type || "") + (m.cwo ? " — " + m.cwo : ""))).join("; ");
        const enr = (row.enrichment || []).map((e) => esc(e.statement || e.item_id || "")).join(" ");
        return "<div class='mx'><b>" + esc(k) + " · " + esc(row.role || "") + "</b> " +
          esc(row.why || "") +
          (mx ? "<div class='muted'>mx (unverified): " + mx + "</div>" : "") +
          (enr ? "<div class='muted'>enrichment: " + enr + "</div>" : "") +
          "</div>";
      }).join("") +
      (a.honesty ? "<p class='muted'>" + esc(a.honesty) + "</p>" : "") +
      "</article>";
  }
  function answerKeyHTML(meta, items) {
    const title = (meta && meta.title) || "Paper";
    const head =
      "<div class='hdr'><div class='board'>Teacher's Twin</div>" +
      "<div class='subj'>Answer key</div>" +
      "<div class='papername'>" + esc(title) + "</div>" +
      "<p class='cap'>Teacher sheet · not a published mark scheme · mix-ups unverified · not printed on the learner paper</p></div><hr class='rule'/>";
    const rows = (items || []).map((it, i) => analysisHTML(it, i)).join("");
    return "<div class='paper answer-key'>" + head +
      (rows || "<p class='muted'>No stored analysis yet.</p>") +
      "</div>";
  }
  function paperHTML(meta, items, opts) {
    opts = opts || {};
    const title = meta.title || "Paper";
    const subj = meta.subject || "Questions";
    const head =
      "<div class='hdr'><div class='board'>Teacher's Twin</div>" +
      "<div class='subj'>" + esc(subj) + "</div>" +
      "<div class='papername'>" + esc(title) + "</div>" +
      "<p class='cap'>" + esc(meta.subtitle || "") + " · " + items.length + " questions" +
      (meta.seed ? " · seed " + esc(meta.seed) : "") + "</p></div><hr class='rule'/>";
    const itemOpts = Object.assign({ showUid: true }, opts);
    const learner = "<div class='paper'>" + head + items.map((it, i) => itemHTML(it, i, itemOpts)).join("") + "</div>";
    const key = opts && opts.withKey && !opts.interactive ? answerKeyHTML(meta, items) : "";
    return learner + key;
  }
  function mountTikz(root) {
    root.querySelectorAll(".tikz-slot").forEach((slot) => {
      if (slot.querySelector("script[type='text/tikz'], svg.tikz, svg.tikzjax, .tikzjax-wrapper")) return;
      const pre = slot.querySelector(".tikz-src");
      if (!pre) return;
      const s = document.createElement("script");
      s.type = "text/tikz";
      const pkgs = slot.getAttribute("data-packages");
      if (pkgs) s.setAttribute("data-tex-packages", pkgs);
      s.textContent = forTikzJax(pre.textContent);
      const wait = slot.querySelector(".tikz-wait");
      if (wait) wait.remove();
      pre.remove();
      slot.appendChild(s);
    });
  }
  function drawOneMol(el) {
    const smi = el.getAttribute("data-smiles");
    if (!smi || el.dataset.drawn) return;
    el.dataset.drawn = "1";
    try {
      if (window.SmiDrawer) {
        new SmiDrawer({ width: 200, height: 140 }).draw(smi, el);
        return;
      }
    } catch (e) { /* fall through */ }
    try {
      if (window.SmilesDrawer && SmilesDrawer.SvgDrawer && SmilesDrawer.parse) {
        const drawer = new SmilesDrawer.SvgDrawer({ width: 200, height: 140, compactDrawing: false });
        SmilesDrawer.parse(smi, function (tree) {
          drawer.draw(tree, el, "light", false);
        }, function () { el.removeAttribute("data-smiles"); });
        return;
      }
    } catch (e) { /* ignore */ }
  }
  function mountSmiles(root) {
    root.querySelectorAll("[data-smiles]").forEach(drawOneMol);
  }
  function mount(root) {
    if (!root) return;
    mountTikz(root);
    mountSmiles(root);
  }
  g.TTwinPaper = { esc, chem, itemHTML, paperHTML, answerKeyHTML, mount, optionLetter, optionTableOf };
})(window);
