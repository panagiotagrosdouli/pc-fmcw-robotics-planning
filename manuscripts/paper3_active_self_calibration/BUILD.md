# Paper 3 build

The canonical source is `paper3.tex`. It is maintained in standard IEEE journal double-column format. T-IV remains a preferred conditional target pending the repository-policy clarification recorded in `TIV_SUBMISSION_CHECKLIST.md`; the manuscript itself is written to be portable across IEEE journal venues.

## Regenerate publication assets

From the repository root:

```bash
python scripts/build_paper3_publication_assets.py \
  --input manuscripts/paper3_active_self_calibration/results_archive \
  --out manuscripts/paper3_active_self_calibration/generated
```

The builder generates:
- `fig_overall.pdf/.svg`;
- `fig_decision_relevance.pdf/.svg`;
- `table_planner_means.tex`;
- `table_primary_regret_effects.tex`;
- `table_scenario_ef.tex`;
- `table_distance_only.tex`;
- `table_support.tex`.

All numerical publication assets are derived from the committed compact frozen evidence snapshots. Do not edit generated numerical tables by hand.

## Compile

```bash
cd manuscripts/paper3_active_self_calibration
latexmk -pdf -interaction=nonstopmode -halt-on-error paper3.tex
```

The repository-wide `.github/workflows/manuscript_ci.yml` regenerates Paper-3 assets and compiles `paper3.tex` together with Papers 1 and 2.

## Evidence checks

Before submission, compare every numerical claim in `paper3.tex` against:

- `results_archive/confirmatory_planner_summary.csv`
- `results_archive/primary_regret_effects.csv`
- `results_archive/scenario_EF.csv`
- `results_archive/distance_only_summary.csv`
- `results_archive/support_studies_summary.csv`
- `CLAIM_EVIDENCE.md`

The compact CSVs are manuscript traceability snapshots. The authoritative full evidence remains the immutable GitHub Actions artifacts recorded in `CLAIM_EVIDENCE.md`.

## Bibliography QA

- `references.bib` contains the citations used by the manuscript.
- `BIBLIOGRAPHY_NOTES.md` maps the literature families to the precise claims they support and records prohibited over-extensions.
- `docs/BIBLIOGRAPHY_AUDIT.md` is the repository-wide metadata audit.

Do not regenerate or retune the frozen primary study from post-confirmatory outcomes. Manual full-research workflows are reproducibility mechanisms, not an invitation to replace the archived confirmation.
