# Paper Methods: PC-FMCW-Informed Predictive Connectivity-Aware Motion Planning

## Scope

This document defines the methods and claim boundary for the dataset-free paper study. The study is a controlled, model-based closed-loop simulation. It does not constitute measured optical-link validation or real-world autonomous-driving validation.

## System boundary

The upstream system is a phase-coded FMCW (PC-FMCW) integrated sensing/communication/illumination concept. The robotics extension begins after a target state/history has been estimated. The planner consumes target observations or predictions; it does not redesign the waveform, communication coding, or sensing front end.

At planning step k, the ego state is represented as

`x_e(k) = [p_x, p_y, psi, v]`,

and a target-motion predictor supplies a common mean future position sequence

`p_t_hat(k+j),  j = 1,...,H`.

For candidate ego trajectory i, the future relative geometry is

`r_i(k+j) = p_t_hat(k+j) - p_e,i(k+j)`.

A PC-FMCW-informed analytical connectivity model maps this relative geometry to modeled communication quantities such as SNR, outage probability, BER, and goodput. The geometry-to-link mapping is a simulation model, not a measured optical-channel calibration.

## Candidate motion and hard safety

Candidate ego trajectories are generated with the repository vehicle dynamics and control limits. Before objective scoring, candidates are filtered using common hard constraints: vehicle limits, road bounds, static obstacles, and time-aligned dynamic-target clearance.

Dynamic-target safety compares candidate state j only with target prediction j. Future target positions are therefore not treated as a simultaneous static obstacle cloud.

The same mean target prediction is used for dynamic safety across P0-P4. This prevents the oracle baseline from receiving privileged future truth for collision avoidance. The configured collision-clearance radius is also passed to every planner as the dynamic-target safety clearance and is reused by the collision indicator and realized TTC diagnostic. Planning feasibility and evaluation therefore share one declared target-clearance boundary rather than independent thresholds.

## Planner definitions

- **P0, mobility-only:** optimizes mobility without a connectivity term; common predicted target motion is still used for safety filtering.
- **P1, reactive connectivity-aware:** scores connectivity using a current/myopic target state while retaining the common predicted target trajectory for safety.
- **P2, predictive connectivity-aware:** evaluates modeled future connectivity along each candidate using the common mean target prediction.
- **P3, stochastic/risk-sensitive predictive:** uses the same mean target predictor and connectivity model as P2, then propagates declared target-prediction uncertainty with Monte Carlo samples for risk-sensitive scoring.
- **P4, oracle connectivity reference:** uses simulator future target truth only for connectivity forecasting. Its dynamic safety filter still receives the common predicted target trajectory. P4 is non-deployable and is an upper-reference baseline, not a deployable method.

After a planner selects a candidate, only its first control is executed. The target is observed again and the process repeats in receding-horizon closed loop.

## Evaluation design

The benchmark uses controlled parameterized target-motion scenarios and seeded observation perturbations. Planner comparisons use matched scenario/seed realizations so that paired statistical analysis is meaningful.

Reported connectivity quantities are model outputs. Safety/mobility diagnostics include path length, progress, minimum target distance, static-obstacle clearance, collision indicator, no-candidate steps, and realized collision-boundary TTC.

The benchmark additionally records the first realized collision time, number of
collision steps, and mutually exclusive candidate-rejection counts for road,
speed, static-obstacle, and dynamic-target filters. Prediction quality is
recorded as time-averaged closed-loop ADE and FDE against simulated future target
truth. These diagnostics are evaluation outputs only and are never exposed to a
deployable planner.

The realized TTC diagnostic uses constant relative velocity at the evaluated state and computes the earliest nonnegative time at which relative position reaches the declared collision-clearance radius. If the current separation is already inside that radius, TTC is zero; if the constant-velocity relative trajectory does not intersect the collision disk, TTC is infinite. This diagnostic is evaluated from realized simulator states and is not exposed to a planner as future information.

## Statistical analysis

Primary comparisons are paired by scenario and seed. The analysis pipeline reports paired effect estimates, bootstrap uncertainty, paired Wilcoxon tests, and Holm multiplicity correction. Robustness plots generated from episode-level sweep outputs use deterministic 95% bootstrap confidence intervals over simulated episodes.

Bootstrap intervals quantify variation across the controlled simulation episodes. They must not be described as physical measurement uncertainty.

## Robustness dimensions

The reproducible sweep runner varies observation noise, target-prediction uncertainty, planning horizon, and connectivity-objective weight. These sweeps test sensitivity of the closed-loop conclusions to declared modeling and planning choices rather than claiming coverage of all real optical or traffic conditions.

## Claim boundary

Supported claims are limited to the implemented controlled simulation: comparative behavior of P0-P4 under the same model, scenario, seed, dynamics, safety, and evaluation framework; effects of predictive versus reactive connectivity-aware planning; and sensitivity to the declared uncertainty/horizon/weight perturbations.

The study does **not** by itself support claims of measured PC-FMCW optical-channel accuracy, hardware performance, real-road safety, real-world generalization, or superiority outside the tested simulation conditions. Any future hardware, measured-link, or real-dataset experiment must be reported as a separate validation layer.

## Reproducibility

The repository maintains seeded benchmark scripts, robustness sweeps, paired statistical analysis, figure generation, unit/regression tests, CI smoke runs, and a manual full-paper experiment workflow with machine-readable provenance metadata. Benchmark CLI inputs are validated before experiment execution, including positive time step and horizon/sample counts and nonnegative uncertainty, connectivity weight, and collision-clearance settings. Numerical paper results should be generated from those reproducible outputs rather than inserted manually or inferred before the experiments are run.

The manual workflow derives both the benchmark seed count and the robustness
job matrix from the same workflow input. This prevents a nominal seed-count
change from silently leaving the robustness experiment fixed at a different
number of seeds.
