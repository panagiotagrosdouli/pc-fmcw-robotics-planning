# When Can an Autonomous Vehicle Trust a Connectivity Map?
## Measurement-Support-Aware Predictive Planning with Field-Measured Vehicular QoS

> Working manuscript. Claims are intentionally restricted to field-measured communication data, offline route-constrained replay, and the implemented decision layer. This paper does **not** claim that 5G measurements validate the PC-FMCW optical link.

## Abstract

Predictive communication-aware motion planning requires a vehicle to reason about link quality at future states that have not yet been selected. With field measurements, this creates a validity problem: a planner may prefer a counterfactual state precisely where its learned connectivity estimate has weak empirical support. We study when future vehicular quality-of-service (QoS) prediction provides decision-relevant information and how an autonomous planner should account for the measurement support of those predictions. Using the CICV5G field-measurement dataset, we construct a leakage-resistant pipeline in which complete acquisition runs are separated across training, calibration, and test partitions. Lightweight causal predictors estimate future communication delay at multiple planning horizons, while an empirical spatial-support model quantifies how well candidate states are represented by training measurements. We then evaluate reactive, predictive, and support-aware planners using route-constrained measured replay: candidate future states are restricted to positions that were actually traversed later in the same held-out run, and their measured future delay is hidden until after the planner selects a candidate. The experiments show that naive learned spatial and tree predictors do not outperform persistence at the one-step horizon, whereas calibration-gated spatial/context information becomes useful at longer planning horizons. Across five grouped split assignments, predictive planning reduces measured delay and the fraction of delay-threshold violations relative to the reactive baseline in all five assignments. Adding measurement-support awareness consistently reduces unsupported decision exposure, but does not produce a stable additional QoS improvement and incurs a mobility-deviation trade-off. These results support a narrower conclusion than generic connectivity-map planning: predictive communication information can influence motion beneficially when evaluated at a decision-relevant horizon, while empirical support should be audited separately from predicted QoS before counterfactual connectivity estimates are trusted.

## 1. Introduction

Autonomous vehicles increasingly depend on wireless communication for cooperative perception, cloud-assisted services, infrastructure interaction, and distributed decision making. This creates a coupling between motion and communication: where a vehicle moves affects the communication conditions it experiences, while predicted communication conditions can in turn influence where the vehicle should move. Communication-aware motion planning is therefore not new. The harder methodological question addressed here is narrower: **when a planner evaluates future motion using a connectivity predictor learned from field measurements, when should it trust the predicted QoS at counterfactual candidate states?**

A field-measured connectivity map is not a physical oracle. Its predictions inherit the spatial, temporal, route, network, and contextual coverage of the measurements used to train it. A candidate trajectory can therefore appear communication-optimal while lying in a region that is weakly represented by the training data. Treating predicted QoS and empirical measurement support as the same quantity hides this failure mode. Likewise, randomly splitting individual samples from a drive can produce optimistic estimates because temporally and spatially adjacent measurements from the same acquisition run leak across training and evaluation.

This work separates three questions that are often conflated. First, does future QoS contain incremental predictive information beyond the current communication state at the horizon relevant to planning? Second, does using that prediction change motion in a way that improves subsequently observed communication outcomes? Third, are the candidate states selected by the planner sufficiently supported by the measurements from which the predictor was learned?

We answer these questions using CICV5G, a field-measured 5G vehicular dataset containing delay, radio indicators, vehicle state, position, and acquisition context. The implemented study uses 38 acquisition runs comprising 43,045 samples. Complete runs, rather than individual rows, are assigned to training, calibration, and test partitions. Prediction uncertainty is estimated from held-out calibration residuals, while empirical spatial support is computed only with respect to training coordinates. The planning evaluation is deliberately conservative: instead of inventing communication ground truth at arbitrary off-route positions, we use route-constrained measured replay, in which candidate states correspond to future states that were actually measured in the held-out run.

The contributions are:

