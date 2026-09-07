# Part B Completion Plan — Predictive Connectivity-Aware Receding-Horizon Motion Planning

## Research question

**Can predictive connectivity-aware motion planning improve future modeled communication reliability relative to reactive planning while maintaining comparable safety and acceptable mobility cost?**

The proposed method is

```text
tau* = argmin_tau [
    J_mobility(tau)
  + lambda * J_connectivity(tau, predicted_target)
  + J_risk(tau, uncertainty)   # P3 only
]
```

subject to common vehicle dynamics, road constraints, static-obstacle safety, and dynamic-target safety.

The study is explicitly a **controlled PC-FMCW-informed analytical simulation**. It is not measured optical validation and not real-world autonomous-driving validation.

## What already exists

- [x] P0 mobility-only planner.
- [x] P1 reactive connectivity-aware planner.
- [x] P2 predictive connectivity-aware planner.
- [x] P3 uncertainty/risk-aware predictive planner.
- [x] P4 oracle connectivity reference.
- [x] Shared candidate generator and vehicle limits.
- [x] Shared road/static-obstacle/dynamic-target safety filtering.
- [x] Oracle fairness rule: P4 receives truth only for connectivity forecasting, not collision avoidance.
- [x] Receding-horizon closed-loop execution.
- [x] PC-FMCW-informed geometry -> SNR/outage/BER/goodput model.
- [x] Explicit separation between upstream reference constants and newly introduced optical geometry assumptions.
- [x] Episode-level communication and robotics/safety metrics.
- [x] Prediction ADE/FDE diagnostics.
- [x] Paired scenario/seed analysis infrastructure.
- [x] Bootstrap intervals, paired Wilcoxon, Holm correction infrastructure.
- [x] Robustness workflow infrastructure.
- [x] Unit/regression tests and CI smoke infrastructure.

## Critical methodological corrections before final execution

- [ ] Extend the primary statistics output to include `cohens_dz`, rank-biserial correlation, and paired win/tie/loss fractions for every declared comparison/metric.
- [ ] Apply Holm correction by predeclared confirmatory family rather than one undifferentiated family across all exploratory metrics unless the frozen protocol explicitly chooses the latter.
- [ ] Freeze directionality and practical non-inferiority/superiority margins for safety and mobility outcomes before the large-seed final run.
- [ ] Report collision/no-candidate outcomes with scenario-specific diagnostics; aggregate rates alone are insufficient.
- [ ] Treat candidate-level rejection counts as diagnostics only, never as independent samples.
- [ ] Add control smoothness/effort metrics if candidate controls make them available without redesigning the planner.
- [ ] Add explicit link-survival/reliability outcome in the benchmark output because it is already produced by the link predictor but not currently stored as an episode metric.
- [ ] Report minimum SNR in addition to mean SNR if the realized-link trace supports it.
- [ ] Add explicit no-candidate rate normalized by episode steps.
- [ ] Add static-obstacle collision/boundary diagnostics if not already derivable from current clearance traces.

## Frozen final benchmark protocol

- [ ] Create `configs/experiments/part_b_final.yaml`.
- [ ] Freeze seed count and seed range before looking at final outcomes.
- [ ] Freeze target-motion scenario families.
- [ ] Freeze observation noise and predictor assumptions.
- [ ] Freeze planning horizon and candidate-generator parameters.
- [ ] Freeze connectivity weight lambda for the confirmatory benchmark using development-only selection or a declared nominal value.
- [ ] Freeze P3 Monte Carlo sample count and risk hyperparameters.
- [ ] Freeze link-model assumptions and provenance.
- [ ] Freeze primary comparisons: P2 vs P1; P3 vs P2; P2 vs P4; optionally P3 vs P4 as descriptive/oracle-gap analysis.
- [ ] Freeze primary communication endpoints and safety/mobility non-inferiority endpoints.
- [ ] Freeze bootstrap sample count/RNG seed and multiplicity family.
- [ ] Freeze all robustness/ablation grids before the final aggregate run.

## Main large-seed closed-loop benchmark

- [ ] Execute all P0-P4 planners on every frozen scenario and every frozen seed.
- [ ] Verify exact paired cardinality by `(scenario, seed)` for all planner comparisons.
- [ ] Preserve raw episode rows.
- [ ] Preserve scenario/seed/planner configuration and exact commit SHA.
- [ ] Preserve Python/package environment and link-model provenance.
- [ ] Generate paired statistics only from the frozen raw rows.

## Primary scientific questions

### RQ1 — Does P2 beat P1?

- [ ] Compare modeled outage.
- [ ] Compare mean and minimum modeled SNR.
- [ ] Compare modeled BER.
- [ ] Compare modeled goodput.
- [ ] Compare link survival/reliability.
- [ ] Compare path length and progress.
- [ ] Compare target/static-obstacle clearance.
- [ ] Compare collisions and TTC diagnostics.
- [ ] Compare no-candidate rate.
- [ ] Compare control smoothness/effort if available.
- [ ] Conclude HELP / NEUTRAL / HURT by scenario and aggregate only after considering both connectivity gains and robotics cost.

### RQ2 — Does P3 add value over P2?

- [ ] Test nominal conditions.
- [ ] Test increasing prediction uncertainty.
- [ ] Test high target maneuverability.
- [ ] Test difficult/threshold-sensitive connectivity regimes.
- [ ] Quantify communication improvement versus conservatism, route/progress penalty and infeasibility.
- [ ] Retain null/negative result if risk-awareness adds no reliable value.

