# Paper 2 build

The canonical submission source is `paper2.tex`. It is intentionally self-contained for environments that have `pdflatex` but no `bibtex`; `references.bib` is also retained for venue/submission workflows.

## Compile PDF

```bash
cd manuscripts/paper2_real_v2x
latexmk -pdf -interaction=nonstopmode -halt-on-error paper2.tex
```

## Regenerate publication assets from archived results

Point the asset builder at an extracted real-V2X artifact root containing `real_v2x_support/`, `real_v2x_multisplit/`, `real_v2x_replay/`, and `real_v2x_replay_multisplit/`, or at the committed compact `results_archive/` snapshot:

```bash
python scripts/build_paper2_publication_assets.py /path/to/extracted/artifact \
  --out manuscripts/paper2_real_v2x/generated

# Compact, committed summaries (figures and descriptive tables only):
python scripts/build_paper2_publication_assets.py manuscripts/paper2_real_v2x/results_archive \
  --out manuscripts/paper2_real_v2x/generated
```

The script generates vector PDF/SVG figures plus CSV/LaTeX tables directly from archived results, avoiding manually transcribed result tables. The compact archive omits the full held-out-run decision and inference records; it cannot replace the authoritative full Actions artifact for final numerical verification.

## Scientific QA

Before submission:

1. verify every numerical statement against archived artifact CSV/JSON files;
2. verify `RESULTS_CHECKLIST.md` and `CLAIM_EVIDENCE.md`;
3. do not treat repeated grouped split assignments as independent replicates;
4. confirm that raw p-values not surviving Holm correction remain labeled exploratory;
5. compile twice and visually inspect every PDF page for clipping/overflow/undefined references.

A successful PDF build is not, by itself, evidence that the scientific claim audit is complete.
