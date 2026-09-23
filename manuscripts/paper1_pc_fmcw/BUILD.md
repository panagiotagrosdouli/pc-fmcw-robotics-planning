# Paper 1 build (IEEE T-IV regular-paper format)

From the repository root:

```bash
python scripts/build_paper1_publication_assets.py \
  --input manuscripts/paper1_pc_fmcw/results_archive/confirmatory_seed_level_effects.csv \
  --out manuscripts/paper1_pc_fmcw/generated/table_confirmatory_effects.tex
cd manuscripts/paper1_pc_fmcw
latexmk -pdf -interaction=nonstopmode -halt-on-error paper1.tex
```

The table is generated from the archived seed-level artifact; do not edit numerical values in the LaTeX output by hand.
