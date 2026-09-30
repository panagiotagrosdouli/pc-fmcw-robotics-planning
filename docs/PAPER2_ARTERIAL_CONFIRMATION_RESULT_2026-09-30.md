# Paper 2 — Arterial Out-of-Scenario Confirmation Result

**Date:** 2026-09-30  
**Frozen branch:** `research/paper2-arterial-confirmation`  
**Workflow head SHA (frozen branch):** `5a98d2e8ea1a948d5cc1d0586d4d63b402a715a7`  
**Executed checkout SHA (artifact provenance):** `3df3a7b4479f7b1e9d6019497b4a5e9ecbb12586`  
**Workflow:** Paper 2 Arterial Confirmation  
**Workflow run:** `36749176921`  
**Result:** success  
**Artifact:** `paper2-arterial-confirmation`  
**Artifact ID:** `11113434687`  
**Artifact SHA256:** `ecd4fdbf593d77799dce8aa0dd678a66e26b8101758e37b8052697af3a40b9f0`

## Frozen protocol

The arterial result was obtained under the pre-written protocol in:

`docs/PAPER2_ARTERIAL_CONFIRMATION_FREEZE_2026-09-30.md`

No scientific parameter was changed after outcome inspection.

Frozen settings:

- CICV5G arterial-road scenario;
- n8 network only;
- 50 vs 80 km/h actions;
- aggregate `all.txt` files excluded;
- whole-run train/donor/query role separation;
- train fraction 0.40;
- donor fraction 0.40;
- split seed 20260930;
- spatial caliper 2 m;
- query thinning 5 m;
- intervention budget 10%;
- same frozen absolute-QoS and pairwise-margin architectures used in the W2S audit;
- 5,000 two-way query-run × donor-run bootstrap replicates.

## Point estimates

| Policy | Mean matched delay |
|---|---:|
| FAST | 18.871 ms |
| PRED_BUDGET | 19.026 ms |
| MARGIN_BUDGET | 18.903 ms |
| ORACLE_BUDGET | 18.281 ms |

## Two-way acquisition-run bootstrap

### Support-bounded measured action opportunity

`ORACLE_BUDGET - FAST`:

- point estimate: **-0.590 ms**;
- 95% interval: **[-1.431, -0.250] ms**;
- valid replicates: **4,409 / 5,000**;
- fraction below zero: **1.000**.

Interpretation:

> A second scenario and a different speed-action pair again contain measured support-bounded action-value headroom.

The magnitude is smaller than in the W2S 30/50-km/h confirmation, but the direction survives two-way acquisition-run resampling.

### Absolute-QoS policy versus measured oracle

`PRED_BUDGET - ORACLE_BUDGET`:

- point estimate: **+0.746 ms**;
- 95% interval: **[+0.344, +1.596] ms**;
- fraction above zero: **1.000**.

Interpretation:

> The frozen absolute-QoS ranking again fails to recover the measured support-bounded opportunity.

### Absolute-QoS policy versus FAST

`PRED_BUDGET - FAST`:

- point estimate: **+0.156 ms**;
- 95% interval: **[+0.038, +0.258] ms**;
- fraction above zero: approximately **0.998**.

Interpretation:

> In the arterial confirmation, the frozen predictive ranking is not merely non-confirmatory; it is measurably worse than the mobility-first FAST baseline under the locked analysis.

This strongly argues against a general claim that a field-trained QoS predictor should automatically alter vehicle speed whenever it predicts communication gain.

### Pairwise margin policy versus FAST

`MARGIN_BUDGET - FAST`:

- point estimate: **+0.032 ms**;
- 95% interval: **[+0.007, +0.061] ms**;
- fraction above zero: approximately **0.991**.

Interpretation:

> The frozen pairwise action-margin model also degrades the measured outcome relative to FAST in this scenario.

### Pairwise margin regret relative to measured oracle

`MARGIN_BUDGET - ORACLE_BUDGET`:

- point estimate: **+0.622 ms**;
- 95% interval: **[+0.277, +1.472] ms**;
- fraction above zero: **1.000**.

The direct action-margin target therefore does not close the decision-evidence gap out of scenario.

## Bootstrap support

Among valid replicates:

- four query acquisition runs are available in the locked arterial split;
- mean unique query runs represented after resampling: approximately 2.74;
- median unique query runs: 3;
- mean nonzero donor runs: approximately 2.86;
- median nonzero donor runs: 3;
- valid replicates: 4,409 / 5,000.

This independent-run count is small and must remain a visible limitation. The result is useful as an out-of-scenario confirmation, not as a large-sample universal estimate.

## Cross-scenario interpretation

The W2S and arterial confirmations agree on the central evidence pattern:

1. a measured support-bounded action opportunity exists;
2. frozen predictive rankings leave measurable regret relative to that opportunity;
3. direct pairwise action-margin modeling does not automatically solve the ranking problem.

They differ in the relationship to FAST:

- **W2S 30/50 km/h:** PRED has a favorable point estimate versus FAST, but the two-way 95% interval crosses zero;
- **arterial n8 50/80 km/h:** PRED is worse than FAST and its two-way 95% interval is entirely above zero.

This heterogeneity strengthens, rather than weakens, the decision-validity framing:

> Prediction-derived motion interventions can be beneficial-looking in one field context and harmful in another, even when measurable action-value headroom exists in both.

The appropriate research conclusion is therefore about **evidential reliability and context dependence**, not a universal speed policy.

## What this result supports

Safe:

- measured action-value heterogeneity exists in more than one CICV5G scenario/action pair;
- prediction-derived action ranking has nonzero regret relative to the measured support-bounded upper-bound diagnostic in both confirmations;
- a favorable predictor or favorable point estimate cannot be generalized automatically across motion contexts;
- direct pairwise action-margin learning does not guarantee robust decision ranking;
- action support and acquisition-run dependence should be explicit in field-log planner evaluation.

Not safe:

- 30, 50, or 80 km/h has a universal causal communication effect;
- the measured oracle is a deployable controller;
- CICV5G provides arbitrary counterfactual ground truth;
- the arterial result alone proves generalization outside CICV5G;
- the predictor is universally harmful.

## Publication implication

The arterial result materially strengthens the Paper-2 methodology/failure-boundary story.

The paper can now support a cross-scenario statement:

> **Across two pre-frozen repeated-field evaluations with different speed-action pairs, measurable action-value headroom exists, while frozen prediction-based rankings fail to recover that opportunity reliably; in the arterial confirmation, the predictive intervention is measurably worse than the mobility-first baseline.**

This remains a finite-dataset empirical conclusion, not a universal theorem.
