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
  function looksLikeDisplayed(text) {
    return /displayed structure|structure of/i.test(String(text || ""));
  }
  function tableHTML(t) {
    if (!t) return "";
    const headers = t.headers || [];
    const rows = t.rows || [];
    const labels = t.row_labels || [];
    const showLab = labels.length > 0;
    return '<div class="fig"><table class="exam"><thead><tr>' +
      (showLab ? "<th></th>" : "") +
      headers.map((h) => "<th>" + chem(h) + "</th>").join("") +
      "</tr></thead><tbody>" +
      rows.map((row, i) => {
        return "<tr>" + (showLab ? "<th>" + chem(labels[i] || "") + "</th>" : "") +
          (row || []).map((c) => "<td>" + chem(c) + "</td>").join("") +
          "</tr>";
      }).join("") +
      "</tbody></table>" +
      (t.caption ? '<div class="cap">' + chem(t.caption) + "</div>" : "") +
      "</div>";
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
  function molCard(st) {
    const lab = st.label ? "<div class='lab'>" + esc(st.label) + "</div>" : "";
    return "<div class='smiles-card'>" + lab +
      "<svg class='mol' data-smiles='" + esc(st.smiles) + "' width='200' height='140'></svg></div>";
  }
  function structuresHTML(it) {
    const sts = it.structures || [];
    if (!sts.length) return "";
    const asOptions = sts.every((s) => s.label && /^[A-D]$/i.test(String(s.label)));
    if (asOptions) return "";
    return "<div class='smiles-row'>" + sts.map(molCard).join("") + "</div>";
  }
  function figHTML(it) {
    const code = String(it.tikz || "").trim();
    if (!code) return "";
    const pkgs = (it.tikz_packages || []).filter(Boolean);
    const pkgAttr = pkgs.length
      ? " data-packages='" + esc(JSON.stringify(Object.fromEntries(pkgs.map((p) => [p, ""])))) + "'"
      : "";
    return (
      "<div class='fig tikz-slot'" + pkgAttr + ">" +
      "<pre class='tikz-src' hidden>" + esc(code) + "</pre>" +
      "<p class='muted tikz-wait'>Drawing figure…</p>" +
      "</div>"
    );
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
  function optionsHTML(it) {
    const o = it.options || {};
    const keys = ["A", "B", "C", "D"].filter((k) => o[k] != null && o[k] !== "");
    const sts = it.structures || [];
    const byLab = {};
    sts.forEach((s) => { if (s.label) byLab[String(s.label).toUpperCase()] = s; });
    const structOpts = keys.length && keys.every((k) => byLab[k]);
    if (it.tikz && it.options_are_figure) {
      return "<ul class='options'>" + keys.map((k) =>
        "<li><span class='lab'>" + esc(k) + "</span></li>").join("") + "</ul>";
    }
    if (structOpts) {
      return "<ul class='options'>" + keys.map((k) =>
        "<li><span class='lab'>" + esc(k) + "</span>" + molCard(byLab[k]) + "</li>"
      ).join("") + "</ul>";
    }
    if (!keys.length) return "";
    return "<ul class='options'>" + keys.map((k) => {
      const txt = looksLikeDisplayed(o[k]) && byLab[k]
        ? molCard(byLab[k])
        : "<span>" + chem(o[k]) + "</span>";
      return "<li><span class='lab'>" + esc(k) + "</span> " + txt + "</li>";
    }).join("") + "</ul>";
  }
  function itemHTML(it, i, opts) {
    const n = i == null ? "" : (i + 1);
    const uid = it.uid || it.item_uid || "";
    const eqs = (it.equations || []).map(eqHTML).join("");
    const tables = (it.tables || []).map(tableHTML).join("");
    return (
      "<article class='q' id='q-" + esc(uid) + "'>" +
      "<div><span class='qnum'>" + esc(n) + "</span>" +
      (opts && opts.showUid === false ? "" : "<span class='uid'>" + esc(uid) + "</span>") +
      "</div>" +
      "<p class='stem'>" + chem(it.stem || it.stem_lead || "(no stem — tagged only)") + "</p>" +
      eqs + tables + figHTML(it) + structuresHTML(it) + statementsHTML(it) + optionsHTML(it) +
      "</article>"
    );
  }
  function paperHTML(meta, items) {
    const title = meta.title || "Chemistry";
    const head =
      "<div class='hdr'><div class='board'>TeacherTwin</div>" +
      "<div class='subj'>Chemistry</div>" +
      "<div class='papername'>" + esc(title) + "</div>" +
      "<p class='cap'>" + esc(meta.subtitle || "") + " · " + items.length + " questions" +
      (meta.seed ? " · seed " + esc(meta.seed) : "") + "</p></div><hr class='rule'/>";
    return "<div class='paper'>" + head + items.map((it, i) => itemHTML(it, i, { showUid: true })).join("") + "</div>";
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
      s.textContent = pre.textContent;
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
  g.TTwinPaper = { esc, chem, itemHTML, paperHTML, mount };
})(window);