1. A leakage-resistant field-measurement pipeline for predictive vehicular QoS planning, with complete-run train/calibration/test separation and explicit provenance.
2. A horizon-dependent prediction study showing that persistence is difficult to beat at short horizons, while calibrated spatial/context information becomes useful at longer decision horizons.
3. An explicit empirical measurement-support audit for counterfactual candidate states, based only on training measurements and kept conceptually separate from QoS prediction uncertainty.
4. A route-constrained measured-replay protocol that hides future measured QoS until after a planner decision, avoiding fabricated off-route communication ground truth.
5. A planner comparison that separates predictive communication utility from inference-validity control: predictive planning improves measured communication outcomes robustly across grouped split assignments, whereas support-aware planning primarily reduces unsupported decision exposure rather than providing a stable additional QoS gain.

## 2. Related Work and Research Gap

Communication-aware robot motion planning, radio-map-aware trajectory optimization, predictive QoS planning, and integrated sensing/communication/control are established research areas. Consequently, this paper does not claim novelty for using predicted connectivity in a motion objective, avoiding communication blackspots, constructing radio maps, or optimizing a trajectory under communication constraints.

Recent work further reduces the novelty available to broad claims. Predictive radio-map planning has incorporated online estimation and uncertainty; autonomous-vehicle trajectory planning has optimized motion to satisfy QoS objectives; V2X studies have predicted QoS from real urban measurements; and optical/FSO/ISAC systems have coupled communication conditions with trajectory optimization. The gap pursued here is therefore methodological rather than categorical.

Our focus is the validity of **counterfactual planner queries to a predictor trained on field measurements**. Specifically, we combine whole-run anti-leakage evaluation, horizon-dependent causal prediction, explicit training-measurement support auditing, and measured-support route replay. The objective is not to propose another generic connectivity-aware planner, but to determine when measured-data predictions contain decision-relevant information and when the planner is querying them outside their empirical support.

## 3. Research Questions and Hypotheses

### RQ1 — Horizon-dependent predictive value
Does spatial/context information improve future-delay prediction beyond persistence at horizons relevant to motion planning?

**H1.** Learned spatial/context information will provide incremental value over persistence at sufficiently long horizons, but need not outperform persistence at one-step prediction.

### RQ2 — Predictive decision utility
Does a planner using future predicted QoS improve subsequently measured communication outcomes relative to a reactive/current-QoS planner?

**H2.** Predictive planning (P2) will reduce measured future delay relative to reactive planning (P1) under held-out route replay, with robustness assessed across grouped split assignments.

### RQ3 — Measurement-support control
Does explicitly penalizing weakly supported counterfactual states reduce the planner's exposure to unsupported decisions?

**H3.** Support-aware planning (P3) will reduce unsupported candidate selection relative to P2, potentially at the cost of greater mobility deviation. A further QoS improvement over P2 is not assumed.

## 4. Data and Leakage-Controlled Experimental Design

### 4.1 CICV5G field measurements

The primary dataset is CICV5G, collected from a real 5G vehicle-to-network-to-vehicle communication loop. Available variables include communication delay, RSRP, SINR, cell identity, UTM position, heading, velocity, timestamps, network type, and scenario context. The present acquisition subset contains 38 runs and 43,045 samples.

The dataset is used only as evidence for the measured communication decision layer. It does not provide optical PC-FMCW measurements and therefore cannot validate an optical propagation or PC-FMCW communication model.

### 4.2 Unit of independence and anti-leakage split

Rows from the same drive are strongly dependent. Random row splitting would allow near-adjacent positions and temporally correlated measurements from the same acquisition run to appear in both training and evaluation. We therefore use the complete acquisition run as the split unit. Training measurements are used to fit predictors and the spatial-support representation; calibration runs are used for residual-based uncertainty calibration and model/fusion selection; test runs remain untouched until final evaluation.

