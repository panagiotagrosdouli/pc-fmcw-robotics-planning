# Paper 2 — Locked Confirmatory Result

**Date:** 2026-09-30  
**Locked code SHA:** `a056d46a5579032d10f51a1d6e90d800d3d017b4`  
**Workflow:** Paper 2 Confirmatory Audit  
**Workflow run:** `36747715208`  
**Result:** success  
**Artifact:** `paper2-locked-confirmatory-audit`  
**Artifact ID:** `11113770831`  
**Artifact SHA256:** `3aa7ab461e2bf6ea266073658ed182cc2f1e07e46b5f51f615943716d009f378`

## Frozen protocol

The result was obtained under the pre-written protocol in:

`docs/PAPER2_CONFIRMATORY_FREEZE_2026-09-30.md`

No scientific parameter was changed after the locked result was opened.

Frozen settings:

- CICV5G W2S only;
- 30 vs 50 km/h actions;
- whole-run train/donor/query separation;
- train fraction 0.40;
- donor fraction 0.40;
- locked split seed 20260930;
- 2 m spatial caliper;
- 5 m query thinning;
- 10% intervention budget;
- frozen absolute-QoS model;
- frozen pairwise-margin model;
- 5,000 two-way acquisition-run bootstrap replicates.

The bootstrap independently resampled query acquisition runs and donor acquisition runs and reconstructed the matched action outcomes inside each replicate.

## Point estimates

| Policy | Mean matched delay |
|---|---:|
| FAST | 23.546 ms |
| PRED_BUDGET | 22.073 ms |
| MARGIN_BUDGET | 21.878 ms |
| ORACLE_BUDGET | 19.369 ms |

The oracle remains a nondeployable support-bounded upper-bound diagnostic because measured donor outcomes are used for action ranking.

## Locked primary estimands

### E1 — support-bounded measured action opportunity

`ORACLE_BUDGET - FAST`:

- point estimate: **-4.177 ms**;
- two-way bootstrap 95% interval: **[-13.659, -2.137] ms**;
- valid bootstrap replicates: 4,945 / 5,000;
- fraction below zero: **1.000**.

Interpretation:

> The locked run-role assignment retains clear measured action-value headroom within the finite matched-support action set.

This is not a causal speed-effect estimate and not deployable-oracle performance.

### E2 — frozen predictor regret relative to measured oracle

`PRED_BUDGET - ORACLE_BUDGET`:

- point estimate: **+2.704 ms**;
- two-way bootstrap 95% interval: **[+1.457, +5.832] ms**;
- fraction above zero: **1.000**.

Interpretation:

> The frozen absolute-QoS ranking leaves a material portion of the measured support-bounded action opportunity unused.

## Secondary estimands

### PRED versus FAST

`PRED_BUDGET - FAST`:

- point estimate: **-1.473 ms**;
- 95% interval: **[-8.167, +0.657] ms**;
- bootstrap fraction below zero: **0.902**.

Interpretation:

The locked point estimate favors PRED, but the dependence-aware interval crosses zero.

**Do not claim confirmatory PRED superiority over FAST.**

### Pairwise margin versus FAST

`MARGIN_BUDGET - FAST`:

- point estimate: **-1.668 ms**;
- 95% interval: **[-9.524, +1.180] ms**;
- bootstrap fraction below zero: **0.783**.

Interpretation:

The frozen pairwise-margin method also does not establish confirmatory superiority over FAST.

### Pairwise margin regret versus oracle

`MARGIN_BUDGET - ORACLE_BUDGET`:

- point estimate: **+2.509 ms**;
- 95% interval: **[+1.572, +5.162] ms**;
- fraction above zero: **1.000**.

Interpretation:

Direct action-margin modeling does not eliminate the measured decision-evidence gap.

## Bootstrap support / coverage

Among valid bootstrap replicates:

- mean unique query runs represented: approximately 4.99;
- median unique query runs: 5;
- maximum unique query runs: 9;
- mean nonzero donor runs: approximately 5.89;
- median nonzero donor runs: 6;
- valid replicates: 4,945 / 5,000.

The finite number of independent acquisition runs remains an important limitation. The bootstrap addresses two-way cluster dependence but does not create new independent field experiments.

## Confirmatory conclusion

The frozen result supports the paper's methodological / failure-boundary thesis:

> **Measured action-value opportunity can remain substantial even when a field-trained QoS predictor does not provide dependence-aware evidence of superior motion decisions.**

More specifically:

1. a support-bounded measured action opportunity is present under the locked split;
2. the frozen predictor misses a statistically stable portion of that upper-bound opportunity;
3. neither the absolute-QoS policy nor the pairwise-margin policy establishes confirmatory superiority over FAST;
4. therefore regression/prediction evidence cannot be promoted automatically into a planner-superiority claim.

## What this result supports

Safe:

- prediction-level utility and measured decision-level evidence are distinct;
- action support and acquisition-run identity materially affect the conclusion;
- disjoint train/donor/query evidence roles expose a gap hidden by model-as-truth evaluation;
- direct pairwise margin learning does not automatically solve the problem;
- dependence-aware inference changes the strength of planner-performance claims.

Not safe:

- PRED is proven better than FAST;
- MARGIN is proven better than FAST;
- 30 km/h causally improves communication;
- the measured oracle is a deployable controller;
- the matched replay is arbitrary real counterfactual ground truth;
- the result is a closed-loop vehicle validation.

## Paper decision after confirmation

### Positive planner-superiority paper

**NO.**

The locked dependence-aware intervals do not establish PRED-over-FAST or MARGIN-over-FAST superiority.

### Measured decision-validity / evidence-boundary paper

**YES.**

The core empirical pattern survived a new frozen run-role assignment and two-way acquisition-run resampling:

- clear measured action headroom;
- clear regret relative to that headroom;
- no confirmatory superiority of the tested deployable rankings.

That is the paper.
