# Paper 3 build

The canonical source is `paper3.tex`. The primary target is **IEEE Transactions on Intelligent Vehicles (T-IV), Regular Paper**, frozen on 2026-09-25. The source uses the required IEEE double-column journal class; final author biography/metadata must be inserted only after the author supplies verified details.

## Regenerate publication assets

From the repository root:

```bash
python scripts/build_paper3_publication_assets.py \
  --input manuscripts/paper3_active_self_calibration/results_archive \
  --out manuscripts/paper3_active_self_calibration/generated
```

This generates vector PDF/SVG figures and LaTeX tables directly from the compact frozen evidence snapshots. Do not edit generated numerical tables by hand.

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

Do not regenerate or retune the frozen primary study from post-confirmatory outcomes. Manual full-research workflows are reproducibility mechanisms, not an invitation to replace the archived confirmation.


## T-IV submission QA

Current venue-specific checks:
- IEEE double-column journal class: satisfied.
- Abstract length: 212 words, within current T-IV 150–250-word guidance.
- Generated figures/tables: regenerated from frozen compact evidence before manuscript CI.
- PDF visual QA: completed after publication-asset generation.
- Author block: no affiliation/email is embedded under the title.
- Remaining manual fields: affiliation/postal address, institutional email, short biography, conflict-of-interest disclosure, funding/acknowledgements, ORCID if used, and traditional-vs-open-access choice.

See `TIV_SUBMISSION_CHECKLIST.md` for the portal-facing checklist.
