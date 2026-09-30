# From QoS Prediction to Measured Decision Validity

## Support-Bounded Matched Field Replay for Vehicular Speed Decisions

**Status:** confirmed research manuscript draft  
**Date:** 2026-09-30  
**Locked confirmatory code SHA:** `a056d46a5579032d10f51a1d6e90d800d3d017b4`

## Abstract

Predictive quality-of-service (QoS) and communication-aware vehicle planning are established research directions, but logged field measurements create an evidential mismatch: prediction models can score alternative motion actions even when the dataset contains no measured outcome for the action not taken. We study this mismatch using repeated CICV5G field drives and a support-bounded matched field replay protocol. Whole acquisition runs are assigned disjoint roles for predictor training, measured outcome donation, and decision queries. At each supported query location, the motion action is a physically interpretable speed choice between 30 and 50 km/h; an action is evaluated only when separate donor runs provide measurements under the same network, direction, and speed within a frozen spatial caliper.

A conventional absolute-QoS predictor and a separately frozen pairwise action-margin predictor are evaluated under a 10% intervention budget. In a locked run-role assignment fixed before inspection, a two-way acquisition-run bootstrap resampling both query and donor runs shows a support-bounded measured oracle advantage of **−4.177 ms** relative to always selecting 50 km/h, with a 95% interval of **[−13.659, −2.137] ms**. The absolute-QoS policy leaves **+2.704 ms** of measured regret relative to this upper-bound diagnostic, with interval **[+1.457, +5.832] ms**, while its comparison with the 50-km/h baseline is **−1.473 ms** with interval **[−8.167, +0.657] ms**. The pairwise margin policy also fails to establish superiority over the baseline.

The result is therefore not a new speed-controller claim. It is evidence that useful QoS structure does not automatically constitute reliable motion-decision evidence when field support and acquisition-run dependence are enforced explicitly.

**Keywords:** predictive QoS, V2X, communication-aware planning, autonomous vehicles, decision validity, matched field replay, empirical support, clustered inference

---

# 1. Introduction

Connected and automated vehicles increasingly depend on wireless communication for cooperative perception, cloud-assisted services, infrastructure interaction, and distributed decision making. Vehicle motion changes the communication environment experienced by the platform, while anticipated communication quality can influence motion selection. This coupling is well established. Communication-aware motion planning, QoS-aware trajectory optimization, radio-map planning, predictive QoS, uncertainty-aware control, and task-aware radio world models all have substantial prior art.

The methodological problem studied here appears when a field-trained communication model is used to justify a different motion action. A logged drive records communication outcomes under the motion that was actually executed. A planner, however, asks which action should be selected among alternatives. If evaluation fills the unobserved action with the same model that made the decision, prediction and “ground truth” become circular. A favorable planner result can then reflect model self-consistency rather than measured decision evidence.

A second issue is statistical. Vehicular samples are correlated in time and space. Multiple query locations can share the same acquisition run, and multiple matched outcomes can reuse the same donor run. Treating timestamps as independent observations exaggerates effective sample size and can turn a favorable point estimate into an overstated performance claim.

This paper asks a narrower question:

> **When can repeated field measurements support a claim about a communication-aware vehicle motion decision without promoting model-generated counterfactuals to measured truth?**

We study this question on the CICV5G field dataset. The motion action is deliberately simple and physically interpretable: choose between **30 and 50 km/h** at locations where separate repeated drives provide measured support for both actions. Complete acquisition runs are assigned disjoint roles for model training, measured outcome donation, and decision queries. The measured donor outcome remains hidden during deployable policy ranking.

## Contributions

1. We operationalize a **support-bounded matched field replay** protocol in which motion actions are evaluated only where disjoint repeated acquisition runs provide measured outcomes for the relevant action and communication context.
2. We separate three evidence roles that are often conflated in logged-data planning studies: predictor training, measured action-outcome donation, and decision querying.
3. We evaluate both a conventional absolute-QoS ranking and a frozen pairwise action-margin ranking, retaining the negative result that direct margin prediction does not automatically solve downstream decision reliability.
4. We use a fixed intervention-budget formulation rather than converting travel-time cost and communication delay into an arbitrary scalar unit.
5. We perform a locked confirmatory audit using **two-way acquisition-run bootstrap resampling over both query and donor runs**. The resulting interval supports measured action-value headroom and predictor regret relative to that headroom, but does not support confirmatory superiority of the deployable predictive policies over the mobility-first baseline.

