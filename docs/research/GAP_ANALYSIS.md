# Research gap analysis — measured-support-aware predictive QoS planning

## What is not novel
Communication-aware motion planning is established at least since Ghaffarkhah & Mostofi (2011). Online radio mapping, resilient connectivity planning, formal QoS-constrained motion, joint communication-motion co-design, QoS-aware AV route selection, real-data predictive QoS, and uncertainty-aware radio-map planning have all been demonstrated. Gordon et al. (INFOCOM NetRobiCS 2026) convert estimated radio maps into service-specific QoS-risk maps and proactively avoid low-quality regions. Ullah et al. (IEEE Access 2025) optimize autonomous-vehicle routes using network QoS, and recent GP/tube-MPC work couples radio-map prediction uncertainty to robust communication-preserving motion. Optical trajectory optimization is also occupied: Nafees et al. (WCNC 2025) combine optical ISAC sensing feedback with UAV trajectory optimization over an FSO/RF architecture. Therefore this project must not claim novelty for predicting communication quality along trajectories, avoiding connectivity blackspots, uncertainty-aware communication planning, optical/FSO-aware trajectory planning, or optical ISAC plus trajectory optimization alone.

## Selected gap
The strongest lightweight gap found in the reviewed literature is the **scientific validity of using field-measured vehicular QoS for counterfactual motion decisions under finite empirical support and grouped distribution shift**.

Real vehicular datasets measure the path that was actually driven. A planner normally scores paths that were not driven. Without an explicit validity layer, a data-driven radio/QoS map may produce confident-looking values in locations or operating contexts with weak empirical support. A second problem is leakage: random sample splits can place temporally and spatially adjacent measurements from the same drive on both sides of the train/test boundary.

The research therefore targets a combined protocol rather than a new prediction primitive:

1. whole-run train/calibration/test splitting to prevent drive-level leakage;
2. transparent causal baselines, especially current-value persistence;
3. prediction at multiple decision horizons rather than only one-step interpolation;
4. explicit spatial measurement-support diagnostics for every queried state;
5. uncertainty evaluation under grouped distribution shift instead of assuming nominal conformal coverage transfers automatically;
6. a support-aware decision layer that penalizes communication predictions outside empirical support;
7. route-constrained measured replay so future measured QoS is used only as an outcome, avoiding fabricated labels at arbitrary counterfactual positions.

The defensible contribution is this **measurement-support / leakage / horizon / decision-value audit as a coherent real-data planning protocol**. We do not make a universal first-ever claim. The safe wording is that the work studies this combination explicitly for field-measured vehicular QoS and audits when counterfactual communication predictions are decision-valid.

## Evidence-driven pivot from the initial hypothesis
The initial hypothesis expected a lightweight spatial or tree predictor to beat a reactive persistence baseline. The actual CICV5G experiments did not support that simple story. On the primary disjoint-run split, persistence achieved about 7.419 ms one-step delay MAE (RMSE about 11.365 ms), while conditioned spatial kNN was about 12.344 ms, Random Forest about 9.291 ms, and ExtraTrees about 8.950 ms. The negative one-step result is retained.

This changes the research question from generic predictor superiority to:

> At what forecast horizons and under what empirical-support conditions does learned spatial/context information add decision value beyond a strong causal persistence baseline?

A calibration-only horizon-adaptive fusion of persistence and spatial information gives improvements at longer horizons. Across five grouped split assignments, the P2-style predictive fusion improves delay MAE versus persistence at 20, 50, and 100 steps in all five assignments (descriptive mean improvements about 1.463, 2.510, and 2.621 ms, respectively). The assignments reuse the same 38 drives and are therefore sensitivity/robustness evidence, not five independent replicates.

## Empirical support finding
Empirical support is decision-relevant, but the relationship is **context-dependent rather than universally monotone**. In the primary support-stratified analysis, delay MAE is about 6.98 ms within 1 m of training support, about 8.51 ms at 1–5 m, and about 10.47 ms at 5–15 m; empirical interval coverage falls from about 0.888 to 0.841 and 0.761 over those strata. Forensic analysis shows that much of the severe degradation is concentrated in particular contexts/segments (notably n8), and within-drive distance/error behavior need not be monotone. The defensible statement is therefore that low empirical support is an observable risk indicator under grouped shift, not a universal distance-to-error law.

## Uncertainty finding
A nominal 90% residual split-conformal interval does not maintain 90% coverage consistently under grouped distribution shift, and coverage degrades in low-support strata in the primary analysis. Ordinary split conformal coverage relies on exchangeability assumptions that need not hold after whole-drive holdout. The project therefore reports empirical coverage and does not call these intervals calibrated event probabilities.

## Measured-route decision finding
In the primary replay split, P2 versus P1 changes mean measured delay by about -0.792 ms. The paired bootstrap interval excludes zero, but the raw Wilcoxon p=0.046875 does **not** survive the declared Holm correction across the 12 replay comparison/metric tests (adjusted p about 0.28125). This is exploratory evidence, not confirmatory significance.

Across five grouped split assignments over the same 38 drives, the P2-P1 measured-delay effect is negative in all five assignments (descriptive mean about -0.501 ms), and the >50 ms violation-fraction effect is also negative in all five (mean about -0.00224). Because the underlying drives are reused, these are descriptive robustness findings only.

P3 does not show stable measured-QoS superiority over P2. Its consistent role is different: P3 reduces unsupported decision exposure in all five grouped split assignments (P3-P2 unsupported-fraction mean about -0.02795) at additional mobility deviation. The primary raw p-value for unsupported exposure does not survive Holm correction. P3 is therefore interpreted as an **inference-validity/support-control mechanism**, not an additional QoS-gain planner.

## Why CICV5G first
CICV5G is public and contains field V2N2V records with synchronized UTM position, heading, velocity, SINR, RSRP, cell/network context, and end-to-end delay over repeated runs and operating conditions. The current study uses 38 runs / 43,045 samples. Whole-run splitting makes it suitable for leakage-resistant holdout studies. The communication measurements are real; the autonomous decisions remain offline.

## Primary research question
Can a lightweight predictive connectivity planner extract useful future QoS information from field measurements **without trusting predictions outside their empirical support**, and does that information provide robust route-constrained decision value relative to a strong reactive persistence baseline?

## Falsification conditions
The horizon-value hypothesis fails if calibrated spatial/context information does not improve predictive performance beyond persistence at decision-relevant longer horizons under grouped holdout. The P2 decision-value hypothesis is weakened or rejected if measured-route outcomes do not show a reproducible favorable direction relative to P1 at comparable mobility cost. The P3 support-validity hypothesis fails if the support-aware penalty does not reduce unsupported decision exposure or if its mobility cost overwhelms any validity benefit. The empirical-support hypothesis fails if training-support diagnostics provide no useful reliability stratification under grouped shift. Negative outcomes remain in the paper.

## Claim boundary
Field communication measurements are real. QoS forecasts are learned. Route-constrained replay decisions are offline. Future measured QoS is hidden from the planner and revealed only after selection. The experiment is not closed-loop real-vehicle validation and does not provide ground truth for arbitrary unmeasured trajectories. CICV5G is 5G V2N2V data and does not validate PC-FMCW optical propagation. The PC-FMCW branch remains a separate technology-specific model-based experiment; the common object being studied is decision-layer methodology and the value/validity of future communication prediction.
