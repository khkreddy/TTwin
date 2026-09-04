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

## D10 · Source question numbers, duplicated A–D, smashed option matrices (phy / bio / maths)

**Symptom.** `9702_m16_qp_12:q22`: stem still starts with `22`, the frequency/amplitude matrix is flattened (`A 1 f 1 A` / `2 2`), and A–D then print again as options. `9702_m17_qp_12:q26`: the M/N list is in the stem **and** as options. Same furniture across physics and biology. Chemistry was already clean.

**Root cause.** Chemistry extract strips the printed question number (only when it matches the source number — `10 g of ammonium nitrate` is content, see `stage1_cleanup.py`) and stores A–D once, with tick matrices as tables of ✓/✗. Physics/biology CMS stems are still page transcriptions. TTwin then rendered stem + options.

**Solution.** Deploy-time overlay `tools/learner_display.py` (does **not** rewrite frozen exam.v1 or CMS). Gate leading-number strip on `:qN`. Peel the A–D block from the stem when options already exist. Rebuild stacked ½ fractions and cid tick/cross matrices to the chemistry shape (table + `frequency ½ f; amplitude ½ A`). `(cid:1)` after a number is °, not a tick. Refuse to strip when A–D in the stem are figure labels (`A , B , C and D`).

**Deploy check.** `9702_m16_qp_12:q22` — no leading `22`; no dumped axis labels (`displacement` / `wave Y`); one frequency/amplitude table; options `½ f` / `½ A`. `9702_m16_qp_12:q21` — `1.40 × 10⁷ m s⁻¹` not `10 7 m s –1`. Chemistry `10 g of ammonium nitrate` unchanged.

---

## D11 · Circuit diagrams blank; crop line-breaks inherited in the stem

**Symptom.** `0625_m15_qp_12:q29` and other circuit items: encoded figure missing on the paper. `0625_m16_qp_22:q23`: stem still has `image` / `F` / `lens` wraps from the crop. `9702_m17_qp_22:q3`: left-hand figure is a distorted composite (car sitting on the graph).

**Root cause.** Exam JSON `preamble_packages` is often only `["tikz"]` even when the body is `\begin{circuitikz}` or `\begin{axis}`. Overlay wrapped non-`tikzpicture` bodies in `\begin{tikzpicture}…`, which nests `circuitikz` and TikZJax draws nothing. Stem overlay copied OCR/crop line-breaks inside a single sentence. Review pack used `visual_assets/rendered/` (failed encoding PNG) instead of `source_crops/`.

**Solution.** `infer_tikz_packages` + `normalize_tikz_source` at pack time (`circuitikz` / `pgfplots` from the body; never wrap `circuitikz` in `tikzpicture`). `join_wrapped_prose` joins a grammatical sentence; figure-label dumps are not inherited from the crop. Internal figure review prefers `source_crops`, exposes a Modify tab (Kimi K3 edits TikZ for that session). Public TTwin still does not display “Kimi”.

**Deploy check.** `0625_m16_qp_12:q32` draws the parallel resistors. `0625_m16_qp_22:q23` stem is one question sentence. Packed `tikz_packages` includes `circuitikz` on circuit items. Cache-bust `?v=11`.

**Internal review (not the public site).** Pack lives at `data/awm_product/generated/figure_review_phybio`, served `0.0.0.0:8775`. Prefer `visual_assets/source_crops` over `rendered/` — `9702_m17_qp_22:q3` rendered PNG is a distorted composite (car on the graph, 29 KB); the exam-page crop is 149 KB. Python 3.12 `http.server` BufferedWriter (~8 KiB) reset small HTML/CSS/JS; send the full HTTP/1.0 response with `connection.sendall`. Crops stay off GitHub Pages.

---

## D12 · Kimi K3 figure Modify: `invalid temperature`

**Symptom.** Internal review **Apply with Kimi K3** returns `invalid temperature: only 1 is allowed for this model`. The encoded pane never redraws.