The contribution is not a new generic planner, a new decision-focused-learning paradigm, or a causal speed-effect estimate. It is a measured field-evidence protocol and an empirical demonstration that prediction-level usefulness and decision-level evidential validity can diverge.

---

# 2. Related Work and Non-Overlap

Communication-aware motion planning already establishes that wireless quality can influence robot or vehicle motion. Predictive QoS studies already show that connectivity can be forecast from mobility, radio, and spatial context. Recent radio-map and task-aware world-model methods go further by incorporating uncertainty and downstream decision relevance.

The remaining distinction in this work is the **evaluation substrate**.

Simulation, analytical propagation, ray tracing, or learned world models can provide a complete outcome surface for candidate actions. A finite field log cannot. The present study therefore does not ask whether another planner can optimize another communication model. It asks what conclusions survive when the evaluator refuses to invent missing field outcomes.

The closest conceptual boundary is:

- communication-aware planning establishes the motion–connectivity coupling;
- predictive QoS establishes forecastability;
- decision-focused learning establishes that prediction loss and downstream decision loss differ;
- task-aware radio world models establish the value of decision-relevant uncertainty;
- the present study focuses on **measured decision evidence under finite repeated-drive action support**.

---

# 3. Field Data and Evidence Roles

## 3.1 CICV5G measurements

CICV5G contains real 5G V2N2V measurements with synchronized network and vehicle context, including delay, SINR, RSRP, position, heading, velocity, cell identity, and timestamps. The repository study uses repeated W2S/S2W acquisition runs under n8/n78 network configurations and multiple vehicle speeds.

The earlier predictor audit uses 38 complete acquisition runs comprising 43,045 synchronized samples. That audit establishes two background facts:

- one-step persistence is a strong causal baseline;
- spatial/context information can add predictive value at longer planning horizons.

Those results motivate future prediction, but they do not establish that a motion action selected from that prediction is better.

## 3.2 Disjoint acquisition-run roles

Complete acquisition runs are partitioned within network, direction, and speed strata into:

- **training runs** — fit QoS and action-margin models;
- **donor runs** — provide measured action outcomes;
- **query runs** — provide decision locations and contexts.

No acquisition run serves more than one role in one configuration.

The locked confirmatory assignment uses:

- train fraction: **0.40**;
- donor fraction: **0.40**;
- remaining runs: query;
- locked split seed: **20260930**.

This split was written into the confirmatory protocol before the result was inspected.

---

# 4. Support-Bounded Matched Field Replay

## 4.1 Motion action

The action set is:

- **SLOW:** 30 km/h;
- **FAST:** 50 km/h.

For a query location and action, a measured outcome is available only when a donor run has:

- the same network context;
- the same travel direction;
- the same nominal speed action;
- position within the frozen spatial caliper.

The locked confirmatory caliper is **2 m**.

Both actions must have measured donor support for a query location to enter comparative evaluation. Query locations are spatially thinned at **5 m** spacing.

## 4.2 Outcome construction

For each supported action, the measured matched delay is the mean of the selected donor measurements, preferring donor-run diversity before repeated nearby samples from the same run.

The donor measurement is never exposed to a deployable policy before the action ranking is made.

This gives a measured post-selection outcome without pretending that arbitrary unsupported positions have field ground truth.

## 4.3 Claim boundary

Matched field replay is still observational.

Separate acquisition runs can differ in:

- network load;
- blockage;
- traffic;
- handovers;
- temporal conditions;
- unobserved communication state.

Therefore the matched outcome is **not a randomized potential outcome** and does not identify a causal speed treatment effect.

---

# 5. Frozen Predictive Rankings

## 5.1 Absolute-QoS predictor

A context-conditioned spatial KNN is fitted only on training-role runs.

For each query location, the model predicts delay for both speed actions. The predicted communication gain from slowing is:

**predicted gain = predicted delay at 50 km/h − predicted delay at 30 km/h.**

Positive gain means that the model expects lower communication delay at 30 km/h.

## 5.2 Pairwise action-margin predictor

A second frozen model is trained directly on matched action margins constructed only from training-role runs.

It estimates:

**margin = measured/predicted delay at 50 km/h − delay at 30 km/h.**