Repeated grouped split assignments are used as a robustness/sensitivity analysis. Because these assignments reuse the same finite set of drives, they are not treated as five independent experimental replicates and are not used to manufacture an inferential sample size of five.

## 5. Future-QoS Prediction

### 5.1 Baselines

We compare persistence/current-QoS prediction with lightweight learned alternatives including spatial k-nearest neighbors and tree ensembles. The design intentionally favors interpretable, reproducible baselines over a high-capacity deep model, because the central question is whether future communication information is decision-relevant rather than whether a complex model can minimize a leaderboard metric.

### 5.2 Horizon-adaptive prediction

At very short horizons, the current measured communication state is a strong predictor of the immediate future. We therefore evaluate prediction error as a function of horizon rather than assuming a learned map should dominate persistence everywhere. A calibration-gated fusion combines persistence with a spatial/context predictor, with fusion weights selected only from calibration data.

### 5.3 Uncertainty

Residual split-conformal intervals are computed using calibration residuals. These intervals are interpreted as empirical uncertainty diagnostics under the evaluated grouped distribution, not as calibrated probabilities of future outage or threshold violation. Coverage is reported globally and conditionally with respect to empirical measurement support.

## 6. Empirical Measurement Support

For every candidate position, the support module computes its relationship to the training measurements, including nearest-training distance and local measurement density. Support is fitted exclusively from training coordinates. This quantity answers a different question from the QoS predictor: not "what delay do we expect?" but "how strongly is this counterfactual query represented by the measurements used to learn the predictor?"

A candidate is marked unsupported according to predeclared spatial-support criteria. P3 incorporates this support information as a planning penalty. The support threshold is not presented as a universal physical boundary; it is an empirical validity control for the present measurement dataset and experimental protocol.

## 7. Route-Constrained Measured Replay

A central evaluation problem is that arbitrary counterfactual trajectories do not have measured communication ground truth. Interpolating or simulating that ground truth would make a real-data claim depend on another model. We instead restrict candidate choices to future states that were actually traversed later in the same held-out acquisition run.

At each decision point, planners receive only information that would be causally available at that point together with predictor outputs derived from training/calibration data. The future measured delay attached to each candidate is hidden. After the planner selects a candidate, that recorded future measurement is revealed solely for evaluation. This produces an offline measured replay rather than a real closed-loop autonomous-driving experiment, but it avoids fabricating communication outcomes at unmeasured positions.

## 8. Planner Definitions

**P0 — Mobility/reference baseline.** Selects the reference mobility choice without communication optimization.

**P1 — Reactive communication baseline.** Uses current/persistent QoS information without exploiting a future spatial prediction.

**P2 — Predictive communication planner.** Scores candidate future states using predicted future QoS and represents the primary test of predictive communication utility.

**P3 — Prediction plus empirical-support control.** Extends P2 with a penalty for weakly supported counterfactual states. P3 is interpreted as an inference-validity controller, not automatically as a stronger QoS optimizer.

An oracle P4 is intentionally omitted from the measured-data branch unless exact counterfactual measured ground truth is available for all choices.

## 9. Evaluation Metrics and Statistics

Prediction metrics include delay MAE and RMSE, uncertainty coverage, and support-stratified error diagnostics. Planning metrics include subsequently measured delay, fraction of decisions exceeding the experimental 50 ms delay operating threshold, fraction of changed decisions relative to the mobility/reference choice, unsupported-selection fraction, and mobility deviation.

Within a fixed held-out split, planner comparisons are paired by acquisition run. Bootstrap confidence intervals and paired Wilcoxon tests are reported, with Holm correction across the predeclared family of planner/metric comparisons. Raw p-values are retained as exploratory diagnostics but are not described as confirmatory when they fail multiplicity correction. Across alternative grouped split assignments, effect direction and magnitude are reported descriptively because the assignments reuse drives and are therefore statistically dependent.

## 10. Results

### 10.1 One-step prediction is dominated by persistence

