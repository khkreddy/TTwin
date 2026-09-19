(function (g) {
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function texHTML(tex, display) {
    const src = String(tex || "").replace(/&amp;/g, "&");
    const disp = !!display || /\\begin\{(?:array|pmatrix|bmatrix|vmatrix|cases|aligned|gather|matrix)\}/.test(src);
    const engine = g.katex;
    if (engine && typeof engine.renderToString === "function") {
      try {
        const html = engine.renderToString(src, {
          throwOnError: false,
          displayMode: disp,
          output: "html",
          strict: "ignore",
        });
        return disp ? "<div class='eq'>" + html + "</div>" : html;
      } catch (e) { /* fall through */ }
    }
    return "<span class='tex'>" + esc(src) + "</span>";
  }
  function protectCurrency(s) {
    // Keep $10$ as TeX; do not treat $10,000 or $4.50 as math delimiters.
    return String(s == null ? "" : s)
      .replace(/\$(\d{1,3}(?:,\d{3})+(?:\.\d+)?)/g, "\u00A4$1")
      .replace(/\$(\d+\.\d{2})(?!\$)/g, "\u00A4$1");
  }
  function restoreCurrency(s) {
    return String(s == null ? "" : s).replace(/\u00A4/g, "$");
  }
  function chem(s) {
    const raw = protectCurrency(String(s == null ? "" : s).replace(/\(cid:\d+\)/g, ""));
    const re = /\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|\$([^$]+?)\$/g;
    let html = "", last = 0, m;
    while ((m = re.exec(raw))) {
      if (m.index > last) html += inlineHTML(raw.slice(last, m.index));
      const tex = m[1] || m[2] || m[3] || m[4] || "";
      html += texHTML(tex, !!(m[1] || m[2]));
      last = m.index + m[0].length;
    }
    html += inlineHTML(raw.slice(last));
    return restoreCurrency(html);
  }
  function inlineHTML(s) {
    return esc(s)
      .replace(/&lt;u&gt;/gi, "<u>").replace(/&lt;\/u&gt;/gi, "</u>")
      .replace(/&lt;sub&gt;/gi, "<sub>").replace(/&lt;\/sub&gt;/gi, "</sub>")
      .replace(/&lt;sup&gt;/gi, "<sup>").replace(/&lt;\/sup&gt;/gi, "</sup>");
  }
  function coerceTable(t) {
    if (!t) return null;
    if (typeof t === "string") {
      const s = t.trim();
      if (!s) return null;
      try { t = JSON.parse(s); } catch (e) { return null; }
    }
    if (typeof t !== "object") return null;
    const labels = (t.row_labels || []).slice();
    if (t.is_option_table && labels.length && !labels.some((L) => /^[A-D]$/i.test(String(L || "")))) {
      t = Object.assign({}, t, {
        row_labels: (t.rows || []).map((_, i) => String.fromCharCode(65 + i)),
      });
    }
    return t;
  }
  function optionTableOf(it) {
    const tables = ((it && it.tables) || []).map(coerceTable).filter(Boolean);
    return tables.find((t) => t && t.is_option_table) || null;
  }
  function isFigureGridTable(t) {
    if (!t || t.is_option_table) return false;
    if ((t.headers || []).some((h) => String(h || "").trim())) return false;
    const rows = t.rows || [];
    const cells = [];
    rows.forEach((row) => { (row || []).forEach((c) => cells.push(c)); });
    if (cells.length < 16) return false;
    let blank = 0;
    for (let i = 0; i < cells.length; i++) {
      const s = String(cells[i] == null ? "" : cells[i]).trim();
      if (!s || s === "-" || s === "—" || /^blank$/i.test(s)) {
        blank++;
        continue;
      }
      if (!/^[A-DWXYZ1-9]$/i.test(s)) return false;
    }
    return blank / cells.length >= 0.7;
  }
  function tableHTML(t, opts) {
    t = coerceTable(t);
    if (!t) return "";
    opts = opts || {};
    const headers = t.headers || [];
    const rows = t.rows || [];
    const labels = t.row_labels || [];
    const showLab = labels.length > 0;
    const interactive = !!opts.interactive;
    const chosen = optionLetter(opts.chosen);
    const reveal = !!opts.reveal;
    const locked = reveal || !!opts.lbsLocked;
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
      if (interactive && L && !locked) {
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
  function extractedKey(it) {
    const a = it && it.assessment;
    if (a && a.key_status === "available") {
      const k = optionLetter(a.mcq_key);
      if (k) return k;
    }
    return optionLetter(it && it.correct);
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
    // One visual only. Exam crop (figure_src) wins when packed; else TikZ.
    const src = String(it.figure_src || "").trim();
    if (src) {
      return "<div class='fig'><img class='orig' src='" + esc(src) + "' alt='exam figure'></div>";
    }
    const rawTikz = it.tikz;
    const code = (Array.isArray(rawTikz) ? rawTikz.join("\n") : String(rawTikz || "")).trim();
    if (!code) return "";
    const pkgs = ((it.tikz_packages || []).filter(Boolean)).slice();
    if (!pkgs.length && (/\\begin\{circuitikz\}/.test(code) || /to\s*\[(battery|lamp|short|nos|switch)/i.test(code))) {
      pkgs.push("circuitikz");
    }
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
  function marksHTML(m) {
    return (typeof m === "number") ? " <span class='marks'>[" + m + "]</span>" : "";
  }
  function leadInStem(it) {
    let stem = String(it.stem || it.stem_lead || "");
    const parts = it.parts || [];
    if (!stem || !parts.length) return stem;
    let first = null;
    for (let i = 0; i < parts.length; i++) {
      const p = parts[i];
      if (!p || typeof p !== "object") continue;
      if (!first) first = p;
      if (String(p.id || "").trim()) { first = p; break; }
    }
    if (!first) return stem;
    const pid = String(first.id || "").trim();
    let cut = -1;
    if (pid) {
      const re = new RegExp(
        "(?:^|\\n)(?:[ \\t]*\\d+[ \\t]+)?[ \\t]*\\(" +
          pid.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") +
          "\\)(?:[ \\t\\n]|\\(|$)",
        "i"
      );
      const m = re.exec(stem);
      if (m) cut = m.index;
    }
    let key = String(first.stem || "").trim().split("\n")[0].trim();
    key = key.replace(/^\([a-z0-9ivx]+\)\s*/i, "");
    if (key.length >= 24) {
      const idx = stem.indexOf(key.slice(0, 80));
      if (idx > 0 && (cut < 0 || idx < cut)) cut = idx;
    }
    if (cut < 0) return stem;
    return stem.slice(0, cut).replace(/\s+$/, "");
  }
  function partsHTML(it) {
    const parts = it.parts || [];
    if (!parts.length) return "";
    return "<ol class='parts'>" + parts.map((p) => {
      if (!p || typeof p !== "object") return "";
      const id = p.id != null && String(p.id).trim() !== "" ? String(p.id) : "";
      const lab = id ? "<span class='part-id'>(" + esc(id) + ")</span> " : "";
      let inner = "<li>" + lab + chem(p.stem || p.text || "") + marksHTML(p.marks);
      const popts = p.options || [];
      if (popts.length) {
        inner += "<ol class='options'>";
        popts.forEach((o) => {
          const id = (typeof o === "string") ? "" : (o && o.id) || "";
          const tx = (typeof o === "string") ? o : (o && o.text) || "";
          inner += "<li>" + (id ? "<span class='opt-id'>" + esc(id) + "</span> " : "") + chem(tx) + "</li>";
        });
        inner += "</ol>";
      }
      const sub = p.subparts || [];
      if (sub.length) {
        inner += "<ol class='subparts'>" + sub.map((sp) => {
          const sid = sp && sp.id != null && String(sp.id).trim() !== "" ? String(sp.id) : "";
          const slab = sid ? "<span class='part-id'>(" + esc(sid) + ")</span> " : "";
          return "<li>" + slab + chem((sp && sp.stem) || "") + marksHTML(sp && sp.marks) + "</li>";
        }).join("") + "</ol>";
      }
      return inner + "</li>";
    }).join("") + "</ol>";
  }
  function optionInner(it, k, o, byOpt) {
    const mols = (byOpt && byOpt[k]) || [];
    if ((it.tikz || it.figure_src) && it.options_are_figure) return "";
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
    if (it.options_are_figure && (it.tikz || it.figure_src)) keys = ["A", "B", "C", "D"];
    if (!keys.length) return "";
    const { byOpt } = partitionStructures(it);
    const interactive = !!opts.interactive;
    const chosen = optionLetter(opts.chosen);
    const reveal = !!opts.reveal;
    const key = extractedKey(it);
    const ulClass = interactive ? "options pick" : "options";
    return "<ul class='" + ulClass + "'>" + keys.map((k) => {
      const cls = [];
      if (interactive) cls.push("pick");
      if (chosen === k) cls.push("sel");
      if (reveal && key === k) cls.push("key");
      if (reveal && chosen === k && key && chosen !== key) cls.push("miss");
      const inner = optionInner(it, k, o, byOpt);
      const lab = "<span class='lab'>" + esc(k) + "</span> ";
      const locked = reveal || !!(opts.lbsLocked);
      const body = interactive
        ? "<button type='button' class='opt' data-opt='" + k + "'" +
          (locked ? " disabled" : "") + (chosen === k ? " aria-pressed='true'" : "") + ">" +
          lab + inner + "</button>"
        : lab + inner;
      return "<li" + (cls.length ? " class='" + cls.join(" ") + "'" : "") + ">" + body + "</li>";
    }).join("") + "</ul>";
  }
  function toolsHTML(it, opts) {
    if (!opts || !opts.teacherTools) return "";
    const uid = it.uid || it.item_uid || "";
    const seeds = (it.assessment && it.assessment.modify_seeds) || [];
    const seedBtns = seeds.length
      ? "<p class='mod-seeds'>" + seeds.map(function (s, i) {
          return "<button type='button' class='sec q-mod-seed' data-uid='" + esc(uid) +
            "' data-seed='" + i + "'>" + esc(s.label || ("seed " + (i + 1))) + "</button>";
        }).join(" ") + "</p>"
      : "";
    return "<div class='q-tools no-print'>" +
      "<button type='button' class='sec q-mod-open' data-uid='" + esc(uid) + "'>Modify</button>" +
      (it.modified ? "<span class='tag'>modified</span>" : "") +
      "<div class='q-mod hidden'>" +
      "<label>How should this item change?</label>" +
      seedBtns +
      "<textarea class='q-mod-text' placeholder='Change the numbers, the species, the figure, or the mix-up. Stem and all four options will be rewritten to match. Or pick a mix-up seed above.'></textarea>" +
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
      correct: extractedKey(it),
    };
    const hasDrawnFig = !!(String(it.figure_src || "").trim() || it.tikz);
    const stemTables = ((it.tables || []).map(coerceTable).filter((t) => {
      if (!t || t.is_option_table) return false;
      if (hasDrawnFig && isFigureGridTable(t)) return false;
      return true;
    })).map((t) => tableHTML(t)).join("");
    const optTable = optionTableOf(it);
    const optTableHtml = optTable ? tableHTML(optTable, optOpts) : "";
    const stage = (opts.lbsStage || {})[uid] || {};
    if (stage.from && !stage.done && !stage.retry) optOpts.lbsLocked = true;
    if (stage.done || stage.retry) optOpts.chosen = null;
    return (
      "<article class='q' id='q-" + esc(uid) + "' data-uid='" + esc(uid) + "'>" +
      "<div><span class='qnum'>" + esc(n) + "</span>" +
      (opts.showUid === false ? "" : "<span class='uid'>" + esc(uid) + "</span>") +
      (it.modified && opts.showUid !== false ? " <span class='tag'>modified</span>" : "") +
      "</div>" +
      (function () {
        const lead = leadInStem(it);
        const more = it.assessment && (it.assessment.one_or_more ||
          (typeof it.assessment.mcq_key === "string" && it.assessment.mcq_key.length > 1));
        const note = more ? "<p class='muted exam-note'>One or more options may be correct.</p>" : "";
        if (lead) return "<p class='stem'>" + chem(lead) + "</p>" + note;
        if ((it.parts || []).length) return note;
        return "<p class='stem'>" + chem("(no stem — tagged only)") + "</p>" + note;
      })() +
      eqs + stemTables + figHTML(it) + structuresHTML(it) + statementsHTML(it) +
      partsHTML(it) +
      optTableHtml + optionsHTML(it, optOpts) +
      followupHTML(it, opts) +
      toolsHTML(it, opts) +
      "</article>"
    );
  }
  function fuFormat(fu) {
    return (fu && fu.format) || "single_mcq";
  }
  function fuKeyLabel(fu) {
    const k = fu && fu.key;
    if (k == null || k === "") return "—";
    if (Array.isArray(k)) return k.join(", ");
    if (typeof k === "object") {
      return Object.keys(k).map(function (id) { return id + "→" + k[id]; }).join(", ");
    }
    return String(k);
  }
  function fuChoiceList(choice) {
    if (choice == null) return [];
    if (Array.isArray(choice)) return choice.map((x) => String(x));
    return [String(choice)];
  }
  function fuOptButtons(fu, stage, letters) {
    const reveal = !!stage.done;
    const chosen = fuChoiceList(stage.followup_choice);
    const fmt = fuFormat(fu);
    const keyRaw = fu.key;
    const keys = fmt === "multi_mcq"
      ? fuChoiceList(keyRaw).map(String)
      : [String(keyRaw == null ? "" : keyRaw)];
    const optsMap = fu.options || {};
    const use = (letters || Object.keys(optsMap)).filter((k) => String(optsMap[k] || "").trim() !== "");
    const toggle = fmt === "multi_mcq" && !reveal;
    return "<ul class='options pick'>" + use.map((k) => {
      const cls = [];
      const on = chosen.indexOf(k) >= 0 || chosen.indexOf(String(k)) >= 0;
      if (on) cls.push("sel");
      if (reveal && keys.indexOf(k) >= 0) cls.push("key");
      if (reveal && on && keys.indexOf(k) < 0) cls.push("miss");
      const attr = toggle ? "data-fu-toggle='" + k + "'" : "data-fu-opt='" + k + "'";
      return "<li" + (cls.length ? " class='" + cls.join(" ") + "'" : "") + ">" +
        "<button type='button' class='opt' " + attr + (reveal ? " disabled" : "") +
        (on ? " aria-pressed='true'" : "") + ">" +
        "<span class='lab'>" + esc(k) + "</span> " + chem(optsMap[k] || "") + "</button></li>";
    }).join("") + "</ul>";
  }
  function fuSelect(name, attr, choices, selected) {
    const opts = ["<option value=''>—</option>"].concat(
      (choices || []).map((c) => {
        const v = (c && typeof c === "object") ? String(c.value) : String(c);
        const lab = (c && typeof c === "object") ? String(c.label) : String(c);
        return "<option value='" + esc(v) + "'" + (selected === v ? " selected" : "") + ">" +
          chem(lab) + "</option>";
      })
    );
    return "<select " + attr + " data-fu-field='" + esc(name) + "'>" +
      opts.join("") + "</select>";
  }
  function followupBody(fu, stage, uid) {
    const fmt = fuFormat(fu);
    const reveal = !!stage.done;
    const choice = stage.followup_choice;
    if (fmt === "true_false") {
      const opts = fu.options && Object.keys(fu.options).length
        ? fu.options
        : { T: "True", F: "False" };
      const order = ["T", "F", "A", "B"].filter((k) => opts[k] != null);
      return "<p class='stem'>" + chem(fu.stem || "") + "</p>" +
        fuOptButtons(Object.assign({}, fu, { options: opts }), stage, order);
    }
    if (fmt === "assertion_reason") {
      let html = "<p class='stem'>" + chem(fu.stem || "Assertion and reason") + "</p>";
      html += "<div class='lbs-ar'><p><b>Assertion (A).</b> " + chem(fu.assertion || "") + "</p>";
      html += "<p><b>Reason (R).</b> " + chem(fu.reason || "") + "</p></div>";
      const opts = fu.options || {
        A: "Both A and R are true, and R is the correct explanation of A",
        B: "Both A and R are true, but R is not the correct explanation of A",
        C: "A is true, but R is false",
        D: "A is false, but R is true"
      };
      return html + fuOptButtons(Object.assign({}, fu, { options: opts }), stage, ["A", "B", "C", "D"]);
    }
    if (fmt === "multi_mcq") {
      let html = "<p class='stem'>" + chem(fu.stem || "") + "</p>";
      html += "<p class='muted'>Select every statement that applies, then check the hint.</p>";
      html += fuOptButtons(fu, stage);
      if (!reveal) {
        html += "<button type='button' class='lbs-submit' data-fu-submit='multi'>Check this hint</button>";
      }
      return html;
    }
    if (fmt === "match") {
      const left = fu.left || {};
      const right = fu.right || {};
      const rightKeys = Object.keys(right);
      const picked = (choice && typeof choice === "object" && !Array.isArray(choice)) ? choice : {};
      const choices = rightKeys.map((k) => ({ value: k, label: k + " · " + right[k] }));
      let html = "<p class='stem'>" + chem(fu.stem || "Match each item") + "</p>";
      html += "<table class='lbs-match'><tbody>";
      Object.keys(left).forEach((id) => {
        const sel = picked[id] || "";
        html += "<tr><th>" + esc(id) + ". " + chem(left[id] || "") + "</th><td>" +
          fuSelect("match-" + id, "data-fu-match='" + esc(id) + "'", choices, sel) +
          "</td></tr>";
      });
      html += "</tbody></table>";
      if (!reveal) html += "<button type='button' class='lbs-submit' data-fu-submit='match'>Check this hint</button>";
      return html;
    }
    if (fmt === "fill_blank") {
      const terms = fu.terms || [];
      const picked = (choice && typeof choice === "object" && !Array.isArray(choice)) ? choice : {};
      const raw = fu.stem || "";
      if (!/\[\[\w+\]\]/.test(raw)) {
        return followupBody(Object.assign({}, fu, { stem: raw + " [[1]]" }), stage, uid);
      }
      let html = "<p class='stem lbs-fill'>";
      raw.split(/(\[\[\w+\]\])/).forEach((part) => {
        const m = part.match(/^\[\[(\w+)\]\]$/);
        if (m) {
          const id = m[1];
          html += fuSelect("blank-" + id, "data-fu-blank='" + esc(id) + "'", terms, picked[id] || "");
        } else {
          html += chem(part);
        }
      });
      html += "</p>";
      if (!reveal) html += "<button type='button' class='lbs-submit' data-fu-submit='fill'>Check this hint</button>";
      return html;
    }
    return "<p class='stem'>" + chem(fu.stem || "") + "</p>" + fuOptButtons(fu, stage);
  }
  function followupHTML(it, opts) {
    if (!opts || !opts.interactive) return "";
    const uid = it.uid || it.item_uid || "";
    const stage = ((opts.lbsStage || {})[uid]) || {};
    if (!stage.from) return "";
    const lbs = it.assessment && it.assessment.learn_by_solve;
    const row = lbs && lbs.wrong && lbs.wrong[stage.from];
    const fu = row && row.followup;
    if (!fu) return "";
    if (stage.done || stage.retry) {
      let note = "<div class='lbs' id='lbs-" + esc(uid) + "' data-lbs-retry='" + esc(uid) + "'>";
      note += "<p class='lbs-prompt'>Hint used — now choose on the original question.</p>";
      if (fu.why) note += "<p class='lbs-why'>" + esc(fu.why) + "</p>";
      return note + "</div>";
    }
    return "<div class='lbs' id='lbs-" + esc(uid) + "'>" +
      "<p class='lbs-prompt'>That choice is not the answer. Think about this first:</p>" +
      followupBody(fu, stage, uid) + "</div>";
  }
  function assessmentSheetHTML(it, i) {
    const a = it && it.assessment;
    const n = i + 1;
    const uid = it.uid || it.item_uid || "";
    const letter = extractedKey(it);
    const src = a && a.key_source === "cambridge_extract"
      ? "extracted mark scheme"
      : a && a.key_source === "olympiad_gold"
        ? "provided gold · not a Cambridge mark scheme"
        : "no extracted key";
    let body = "";
    if (a && a.mark_scheme && a.mark_scheme.text) {
      body += "<pre class='ms'>" + esc(a.mark_scheme.text) + "</pre>";
    }
    if (a && a.examiner_comment && a.examiner_comment.present && a.examiner_comment.text) {
      body += "<p class='ex'><b>Examiner comment</b></p><p>" +
        esc(a.examiner_comment.text).replace(/\n/g, "<br>") + "</p>";
    }
    const lbs = a && a.learn_by_solve;
    if (lbs && (lbs.solve || lbs.wrong)) {
      if (lbs.solve) body += "<p class='ex'><b>How to see it</b></p><p>" + esc(lbs.solve) + "</p>";
      ["A", "B", "C", "D"].forEach((k) => {
        if (letter && k === letter) return;
        const row = (lbs.wrong || {})[k];
        if (!row) return;
        const fu = row.followup || {};
        body += "<div class='mx'><b>If " + esc(k) + "</b> [" + esc(row.mx_type || "") + "] " +
          esc(row.pathway || "") +
          (fu.stem ? "<div class='muted'><i>Follow-up" +
            (fu.format ? " · " + esc(fu.format) : "") + ":</i> " + esc(fu.stem) +
            " (key " + esc(fuKeyLabel(fu)) + ")</div>" : "") +
          "</div>";
      });
    }
    if (!letter && !body) {
      body = "<p class='muted'>No extracted key or examiner comment for this item.</p>";
    }
    return "<article class='key-q'>" +
      "<div><span class='qnum'>" + esc(n) + "</span> " +
      "<span class='tag'>" + esc(letter || "—") + "</span> " +
      "<span class='uid'>" + esc(uid) + "</span></div>" +
      "<p class='muted'>" + esc(src) + "</p>" + body +
      "</article>";
  }
  function analysisHTML(it, i) {
    const a = it.analysis;
    if (!a) return assessmentSheetHTML(it, i);
    const n = i + 1;
    const uid = it.uid || it.item_uid || "";
    const opts = a.options || {};
    const letters = ["A", "B", "C", "D"].filter((k) => opts[k] || (it.options && it.options[k]));
    const mapBits = [];
    if (a.map && a.map.chapter_title) mapBits.push(a.map.chapter_title);
    if (a.map && a.map.decision) mapBits.push(a.map.decision);
    const letter = a.correct || extractedKey(it) || "?";
    const extractBits = [];
    if (it.assessment && it.assessment.key_source === "cambridge_extract") {
      extractBits.push("extracted mark scheme");
    }
    if (it.assessment && it.assessment.examiner_comment && it.assessment.examiner_comment.present) {
      extractBits.push("examiner comment on pack");
    }
    return "<article class='key-q'>" +
      "<div><span class='qnum'>" + esc(n) + "</span> " +
      "<span class='tag'>" + esc(letter) + "</span> " +
      "<span class='uid'>" + esc(uid) + "</span></div>" +
      (extractBits.length ? "<p class='muted'>" + esc(extractBits.join(" · ")) + "</p>" : "") +
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
      (it.assessment && it.assessment.mark_scheme && it.assessment.mark_scheme.text
        ? "<pre class='ms'>" + esc(it.assessment.mark_scheme.text) + "</pre>" : "") +
      (it.assessment && it.assessment.examiner_comment && it.assessment.examiner_comment.present
        ? "<p class='ex'><b>Examiner comment</b></p><p>" +
          esc(it.assessment.examiner_comment.text).replace(/\n/g, "<br>") + "</p>" : "") +
      lbsKeyHTML(it) +
      "</article>";
  }
  function lbsKeyHTML(it) {
    const lbs = it.assessment && it.assessment.learn_by_solve;
    if (!lbs || !(lbs.solve || lbs.wrong)) return "";
    const letter = extractedKey(it);
    let html = "";
    if (lbs.solve) html += "<p class='ex'><b>How to see it</b></p><p>" + esc(lbs.solve) + "</p>";
    ["A", "B", "C", "D"].forEach((k) => {
      if (letter && k === letter) return;
      const row = (lbs.wrong || {})[k];
      if (!row) return;
      const fu = row.followup || {};
      html += "<div class='mx'><b>If " + esc(k) + "</b> [" + esc(row.mx_type || "") + "] " +
        esc(row.pathway || "") +
        (fu.stem ? "<div class='muted'><i>Follow-up" +
          (fu.format ? " · " + esc(fu.format) : "") + ":</i> " + esc(fu.stem) +
          " (key " + esc(fuKeyLabel(fu)) + ")</div>" : "") +
        "</div>";
    });
    return html;
  }
  function answerKeyHTML(meta, items) {
    const title = (meta && meta.title) || "Paper";
    const head =
      "<div class='hdr'><div class='board'>Teacher's Twin</div>" +
      "<div class='subj'>Answer key</div>" +
      "<div class='papername'>" + esc(title) + "</div>" +
      "<p class='cap'>Teacher sheet · extracted mark scheme and examiner comments where present · mix-ups unverified · not printed on the learner paper</p></div><hr class='rule'/>";
    const rows = (items || []).map((it, i) => analysisHTML(it, i)).join("");
    return "<div class='paper answer-key'>" + head +
      (rows || "<p class='muted'>No extracted key or stored analysis yet.</p>") +
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
    const body = (items || []).map((it, i) => {
      try {
        return itemHTML(it, i, itemOpts);
      } catch (e) {
        return "<article class='q'><div class='qhead'><span class='qnum'>" + (i + 1) +
          "</span></div><p class='muted'>Could not render this item" +
          (it && it.uid ? " (" + esc(it.uid) + ")" : "") + ".</p></article>";
      }
    }).join("");
    const learner = "<div class='paper'>" + head + (body || "<p class='muted'>No questions in this selection.</p>") + "</div>";
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
  g.TTwinPaper = { esc, chem, itemHTML, paperHTML, answerKeyHTML, mount, optionLetter, extractedKey, optionTableOf };
})(window);
