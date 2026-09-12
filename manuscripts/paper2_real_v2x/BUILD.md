# Paper 2 build

The manuscript source is `paper2.tex`. It is intentionally self-contained for environments that have `pdflatex` but no `bibtex`; `references.bib` is also retained for venue/submission workflows.

Compile with:

```bash
pdflatex -interaction=nonstopmode -halt-on-error paper2.tex
pdflatex -interaction=nonstopmode -halt-on-error paper2.tex
```

Before submission, regenerate/check every numerical statement against archived result artifacts and analysis scripts. A successful PDF build is not, by itself, evidence that every venue-specific submission check is complete.
