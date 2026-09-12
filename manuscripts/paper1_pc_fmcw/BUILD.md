# Paper 1 build and status

The manuscript source is `paper1.tex`. It is intentionally self-contained for environments that have `pdflatex` but no `bibtex`; `references.bib` is retained for venue/submission workflows.

Compile with:

```bash
pdflatex -interaction=nonstopmode -halt-on-error paper1.tex
pdflatex -interaction=nonstopmode -halt-on-error paper1.tex
```

## Scientific gate

This manuscript is intentionally **not final** until the repository's V2 safety-development gate and fresh confirmatory protocol complete successfully. Historical V1 communication results are included only as exploratory/model-based evidence.

Do not replace the pending section with V1 values and call them confirmatory.
