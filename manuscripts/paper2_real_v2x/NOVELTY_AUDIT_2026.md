# Paper 2 — 2026 Novelty Audit

**Updated:** 2026-09-30

## Reviewer-style question

If communication-aware planning, predictive QoS, radio maps, decision-focused learning, regret diagnostics, task-aware radio world models, and QoS policy evaluation already exist, why is this paper not redundant?

## Answer

Because the paper does not claim novelty at any of those generic layers.

Its research object is the **measured evidential validity of a vehicular motion-action claim drawn from finite repeated field drives**.

The key mismatch is:

```text
field log:
observes communication outcomes under executed runs/actions

motion decision:
asks which action should be selected among alternatives
```

A model can score every candidate, but those scores cannot be silently promoted to measured truth for actions without field support.

The paper therefore constrains the evaluation itself.

## Defensible non-overlap

The contribution is the combination of:

1. physically interpretable vehicular speed actions;
2. repeated real V2X field drives;
3. disjoint acquisition-run roles for training, measured outcome donation, and decision querying;
4. exact action/context matching plus a frozen spatial support rule;
5. measured donor outcomes hidden during deployable action ranking;
6. explicit donor-outcome provenance;
7. two-way query-run × donor-run dependence-aware inference;
8. a separately pre-frozen out-of-scenario confirmation;
9. retention of negative results from a frozen direct action-margin model.

No single primitive above is claimed as universally new. The paper's contribution is the **field-evidence protocol and the conclusion it changes**.

## What prior work already owns

Do not claim novelty for:

- communication-aware motion planning;
- predictive V2X QoS;
- radio-map planning;
- uncertainty-aware connectivity control;
- task-aware radio world models;
- generic predict-then-optimize / decision-focused learning;
- oracle-referenced regret;
- generic QoS policy evaluation;
- counterfactual simulation or learned world-model rollout.

## Confirmed empirical contribution

### W2S 30/50-km/h confirmation

Measured headroom exists:

- ORACLE − FAST: **−4.177 ms**, 95% CI **[−13.659, −2.137]**.

The predictor does not recover it fully:

- PRED − ORACLE: **+2.704 ms**, 95% CI **[+1.457, +5.832]**.

PRED-over-FAST superiority is not confirmatory:

- PRED − FAST: **−1.473 ms**, 95% CI **[−8.167, +0.657]**.

### Arterial n8 50/80-km/h confirmation

Measured headroom again exists:

- ORACLE − FAST: **−0.590 ms**, 95% CI **[−1.431, −0.250]**.

The frozen predictive intervention is worse than FAST:

- PRED − FAST: **+0.156 ms**, 95% CI **[+0.038, +0.258]**.

The frozen pairwise margin intervention is also worse:

- MARGIN − FAST: **+0.032 ms**, 95% CI **[+0.007, +0.061]**.

## Strongest novelty wording

Preferred:

> We operationalize a support-bounded measured replay protocol for vehicular motion actions using disjoint training, donor-outcome, and query acquisition runs, and show that useful QoS prediction does not automatically constitute reliable motion-decision evidence.

Also safe:

> The contribution is an empirical decision-validity audit under repeated field measurements, not a new generic communication-aware planner.

Avoid:

- "first decision-focused vehicular planner";
- "first regret-aware V2X system";
- "real counterfactual ground truth";
- "causal speed optimization";
- "PRED significantly outperforms FAST";
- "pairwise margin learning solves decision reliability".

## Main reviewer risks

1. finite number of independent acquisition runs;
2. observational, not randomized, speed conditions;
3. simple spatial support/matching rule;
4. measured oracle is an optimistic upper-bound diagnostic;
5. both confirmations remain within CICV5G;
6. no closed-loop autonomous-vehicle deployment.

These are explicit limitations, not hidden weaknesses.
