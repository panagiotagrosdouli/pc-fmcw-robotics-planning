# Paper experiment freeze

> Supersession notice (2026-09-20): the canonical Paper-1 evidence is the
> frozen V7 protocol and artifacts below. The older `paper-closure` benchmark
> description is retained as historical context and is not the submission
> evidence package.

## Canonical V7 evidence state

- Frozen protocol commit: `9deb72e57dc6691e6cc60b5bdade3eeacf0ee5de`
- Tree-identical workflow trigger: `409210803356640ef50caaa8c432c445abad91c7`
- Development seeds: `18000..18019`; selected buffer: `0.5 m`
- Confirmatory seeds: `19000..19049`; hard gate: PASS
- Geometry seeds: `20000..20019`; authorized after the confirmatory gate
- Workflow run: <https://github.com/panagiotagrosdouli/pc-fmcw-robotics-planning/actions/runs/35496870246>
- Development archive: `results_archive/part_b_v7_development/`
- Publication snapshot: `manuscripts/paper1_pc_fmcw/results_archive/`

V7 is immutable evidence. Any later implementation change requires a new
protocol version and new untouched seeds; it must not retroactively alter V7.

## Historical freeze

## Canonical code state

- Base commit: `ef1ff4a9d93960f4aba6be17e71f14d046000b9e`
- Closure branch: `paper-closure`
- Study boundary: controlled, dataset-free PC-FMCW-informed closed-loop robotics simulation. Results are not optical-hardware measurements or real-vehicle validation.

Any methodological bug fix after this freeze requires a new commit identifier and rerunning every affected experiment.

## Canonical benchmark

The publication benchmark uses:

- seeds: 20 (`0..19`)
- P3 Monte Carlo samples: 32
- paired-bootstrap samples: 10,000
- benchmark planners: P0--P4
- benchmark defaults from `run_pc_fmcw_robotics_benchmark.py` unless explicitly recorded in the generated manifest

Primary confirmatory comparison: P1 reactive vs P2 predictive. P2 vs P3 and P2 vs P4 quantify marginal value beyond causal prediction. Safety is reported separately and no collision-safety improvement is claimed unless supported by the frozen experiment.

## Required outputs before manuscript freeze

1. `episodes.csv`, `summary.csv`, and `manifest.json` from the canonical benchmark.
2. Overall paired effects with 10,000-bootstrap confidence intervals and multiplicity-corrected Wilcoxon tests.
3. Per-scenario paired effects for P1--P2 and P2--P4, interpreted as scenario-stratified evidence rather than independent candidate-level samples.
4. Safety/feasibility diagnostics: collision rate, no-candidate step rate, and road/speed/static/dynamic rejection fractions.
5. Aggregated robustness results across all 20 seeds; individual shards are not publication results.
6. Prediction-horizon and connectivity-weight ablations with aggregate uncertainty/statistical summaries.
7. Final figures/tables generated only from the frozen outputs.

## Statistical unit and interpretation

Planner comparisons are paired by `(scenario, seed)`. Candidate evaluations and candidate rejection counts are diagnostic event counts and must not be treated as independent statistical samples. Scenario-level results should report effect sizes and confidence intervals; multiplicity correction must match the explicitly reported hypothesis family.

## Reproducibility

Every final artifact must identify the commit SHA and retain the benchmark manifest. Legacy Stage-9 `make_paper_*` artifacts are not authoritative publication results for this study.
