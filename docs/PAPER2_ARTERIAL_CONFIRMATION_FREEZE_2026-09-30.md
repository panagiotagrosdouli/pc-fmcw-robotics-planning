# Paper 2 — Out-of-Scenario Arterial Confirmation Freeze

**Freeze date:** 2026-09-30  
**Branch:** `research/paper2-arterial-confirmation`  
**Status:** frozen before arterial-road outcome inspection.

## Purpose

Test whether the Paper-2 decision-validity conclusion generalizes beyond the W2S subset using a different CICV5G scenario and a different physically interpretable speed-action pair.

This is not a new-model development experiment.

## Dataset scope

- Dataset: CICV5G.
- Scenario: arterial road.
- Network: **n8 only**.
- Candidate actions: **50 km/h vs 80 km/h**.
- Aggregate `all.txt` files are excluded to avoid duplicate samples.
- Only repeated per-run raw measurement files are used.

Why n8 only:

- n8 provides five repeated 50-km/h runs and seven repeated 80-km/h runs;
- the n78 arterial 80-km/h condition has only two runs, which is insufficient for disjoint training, donor, and query evidence roles.

## Locked evidence-role split

Within network × direction × speed strata:

- train fraction: 0.40;
- donor fraction: 0.40;
- remainder: query;
- split seed: **20260930**.

The arterial files do not encode a directional label in the filename, so the existing metadata parser assigns the common `unknown` direction category. This is accepted because all compared arterial n8 runs use the same metadata convention.

## Locked matching protocol

- spatial caliper: **2.0 m**;
- query thinning: **5.0 m**;
- requested matched donor samples: up to **5**, preferring donor-run diversity;
- measured donor outcomes remain hidden during deployable policy ranking.

## Frozen models

No hyperparameter tuning is permitted on arterial outcomes.

### Absolute-QoS predictor

Same architecture used in W2S:

- conditioned spatial KNN;
- 20 neighbors;
- context includes network, direction, nominal speed;
- minimum group size 100.

### Pairwise margin model

Same frozen development architecture:

- target: measured fast-minus-slow delay margin;
- 25 spatial neighbors;
- network + direction context;
- minimum group size 50.

The margin model is retained as a negative comparator rather than promoted as a new method.

## Frozen policy operating point

Primary intervention budget: **10% per query run**.

Policies:

1. `FAST`: always 80 km/h.
2. `PRED_BUDGET`: rank by absolute-QoS predicted gain.
3. `MARGIN_BUDGET`: rank by frozen pairwise margin score.
4. `ORACLE_BUDGET`: measured support-bounded upper-bound diagnostic only.

## Primary questions

### Q1 — Does measured action heterogeneity exist in a different scenario?

Quantify the support-bounded `ORACLE_BUDGET - FAST` mean-delay difference.

The oracle is an upper-bound diagnostic, not an unbiased deployable-policy estimate.

### Q2 — Does predictive reliability generalize?

Measure:

- `PRED_BUDGET - FAST`;
- `PRED_BUDGET - ORACLE_BUDGET`.

### Q3 — Does the frozen pairwise negative result generalize?

Measure:

- `MARGIN_BUDGET - FAST`;
- `MARGIN_BUDGET - ORACLE_BUDGET`.

No retuning is allowed regardless of outcome.

## Interpretation

Three outcomes are scientifically acceptable.

### A. Oracle headroom + unreliable predictors

This would externally reinforce the W2S failure-boundary story.

### B. Oracle headroom + reliable PRED policy

This would show that decision reliability is context-dependent and that the evidence protocol distinguishes settings where predictive QoS can or cannot justify motion changes.

### C. Little measured headroom

This would show that communication-aware speed intervention is not universally relevant even when QoS can be predicted.

The paper will report whichever outcome is observed.

## Claim boundary

This arterial confirmation does not establish:

- a causal speed treatment effect;
- arbitrary counterfactual ground truth;
- closed-loop autonomous speed control;
- generalization outside the CICV5G testbed.

It is an **out-of-scenario repeated-field confirmation** within CICV5G.

## Publication value

A successful confirmation is useful because the W2S development story cannot then be dismissed as an artifact of one route or one 30/50-km/h action pair.

A null or opposite result is also useful because it establishes the context boundary of the measured decision-validity framework.