On the primary grouped split, persistence achieves approximately 7.42 ms delay MAE and 11.37 ms RMSE. Conditioned spatial kNN, Random Forest, and Extra Trees obtain approximately 12.34, 9.29, and 8.95 ms MAE, respectively. Thus, the naive learned spatial/tree predictors do not beat persistence at one-step prediction. This negative result is retained because it motivates the horizon-dependent analysis rather than post hoc model replacement.

### 10.2 Predictive value emerges at longer horizons

Across five grouped split assignments, the calibration-gated horizon-adaptive predictor improves delay MAE relative to persistence in all five assignments at 20, 50, and 100 steps. The mean improvements are approximately 1.46 ms, 2.51 ms, and 2.62 ms, respectively. Improvements at 1, 5, and 10 steps are small or inconsistent. The evidence therefore supports H1 only in its horizon-qualified form: spatial/context information becomes useful at sufficiently long decision horizons rather than being universally superior to persistence.

### 10.3 Measurement support exposes a distinct validity axis

Prediction error and conformal coverage vary with empirical measurement support. In the primary split, delay MAE is approximately 6.98 ms for queries within 1 m of a training measurement, 8.51 ms at 1–5 m, and 10.47 ms at 5–15 m, while empirical interval coverage decreases from approximately 0.888 to 0.841 and 0.761 across the same bins. More detailed forensic analysis shows that this relationship is context dependent rather than universally monotonic within every drive; degradation is concentrated in particular contexts and low-support segments. We therefore interpret support as an empirical risk indicator, not a deterministic error law.

### 10.4 Predictive planning improves measured outcomes relative to reactive planning

In the primary held-out replay, P1 obtains approximately 11.77 ms mean measured delay and a 0.0166 fraction of decisions above the 50 ms operating threshold. P2 reduces these values to approximately 10.97 ms and 0.0138, while changing approximately 12.0% of decisions and introducing approximately 0.060 mobility deviation under the implemented metric.

The paired primary-split P2–P1 mean-delay effect is approximately -0.792 ms, with a bootstrap 95% interval of approximately [-1.723, -0.138] ms. The raw paired Wilcoxon p-value is 0.046875, but this effect does not remain significant after Holm correction across the full predeclared 12-test family (adjusted p approximately 0.281). It is therefore not presented as a multiplicity-corrected confirmatory discovery.

The direction is nevertheless robust to grouped split assignment. P2–P1 measured-delay effects across five split seeds are approximately -0.792, -1.253, -0.069, -0.263, and -0.130 ms: all five favor P2, with a descriptive mean effect of approximately -0.501 ms. The >50 ms violation-fraction effect is also negative in all five assignments, with mean change approximately -0.00224. Because the same 38 drives are reused, this 5/5 consistency is descriptive robustness evidence rather than an independent n=5 hypothesis test.

### 10.5 P3 controls unsupported decisions rather than reliably improving QoS

In the primary split, P3 reduces unsupported decision exposure from approximately 0.1056 under P2 to 0.0873, while mean measured delay changes from approximately 10.974 to 11.047 ms and mobility deviation rises from approximately 0.0602 to 0.0707. Across five grouped split assignments, the P3–P2 unsupported-selection effects are approximately -0.0184, -0.0153, -0.0190, -0.0562, and -0.0309, all favoring P3, with descriptive mean approximately -0.0280.

By contrast, P3–P2 measured-delay effects have mixed sign across the same assignments (+0.073, +0.015, +0.143, -0.031, -0.229 ms), with a mean near zero. Thus H3 is supported in the narrow sense that P3 consistently reduces unsupported decision exposure, but the data do not support claiming a stable additional QoS improvement over P2. This distinction is central to the paper: empirical-support control changes **where the planner is willing to trust its predictor**, not necessarily the optimum of the measured communication metric.

## 11. Discussion

