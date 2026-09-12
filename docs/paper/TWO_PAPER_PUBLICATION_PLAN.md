# Two-Paper Publication Plan

## Purpose

The repository now supports two related but scientifically distinct manuscripts. This document freezes the intended separation so that future writing does not blur evidence, duplicate contributions, or overclaim novelty.

## Paper 1 — PC-FMCW Predictive Connectivity-Aware Motion Planning

### Working title

**Predictive Connectivity-Aware Motion Planning for PC-FMCW Integrated Sensing, Communication, and Illumination**

### Primary question

Can a safety-constrained autonomous vehicle exploit predicted future PC-FMCW-informed link quality to make better receding-horizon motion decisions than reactive connectivity-aware planning?

### Main contribution

A perception-to-action extension downstream of the PC-FMCW sensing/tracking architecture. Candidate ego trajectories are evaluated using predicted target motion and trajectory-conditioned future optical-link quality while all deployable planners share the same hard safety information.

### Required evidence

1. Frozen 50-seed P0–P4 confirmatory benchmark.
2. Seed-level paired inference for P2 vs P1 and P3 vs P2.
3. Mobility/connectivity/safety trade-off analysis.
4. Directional-vs-distance-only optical mechanism ablation.
5. Prediction/uncertainty robustness analysis.
6. Oracle-gap interpretation without oracle safety leakage.
7. Computational-cost reporting.
8. Failure cases and scenario-level diagnostics.

### Central figures

1. PC-FMCW perception-to-action architecture.
2. Candidate-trajectory future-link evaluation schematic.
3. P0–P4 aggregate performance with uncertainty.
4. Mobility–communication trade-off/Pareto figure.
5. Directional-vs-distance-only mechanism ablation.
6. Prediction uncertainty / robustness figure.
7. Representative trajectory/QoS time-series case.

### Central tables

1. PC-FMCW/upstream vs robotics-side parameter provenance.
2. P0–P4 planner information/fairness matrix.
3. Frozen confirmatory aggregate results.
4. Paired effect sizes, confidence intervals, corrected p-values.
5. Mechanism/robustness ablations and computation time.

### Novelty wording

Do not claim that communication-aware planning, optical trajectory optimization, FSO trajectory optimization, or ISAC-aware motion optimization is itself novel.

The defensible novelty is the specific closed-loop bridge from a PC-FMCW vehicular ISCAI sensing/tracking architecture to safety-constrained predictive ego-motion decisions, together with technology-specific directional-link mechanism analysis and controlled P0–P4 evidence.

### Evidence boundary

This paper is model-based. It does not contain measured PC-FMCW optical-channel validation unless such measurements are added in future work.

---

## Paper 2 — Measurement-Support-Aware Predictive V2X Planning

### Working title

**When Can an Autonomous Vehicle Trust a Connectivity Map? Measurement-Support-Aware Predictive Planning with Field-Measured Vehicular QoS**

Alternative conservative title:

**Measurement-Support-Aware Predictive Connectivity Planning with Field-Measured Vehicular QoS**

### Primary question

When does future-QoS prediction from field measurements provide actionable planning benefit, and how should the planner respond when candidate decisions move into poorly supported regions of the measured data distribution?

### Main contribution

A lightweight real-data predictive-planning methodology that combines whole-drive anti-leakage QoS prediction, decision-horizon evaluation, empirical measurement-support auditing, and route-constrained measured-outcome replay.

### Required evidence

1. Dataset provenance and EDA for 38 drives / 43,045 samples.
2. Persistence and lightweight predictor baselines.
3. Whole-drive/blocked prediction evaluation.
4. Planning-horizon study.
5. Route-constrained measured replay for P1/P2/P3.
6. Held-out-run paired statistics with multiplicity correction.
7. Five grouped split assignments as sensitivity, not independent replication.
8. Empirical-support analysis and unsupported-selection exposure.
9. P3 negative/nuanced QoS result retained explicitly.
10. Computation-time and failure-case analysis.

### Central figures

1. Dataset route/QoS coverage map.
2. Prediction error vs horizon.
3. Persistence vs learned predictor comparison.
4. Example route-constrained planner replay.
5. Measured delay/violation comparison P1 vs P2.
6. Unsupported-exposure comparison P2 vs P3.
7. Support/context failure analysis.
8. Mobility–communication/support trade-off.

### Central tables

1. Dataset statistics and split manifest.
2. Predictor performance by horizon.
3. Primary held-out-run planner effects.
4. Five-split directional robustness summary.
5. Support-aware P3 effects and computation time.
6. Claim/limitation table.

### Main empirical story

P2 provides the predictive communication benefit: P2-minus-P1 measured delay is negative in all five grouped split assignments currently evaluated.

P3 should not be sold as a universally better QoS planner. Its stable role is to reduce decisions made in empirically unsupported regions. Thus the paper separates communication utility from epistemic/support validity.

### Novelty wording

Do not claim that radio-map planning, communication-aware planning, predictive QoS, or uncertainty-aware planning is new in isolation.

The defensible contribution is the combination of field-measured vehicular QoS, leakage-safe whole-drive evaluation, explicit decision-horizon testing, empirical support auditing for counterfactual planner queries, and measured-support-constrained replay that avoids fabricating ground truth at unobserved positions.

### Evidence boundary

The replay is offline and route constrained. It is not a real-road closed-loop autonomous-driving trial. The CICV5G data are not PC-FMCW measurements and cannot validate PC-FMCW optical propagation.

---

## Shared material allowed between papers

The papers may share high-level motivation and the generic receding-horizon abstraction:

```text
state/history → prediction → candidate trajectories → safety → future QoS → decision
```

They may also cross-reference the common P0/P1/P2/P3 terminology if useful.

However, they should not reuse identical contribution paragraphs, identical primary experiments, or imply that one evidence source validates the other technology.

## Recommended submission order

1. Finish and freeze Paper 1's 50-seed PC-FMCW confirmatory artifact and mechanism ablation.
2. Draft/submit Paper 1 as the direct extension of the upstream PC-FMCW work.
3. Freeze Paper 2's measured-data tables/figures and claim audit.
4. Draft/submit Paper 2 around the counterfactual trust/support problem, citing Paper 1 as prior/shared architecture only when publication status permits.

The order can be reversed if Paper 2 reaches a target venue deadline first, but the manuscripts must preserve independent research questions.

## Definition of manuscript-ready

A paper is not ready because the code runs. It is ready only when:

- the primary hypothesis is frozen;
- primary experimental units are defined correctly;
- all primary comparisons are complete;
- confidence intervals/effect sizes are generated from frozen artifacts;
- multiplicity treatment is declared;
- ablations support the mechanism claim;
- negative results are retained;
- figures regenerate from machine-readable outputs;
- claim audit contains no unresolved high-risk statement;
- limitations distinguish simulation, measurement, prediction, and inference;
- reproduction commands work from a clean checkout.
