# Paper 2 — Locked Dependence-Aware Confirmatory Split

**Freeze date:** 2026-09-30  
**Status:** frozen before the new split and two-way cluster-bootstrap results are inspected.  
**Purpose:** test the measured decision-validity finding on a new acquisition-run role assignment while accounting explicitly for both query-run and donor-run dependence.

## Scientific question

The development study established two observations:

1. support-bounded measured action headroom is present across many run-role assignments;
2. absolute-QoS and pairwise-margin policies do not exploit that headroom reliably.

The confirmatory audit asks:

> On a newly locked run-role assignment, how large is the support-bounded measured action opportunity, and how much measured action regret remains for the frozen predictive policies when uncertainty is resampled at both the query-run and donor-run levels?

This is **not** a confirmatory test of a new superior controller.

## Frozen data scope

- Dataset: CICV5G W2S public field measurements.
- Direction: W2S only.
- Candidate actions: 30 km/h and 50 km/h.
- Network modes: n8 and n78 where the split provides all evidence roles.
- Whole-run role split within network × direction × speed.
- Train fraction: 0.40.
- Donor fraction: 0.40.
- Remaining runs: query role.
- **Locked split seed: 20260930.**
- Spatial matching caliper: **2.0 m**.
- Query thinning: **5.0 m**.
- Matched donor request: up to **5 samples**, preferring donor-run diversity.

The split seed is new relative to the previously inspected development seeds 0–4.

## Frozen predictive methods

No retraining design or hyperparameter change is permitted after this freeze.

### Absolute-QoS model

- context-conditioned spatial KNN;
- 20 neighbors;
- context: network + direction + nominal speed;
- minimum group samples: 100.

### Pairwise decision-margin model

Frozen development model retained as a negative comparator:

- matched action-margin target: measured `delay_50 - delay_30`;
- 25 spatial neighbors;
- context: network + direction;
- minimum group samples: 50;
- no post-audit retuning.

## Frozen policy operating point

Primary intervention budget: **10% per query run**.

Policies:

1. `FAST` — always choose 50 km/h.
2. `PRED_BUDGET` — use the frozen absolute-QoS predicted action gain.
3. `MARGIN_BUDGET` — use the frozen pairwise action-margin score.
4. `ORACLE_BUDGET` — nondeployable measured ranking, used only to quantify support-bounded action opportunity.

A policy never spends intervention budget when its own estimated communication gain is non-positive.

## Primary estimands

All effects are defined in milliseconds of matched measured delay. Lower is better.

### E1 — support-bounded measured action opportunity

[
E_1 = Y_{mathrm{ORACLE}} - Y_{mathrm{FAST}}.
]

A negative value means that, within the measured-support action set, there exists communication-delay headroom relative to always selecting FAST.

### E2 — predictive action regret relative to measured oracle

[
E_2 = Y_{mathrm{PRED}} - Y_{mathrm{ORACLE}}.
]

A positive value measures how much of the support-bounded opportunity is missed by the frozen absolute-QoS ranking.

### Secondary estimands

- `PRED_BUDGET - FAST`;
- `MARGIN_BUDGET - FAST`;
- `MARGIN_BUDGET - ORACLE_BUDGET`.

The pairwise margin policy remains a frozen negative comparator. It will not be reinterpreted as promising unless the confirmatory result independently supports that conclusion.

## Dependence-aware resampling

The matched outcome for one query/action is an average of measurements from one or more donor acquisition runs. Query locations within one query run are correlated, and donor measurements are reused across many query locations.

Therefore row-level or query-only bootstrap inference is prohibited.

The confirmatory analyzer will use a **two-way acquisition-run bootstrap**:

1. resample query acquisition runs with replacement;
2. independently resample donor acquisition runs with replacement;
3. reconstruct each matched action outcome from the resampled donor contributions;
4. recompute `ORACLE_BUDGET` ranking inside each bootstrap replicate;
5. keep `PRED_BUDGET` and `MARGIN_BUDGET` rankings determined only by their frozen deployable scores;
6. aggregate effects at the query-run level;
7. report percentile 95% intervals from 5,000 replicates.

A bootstrap replicate may drop a query context if one action has no donor contribution after donor-run resampling. Replicate coverage will be reported.

This is a finite-sample resampling audit, not a guarantee of exact asymptotic coverage.

## Interpretation rules

### Support-bounded opportunity

The development claim is strengthened if:

- E1 is negative;
- the 95% two-way bootstrap interval is predominantly or entirely below zero;
- adequate bootstrap coverage remains after donor resampling.

### Prediction-to-decision gap

The evidence-validity claim is strengthened if:

- E2 is positive;
- PRED does not recover most of the measured oracle opportunity;
- the conclusion is not driven by one query run or one donor run.

### Pairwise-margin comparator

No tuning is allowed.

If the margin model remains inconsistent or high-regret, retain that result.

If it unexpectedly improves on this locked split, report it as a confirmatory-split observation but do not erase the pre-frozen 15-configuration development failure.

## Claim boundary

Even a strong result does **not** establish:

- causal speed effects;
- physical counterfactual ground truth;
- a deployable oracle;
- autonomous-vehicle closed-loop validation;
- independence of field runs from time-varying network conditions.

The intended conclusion remains about **measured decision evidence under finite repeated-drive support**.

## After this freeze

Allowed:

- add donor-contribution provenance required for two-way resampling;
- implement the frozen estimator exactly;
- fix software bugs that violate the written protocol, with transparent documentation.

Not allowed:

- tune model parameters;
- change the 10% budget;
- choose another seed because the result is more favorable;
- choose another caliper because the result is more favorable;
- remove negative policy results;
- change the primary estimands after opening results.