This model was frozen before its development audit:

- 25 spatial neighbors;
- network + direction conditioning;
- no post-result hyperparameter tuning.

The pairwise model is retained as a negative comparator rather than promoted as the novelty.

---

# 6. Budgeted Decision Policies

An application-specific conversion between travel-time seconds and communication-delay milliseconds is not available in the dataset. The paper therefore does not hide that trade-off inside an arbitrary scalar weight.

Instead, a policy receives a maximum intervention budget.

In the locked confirmatory audit, at most **10%** of supported query locations within one query run may select SLOW.

Policies:

- **FAST:** always select 50 km/h.
- **PRED_BUDGET:** spend intervention budget on locations with the largest positive absolute-QoS predicted gain.
- **MARGIN_BUDGET:** spend budget using the frozen pairwise-margin score, requiring training support.
- **ORACLE_BUDGET:** rank by measured matched action gain.

ORACLE_BUDGET is **nondeployable** and serves only as a support-bounded upper-bound diagnostic. Because measured donor outcomes enter its ranking, it is not interpreted as an unbiased deployable-policy performance estimate.

---

# 7. Statistical Protocol

## 7.1 Development sensitivity

Before the locked confirmation, the replay was evaluated over:

- 5 whole-run split seeds;
- 3 spatial calipers: 1, 2, and 5 m;
- 15 dependent development configurations total.

These configurations reuse the finite drive pool and are not treated as independent experiments.

Development results:

- ORACLE favorable to FAST in **15/15** configurations for mean matched delay;
- PRED favorable in only **9/15** for mean delay;
- PRED favorable in **8/15** for matched p95 delay;
- the frozen pairwise-margin method failed its predeclared “promising method” criteria.

## 7.2 Locked confirmation

The confirmatory protocol fixed before result inspection:

- split seed: 20260930;
- W2S direction;
- 30/50-km/h actions;
- 40/40 train/donor fractions;
- 2-m spatial caliper;
- 5-m query thinning;
- 10% intervention budget;
- frozen absolute-QoS model;
- frozen pairwise-margin model.

## 7.3 Two-way acquisition-run bootstrap

Matched decision outcomes have two cluster dimensions:

1. query acquisition run;
2. donor acquisition run.

The confirmatory analysis therefore independently resamples both types of runs.

For each bootstrap replicate:

1. query runs are sampled with replacement;
2. donor runs are sampled with replacement;
3. each matched action outcome is reconstructed from the resampled donor contributions;
4. ORACLE_BUDGET is recomputed inside the replicate;
5. PRED_BUDGET and MARGIN_BUDGET keep their frozen model-based rankings;
6. effects are aggregated at the query-run level.

The locked audit uses **5,000 replicates**.

---

# 8. Results

## 8.1 Prediction-level diagnostics are not enough

The archived predictor study confirms that one-step persistence is difficult to beat:

- persistence MAE: **5.576 ms**;
- spatial kNN MAE: **10.862 ms**;
- Random Forest MAE: **7.150 ms**;
- Extra Trees MAE: **6.659 ms**.

At longer planning horizons, calibration-gated spatial/context prediction becomes more useful.

This establishes predictive structure, but not downstream motion superiority.

## 8.2 Locked policy point estimates

Mean matched delay:

| Policy | Mean delay |
|---|---:|
| FAST | 23.546 ms |
| PRED_BUDGET | 22.073 ms |
| MARGIN_BUDGET | 21.878 ms |
| ORACLE_BUDGET | 19.369 ms |

The point estimates alone would tempt a planner-performance interpretation. The two-way cluster analysis shows why that would be too strong.

## 8.3 Dependence-aware confirmatory effects

| Estimand | Point | 95% two-way bootstrap interval |
|---|---:|---:|
| ORACLE − FAST | −4.177 ms | [−13.659, −2.137] |
| PRED − ORACLE | +2.704 ms | [+1.457, +5.832] |
| PRED − FAST | −1.473 ms | [−8.167, +0.657] |
| MARGIN − FAST | −1.668 ms | [−9.524, +1.180] |
| MARGIN − ORACLE | +2.509 ms | [+1.572, +5.162] |

Valid replicates: **4,945 / 5,000**.

### Measured action opportunity

ORACLE − FAST is below zero in every valid bootstrap replicate.

This supports the existence of substantial measured action-value heterogeneity within the finite supported action set.

