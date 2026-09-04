# Research and implementation audit — 2026-09-04

## Scope and claim boundary

This audit evaluates the repository as a controlled, model-based study of
PC-FMCW-informed predictive connectivity-aware motion planning. It does not
interpret modeled SNR, outage, BER, or goodput as optical measurements and does
not treat simulated collision diagnostics as real-road safety validation.

## Executive finding

The repository contains a coherent P0–P4 closed-loop benchmark, common dynamic
safety interface, paired statistical analysis, robustness sweeps, documented
link-model provenance, and CI/full-experiment workflows. The strongest existing
claim remains the P1-to-P2 improvement in modeled connectivity outcomes. The
project is not yet paper-ready solely from the checked-in artifacts because the
aggregated robustness package, final scenario-level diagnosis, final figures,
and frozen release are not present on the audited default branch.

## Roadmap status

| Roadmap item | Status at audit | Evidence or remaining gate |
|---|---|---|
| Aggregated robustness results | Partial | Sharded workflow and merge/plot scripts exist; final aggregate is not checked in. |
| Per-scenario safety diagnosis | Implemented in this change | Benchmark now exports collision timing/counts; diagnostic script produces scenario tables. |
| No-candidate/feasibility diagnosis | Implemented in this change | Mutually exclusive road/speed/static/dynamic rejection counts are recorded in the planner's existing filter pass. |
| Connectivity-sensitive scenarios | Partial | Five scenario families exist; sensitivity still requires final large-seed per-scenario effect analysis. |
| Prediction/horizon ablation | Partial | Horizon sweep exists; final aggregate and interpretation are pending. |
| Connectivity-weight trade-off | Partial | Weight sweep and outage/progress figures exist; final aggregate is pending. |
| Prediction ADE/FDE | Implemented in this change | Closed-loop ADE/FDE against simulator truth are exported per episode. |
| Oracle-gap interpretation | Partial | P2–P4 pairing exists; interpretation remains dependent on final scenario/robustness results. |
| Link-model provenance/calibration | Substantially complete | `LINK_MODEL_PROVENANCE.md` declares traced and assumed parameters; no measured calibration is claimed. |
| Final figures/tables | Incomplete | Robustness plotting exists, but the older `make_paper_*` scripts target legacy Stage-9 artifacts. |
| Final statistical summary | Partial | Paired bootstrap/Wilcoxon/Holm outputs exist; final large-seed artifacts remain required. |
| Frozen reproducibility release | Incomplete | No audited frozen tag/release and immutable result bundle. |
| Manuscript/report | Incomplete | Methods and reporting rules exist; final results section must be artifact-derived. |

## Verified implementation properties

- P4 receives truth for connectivity forecasting while safety uses the common
  predicted mean.
- P2 and P3 share the same mean prediction; P3 adds uncertainty sampling.
- Planning and realized collision evaluation use the configured target-clearance
  radius.
- Statistical pairing keys are scenario and seed, with duplicate-pair rejection.
- Benchmark inputs are validated and artifacts include explicit claim boundaries.
- The complete unit suite passed after the diagnostic implementation.

## Provisional diagnostic observation

A two-seed smoke run was used only to verify the data path, not for inferential
claims. In that run, collisions occurred in `following_lateral_offset` and
`overtake`, while `lane_choice` and `occluding_cut_in` exhibited long
no-candidate periods attributable primarily to the static-obstacle stage. This
explains why the aggregate collision rate alone is scientifically insufficient:
it combines scenario-specific collision and feasibility failure modes. The
observation must be re-estimated using the frozen large-seed experiment before
publication.

## Methodological risks still requiring closure

1. The large-seed aggregated robustness artifacts must be regenerated from one
   commit and inspected before claiming robustness.
2. Per-scenario P1–P2 and P2–P4 effect intervals are needed to identify where
   prediction is consequential and why the oracle gap is small.
3. Candidate rejection fractions should be reported together with no-candidate
   step rates; candidate-level counts alone are not independent samples.
4. Final paper figures must use the current dataset-free benchmark schema. The
   legacy Stage-9 figure/table scripts must not be presented as current results.
5. Collision findings must remain diagnostic limitations, not safety-improvement
   claims.

## Reproducible commands

```bash
python -m pytest -q
python scripts/run_pc_fmcw_robotics_benchmark.py --seeds 20 --mc-samples 32 --output-dir results/paper/benchmark
python scripts/analyze_pc_fmcw_benchmark.py --input results/paper/benchmark/episodes.csv --output-dir results/paper/benchmark --bootstrap-samples 10000
python scripts/diagnose_pc_fmcw_benchmark.py --input results/paper/benchmark/episodes.csv --output-dir results/paper/benchmark/diagnostics
```

The GitHub Actions `Paper Experiments` workflow is the preferred full robustness
execution path. Its robustness matrix now follows the requested seed count
instead of remaining hard-coded to 20.
