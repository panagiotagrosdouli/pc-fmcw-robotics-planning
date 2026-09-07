# Publication-Style Experimental Study

## Research questions and confirmatory hypotheses

This study evaluates whether predictive communication-aware motion planning provides statistically meaningful benefits under a controlled PC-FMCW-informed simulation model.

**RQ1.** Does predictive connectivity-aware planning outperform reactive connectivity-aware planning in modeled communication reliability while maintaining comparable safety and mobility?

- H1a: P2 has lower modeled outage probability than P1 under matched scenario/seed conditions.
- H1b: P2 has higher modeled mean/minimum SNR and modeled goodput, and lower modeled BER, than P1.
- H1c: P2 does not exhibit a practically important degradation in progress, path length, minimum clearance, collision rate, TTC-at-boundary, or no-feasible-candidate rate relative to P1.

**RQ2.** Does uncertainty-aware planning improve robustness when target-motion prediction is imperfect?

- H2: P3 has lower modeled outage and/or better modeled minimum SNR than P2 as prediction error, maneuverability, or uncertainty increases, without a disproportionate safety/mobility penalty.

**RQ3.** How close can predictive planners approach an oracle connectivity planner with access to ground-truth future target motion?

- H3: The P2/P3-to-P4 gap quantifies the remaining value of future target-motion information. P4 receives ground-truth target motion only for connectivity forecasting; its collision-avoidance checks use the same non-oracle safety prediction as P0-P3.

## Planner definitions and fairness

- P0: mobility-only baseline.
- P1: reactive connectivity-aware planner.
- P2: predictive connectivity-aware planner.
- P3: predictive risk-aware planner with uncertainty propagation.
- P4: oracle connectivity reference.

All planners use the same candidate trajectory generator, vehicle constraints, road bounds, static-obstacle constraints, and target-safety filtering. The same predicted target trajectory is supplied to all non-oracle safety checks. Oracle information is restricted to P4 connectivity forecasting and is not used for collision avoidance.

## Experimental unit and pairing

The inferential experimental unit is one complete closed-loop episode identified by `(experiment family, setting, scenario, seed, planner)`. Each planner is evaluated on identical scenario seeds. Planner comparisons are paired on `(experiment family, setting, scenario, seed)`.

Candidate evaluations and receding-horizon planning steps are diagnostics, not independent inferential samples.

## Outcomes

Connectivity outcomes are model outputs:

- mean SNR and minimum SNR,
- mean modeled outage probability,
- mean modeled BER,
- mean modeled goodput.

Mobility/safety outcomes are:

- path length,
- progress,
- minimum target clearance,
- minimum static-obstacle clearance,
- collision indicator/rate,
- realized TTC to the configured collision boundary,
- no-feasible-candidate count and rate.

## Statistical protocol

Primary effects are paired candidate-minus-baseline differences. For each comparison and outcome, report the paired mean difference and a 95% bootstrap confidence interval. Confirmatory paired hypothesis tests use the two-sided Wilcoxon signed-rank test. Holm correction controls family-wise error within each predeclared experiment family. In addition to raw-scale effects, report a paired standardized mean difference (`dz = mean(delta) / sd(delta)`) and rank-biserial correlation from the signed paired differences.

The core confirmatory comparison family is P1 vs P2, P2 vs P3, and P2 vs P4. Robustness and ablation analyses are interpreted as sensitivity analyses unless explicitly promoted to a preregistered confirmatory family before inspecting outcomes.

## Controlled ablation and robustness studies

The publication runner should vary, using matched seeds where applicable:

1. target prediction noise / bias / delay,
2. planning horizon,
3. connectivity weight,
4. target maneuverability,
5. obstacle density,
6. communication-model parameters including reference-SNR offset, path-loss scaling, beam-width scaling, outage threshold, and modeled blockage/attenuation.

Robustness plots show point estimates with 95% bootstrap confidence intervals over independent episode units.

## Parameter provenance

Two parameter classes must be reported separately.

### Parameters inherited from the PC-FMCW reference system

Parameters exposed by the repository PC-FMCW bridge that represent the reference sensing/communication system should retain their provenance and naming. They should not be silently retuned per planner.

### New simulation assumptions

The robotics study introduces an analytical mapping from future relative geometry to modeled communication quality. Parameters governing range/path-loss response, pointing/beam response, outage mapping, BER mapping, goodput mapping, artificial blockage, or other geometry-to-link effects are simulation assumptions unless independently calibrated against measurements.

Accordingly, the results support statements about **PC-FMCW-informed modeled connectivity** under controlled simulation. They do not establish measured optical-link performance, hardware validation, or real-world autonomous-driving safety.

## Reporting and figures

Publication figures should include:

- planner comparison violin/box plots for key connectivity and mobility/safety metrics,
- paired P2-P1, P3-P2, and P4-P2 improvement plots,
- robustness curves with 95% bootstrap confidence intervals,
- representative matched-seed trajectory visualizations,
- reliability-versus-progress and reliability-versus-clearance trade-off plots.

Negative or null results are retained. Safety outcomes must be reported separately from communication outcomes so a connectivity improvement cannot be described as an overall improvement when safety or mobility materially worsens.

## Reproducibility

Install dependencies, run the publication experiment matrix with a fixed seed range, then run the analysis/plot scripts on the resulting episode-level CSV. Preserve the generated manifest, git commit SHA, configuration file, Python/package versions, random seed list, and raw episode-level outputs with every reported result.

Large-seed numerical conclusions must be generated from the experiment outputs. This repository documentation must not contain invented or anticipated numerical results.
