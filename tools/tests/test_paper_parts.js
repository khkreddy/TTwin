#!/usr/bin/env node
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../..");
const src = fs.readFileSync(path.join(ROOT, "js/paper.js"), "utf8");
if (/\bmodule\.exports\b|\brequire\s*\(/.test(src)) {
  throw new Error("paper.js must load in a window global with no Node module/require");
}
const sandbox = { console };
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(src, sandbox);
const TTwinPaper = sandbox.TTwinPaper;
if (!TTwinPaper || typeof TTwinPaper.itemHTML !== "function") {
  throw new Error("TTwinPaper.itemHTML missing");
}

const structured = {
  uid: "demo-struct",
  item_type: "structured",
  stem: "Some properties of the halogens are shown in the table.\n(a) Complete the table.\n[2]\n(b) Explain the trend.\n[4]",
  parts: [
    { id: "a", stem: "Complete the table.", marks: 2, subparts: [] },
    {
      id: "b",
      stem: "Explain the trend.",
      marks: 4,
      subparts: [
        { id: "i", stem: "melting point", marks: 2 },
        { id: "ii", stem: "colour", marks: 2 },
      ],
    },
  ],
  tables: [{ headers: ["halogen", "bp"], rows: [["Cl", "-35"]], row_labels: [], caption: "" }],
  tikz: "\\begin{tikzpicture}\\draw (0,0)--(1,0);\\end{tikzpicture}",
  assessment: { key_source: "none", key_status: "not_applicable", examiner_comment: { present: false } },
};
const html = TTwinPaper.itemHTML(structured, 0, {});
if (!html.includes("class='parts'") && !html.includes('class="parts"')) {
  throw new Error("structured render missing parts list");
}
if (!html.includes("(a)") || !html.includes("(b)") || !html.includes("(i)")) {
  throw new Error("structured render missing labelled parts: " + html.slice(0, 400));
}
if (!html.includes("tikz-slot")) {
  throw new Error("structured render missing tikz-slot");
}
if (!html.includes("<table")) {
  throw new Error("structured render missing table");
}
const smashedOnly = html.includes("Complete the table.") && !html.includes("class='parts'");
if (smashedOnly) throw new Error("stem-only flatten");
const stemP = html.match(/<p class='stem'>[\s\S]*?<\/p>/);
if (stemP && /\(a\)/.test(stemP[0])) {
  throw new Error("stem paragraph still reprints part labels: " + stemP[0]);
}
if ((html.match(/Complete the table\./g) || []).length !== 1) {
  throw new Error("part body reprinted outside parts");
}
sandbox.module = { exports: {} };
sandbox.exports = sandbox.module.exports;
vm.runInContext(fs.readFileSync(path.join(ROOT, "js/vendor/katex.min.js"), "utf8"), sandbox);
sandbox.katex = sandbox.module.exports.default || sandbox.module.exports;
const mathItem = {
  uid: "latex-demo",
  item_type: "open_response",
  stem: "Let $ABC$ be a triangle. Find $\\omega$ and $$x^2+y^2=1$$.",
  parts: [],
  assessment: { key_source: "none", key_status: "not_applicable", examiner_comment: { present: false } },
};
const mh = TTwinPaper.itemHTML(mathItem, 0, {});
if (mh.includes("$ABC$") || mh.includes("$$x^2")) {
  throw new Error("raw latex delimiters still in stem: " + mh.slice(0, 300));
}
if (!mh.includes("katex")) throw new Error("expected katex html");
const olympiad = JSON.parse(fs.readFileSync(path.join(ROOT, "data/questions/maths-olympiad.json"), "utf8"));
const q44 = olympiad.find((x) => x.uid === "jeebench:srcjson:math:jee_adv_2016_paper_1:q44");
if (!q44) throw new Error("q44 missing");
const qh = TTwinPaper.itemHTML(q44, 0, {});
if (qh.includes("\\begin{array}")) throw new Error("q44 still raw array env");
if (!qh.includes("katex")) throw new Error("q44 not typeset");
if (!qh.includes("One or more options may be correct")) throw new Error("q44 missing multi-correct note");
console.log("paper_parts_ok", html.includes("tikz-slot"), html.includes("(a)"));
console.log("latex_ok", mh.includes("katex"));
console.log("q44_ok", !qh.includes("\\begin{array}"));
