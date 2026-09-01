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
    return "<ol class='opts' type='A'>" + keys.map((k) => "<li>" + chem(o[k]) + "</li>").join("") + "</ol>";
  }
  function statementsHTML(it) {
    const s = it.statements || [];
    if (!s.length) return "";
    return "<ol class='stmts'>" + s.map((x) => "<li>" + chem(x.text || x) + "</li>").join("") + "</ol>";
  }
  function itemHTML(it, i, opts) {
    const showUid = !opts || opts.showUid !== false;
    const fig = it.has_figure ? "<p class='muted'>Figure on the source paper (not reproduced here).</p>" : "";
    return (
      "<article class='item' id='q-" + esc(it.uid) + "'>" +
      "<div class='uid'>" + (i != null ? (i + 1) + ". " : "") +
      (showUid ? "<span class='uid'>" + esc(it.uid) + "</span>" : "") + "</div>" +
      "<p>" + chem(it.stem || it.stem_lead || "(no stem — tagged only)") + "</p>" +
      statementsHTML(it) + fig + optionsHTML(it) +
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
  g.TTwinPaper = { esc, chem, itemHTML, paperHTML };
})(window);
