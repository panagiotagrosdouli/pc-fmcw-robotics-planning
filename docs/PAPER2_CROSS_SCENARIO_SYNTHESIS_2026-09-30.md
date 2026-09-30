# Paper 2 — Cross-Scenario Synthesis

**Date:** 2026-09-30

This note combines the two pre-frozen matched-field confirmations without changing either protocol after outcome inspection.

## Confirmations

### W2S, 30 vs 50 km/h

Locked workflow: `36747715208`  
Workflow head SHA: `a056d46a5579032d10f51a1d6e90d800d3d017b4`  
Executed checkout SHA recorded by artifact: `e4f6430f8b6368f64edee421b827895b11280115`

- ORACLE − FAST: **−4.177 ms**, 95% CI **[−13.659, −2.137]**
- PRED − ORACLE: **+2.704 ms**, 95% CI **[+1.457, +5.832]**
- PRED − FAST: **−1.473 ms**, 95% CI **[−8.167, +0.657]**
- MARGIN − FAST: **−1.668 ms**, 95% CI **[−9.524, +1.180]**
- MARGIN − ORACLE: **+2.509 ms**, 95% CI **[+1.572, +5.162]**

Interpretation: measurable action-value headroom exists and the predictor leaves regret relative to that headroom, but deployable-policy superiority over FAST is not confirmed.

### Arterial n8, 50 vs 80 km/h

Locked workflow: `36749176921`  
Workflow head SHA: `5a98d2e8ea1a948d5cc1d0586d4d63b402a715a7`  
Executed checkout SHA recorded by artifact: `3df3a7b4479f7b1e9d6019497b4a5e9ecbb12586`

- ORACLE − FAST: **−0.590 ms**, 95% CI **[−1.431, −0.250]**
- PRED − ORACLE: **+0.746 ms**, 95% CI **[+0.344, +1.596]**
- PRED − FAST: **+0.156 ms**, 95% CI **[+0.038, +0.258]**
- MARGIN − FAST: **+0.032 ms**, 95% CI **[+0.007, +0.061]**
- MARGIN − ORACLE: **+0.622 ms**, 95% CI **[+0.277, +1.472]**

Interpretation: measurable action-value headroom again exists, but both frozen prediction-derived policies are measurably worse than FAST.

## Cross-scenario finding

The shared result is not a universal speed effect.

It is:

> **Across two pre-frozen repeated-field evaluations using different scenarios and speed-action pairs, support-bounded measured action-value headroom exists, while frozen prediction-based rankings fail to recover that opportunity reliably.**

The two scenarios provide complementary evidence:

- W2S shows why a favorable point estimate is not enough once query/donor dependence is respected.
- Arterial shows that the same prediction-to-action logic can become measurably harmful in another context even though measurable oracle headroom still exists.

This supports a stronger evidence-validity claim:

> **Prediction-derived motion interventions should not be generalized from regression performance or from one favorable replay configuration. Decision evidence must be established at the action-support and acquisition-run level.**

## Reviewer-safe interpretation

Supported:

- prediction utility and measured decision validity are distinct;
- field action support is finite and context-specific;
- acquisition-run dependence matters;
- model-as-truth evaluation can overstate planner evidence;
- direct pairwise margin prediction does not automatically solve the problem;
- context shift can reverse the sign of a prediction-derived intervention relative to a mobility-first baseline.

Not supported:

- one speed is universally better;
- a causal speed effect has been identified;
- the measured oracle is a deployable policy;
- the result generalizes outside CICV5G;
- all predictive QoS interventions are harmful.

## Publication implication

The paper should include both confirmations.

The arterial experiment materially improves the submission because the central failure-boundary pattern is no longer dependent on one route/action pair.

The recommended central empirical statement is:

> **Measured action-value headroom was observed in both frozen field confirmations, yet prediction-derived rankings did not recover it reliably: superiority over FAST was unconfirmed in W2S and the same frozen predictive intervention was worse than FAST in the arterial scenario.**