### RQ3 — Distance from Oracle

- [ ] Quantify P4-P2 and P4-P3 gaps on identical scenario/seed units.
- [ ] Report oracle gap for connectivity only.
- [ ] State clearly that P4 is not a globally optimal motion planner and receives no oracle safety advantage.
- [ ] Identify scenarios where prediction error, not planner structure, is the dominant remaining gap.

## Robustness study

Use matched seeds and one-axis-at-a-time sweeps unless a multivariate design is predeclared.

- [ ] Target prediction error/noise.
- [ ] Prediction bias/delay if implemented.
- [ ] Connectivity weight lambda.
- [ ] Planning horizon.
- [ ] Target maneuverability.
- [ ] Obstacle density.
- [ ] Reference SNR offset.
- [ ] Path-loss scaling/exponent.
- [ ] Beam-width/pointing sensitivity.
- [ ] Outage threshold.
- [ ] Outage softness/model parameters.
- [ ] Blockage/attenuation/channel mismatch assumptions.
- [ ] P3 uncertainty scale.
- [ ] P3 Monte Carlo sample sensitivity where computationally relevant.

For each sweep, report connectivity **and** mobility/safety outcomes. A higher SNR alone is not sufficient for a positive conclusion.

## Ablations

- [ ] No prediction: reactive P1.
- [ ] No connectivity term: P0 / lambda=0 consistency check.
- [ ] Predictive mean without risk: P2.
- [ ] Predictive uncertainty/risk: P3.
- [ ] Short versus long horizon.
- [ ] Connectivity-weight ablation.
- [ ] Prediction-perfect oracle reference: P4 connectivity only.

## Safety–connectivity trade-off

- [ ] Build Pareto-style reliability vs progress/path-length plots.
- [ ] Build reliability vs minimum-clearance/no-candidate plots.
- [ ] Identify dominated configurations.
- [ ] Quantify practical mobility cost per communication gain where interpretable.
- [ ] Explicitly flag any regime where communication improves while safety/infeasibility materially worsens.

## Final statistics

For each predeclared comparison/outcome:

- [ ] Paired mean/median difference.
- [ ] 95% paired bootstrap CI.
- [ ] Paired Wilcoxon signed-rank test.
- [ ] Holm-adjusted p-value within the frozen family.
- [ ] Paired Cohen dz.
- [ ] Rank-biserial correlation.
- [ ] Win/tie/loss fraction.
- [ ] Independent episode count and scenario count.
- [ ] Scenario-specific effect table.

Do not infer from candidate samples, planning steps or Monte Carlo draws as if they were independent episodes.

## Publication figures/tables

- [ ] System architecture / method figure.
- [ ] P0-P4 planner hierarchy figure.
- [ ] Main paired P2-P1 communication effects.
- [ ] Main paired P2-P1 safety/mobility effects.
- [ ] P3-P2 risk-awareness effects.
- [ ] Oracle-gap figure.
- [ ] Robustness curves with 95% episode-level bootstrap CIs.
- [ ] Reliability-vs-progress trade-off figure.
- [ ] Reliability-vs-clearance/infeasibility figure.
- [ ] Representative matched-seed closed-loop trajectories.
- [ ] Scenario-level failure-mode table.
- [ ] Frozen parameter/provenance table.
- [ ] Main statistical table with effect sizes and corrected p-values.

All paper numbers must be generated from saved artifacts. No manual numerical insertion.

## Final paper/report

- [ ] Abstract.
- [ ] Introduction.
- [ ] Related Work.
- [ ] System Model.
- [ ] Problem Formulation.
- [ ] Proposed Predictive Planner.
- [ ] Baselines.
- [ ] Experimental Protocol.
- [ ] Results.
- [ ] Statistical Analysis.
- [ ] Ablations.
- [ ] Robustness.
- [ ] Safety–Connectivity Trade-off.
- [ ] Discussion.
- [ ] Limitations.
- [ ] Conclusion.
- [ ] Reproducibility.

## Claim boundary

Allowed wording:

- predictive connectivity-aware planning under a controlled PC-FMCW-informed analytical simulation;
- modeled SNR/BER/outage/goodput;
- comparative simulated safety/mobility diagnostics;
- operating regimes where predictive information helps, is neutral, or hurts.

Not allowed without new evidence:

- measured optical performance;
- hardware validation;
- real-vehicle validation;
- real-world autonomous-driving safety;
- physical experiment;
- universal superiority beyond the tested model/scenarios.

## Final audit questions

1. What existed before the final study?
2. What code/config/methodology changed?
3. What was actually executed on the frozen commit?
4. Does P2 beat P1 on communication while satisfying the safety/mobility gate?
5. Does P3 add value over P2, and in which uncertainty regimes?
6. How far are P2/P3 from P4?
7. What safety/mobility cost accompanies the communication gains?
8. What model/data/validation limitations remain?
9. Is the work ready as a Part B technical extension?
10. Is it publication-ready at the claimed evidence level?

## Submission gate

The project is **not publication-ready** until the frozen large-seed benchmark, robustness matrix, ablations, paired statistics with effect sizes, final figures/tables, provenance bundle, and artifact-derived manuscript have all been completed and audited.
