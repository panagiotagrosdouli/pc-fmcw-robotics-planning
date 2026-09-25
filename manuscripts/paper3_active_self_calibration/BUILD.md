# Paper 3 build

The canonical source is `paper3.tex` in generic IEEE journal format. Venue-specific formatting is intentionally deferred until a venue is selected.

## Compile

```bash
cd manuscripts/paper3_active_self_calibration
latexmk -pdf -interaction=nonstopmode -halt-on-error paper3.tex
```

The repository-wide `.github/workflows/manuscript_ci.yml` discovers `paper3.tex` automatically and compiles it together with Papers 1 and 2.

## Evidence checks

Before submission, compare every numerical claim in `paper3.tex` against:

- `results_archive/confirmatory_planner_summary.csv`
- `results_archive/primary_regret_effects.csv`
- `results_archive/scenario_EF.csv`
- `results_archive/distance_only_summary.csv`
- `results_archive/support_studies_summary.csv`
- `CLAIM_EVIDENCE.md`

The compact CSVs are manuscript traceability snapshots. The authoritative full evidence remains the immutable GitHub Actions artifacts recorded in `CLAIM_EVIDENCE.md`.

Do not regenerate or retune the frozen primary study from post-confirmatory outcomes. Manual full-research workflows are reproducibility mechanisms, not an invitation to replace the archived confirmation.
