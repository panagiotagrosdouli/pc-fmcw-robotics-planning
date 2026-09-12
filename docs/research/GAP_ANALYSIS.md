# Research gap analysis — measured-support-aware predictive QoS planning

## What is not novel
Communication-aware motion planning is established at least since Ghaffarkhah & Mostofi (2011). Online radio mapping, resilient connectivity planning, formal QoS-constrained motion, joint communication-motion co-design, QoS-aware AV route selection, real-data predictive QoS, and uncertainty-aware radio-map planning have all been demonstrated. Gordon et al. (INFOCOM NetRobiCS 2026) already convert estimated radio maps into service-specific QoS-risk maps and proactively avoid low-quality regions. Recent GP/tube-MPC work also couples radio-map uncertainty to robust motion. Therefore this project must not claim novelty for "predicting communication quality along trajectories", "avoiding connectivity blackspots", or "adding uncertainty to communication-aware planning" alone.

## Selected gap
The strongest lightweight gap found in the reviewed literature is the **scientific validity of using field-measured vehicular QoS for counterfactual motion decisions under finite empirical support and distribution shift**.

Real vehicular datasets measure the path that was actually driven. A planner normally scores paths that were not driven. Without an explicit validity layer, a data-driven radio/QoS map may produce confident-looking values in locations or operating contexts with weak empirical support. A second problem is leakage: random sample splits can place temporally and spatially adjacent measurements from the same drive on both sides of the train/test boundary.

The research therefore targets a combined protocol rather than a new prediction primitive:

1. whole-run train/calibration/test splitting to prevent drive-level leakage;
2. transparent causal baselines, especially current-value persistence;
3. prediction at multiple decision horizons rather than only one-step interpolation;
4. explicit spatial measurement-support diagnostics for every queried state;
5. uncertainty evaluation under grouped distribution shift instead of assuming nominal conformal coverage transfers automatically;
6. a support-aware decision layer that penalizes communication predictions outside empirical support;
7. route-constrained measured replay so future measured QoS is used only as an outcome, avoiding fabricated labels at arbitrary counterfactual positions.

The defensible contribution is this **measurement-support / leakage / horizon / decision-value audit as a coherent real-data planning protocol**. We have not established a universal first-ever claim; the wording should be "we found no close prior work in the reviewed literature that combines these elements for field-measured vehicular QoS planning."

## Evidence-driven pivot from the initial hypothesis
The initial hypothesis expected a lightweight spatial or tree predictor to beat a reactive persistence baseline. The actual CICV5G experiments did not support that simple story. On the primary disjoint-run split, persistence achieved 5.58 ms one-step delay MAE, while spatial KNN, Extra Trees, and Random Forest were worse. SINR was even more temporally persistent.

This negative result changes the research question. The question is no longer "can generic ML predict QoS better than reactive information?" Instead it is:

> At what forecast horizons and under what empirical-support conditions does learned spatial/context information add decision value beyond a strong causal persistence baseline?

A calibration-only context-adaptive fusion of persistence and spatial information gives modest improvements at longer horizons. Across five grouped split seeds, every seed improved over persistence at approximately 1.1 s, 2.8 s, and 5.5 s horizons. This is more defensible than claiming universal ML superiority.

## Empirical support finding
Prediction quality worsens as held-out points move farther from training measurements. In the primary split, delay MAE increased from about 5.33 ms within 1 m of training support to about 9.58 ms in the 5–15 m stratum. Interval coverage also fell from about 0.888 to about 0.761 over those strata. This makes empirical support a measurable reliability variable rather than a cosmetic diagnostic.

## Uncertainty finding
A nominal 90% split-conformal interval does not maintain 90% coverage consistently across grouped splits. Mean held-out coverage across the five robustness splits is closer to the mid-0.8 range, and some splits are materially lower. This is consistent with the known limitation that ordinary split conformal coverage relies on exchangeability and need not survive distribution shift. The project therefore must not call these intervals universally calibrated probabilities.

## Why CICV5G first
CICV5G is public and contains field V2N2V records with synchronized UTM position, heading, velocity, SINR, RSRP and end-to-end delay over repeated runs, frequencies and nominal speeds. The public measurements are directly downloadable and suitable for grouped holdout studies. The data are real; the autonomous decisions remain offline.

## Primary research question
Can a lightweight predictive connectivity planner extract useful future QoS information from field measurements **without trusting predictions outside their empirical support**, and does that information improve route-constrained offline decisions relative to a strong reactive persistence baseline?

## Falsification conditions
The decision-value hypothesis fails if P2/P3 do not improve measured held-out QoS outcomes relative to P1 at comparable mobility cost. The uncertainty-aware hypothesis fails if P3 adds no benefit beyond P2 or merely increases conservatism. The empirical-support hypothesis fails if support distance/density does not correlate with reliability or does not affect decision validity. Negative outcomes must remain in the paper rather than being removed.

## Claim boundary
Field communication measurements are real. QoS forecasts are learned. Route-constrained replay decisions are offline. The experiment is not closed-loop real-vehicle validation and does not provide ground truth for arbitrary unmeasured trajectories. CICV5G is 5G V2N2V data and does not validate PC-FMCW optical propagation. The existing PC-FMCW branch remains a separate technology-specific model-based experiment; the common object being tested is the decision-layer methodology.