**Root cause.** `kimi-k3` is a thinking model. Moonshot pins `temperature=1` (also `top_p`, `n`, penalties). Any other value is HTTP 400. Review JS sent `temperature: 0.3`. TeacherTwin `js/kimi.js` already uses `1`. After a successful edit, the new TikZ must be mounted as `script[type=text/tikz]` so TikZJax draws it (session only; frozen exam.v1 is not rewritten).

**Solution.** Send `temperature: 1` (or omit the field). Do not send `top_p`. Unwrap accidental `\begin{tikzpicture}…\begin{circuitikz}`. Public TTwin still does not display “Kimi”.

Default `reasoning_effort` is `"max"`; with `max_tokens` 8192 the browser fetch never returns. Figure Modify uses `reasoning_effort: "low"`, 4096 completion tokens, a 90s abort, and an elapsed-second status. Typical 20–60s.

**Deploy check.** Modify a circuit (`0625_m16_qp_12:q32`): prompt, Apply, right pane shows the new diagram. Revert restores the packed TikZ. Status must not sit on “editing…” past 90s.

---

## D13 · Two figures in one TikZ picture overlap

**Symptom.** `9702_m17_qp_22:q3`: Fig. 3.1 (car on a slope) and Fig. 3.2 (F_D vs v graph) render on top of each other.

**Root cause.** One `\begin{tikzpicture}` holds the car drawing and a `\begin{axis}` placed with `at={(-1.35,-2.4)}` whose height collides with the car. The printed paper stacks them. Display inherited the encoding’s overlapping coordinates.

**Solution.** Overlay `split_tikz_figures` / `separate_tikz_figures` (does **not** rewrite frozen exam.v1). If a picture contains both ordinary draws and a pgfplots axis, emit two `tikzpicture`s. Strip `at=` / `anchor=` on the split graph. Renderer mounts each block in its own TikZJax slot with vertical gap. Corpus-wide at TTwin pack time and internal figure review.

**Deploy check.** `9702_m17_qp_22:q3` — two stacked figures, car not on the graph. Cache-bust `?v=12`.

---

## D14 · Test maker Modify is ISO-GEN on the whole item; student-take; phy/bio syllabus map

**Symptom.** Test maker could assemble a paper but not change an item. Figure-only Modify (internal review) left stem and options stale. Physics/biology Map was a wall: “NCERT comprehensive map is chemistry.”

**Root cause.** Packed exam items have no published key. ISO-GEN authored new chemistry items from hinge packs, not edits of an existing stem+options(+figure). Phy/bio have no V15 hinge freeze; candidate chapter_intelligence is not a complete map.

**Solution.**
- **Modify** on every Test maker item (text and figure). Teacher prompt → ISO-GEN rewrite of stem **and** all four options; TikZ only if the change needs it. Session-only; frozen exam.v1 is not rewritten. Public UI says “AI”, never “Kimi”.
- **Take as student**: A–D become select buttons; responses recorded; Finish scores. Keys from Modify when present; otherwise AI-inferred with honesty *not a published mark scheme*. Feedback is AI prose to the student.
- **Physics / biology Map**: published NCERT chapter list (`syllabus_interim`). Class 11–12 titles from existing `ncert_chapter_candidates_pack_c`; Class 9–10 from the Science book chapters for that subject. Mx empty. Do not copy candidate chapter_intelligence, do not dump the chemistry comprehensive map.

**Deploy check.** Cache-bust `?v=13`. Map on Physics shows Class 11 Units and Measurement. Test maker: Modify a text item — options change with the stem. Toggle student, pick letters, Finish shows a score.

---

## D15 · Option matrices must stay tables; student selects a row

**Symptom.** `9702_m18_qp_12:q23` asked “which row…” but A–D printed as flattened strings (`10⁻⁶ 10⁻¹⁰ …`). `9702_m17_qp_12:q26` (M and N, λ_M / λ_N = 10⁵) split “visible light” / “γ-rays” into extra columns and dropped the stacked ratio.

