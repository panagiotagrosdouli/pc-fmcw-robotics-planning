# Paper 2 — defensible contribution statement

The paper is now framed around **decision validity under logged field measurements**, not around generic communication-aware planning.

## Contribution 1 — decision-validity decomposition

We separate three questions that are often conflated in predictive communication planning:

- whether future QoS is predictively useful at the motion-planning horizon;
- whether the queried candidate state is empirically represented by training measurements;
- whether the consequence of the selected counterfactual action can be evaluated using a withheld field measurement.

This decomposition is the central research framing.

## Contribution 2 — leakage-resistant horizon study with a strong causal baseline

Complete CICV5G acquisition runs, not individual rows, are assigned to train/calibration/test partitions. Persistence is treated as the mandatory short-horizon baseline. The paper therefore does not equate model complexity with predictive value and reports that naive learned models lose to persistence at one step.

The learned spatial/context component is only credited where calibration-gated fusion adds value at longer planning horizons.

## Contribution 3 — empirical-support audit distinct from predictive uncertainty

Every trajectory-conditioned query can be accompanied by training-measurement support diagnostics such as nearest-measurement distance and local density.

The paper explicitly separates:

- residual/predictive uncertainty, from
- empirical support / extrapolation risk.

This avoids claiming that a narrow uncertainty interval proves that a candidate is in-distribution.

## Contribution 4 — measurement-supported counterfactual replay (MSCR)

For offline decision evaluation, candidate actions are restricted to future states that actually occur later in the held-out measured route.

The future measured QoS associated with a candidate:

1. exists in the log,
2. is hidden during planner scoring,
3. is revealed only after selection for outcome evaluation.

This prevents the learned predictor or an interpolated radio map from defining its own counterfactual ground truth.

MSCR is explicitly **route constrained** and is not claimed to equal a real intervention or closed-loop vehicle experiment.

## Contribution 5 — separate predictive utility from support-risk control

P2 tests whether future QoS information changes decisions beneficially relative to reactive P1.

P3 tests a different question: whether penalizing weakly supported queries reduces unsupported decision exposure.

The evidence does not support a stable P3-over-P2 QoS advantage. That negative result is retained and interpreted as a validity-versus-mobility trade-off.

## Claims that must not appear

Do not claim:

- communication-aware planning is new;
- predictive QoS is new;
- field-measured vehicular QoS prediction is new;
- radio maps or predictive radio maps are new;
- QoS-aware AV trajectory planning is new;
- uncertainty-aware communication planning is new;
- task-aware or counterfactual radio world models are new;
- whole-run splitting is by itself a first-ever contribution;
- P2 is confirmatorily superior to P1 after multiplicity correction;
- P3 improves communication QoS over P2;
- repeated split assignments are independent replications;
- route replay is a real closed-loop intervention;
- CICV5G validates the PC-FMCW optical model.

## Main novelty phrasing

Preferred:

> This paper studies the evidential boundary between predictive QoS and motion decisions under logged field measurements by jointly auditing causal horizon, empirical measurement support, and measured post-selection evaluability.

Acceptable:

> We formulate a measurement-supported counterfactual replay protocol for evaluating communication-aware vehicle decisions without assigning fabricated field ground truth to unvisited states.

Avoid:

> We propose the first predictive communication-aware autonomous vehicle planner.
