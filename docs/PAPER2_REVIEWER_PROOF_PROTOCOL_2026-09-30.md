# Paper 2 — Reviewer-Proof Research Protocol

**Date:** 2026-09-30  
**Status:** development protocol; claims are not frozen for submission  
**Branch:** `research/paper2-matched-speed-replay`

## Purpose

This document defines the minimum evidence required before the matched-speed research direction can replace the current Paper-2 replay as the canonical scientific story.

The objective is not to obtain a favorable planner result. The objective is to determine whether repeated field drives can support a defensible, motion-conditioned decision claim without treating a learned QoS model or simulator as counterfactual ground truth.

---

## Literature boundary

The paper must explicitly concede prior art in:

- predictive QoS for automotive applications;
- communication-aware motion planning;
- QoS-aware vehicle routing/control;
- radio-map prediction and radio-map-based control;
- decision-focused / predict-then-optimize learning;
- regret-aware decision diagnostics;
- task-aware radio world models and value-of-information channel learning;
- generic off-policy evaluation under logged observational data.

Therefore the paper must **not** claim:

- the first QoS-aware speed controller;
- the first decision-focused vehicular predictor;
- the first use of regret for vehicular communication decisions;
- the first predictive-QoS system for vehicle adaptation;
- the first task-aware channel-learning method;
- causal speed effects from the current observational repeated-drive design.

The defensible research object is narrower:

> **How can downstream motion-action reliability be evaluated and calibrated when QoS predictors are trained from field logs and candidate-action outcomes are only available through finite, support-bounded repeated drives?**

---

## Current development evidence

### 1. Original route-constrained replay weakness

The archived Paper-2 replay has identical P0 and P1 primary outcomes.

That means the previous P2-P1 comparison does not constitute a strong predictive-versus-reactive communication-aware baseline.

This weakness must remain documented.

### 2. Matched-speed replay

A new motion-conditioned replay uses 30-km/h and 50-km/h actions already present in CICV5G repeated field drives.

Evidence roles are disjoint:

- training runs fit the QoS predictor;
- donor runs provide measured candidate outcomes;
- query runs provide decision locations.

Donor measured delay is unavailable during action selection.

### 3. Initial seed-0 result

With a 2-m spatial caliper, the first development run contained 1,203 eligible matched query locations across 11 query runs.

The naive PRED policy did not improve mean matched delay over FAST and slightly worsened p95 delay.

The matched oracle showed nonzero action headroom.

### 4. Split/caliper robustness audit

A 5-seed x 3-caliper development sweep produced 15 configurations.

For mean matched delay:

- ORACLE_MATCHED beat FAST in **15/15** configurations;
- PRED beat FAST in **9/15** configurations;
- PRED was worse in **6/15** configurations.

For matched p95 delay:

- ORACLE_MATCHED beat FAST in **15/15** configurations;
- PRED beat FAST in **12/15** configurations;
- PRED was worse in **3/15** configurations.

The oracle direction is stable, but the magnitude varies substantially by evidence-role split.

This is not evidence of a robust PRED benefit.

It is evidence that:

1. measurable action-dependent headroom exists under the matching construction;
2. a standard QoS predictor does not recover that action value consistently;
3. donor-run composition materially affects the estimated matched outcome.

---

## Major validity risk discovered by the robustness sweep

Many network/direction/speed strata contain only one donor run in the original 50/25/25 evidence-role split.

Consequently, a large number of matched query outcomes share the same donor acquisition run.

The apparent number of matched locations is therefore much larger than the number of independent outcome sources.

This creates:

- shared-donor dependence;
- run-specific outcome sensitivity;
- possible temporal/network-load confounding;
- unstable absolute matched-delay levels across split seeds.

Timestamp-level sample counts must never be interpreted as independent replication.

---

# Required evidence before a positive paper claim

## Gate A — donor support

The primary protocol must have enough independent donor runs per action to make the matched outcome an average over repeated acquisition runs rather than effectively one donor trajectory.

If this cannot be achieved with CICV5G while preserving separate training and query roles, the dataset is not sufficient for a strong positive motion-decision claim.

## Gate B — support-balanced robustness

The result must be audited under:

- multiple whole-run role assignments;
- predeclared spatial calipers;
- exact network/direction/speed matching;
- multiple independent donor runs per candidate action where available.

A positive policy claim is not allowed if its sign changes primarily with donor-run identity.

## Gate C — decision-focused baseline

The final paper must compare:

- a prediction-accuracy-trained policy;
- a decision-margin / regret-calibrated policy;
- a mobility-first baseline;
- a nondeployable matched oracle;
- an abstaining/support-aware policy.

The research question is whether decision calibration improves **action reliability**, not whether one can tune a cost weight to improve average delay.

## Gate D — untouched confirmation

Development and confirmation must use disjoint acquisition-run role assignments established before the final model is evaluated.

Hyperparameters, matching calipers, action-margin thresholds, and primary endpoints must be frozen before the confirmatory outcomes are opened.

## Gate E — dependence-aware inference

Final inference must account for dependence through shared query and donor acquisition runs.

Acceptable approaches include:

- multiway cluster bootstrap over query and donor run IDs;
- a hierarchical model with acquisition-run random effects;
- cross-fitting in which donor pools are rotated and the final estimand aggregates independent fold-level units.

A simple timestamp bootstrap or query-row bootstrap is invalid.

---

# Primary estimand

The primary paper estimand should be decision regret relative to the support-bounded matched oracle:

[
R(x)=U(x,hat a(x))-U(x,a^*_{mathrm{matched}}(x)).
]

The primary comparison should be:

[
Delta R = R_{mathrm{decision calibrated}}-R_{mathrm{predict then optimize}}.
]

Negative values favor the decision-calibrated method.

Absolute delay MAE should remain a secondary diagnostic.

---

# Proposed decision-calibration method

For two actions, define the field-supported action margin:

[
Delta U(x)=U(x,30)-U(x,50).
]

Instead of minimizing separate absolute QoS prediction errors, estimate:

- expected action margin;
- probability that the margin exceeds the mobility penalty;
- uncertainty in that margin;
- empirical measurement support for both actions.

The policy changes from the mobility-first action only when:

[
P(Delta U(x)<-	aumid x,mathcal D_{mathrm{train}}) > 1-alpha
]

and both actions pass the predeclared support gate.

Otherwise it abstains and selects the mobility-first action.

This is **not claimed as a new general decision-focused-learning principle**. The scientific contribution is its evaluation under a field-measured, support-bounded repeated-drive protocol.

---

# Go / no-go rules

## Positive-paper GO

A positive paper claim requires all of:

1. stable oracle headroom under support-balanced matching;
2. sufficient independent donor support;
3. decision-calibrated policy lower regret than predict-then-optimize in the untouched confirmation;
4. effect direction stable across declared network/direction strata or explicitly explained heterogeneity;
5. dependence-aware uncertainty supporting the claimed effect;
6. no post-confirmation retuning.

## Boundary-paper GO

If oracle headroom is stable but deployable policies cannot recover it reliably, the paper may instead support:

> Field QoS logs can contain measurable action-dependent communication differences while remaining insufficient for reliable motion-policy optimization under honest disjoint-run evaluation.

That is a scientifically useful result if the negative finding is protocol-stable.

## Dataset NO-GO

Do not use CICV5G for a strong motion-policy paper if:

- honest donor overlap is too sparse;
- the oracle effect changes sign under reasonable support controls;
- apparent policy gains are driven by one acquisition run;
- valid inference cannot separate query- and donor-run dependence.

In that case, retain CICV5G for prediction/methodology evidence and design a new repeated or randomized driving experiment for the action-calibration question.

---

# Submission-language lock

Safe language:

- "support-bounded matched field replay";
- "measured donor outcome";
- "repeated-drive action evidence";
- "decision reliability";
- "action-ranking regret";
- "observational matched outcome";
- "development/confirmatory run separation".

Unsafe language:

- "true counterfactual";
- "causal speed effect";
- "real-world oracle";
- "independent 1,203 trials";
- "first decision-focused vehicular communication";
- "proves communication-aware speed control improves QoS".

---

# Current decision

**Do not submit the matched-speed story yet.**

The research gap is credible enough to continue, but the current evidence is still development evidence.

The next required milestone is the support-balanced W2S audit followed by a frozen decision-margin development protocol.
