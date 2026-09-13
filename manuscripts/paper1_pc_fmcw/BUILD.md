# Paper 1 build and scientific status

The manuscript source is `paper1.tex`. It is intentionally self-contained for environments that have `pdflatex` but no `bibtex`; `references.bib` is retained for venue/submission workflows.

Compile with:

```bash
pdflatex -interaction=nonstopmode -halt-on-error paper1.tex
pdflatex -interaction=nonstopmode -halt-on-error paper1.tex
```

## Scientific gate

This manuscript is intentionally **not final**. The V2 development safety gate failed and its confirmatory seeds were therefore not executed. Historical V1 communication results remain exploratory/model-based evidence only.

The active remediation protocol is V3. V3 uses development-only seeds 6000--6019 to select the minimum predeclared prediction-safety margin that yields zero collisions and zero no-candidate episodes under the shared braking-plus-lateral safety envelope. Only after that selector passes may fresh confirmatory seeds 7000--7049 and fresh directional-geometry seeds 8000--8019 run.

Do not replace the gated Results section with V1 or failed-V2 values and call them confirmatory. The final manuscript must be regenerated only from a successful fresh post-remediation artifact.