### Absolute-QoS decision regret

PRED − ORACLE is above zero in every valid replicate.

The frozen absolute-QoS ranking therefore leaves a material portion of the support-bounded measured opportunity unused.

### No confirmatory PRED-over-FAST superiority

PRED − FAST has a favorable point estimate, but its 95% interval crosses zero.

Therefore:

> **The paper must not claim confirmatory superiority of PRED_BUDGET over FAST.**

### Pairwise margin negative result

MARGIN − FAST also crosses zero.

MARGIN − ORACLE remains strictly positive over its interval.

Therefore direct action-margin prediction does not automatically resolve the measured decision-evidence gap.

---

# 9. Discussion

## 9.1 Prediction utility is not measured decision evidence

The predictor is not useless. It contains actionable structure and produces a favorable point estimate on the locked split.

The stronger result is that this is still insufficient for a planner-superiority claim.

Once field action support and query/donor run dependence are enforced, the evidence supports:

- measurable action-value opportunity;
- measurable predictor regret relative to that opportunity;
- but not confirmatory superiority over the mobility-first baseline.

This distinction is the paper.

## 9.2 Why donor identity matters

Repeated cellular drives are not interchangeable timestamps. Different donor runs can differ because of network load, blockage, cell state, traffic, and other latent factors.

Development sweeps showed substantial variation across run-role assignments.

The two-way bootstrap weakens the apparent certainty of the planner comparison while strengthening the scientific validity of the conclusion.

## 9.3 Why the pairwise failure matters

A simple reaction to the prediction-to-decision gap would be to train directly on an action-margin target.

The frozen experiment shows that this is not enough.

The failure indicates that downstream reliability depends on more than the supervised target:

- finite action overlap;
- donor quality;
- latent run context;
- decision boundary stability;
- acquisition-run uncertainty.

## 9.4 Relationship to task-aware radio models

Task-aware radio world models address how communication models should represent decision-relevant uncertainty and counterfactual credibility.

This paper addresses a complementary question:

> **What may legitimately count as measured decision evidence when the source is a finite field log?**

The evaluator does not synthesize unsupported action outcomes.

---

# 10. Threats to Validity

First, matched field replay is observational and does not identify causal speed effects.

Second, the measured oracle is an upper-bound diagnostic, not a deployable controller.

Third, the number of independent acquisition runs is modest. Two-way bootstrap respects run dependence but cannot create new independent experiments.

Fourth, spatial matching is intentionally simple. A 2-m caliper plus exact network/direction/speed matching cannot remove all latent context mismatch.

Fifth, the 10% intervention budget is a methodological operating point, not an application-optimal mobility policy.

Sixth, CICV5G supports the measured 5G/V2N2V study only. It does not validate the repository's separate PC-FMCW optical model.

---

# 11. Reproducibility

Locked confirmatory workflow:

- workflow run: **36747715208**;
- code SHA: **a056d46a5579032d10f51a1d6e90d800d3d017b4**;
- artifact ID: **11113770831**;
- artifact SHA256: **3aa7ab461e2bf6ea266073658ed182cc2f1e07e46b5f51f615943716d009f378**.

The artifact contains:

- run-role metadata;
- matched comparison contexts;
- donor contribution provenance;
- policy point estimates;
- two-way bootstrap summaries;
- bootstrap coverage;
- CICV5G provenance manifest.

The numerical result is therefore traceable from public field measurements to the manuscript claim.

---

# 12. Conclusion

Communication-aware motion planning and predictive QoS are mature research areas. The unresolved issue studied here is evidential: when a field-trained connectivity model recommends a different vehicle motion, what measured evidence supports the resulting decision claim?

Using repeated CICV5G drives, we separate model training, measured action-outcome donation, and decision queries across complete acquisition runs. A locked two-way query/donor bootstrap reveals clear support-bounded measured action-value headroom relative to a mobility-first baseline. The frozen absolute-QoS and pairwise-margin rankings both leave significant regret relative to that measured upper bound, while neither establishes confirmatory superiority over FAST.

The conclusion is intentionally narrow:

> **Prediction accuracy, predictive utility, and measured motion-decision validity are different quantities.**

Field-measured communication models should not be promoted from regression evidence to planner-superiority claims unless action support, outcome provenance, and acquisition-run dependence are made explicit.
