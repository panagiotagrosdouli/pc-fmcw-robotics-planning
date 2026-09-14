# Paper 3 — Actionability of Communication Forecasts

## Status

Pre-result protocol. This document defines the research question, hypotheses, information boundary, outcome metrics, and failure rules before any Paper-3 result is inspected.

## Research question

**When is a predicted communication improvement sufficiently supported and decision-relevant to justify changing autonomous motion?**

The paper is not about whether communication-aware planning exists, nor whether a predictor can achieve lower regression error in isolation. The object of study is the mapping from a forecast to a motion change.

## Core distinction

Prediction accuracy and planning utility are different quantities.

A predictor may have lower MAE yet induce worse actions. Conversely, a modest predictor may be more useful if it identifies when a forecast is too uncertain or poorly supported to justify motion deviation.

## Evidence boundary

Paper 3 reuses measured-data infrastructure only where the causal information boundary remains valid.

- Candidate future states must be states for which measured outcomes are legitimately available after selection (for example, route-constrained measured replay).
- Future measured QoS is hidden from every planner and gating rule until after a decision is made.
- Train/calibration/test separation remains whole-run/whole-drive, never random-row.
- Empirical support is fitted from training coordinates/data only.
- Conformal intervals are reported as empirical coverage intervals, not calibrated probabilities.
- CICV5G measurements are not optical PC-FMCW validation.
- Paper-1 simulation evidence and Paper-2 measured evidence remain separate from Paper-3 confirmatory claims.

## Planner family

The primary comparison is intentionally narrow.

- **A0 — reactive reference:** no future QoS-induced motion change.
- **A1 — predictive mean:** change motion when predicted QoS utility favors an admissible future candidate.
- **A2 — actionability gate:** permit the predictive motion change only when the candidate is empirically supported and its conservative predicted benefit exceeds the frozen decision threshold/cost.

A2 is not defined as "A1 plus a better predictor." It uses the same predictive information as A1 and changes only the decision rule.

## Frozen hypotheses

### H1 — Prediction/decision separation

Predictor ranking by held-out QoS error will not necessarily equal planner ranking by realized decision utility.

### H2 — Actionability

Relative to A1, A2 will reduce unsupported or unjustified motion changes while preserving a meaningful fraction of realized communication benefit.

### H3 — Conservative decision value

Among actions admitted by A2, the rate of realized beneficial changes will be higher than among all A1 motion changes.

H2/H3 are allowed to fail. A clean negative result is preferable to post-hoc threshold tuning.

## Decision-time information

At each replay decision, a method may use only:

- current/past measured state and QoS;
- training-fitted predictor outputs for admissible future candidates;
- calibration-fitted uncertainty intervals;
- training-fitted empirical-support diagnostics;
- mobility/candidate geometry available at decision time.

It may not use:

- future measured test QoS;
- test-set residuals to tune thresholds;
- support computed using test/future coordinates;
- arbitrary measured truth for an unobserved counterfactual location.

## Actionability rule

For a lower-is-better QoS quantity such as delay, define the conservative predicted gain of candidate `c` over the reactive/reference action `r` as

`conservative_gain(c) = lower_bound_delay(r) - upper_bound_delay(c)`

when interval bounds for both are available. If the reference is treated as current/persistence, the exact reference construction must be frozen in the executable experiment config before confirmatory evaluation.

A2 may change motion only if all frozen gates pass:

1. the candidate is admissible under the replay geometry;
2. empirical support passes the frozen training-derived rule;
3. conservative predicted gain is strictly positive after the frozen mobility penalty/threshold;
4. no future measured outcome has been queried.

If any gate fails, A2 falls back to A0/reference behavior.

## Primary outcomes

The paper must report prediction and decision outcomes separately.

### Prediction outcomes

- held-out MAE/RMSE by horizon;
- empirical interval coverage and width;
- support-stratified error diagnostics.

### Decision outcomes

- realized QoS change versus A0/reference;
- rate of QoS-threshold violations at the predeclared experimental operating point;
- motion-change rate;
- unsupported-action rate;
- realized beneficial-change rate among changed decisions;
- realized harmful-change rate among changed decisions;
- decision regret over the legitimately measured candidate set;
- mobility deviation/cost.

## Decision regret

Regret is an offline evaluation quantity only. For a decision event with a legitimately measured candidate set `C`,

`regret = realized_loss(chosen) - min(realized_loss(c) for c in C)`.

Future measured outcomes may be used to compute regret only after the planner has committed to a choice. Regret must never enter candidate scoring.

## Statistical unit

The independent unit is the held-out run/drive, not individual timestamps. Timestamp-level rows are never treated as independent replicates.

Primary paired effects are aggregated within held-out run first, followed by paired run-level inference. Bootstrap confidence intervals and paired non-parametric tests may be used where assumptions are appropriate. Multiplicity correction must be applied to the frozen primary endpoint family.

Multiple grouped train/calibration/test assignments are sensitivity analysis because the finite set of drives is reused; they are not independent replications.

## Development and confirmatory separation

Any threshold, support cutoff, mobility penalty, horizon choice, or gating constant that is not already scientifically fixed must be chosen using training/development/calibration data only.

After these values are frozen, confirmatory test runs are evaluated once. If the confirmatory result is negative, the result remains negative; the same held-out runs are not used for retuning.

## Primary claim boundary

A positive result may support only the claim that a support/uncertainty-aware decision gate improves the reliability of deciding **when to act on a communication forecast** under the tested measured replay protocol.

It must not be generalized to:

- arbitrary real-world counterfactual trajectories;
- closed-loop on-road autonomy;
- optical PC-FMCW hardware validation;
- universal QoS thresholds;
- calibrated event probabilities unless separately demonstrated;
- novelty of communication-aware planning in general.

## Required pre-confirmatory checks

Before any confirmatory Paper-3 replay is allowed:

- automated test proves future measured QoS cannot affect ranking/gating;
- automated test proves regret is computed only post-selection;
- whole-drive split manifest is frozen;
- support model uses training data only;
- uncertainty calibration uses calibration data only;
- actionability thresholds are frozen and provenance-recorded;
- all primary endpoints and multiplicity family are recorded in the experiment manifest.
