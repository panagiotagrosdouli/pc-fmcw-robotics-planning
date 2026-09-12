# Research decision

## Primary question
Can a lightweight autonomous planner use **field-measured vehicular QoS** proactively while explicitly accounting for **prediction uncertainty and measurement-support validity**, rather than trusting an unconstrained radio/QoS map?

## Selected method
Use CICV5G W2S repeated runs as the first real-data benchmark. Train on whole runs, calibrate uncertainty on disjoint whole runs, and test on disjoint whole runs. Compare persistence, spatial KNN and tree ensembles. Fit a split-conformal residual interval to the selected predictor. Fit a spatial support model only on training coordinates. A future planner query is marked unsupported when it is farther than a configurable radius from training data or lacks local measurement density.

## Why this beats the initial generic idea
"Predict QoS and avoid blackspots" is too close to existing communication-aware radio-map planning. The defensible differentiator is that real-data counterfactual planning is treated as an inference-validity problem: no planner receives a free assumption that predicted QoS is trustworthy everywhere.

## Relationship to PC-FMCW
The existing PC-FMCW branch remains the technology-specific model-based optical experiment. The new real-V2X branch tests whether the same decision-layer concept remains useful under measured communications. No 5G measurement is relabeled as PC-FMCW.

## Primary hypotheses
H1: On disjoint runs, at least one lightweight spatiotemporal predictor improves delay MAE over persistence.

H2: Split-conformal intervals achieve approximately their nominal held-out coverage under the in-distribution run split and widen the planner's effective risk region near QoS degradation.

H3: Support-aware predictive planning reduces high-delay exposure relative to reactive planning without requiring unsupported counterfactual predictions, at a measurable mobility cost.

## Primary endpoint
Episode/run-level fraction of states exceeding the configured delay threshold, paired where trajectory replay support permits.

## Secondary endpoints
Delay MAE/RMSE, interval coverage/width, unsupported prediction fraction, added path/time cost, SINR diagnostics, and compute time.
