# When Can an Autonomous Vehicle Trust a Connectivity Map?
## Measurement-Support-Aware Predictive Planning with Field-Measured Vehicular QoS

> **Artifact reconciliation.** Numerical values in this working manuscript are reconciled to the archived `real-v2x-dual-branch-run34` artifacts. Older working-note absolute levels are superseded where they disagree with the archive. The paired planner effects were unchanged by this reconciliation.

## Abstract

Predictive communication-aware motion planning requires a vehicle to reason about link quality at future states that have not yet been selected. With field measurements, this creates a validity problem: a planner may prefer a counterfactual state precisely where its learned connectivity estimate has weak empirical support. We study when future vehicular quality-of-service (QoS) prediction provides decision-relevant information and how a planner should account for the measurement support of those predictions. Using CICV5G, complete acquisition runs are separated across training, calibration, and test partitions. Lightweight causal predictors estimate future delay at multiple planning horizons, while an empirical spatial-support model quantifies how well candidate states are represented by training measurements. We evaluate P0–P3 using route-constrained measured replay: candidate future states correspond to positions actually traversed later in the same held-out run, while their measured future delay remains hidden until after selection. Naive learned spatial/tree predictors do not outperform persistence at one-step prediction, whereas calibration-gated spatial/context information becomes useful at longer planning horizons. Across five grouped split assignments, P2 reduces measured delay and >50-ms threshold violations relative to P1 in all five assignments. P3 consistently reduces unsupported decision exposure but does not show a stable additional QoS gain. The evidence supports a narrow conclusion: predictive communication information can become decision-relevant at planning horizons, while empirical measurement support should be audited separately from predicted QoS before counterfactual estimates are trusted.

## 1. Introduction

Communication-aware motion planning, radio-map navigation, and QoS-aware vehicle trajectory planning are established research directions. This work therefore does not claim novelty for adding a communication cost to motion. The narrower question is: **when a planner evaluates future motion with a predictor learned from field measurements, when should it trust predicted QoS at counterfactual candidate states?**

We separate three questions: (1) whether future QoS contains incremental information beyond current-value persistence at planning-relevant horizons; (2) whether using that information changes decisions in a way that improves subsequently measured outcomes; and (3) whether selected counterfactual states are empirically represented by the training measurements.

The contribution is the combination of whole-run anti-leakage evaluation, horizon-dependent causal prediction, explicit training-measurement support auditing, and route-constrained measured replay. P2 represents predictive communication utility. P3 represents inference-validity/support control rather than an assumed extra QoS gain.

## 2. Dataset and leakage-controlled design

CICV5G supplies field-measured vehicular 5G/V2N2V delay together with synchronized radio and vehicle context. The archived repository study uses 38 acquisition runs and 43,045 samples. The primary split contains 22 training runs (22,441 samples), 7 calibration runs (8,846 samples), and 9 test runs (11,758 samples).

Complete runs are assigned to exactly one partition. Predictors and empirical spatial support use training runs only. Model/fusion selection and residual uncertainty calibration use calibration runs. Final replay evaluation uses held-out test runs. There is no random row split and no use of test-run data for predictor training, support fitting, conformal calibration, or horizon-fusion selection.

Repeated grouped split assignments reuse the same finite set of drives. They are therefore used as descriptive sensitivity analyses, not as five independent experiments.

## 3. Prediction and empirical support

For horizon `h`, the persistence baseline predicts the current measured delay. Lightweight learned alternatives include spatial kNN, Random Forest, Extra Trees, and the implemented spatial/context predictor. Horizon-adaptive fusion weights are selected using calibration data only.

On the archived primary split, one-step persistence obtains delay MAE **5.576 ms** and RMSE **20.914 ms**. Spatial kNN, Random Forest, and Extra Trees obtain delay MAE **10.862**, **7.150**, and **6.659 ms**, respectively. The negative result is retained: naive learned models do not outperform persistence at one step.

Across five grouped split assignments, calibration-gated prediction improves over persistence in all five assignments at 20, 50, and 100 steps. Mean MAE improvements are approximately **1.460, 2.506, and 2.622 ms**, respectively. Shorter 1/5/10-step effects are smaller and less consistent. Thus predictive value is horizon dependent.

Empirical support is fitted only from training coordinates. On the archived primary split, delay MAE / empirical conformal coverage are:

- <=1 m from training support: **5.332 ms / 0.888**;
- 1–5 m: **7.120 ms / 0.864**;
- 5–15 m: **9.579 ms / 0.761**.

This pattern is useful diagnostically but is not claimed to be a universal monotonic law across every route/context. Conformal intervals are treated as residual uncertainty diagnostics, not calibrated probabilities of threshold violation.

## 4. Route-constrained measured replay

Arbitrary off-route counterfactual positions generally have no measured QoS ground truth. Candidate choices are therefore restricted to later states actually present in the same held-out measured trajectory. Future measured QoS is hidden during scoring and revealed only after selection. This avoids fabricating a radio map for unvisited coordinates.

