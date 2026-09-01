(function (g) {
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function chem(s) {
    return esc(s)
      .replace(/&lt;sub&gt;/gi, "<sub>").replace(/&lt;\/sub&gt;/gi, "</sub>")
      .replace(/&lt;sup&gt;/gi, "<sup>").replace(/&lt;\/sup&gt;/gi, "</sup>");
  }
  function optionsHTML(it) {
    const o = it.options || {};
    const keys = Object.keys(o).sort();
    if (!keys.length) return "";
    if (it.options_are_figure && it.tikz) {
      return "<div class='opt-labs'>" + keys.map((k) => "<span class='tag'>" + esc(k) + "</span>").join(" ") + "</div>";
    }
    return "<ol class='opts' type='A'>" + keys.map((k) => "<li>" + chem(o[k]) + "</li>").join("") + "</ol>";
  }
  function statementsHTML(it) {
    const s = it.statements || [];
    if (!s.length) return "";
    return "<ol class='stmts'>" + s.map((x) => "<li>" + chem(x.text || x) + "</li>").join("") + "</ol>";
  }
  function figHTML(it) {
    const code = String(it.tikz || "").trim();
    if (!code) {
      return it.has_figure
        ? "<p class='muted'>Figure encoding is not in this pack.</p>"
        : "";
    }
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
  function itemHTML(it, i, opts) {
    const showUid = !opts || opts.showUid !== false;
    return (
      "<article class='item' id='q-" + esc(it.uid) + "'>" +
      "<div class='uid'>" + (i != null ? (i + 1) + ". " : "") +
      (showUid ? "<span class='uid'>" + esc(it.uid) + "</span>" : "") + "</div>" +
      "<p>" + chem(it.stem || it.stem_lead || "(no stem — tagged only)") + "</p>" +
      statementsHTML(it) + figHTML(it) + optionsHTML(it) +
      "</article>"
    );
  }
  function paperHTML(meta, items) {
    const title = meta.title || "TeacherTwin paper";
    const head =
      "<header><p class='kicker'>TeacherTwin · NCERT chemistry</p>" +
      "<h1>" + esc(title) + "</h1>" +
      "<p class='muted'>" + esc(meta.subtitle || "") + " · " + items.length + " items" +
      (meta.seed ? " · seed " + esc(meta.seed) : "") + "</p></header>";
    return "<div class='paper-sheet'>" + head + items.map((it, i) => itemHTML(it, i, { showUid: true })).join("") + "</div>";
  }
  function mount(root) {
    if (!root) return;
    root.querySelectorAll(".tikz-slot").forEach((slot) => {
      if (slot.querySelector("script[type='text/tikz'], svg.tikz, svg.tikzjax, .tikzjax-wrapper")) return;
      const pre = slot.querySelector(".tikz-src");
      if (!pre) return;
      const s = document.createElement("script");
      s.type = "text/tikz";
      const pkgs = slot.getAttribute("data-packages");
      if (pkgs) s.setAttribute("data-tex-packages", pkgs);
      const libs = slot.getAttribute("data-tikz-libraries");
      if (libs) s.setAttribute("data-tikz-libraries", libs);
      s.textContent = pre.textContent;
      const wait = slot.querySelector(".tikz-wait");
      if (wait) wait.remove();
      pre.remove();
      slot.appendChild(s);
    });
  }
  g.TTwinPaper = { esc, chem, itemHTML, paperHTML, mount };
})(window);
