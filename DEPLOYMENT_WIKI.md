# TeacherTwin deployment wiki

Issues found while standing up the GitHub Pages chemistry showcase. Sort these **at deploy time** (rebuild `tools/build_data.py`, bump `?v=` on CSS/JS, hard-refresh `https://khkreddy.github.io/TTwin/` — not `/AWM/`).

---

## D1 · Wrong site / stale cache looks like “the old website”

**Symptom.** Figures missing, old chrome, “Cambridge chapter”, uid lists not papers.

**Root cause.** Two public sites: `khkreddy.github.io/AWM/` (Aug 2026 assemble demo) vs `khkreddy.github.io/TTwin/`. GitHub Pages `Cache-Control: max-age=600`. Browse originally listed uids only; TikZ ran only after Test maker.

**Solution.** Use TTwin URL. Cache-bust `css/*.css?v=N` and `js/*.js?v=N` on each figure/render release. Browse typesets a paper preview. Jump-uid on Test maker.

---

## D2 · TikZ generated but not drawn

**Symptom.** `9701_m16_qp_12:q5` (and 1,254 others) showed “figure not reproduced”.

**Root cause.** Exam JSON already had `figure.tikz.code`. `build_data.py` kept only `has_figure: true`. GitHub Pages cannot run `pdflatex`.

**Solution.** Pack `tikz` (+ extra TeX packages). Browser TikZJax (`@rod2ik/tikzjax`) compiles on view. Do **not** commit PNGs unless a package TikZJax cannot draw (pgfplots subset).

**Deploy check.** Packed questions with `tikz` ≥ 1200. Paper HTML contains `tikz-slot`. Live `index.html` loads TikZJax + `?v=` assets.

---

## D3 · SMILES structures drawn twice (A–D in a row **and** as options)

**Symptom.** `9701_m16_qp_12:q27`: propane-1,2-diol plus four solvents appear in a figure strip, then A–D appear again as option drawings.

**Root cause.** `structures[]` mixes **stem** molecules (`label: null`, e.g. the diol) with **option** molecules (`label: A|B|C|D`). Renderer treated “not every label is A–D” as “draw the whole array as a figure”, then also bound A–D into options.

**Solution.** Partition: unlabeled / numeric / other labels → stem figure once. Labels A–D → options once. Never both.

**Deploy check.** Open `9701_m16_qp_12:q27`. Stem shows **one** diol. Options show **four** structures, not eight.

---

## D4 · Paired option structures collapsed to one molecule

**Symptom.** `9701_m17_qp_12:q30` “Which two compounds can react together to produce an ester?” Each option is a **pair**. Only one structure per letter showed.

**Root cause.** Exam `structures` repeats `label: "A"` (etc.) twice. JS `byLab[k] = s` overwrote the first SMILES. `asOptions` hid the stem row, so the dropped partner never appeared.

**Solution.** Group by label into arrays. Each option renders **all** molecules with that letter (side by side). If drawings exist for a letter, do not also print transcribed names/formulae as a second copy of the same choice.

**Deploy check.** `9701_m17_qp_12:q30` — each of A–D shows **two** skeletons. Same pattern: `9701_w09_qp_11:q30`.

---

## D5 · SMILES never reached the site at all (first ship)

**Symptom.** Organic displayed-structure items were text-only.

**Root cause.** Packer comment “Never copy SMILES” (learner-paper law: do not **print** the SMILES string). That was over-read as “do not pack for drawing”.

**Solution.** Pack `structures[{label,smiles}]` for the drawer only. Never put SMILES in visible option text. Draw with SmilesDrawer. Frozen exam still does not print SMILES.

---

## D6 · Tables / equations omitted from the pack

**Symptom.** Many Paper-1 items look incomplete (no grid).

**Root cause.** Slim pack dropped `tables` until the exam-quality pass. **2,408** items have tables in exam JSON.

**Solution.** Pack `tables` (`headers`, `rows`, `row_labels`, `caption`). Render `table.exam` on the paper.

---

## D7 · Lesson AI prose was generic and enrichment-only

**Symptom.** Digest not actionable. Model never saw map mx / mechanism / teacher notes.

**Root cause.** `LESSON_SYS` asked for 350–500 words from enrichment rows only. No Zinsser constraint. No hinge pack. No overlay.

**Solution.** Prompt: Zinsser (short, concrete, numbered actions). Payload: map hinges (decision, mechanism, CANDIDATE mx) + enrichment + teacher overlay for the selected hinges. Cap each layer (8). Null URL → no invented DOI.

---

## D8 · Teacher notes had no home on the sheaf

**Symptom.** Comments/links could not reappear on the matching lesson.

**Root cause.** Overlay was C4-off in AWM product. Pages has no server.

**Solution.** **Journal** tab. Notes live in `localStorage` (`ttwin.journal.v1`). AI maps each note to 1–4 `unit_id`s from the closed hinge list. Lesson planner shows overlay next to enrichment. AI prose includes overlay when present.

---

## D9 · ISO-GEN started from hinge codes, not the teacher’s idea

**Symptom.** Textarea defaulted to `science/grade_11/chem_ch_105/H009`. Button said “Load hinge pack”. Teachers had to carry unit ids.

**Root cause.** ISO-GEN treated `hinge_pack(unit_id)` as the *teacher* start. Codes, node lists, and the 523-hinge catalog are system-facing. A teacher arrives with a fuzzy idea.

**Solution.** One box: ordinary language. AI (1) restates intent against the 21 map nodes + chapter titles — no unit ids in that call; (2) picks `unit_id` from the **filtered** hinge list; (3) authors from that pack, honouring the teacher’s framing. Pasted `unit_id` is a shortcut only. Teacher surface shows “What we heard” + decision hinge + chapter/band — not codes. CANDIDATE, `serve_eligible=false`. Frozen L20 untouched. Cache-bust `?v=6`.

**Deploy check.** ISO-GEN has no prefilled `H009`, no “Load hinge pack”. A prompt like “senior reaction profiles, mix up ΔH with activation energy” yields a mapped hinge in teacher language, then an item.

---

## Deploy checklist

1. `python3 tools/build_data.py` from a tree that still has exam JSON + comprehensive map.
2. Confirm counts: tikz ~1255, structures ~487, tables ~2408.
3. Bump `?v=` on `index.html` scripts/styles (ISO-GEN teacher-prompt is `v=6`).
4. `git push` `main`. Hard-refresh TTwin Pages.
5. Spot: `9701_m16_qp_12:q5` (TikZ four panels), `q27` (diol + four options once), `q30` (pairs).
6. Journal: save a note, ingest, open Lesson on that node — overlay visible; AI prose cites it without calling it a publication.
7. ISO-GEN: empty box, ordinary-language placeholder, one **Author question** button. No hinge id required.