**Root cause.** Overlay built an `is_option_table` only from tick/cid matrices or 2–4 raw tokens. Scientific-notation cells (`10 –6`) and two-word labels did not parse. Renderer always also printed `ul.options`, so even a good table was duplicated as prose. Student-take clicked letters, not rows.

**Solution.** Overlay: reconstruct stacked “The ratio / numerator / = value / denominator”; split 10ⁿ cells and named EM pairs; peel leftover header lines after the question into the option table. Renderer: `is_option_table` **is** the options (not also A–D prose). Student mode: the row is the select target.

**Deploy check.** Jump `9702_m18_qp_12:q23` — four columns (microwaves … X-rays), D is 10² not `10 2`. Jump `9702_m17_qp_12:q26` — stem has (wavelength of M)/(wavelength of N)=10⁵; table columns M, N; “visible light” one cell.

---

## D16 · Answer key + solution-analysis sub-layer (write once, RAG later)

**Symptom.** Assembled papers printed the questions and no key. Each sitting re-asked the model for letters. Distractor talk was not stored on the item.

**Root cause.** Packed exam.v1 has no mark scheme. Analysis was treated as a chat, not a corpus layer.

**Solution.** On Test maker assemble: for each uid, fingerprint stem+options+option-table (`item_sha256`). If `data/solutions/index.json` (or local overlay) has that uid+sha, retrieve with **zero** provider calls. Else one LLM write: map slice (capped), CANDIDATE mx, enrichment → stored analysis (key, rationale, per-option why, mx/enrichment copies). Home: `data/solutions/items.jsonl` + `index.json`. Local `serve.py` POST `/solution` appends. GitHub Pages cannot write; browser keeps a local overlay and **Download new analyses** for the next site push. Learner paper still has no mx. Teacher answer key is a second sheet (page-break). Honesty: not a published mark scheme.

**Deploy check.** Assemble `9702_m18_qp_12:q23` twice. First time may call AI (key in Settings). Second time status “1 from stored analysis · 0 newly written”. Print: question paper then answer key. Student toggle hides the key.

---

## Deploy checklist

1. `python3 tools/build_data.py` from a tree that still has exam JSON + comprehensive map.
2. Confirm counts: tikz ~1255, structures ~487, tables ~2408.
3. Bump `?v=` on `index.html` scripts/styles (option tables + solution analysis is `v=14`).
4. `git push` `main`. Hard-refresh TTwin Pages.
5. Spot: `9701_m16_qp_12:q5` (TikZ four panels), `q27` (diol + four options once), `q30` (pairs).
5b. Spot: `9702_m16_qp_12:q22` (no source number, fraction table once), `9702_m17_qp_12:q26` (A–D not in the stem).
5c. Spot: `0625_m16_qp_12:q32` (circuit draws), `0625_m16_qp_22:q23` (one-sentence stem).
5d. Internal review only: Modify tab Apply uses `temperature: 1`; the figure redraws. Not a Pages check.
5e. Spot: `9702_m17_qp_22:q3` — Fig. 3.1 and Fig. 3.2 stacked, not overlapping.
6. Journal: save a note, ingest, open Lesson on that node — overlay visible; AI prose cites it without calling it a publication.
7. ISO-GEN: empty box, ordinary-language placeholder, one **Author question** button. No hinge id required. Physics/biology ISO-GEN sits on the syllabus-interim chapter list.
8. Test maker: **Modify** on a text item rewrites stem + A–D. **Take as student** records letters or table rows; Finish shows score + feedback. Print still has no mx on the learner sheet; teacher answer key is a second page.
9. Map: Chemistry hinges unchanged. Physics/biology = published NCERT chapters, mx empty.
10. Jump `9702_m18_qp_12:q23` (option table) and `9702_m17_qp_12:q26` (M/N ratio table). Second assemble of the same uid must RAG the stored analysis.
