# Paper 2 Pivot — Prediction Is Not Decision Value

**Date:** 2026-09-30  
**Status:** development result from measured matched-speed replay  
**Branch:** `research/paper2-matched-speed-replay`  
**Workflow:** Matched Speed Replay, run `36736454013`  
**Artifact:** `matched-speed-replay-development`, artifact ID `11106858530`

## Empirical result

The stronger motion-conditioned field replay succeeded technically and produced 1,203 eligible matched query locations across 11 query runs.

The first deployable predictive speed policy does **not** beat the mobility-first FAST policy.

Development run-level effects:

| Endpoint | PRED - FAST | Development bootstrap 95% interval |
|---|---:|---:|
| Mean matched delay | +0.104 ms | [-0.482, +0.737] ms |
| Matched p95 delay | +0.600 ms | [+0.010, +1.332] ms |
| Changed-from-FAST fraction | +0.0445 | [+0.0278, +0.0617] |

The initial support-gated policy is numerically identical to PRED in this run, so the present support rule does not improve the decision.

Always choosing 30 km/h is substantially worse than FAST in matched measured communication outcomes:

- mean-delay delta: +9.822 ms;
- p95-delay delta: +18.736 ms.

This rules out a simplistic story that lower speed automatically improves the link.

However, the matched measured oracle has nonzero headroom:

| Endpoint | ORACLE_MATCHED - FAST | Development bootstrap 95% interval |
|---|---:|---:|
| Mean matched delay | -0.936 ms | [-1.415, -0.475] ms |
| Matched p95 delay | -0.747 ms | [-1.526, -0.147] ms |

These intervals are development diagnostics only because shared donor runs induce dependence not handled by the current query-run bootstrap.

## Scientific interpretation

This is a useful negative result.

The field data contain locations where a different speed action is associated with a better matched measured communication outcome, but the current QoS predictor does not reliably identify those decisions.

Therefore the stronger research question is no longer:

> Can QoS prediction improve speed planning?

It becomes:

> **Why can a predictor with useful QoS structure fail to recover downstream action value, and what decision-calibration evidence is required before a field-trained connectivity model should alter vehicle motion?**

This separates two objectives that are often conflated:

1. **prediction quality** — minimizing QoS error;
2. **decision quality** — ranking available actions correctly when their utility difference matters.

A predictor can improve MAE while still choosing the wrong action near a decision boundary.

## New research gap

Communication-aware planning, predictive QoS, radio maps, decision-focused learning, and task-aware radio world models are all prior art.

The narrow gap is:

> **decision calibration for motion actions under support-bounded, measured field replay, where action-ranking regret can be evaluated using disjoint repeated drives rather than the predictor itself.**

The intended paper should not claim that decision-focused prediction is new.

Its contribution would instead be the combination of:

- physically interpretable motion actions already executed in repeated field runs;
- disjoint training, donor-outcome, and query-run evidence roles;
- measured post-selection evaluation;
- explicit action-overlap/support requirements;
- separation of QoS regression error from action-ranking error;
- calibrated abstention when the predicted action margin is not decision-reliable.

## Next method: decision-margin calibration

For two speed actions (a_s) and (a_f), define the measured matched action advantage

[
Delta y(x)=y(x,a_s)-y(x,a_f).
]

The planner does not need perfect absolute delay prediction to make the correct choice. It needs the sign and useful magnitude of (Delta y(x)).

The next model should therefore estimate a **decision margin** rather than score two absolute QoS predictions independently.

Candidate approaches for development:

1. pairwise regression of the matched action-delay difference;
2. probabilistic classification of which action has lower communication cost;
3. calibrated probability that the communication advantage exceeds the mobility penalty;
4. abstention/fallback to FAST when the estimated advantage is smaller than a predeclared uncertainty margin.

The deployable decision rule should have the form:

[
	ext{choose SLOW only if }
P(Delta U < 0 mid x) > 1-alpha
	ext{ and expected gain exceeds } 	au.
]

Otherwise choose the mobility-first FAST action.

## Primary scientific endpoints

The next development protocol should prioritize:

- matched measured decision regret relative to ORACLE_MATCHED;
- wrong-action rate on locations with meaningful oracle action margin;
- mean matched delay;
- matched tail delay;
- intervention/change rate relative to FAST;
- abstention rate;
- coverage as a function of matched-data support.

Regression MAE becomes a secondary diagnostic rather than the paper's success criterion.

## Critical evaluation rule

The next model must not be tuned on the same donor/query outcomes used for its final evaluation.

A valid protocol should create separate development and untouched confirmation roles before the final result is opened.

The final inferential procedure must account for shared donor-run dependence, for example through multiway cluster resampling over query and donor acquisition runs.

## Paper interpretation if the next model succeeds

A defensible claim would be:

> Field-trained QoS models should be calibrated for downstream action ranking, not only regression error; under support-bounded matched replay, uncertainty-aware decision-margin gating reduces measured action regret while limiting unnecessary motion changes.

## Paper interpretation if the next model fails

A negative result remains publishable if the evaluation is strong:

> Despite measurable oracle action headroom, the available field covariates are insufficient to identify communication-beneficial speed changes reliably under disjoint-run evaluation.

That would establish an important limitation of using observational vehicular QoS logs for motion-policy claims.

## Candidate title

**Prediction Is Not Decision Value: Cross-Run Matched Field Replay for Communication-Aware Vehicle Speed Planning**

More conservative alternative:

**From QoS Prediction to Decision Calibration: Matched Field Replay for Communication-Aware Vehicle Speed Planning**

## Development decision

**Do not merge the naive PRED policy into the canonical paper as a positive planner result.**

Use it as the baseline negative result that motivates decision-margin calibration.
