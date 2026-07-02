# npj Digital Medicine restructure — validation report

**Manuscript:** `npj_paper.tex` (v3, results-forward)
**Class:** `\documentclass[pdflatex,sn-nature]{sn-jnl}` (Springer Nature, Nature Portfolio style)
**Date of this report:** generated with the restructure.

---

## 1. What changed (v2 → v3)

The manuscript was inverted from a computer-science-style
Methods-first structure into the npj Digital Medicine **results-forward**
structure requested for initial-review acceptance.

| | Before (v2) | After (v3) |
|---|---|---|
| Section order | Intro → Related Work → **Methodology** → Experiments → Conclusion | **Introduction → Results → Discussion → Methods** → Declarations |
| Differential-geometry derivations | in main-text Methodology (front) | relocated to **Methods** (back) |
| Algorithms (scaling-squaring, training) | main-text Methodology | **Methods** |
| Complexity analysis | main-text | **Methods** |
| Related Work | standalone 6-subsection section | condensed into Introduction + Methods |
| Main figures | 5 legacy single-panel figures | **5 composite figures (1 schematic + 4 data), 6–9 panels each** |
| Raw medical data shown | limited | real H&E tiles, deformation fields, energy maps, external tiles, failure cases throughout |

All quantitative values (tables, per-class numbers, ablations, efficiency,
robustness) are carried **verbatim** from the source paper — no reported
number was altered by the restructure. The 10 data tables are preserved and
re-cited from the Results/Methods text.

## 2. Figure inventory

| Figure | File | Panels | Content |
|---|---|---|---|
| Fig 1 | `Fig1_overview.pdf` | 6 (a–f) | Study overview: 9-class H&E gallery, heterogeneity, DCA schematic, conformal normalization on tissue, per-class MV, study design |
| Fig 2 | `Fig2_normalization.pdf` | 7 (a–g) | Geometric normalization on real tissue (TUM/NORM/MUS × original/field/normalized/energy) + deformation, angle-distortion, adaptivity, quasiconformal stats |
| Fig 3 | `Fig3_performance.pdf` | 6 (a–f) | 21-method accuracy, per-class bars, confusion matrices, MV-vs-gain (r=0.94), dominant confusions, per-class Δ |
| Fig 4 | `Fig4_efficiency.pdf` | 6 (a–f) | Learning curves, label-efficiency crossing, cross-dataset bars, domain-shift drop, external tiles, efficiency summary |
| Fig 5 | `Fig5_robustness.pdf` | 5 (a–e) | Corruption robustness, component ablation, hyperparameter heatmap, failure-mode distribution, real failure cases |

Every figure is built from **real CRC-VAL-HE-7K tissue tiles** and the
paper's verbatim table values (see `make_fig1.py`–`make_fig5.py`). Both PNG
(400 dpi) and vector PDF are provided; the manuscript embeds the PDFs.

## 3. Static validation (npj_paper.tex v3)

Checked with a LaTeX-aware parser (compilation in-sandbox is blocked by
environment, not by any manuscript defect — see build instructions):

- Brace balance: **0** (balanced)
- `\begin{env}`/`\end{env}` mismatches: **none**
- `\begin{document}`…`\end{document}`: **exactly one, well-formed**
- Citation keys: **19 unique, all resolve** against `references.bib` (44 keys); 0 missing
- `\label`/`\ref`/`\eqref`: 28 labels, 22 references, **0 dangling**
- Figure files referenced: **all 5 present on disk**
- Theorem environments (`definition`, `proposition`) and `algorithm`/`algorithmic`
  packages: defined in preamble, used consistently in Methods
- Residual elsarticle commands (`frontmatter`, `\ead`, `\linenumbers`): **none**

## 4. Substantive issues flagged for the authors

### 4.1 Source-paper efficiency inconsistency (please resolve before submission)
The source abstract claims **4.2× data efficiency** ("10% of labels matches
standard training on 42%"), but the paper's own per-fraction table (Table 4)
places ResNet-18 at DCA's 10%-data accuracy (66.4%) at only **~33% of the
labels** — a ~3.3× gap. The source text itself (Data Efficiency subsection)
states both a **3.7×** value (linear interpolation, 36.6%) and the **4.2×**
value in adjacent sentences. These are internally inconsistent.

**How v3 handles it (honestly, without overriding your numbers):**
- Fig 4b marks the crossing point *on the plotted ResNet-18 curve* (~33%),
  derived by interpolation, rather than a hardcoded 42%.
- Fig 4f and the abstract keep 4.2× only as the paper's **"reported peak
  label-efficiency (up to 4.2×)"**, attributed rather than asserted.
- Results text states "roughly three-to-four times more labelled data" and
  gives the ~33% figure explicitly.

**Action:** decide on the single efficiency multiplier you want to stand
behind, recompute it consistently from Table 4, and we will set every mention
(abstract, Fig 4, Results) to that one value.

### 4.2 Placeholder content that must be completed before submission
- **Authors / affiliations / emails** — currently `First/Second Author`,
  `Organization 1/2`, `author1@example.com`. Insert real values.
- **Code URL** — `https://github.com/xxx/DCA` is a placeholder.
- **Data availability DOI/URL** — a red author-action note marks where to
  insert the exact NCT-CRC-HE-100K / CRC-VAL-HE-7K repository DOI (do not
  invent one).
- **References** — 25 of 44 bib entries are no longer cited after Related
  Work was condensed; unused entries simply won't appear. If you want any
  specific citation retained, add a `\cite` in the relevant Results/Methods
  sentence.

## 5. Provenance note
Per your instruction, all headline numbers (93.2% accuracy, 100K images,
5-fold CV, A100, 4.2× efficiency, etc.) are treated as **real results from a
full run held on your cluster** and carried verbatim. The only run present in
this workspace is a 1-epoch CPU smoke test (val acc 42.4%) which was **not**
used for any figure or number.
