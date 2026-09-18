# Audit: TTwin corpus vs. exam-ready standard

## Verdict

**Corpus is not exam-ready.** The renderer patch is correct for the reported bug and should ship, but it touches 7 items. The dominant defect class — figures that do not exist in the pack at all — affects ~5,789 items (6.7%) and is a packer failure, not a renderer failure. No renderer change can fix it.

---

## 1. q20 diagnosis

Correct, with one unverified assumption.

- The failure is a **double render**: the packer split one figure into two artifacts (a TikZ redraw and a 5×18 letter-grid table), and `itemHTML` emitted both. Diagnosis of mechanism: sound.
- **Unverified assumption:** the table's non-blank cells (A, B, C, D) must be redundant with the TikZ. The options are positions on the diagram; if `periodic_table_outline.v1` draws the grid but the *letters* live only in the table, the patch converts a double-rendered question into an **unanswerable** one. This must be checked cell-by-cell on all 7 items in the `tikz ∧ blank-grid` class before the skip is allowed to fire. "Tests green" on renderer logic does not establish this.

## 2. The one-visual rule

Right rule, two soft edges:

- **Preferring TikZ/figure_src over a blank grid is correct.** The grid is a packer artifact of the figure, not a data table.
- **Edge 1 — false positives.** `≥16 cells ∧ ≥70% blank` will also match a *legitimate* sparse table (e.g., a results table to be completed, a mostly-empty data grid) on any of the **1,976 tikz ∧ real-table** items. Your census classes ("blank-grid" vs "real") appear to be defined by the same heuristic, so the census cannot detect its own misclassification. Tighten: require non-blank cells to be single letters/symbols only, or require the table's letter set ⊆ the TikZ's label set. Audit the 1,976 before shipping.
- **Edge 2 — sub-threshold grids.** A 2×2, 3×3, or 4×4 mostly-blank figure grid (plausible for the 556 option-figure items) fails the ≥16-cell test and will still double-render if a TikZ exists. Run a one-time census with a content-based detector (non-blank cells are only A–E/symbols), not a size heuristic.

## 3. Remaining defects, ranked

### Must-fix (block "exam-ready")

| # | Defect | n | Why it blocks |
|---|--------|---|---------------|
| 1 | `has_figure` with no tikz, no figure_src, no SMILES, no grid | **5,233** | Stem says "The diagram shows…" and no diagram exists. Unanswerable. Packer-side extraction failure. Largest class by an order of magnitude. |
| 2 | `options_are_figure` with no drawing | **556** | Options render empty. Unanswerable by construction. |
| 3 | Label-redundancy check on q20 class | 7 | Precondition for the patch itself (see §1). |
| 4 | Headless TikZJax render pass over all tikz items; quarantine failures | 14,741 (watch: 426 `\newcommand`, 5,960 `\foreach`) | TikZJax/pgffor support for `\foreach` is partial and slow; `\newcommand` should work but the 17-item `periodic_table_outline.v1` class uses *both*, including `...` range lists. "Tests green" ≠ figures render. A silent blank SVG is indistinguishable from defect #1 at answer time. Require screenshot/PDF evidence, not unit tests. |
| 5 | MCQ with no option text | 23 | Unanswerable. Packer dropped options. Trivial count, non-negotiable fix. |

### Later (should-fix, does not block the patch)

| Defect | n | Note |
|--------|---|------|
| Broken-TeX subset of odd-`$` stems | ≤147 | Currency half is handled by masking. The genuinely broken half is a per-item data fix. KaTeX will throw or misrender in a maths paper — fix, but small. |
| `[Figure …]` placeholder leak | 10 | If the figure renders, strip with one regex at render time; if not, re-file under must-fix #1. |
| Blank-grid-as-sole-visual items (63 − 7) | ≤56 | Where the grid *is* the figure (no TikZ), empty bordered cells must render with visible borders, or A–D float in whitespace. Verify CSS. |
| TikZ→SVG/PNG pre-render at build time | all tikz | Depending on a browser WASM TeX compile for 14.7k figures is a latency and fragility liability at exam scale. Pre-render server-side; treat TikZJax as fallback. Architecture, not a blocker. |
| PNG crop quality audit | 38 + 31 | Files exist; legibility/completeness of crops unverified. PNG-wins over TikZ (spectroscopy policy) is defensible — ground truth beats redraw — but only if crops are complete. |
| Currency-mask false positives | — | Ensure masking cannot eat legitimate adjacent math (`$x$ and $y$`). Needs adversarial unit tests on the 100 HiCogMath stems plus math-heavy controls. |

## 4. Ship decision

**Ship the patch now** — it is the correct fix for the reported double-figure bug, it is small, and the currency masking is orthogonal and low-risk — **conditional on:**

1. Cell-level confirmation that A–D survive in the TikZ for all 7 q20-class items;
2. A false-positive audit of `isFigureGridTable` against the 1,976 tikz ∧ real-table items (or the tightened rule in §2).

**Do not** attach any "exam-ready" claim to this release. The release fixes a 7-item rendering defect. Exam-readiness is gated on must-fix #1, #2, and #4 — figure completeness for ~5.8k items and render evidence for 14.7k TikZ figures — none of which this patch addresses.