The evaluation is **offline route-constrained measured replay**, not closed-loop autonomous-driving validation.

## 5. Planner definitions

- **P0:** mobility/reference choice.
- **P1:** reactive/current-QoS persistence choice.
- **P2:** predictive future-QoS choice.
- **P3:** P2 plus an empirical-support penalty.

The experimental 50-ms delay threshold is an operating point, not a universal standard.

## 6. Primary replay results

Archived primary-split means are:

| Planner | Mean measured delay (ms) | >50 ms violation fraction | Changed-decision fraction | Unsupported-selection fraction | Mobility deviation |
|---|---:|---:|---:|---:|---:|
| P0 | 23.318 | 0.02179 | 0 | 0.15616 | 0 |
| P1 | 23.318 | 0.02179 | 0 | 0.15616 | 0 |
| P2 | 22.526 | 0.01900 | 0.02508 | 0.15634 | 0.01254 |
| P3 | 22.598 | 0.01934 | 0.04611 | 0.13798 | 0.02305 |

For P2 vs P1, the paired mean-delay effect is **-0.791924 ms**, with bootstrap 95% CI **[-1.723327, -0.137729] ms**. The raw paired Wilcoxon value is **p=0.046875**, but the Holm-adjusted value across the declared 12-test planner/metric family is approximately **0.28125**. It is therefore exploratory rather than multiplicity-corrected confirmatory evidence.

For the >50-ms violation fraction, P2–P1 is **-0.002791**; the direction is favorable but the result is not presented as a multiplicity-corrected discovery.

P3 does not improve measured delay over P2 on the primary split. Its supported role is different: the unsupported-selection fraction decreases by approximately **0.01836 absolute** while mobility deviation increases.

## 7. Multi-split descriptive robustness

P2–P1 measured-delay effects across five grouped split assignments are approximately:

`[-0.791924, -1.253015, -0.069188, -0.262972, -0.129775] ms`.

All five favor P2. Their descriptive mean is **-0.501375 ms**. The >50-ms violation-fraction effect is also negative in all five assignments, with descriptive mean **-0.002239**.

P3–P2 unsupported-selection effects are approximately:

`[-0.018361, -0.015286, -0.019048, -0.056201, -0.030872]`,

again favoring P3 in all five assignments; descriptive mean **-0.027954**. P3–P2 measured-delay effects have mixed sign and descriptive mean near zero (**-0.005765 ms**), so no stable extra QoS benefit is claimed.

These five assignments are dependent because they reuse drives. Historical split-level Wilcoxon fields, if present in archived CSV output, are not used as independent-sample inference.

## 8. Computational implementation

The archived vectorized replay reports about **83.1 microseconds per candidate** for batched QoS/support evaluation and approximately **9.85 microseconds mean decision-scoring time**. These are implementation-level CI timings only, not embedded-system or end-to-end real-time guarantees.

## 9. Discussion

The first result is a warning against weak baselines: one-step vehicular QoS is sufficiently persistent that a learned model can appear unnecessary at the next sample while still containing useful information seconds ahead. Prediction should therefore be evaluated at the horizon where the motion planner acts.

The second result separates predictive utility from inference validity. P2 uses future communication information and exhibits a consistent directional advantage over P1 across grouped split assignments. P3 spends additional mobility deviation to rely less often on weakly supported predictions; it should not be marketed as an automatic QoS improvement.

## 10. Limitations

The evaluation is offline replay rather than closed-loop vehicle deployment. Candidate states are constrained to measured route states. The 50-ms threshold is experimental. Residual conformal intervals do not represent calibrated event probabilities and can degrade under grouped distribution shift. The multi-split assignments are not independent replicates. CICV5G validates only the field-measured 5G decision branch and does not validate the separate PC-FMCW optical model.

## 11. Data and code availability

CICV5G is documented in the Scientific Data dataset paper (DOI `10.1038/s41597-026-07239-7`) and archived under Zenodo DOI `10.5281/zenodo.17475688`. Repository scripts record the subset preparation, grouped split, prediction, support audit, replay, and statistical analysis pipeline. Publication figures/tables should be regenerated directly from archived artifact CSVs using `scripts/build_paper2_publication_assets.py`.

## 12. Conclusion

Field-measured communication prediction can become decision-relevant at planning horizons even when persistence dominates one-step prediction. Predictive P2 shows a consistent directional reduction in measured delay relative to reactive P1 across grouped split assignments, while P3 consistently reduces unsupported decision exposure without a stable additional QoS gain. A trustworthy connectivity planner should therefore be evaluated not only by predictive accuracy but also by causal horizon, empirical measurement support, multiplicity-aware statistics, and the validity of counterfactual states on which it acts.

## References

The verified bibliography and DOI audit are maintained in `REFERENCES.md` and `references.bib`. The submission-ready source is `paper2.tex`.
