# Building the npj manuscript PDF

`npj_paper.tex` uses the Springer Nature `sn-jnl` class in Nature Portfolio
style (`sn-nature`), required by npj Digital Medicine.

## Use the submission bundle
Download **`npj_submission.tar.gz`** and extract it — it contains the
manuscript, class/style files, bibliography, and all five figures with
correct, compile-ready `\includegraphics` paths (plain figure stems, e.g.
`{Fig1_overview}`). Build from the extracted folder with either option below.

> Note: open the `.tex` from the **tarball**, not the standalone
> `npj_paper.tex` artifact preview — the web artifact view rewrites bare
> figure filenames into `{{artifact:…}}` embed markers, which are not valid
> LaTeX. The copy inside the tarball is the canonical, compilable source.

## Files needed in the build directory
- `npj_paper.tex`            — the manuscript (results-forward v3)
- `sn-jnl.cls`               — Springer Nature class (provided)
- `sn-nature.bst`            — Nature Portfolio bibliography style (provided)
- `references.bib`           — bibliography database
- `Fig1_overview.pdf` … `Fig5_robustness.pdf` — the 5 composite figures (provided)

## Option A — local TeX Live / MiKTeX (recommended)
```bash
pdflatex  npj_paper
bibtex    npj_paper
pdflatex  npj_paper
pdflatex  npj_paper
```
or, in one step:
```bash
latexmk -pdf npj_paper.tex
```

## Option B — Overleaf
1. New Project → Upload Project, add all files above.
2. Menu → Compiler → **pdfLaTeX**.
3. Menu → Main document → `npj_paper.tex`. Recompile.

## Why the PDF was not built here
The sandbox has three independent, environmental blockers — none is a defect
in the manuscript:
1. The only conda `texlive-core` build ships binaries but **no** `.sty`/`.cls`
   files, so it cannot typeset.
2. Tectonic 0.16.9 panics under the macOS sandbox (SCDynamicStore).
3. TeX package CDNs (CTAN, Tectonic bundle) are off the network allowlist.

The manuscript passed full LaTeX-aware static validation instead (see
`VALIDATION_REPORT.md`).

## Change log
- **v3 (this build):** restructured to npj results-forward
  (Introduction → Results → Discussion → Methods); CS theory, algorithms, and
  complexity moved to Methods; 5 new composite figures (6–9 panels each) built
  from real tissue; abstract efficiency claim reconciled to attributed framing.
- v2: Data-availability Zenodo DOI (fabricated) removed, replaced with a
  citation-only statement + author-action note.
- v1: initial Elsevier → npj conversion.

## Pre-submission checklist (author actions)
- [ ] Real author names, affiliations, corresponding email
- [ ] Real code repository URL (replace `github.com/xxx/DCA`)
- [ ] Exact dataset DOI/URL in Data availability (red note marks the spot)
- [ ] Decide and unify the single data-efficiency multiplier (see
      VALIDATION_REPORT.md §4.1)
- [ ] Funding statement, if any
- [ ] Confirm generative-AI-use declaration wording