The results suggest that the value of communication prediction should be evaluated at the decision horizon rather than inferred from one-step prediction accuracy. Persistence is a strong short-horizon baseline because vehicular communication measurements are temporally correlated. A learned connectivity representation can therefore appear unnecessary in a one-step benchmark while still contain information that matters several seconds ahead, when a motion planner must act before degradation occurs.

The second finding is that predictive quality and inference validity are different planning quantities. P2 exploits future QoS estimates and exhibits a robust directional improvement over the reactive baseline across grouped split assignments. P3 asks an additional question: whether the locations preferred by that predictor are empirically represented by the training measurements. Its consistent reduction in unsupported selections, combined with mixed QoS effects and increased mobility deviation, shows that support awareness should be interpreted as a validity/risk trade-off rather than a free communication gain.

This distinction also constrains statistical interpretation. A nominal conformal interval is not an outage probability, and repeated train/test partitions of the same 38 acquisition runs do not create independent experimental subjects. We therefore separate within-split paired inference from across-split descriptive robustness and retain negative results where the evidence does not support a stronger claim.

## 12. Limitations

The evaluation is offline route-constrained replay, not closed-loop vehicle deployment. Candidate states are restricted to states actually traversed in the recorded run, which improves measurement validity but limits the planner's counterfactual action space. CICV5G communication measurements represent the network conditions of its acquisition campaign and cannot establish universal behavior across operators, cities, traffic loads, or radio technologies. The 50 ms threshold is an experimental operating point rather than a universal V2X requirement. Spatial support is an empirical dataset-coverage diagnostic, not a physical propagation confidence measure. Finally, the lightweight prediction models are deliberately conservative baselines; stronger sequence models could improve predictive accuracy but would not remove the need for anti-leakage evaluation and counterfactual support auditing.

## 13. Conclusion

Field-measured connectivity prediction becomes useful to autonomous motion planning only when prediction accuracy, planning horizon, and empirical validity are considered together. In CICV5G replay, persistence remains difficult to beat at short horizons, while spatial/context information provides consistent incremental value at longer horizons. Predictive planning then improves measured communication outcomes relative to a reactive baseline across grouped split assignments. Explicit measurement-support control consistently reduces decisions made in weakly supported regions, but does not provide a stable additional QoS gain and trades against mobility deviation. The resulting design principle is simple: a planner should not ask only what connectivity is predicted at a future state; it should also ask whether the measurements justify trusting that prediction there.

## Planned Figures and Tables

- Fig. 1: End-to-end measured-data pipeline and causal information flow.
- Fig. 2: Whole-run train/calibration/test split and route-constrained replay protocol.
- Fig. 3: Delay MAE versus prediction horizon for persistence and horizon-adaptive prediction.
- Fig. 4: Prediction error and empirical interval coverage versus measurement-support distance.
- Fig. 5: P1/P2/P3 measured delay, violation fraction, unsupported exposure, and mobility deviation.
- Fig. 6: Across-split paired effect directions for P2-P1 and P3-P2.
- Table I: CICV5G variables, acquisition subset, and split protocol.
- Table II: One-step predictor baselines.
- Table III: Horizon study across grouped split assignments.
- Table IV: Primary route-replay planner metrics.
- Table V: Paired inference with raw and Holm-adjusted p-values.
- Table VI: Claim/evidence boundary and limitations.

## Reproducibility Mapping

- Dataset preparation: `scripts/prepare_cicv5g.py`
- Primary study: `scripts/run_real_v2x_study.py`
- Horizon study: `scripts/run_real_v2x_horizon_study.py`
- Multi-split robustness: `scripts/run_real_v2x_multisplit.py`
- Measured route replay: `scripts/run_real_v2x_replay_planning.py`
- Primary replay statistics: `scripts/analyze_real_v2x_replay.py`
- Multi-split descriptive robustness: `scripts/analyze_real_v2x_replay_multisplit.py`
- Configuration: `configs/real_v2x.yaml`
- Tests: `tests/test_real_v2x.py`
