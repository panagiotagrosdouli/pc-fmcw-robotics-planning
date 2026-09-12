# Research decision

## Primary question
Can a lightweight autonomous planner extract useful future QoS information from **field-measured vehicular communication data** while explicitly respecting **empirical measurement support and distribution shift**, rather than trusting an unconstrained learned radio/QoS map?

## Final selected direction
Use CICV5G repeated field runs as the primary measured-data benchmark. Train, calibrate and test on disjoint whole runs. Treat current-value persistence as a serious baseline, not a straw man. Evaluate prediction at planning-relevant horizons. Add spatial/context information only when calibration data show it improves over persistence. Audit every queried future state against training-coordinate support. Evaluate uncertainty on genuinely held-out runs. For decision-value testing, restrict replay choices to measured future states on the same held-out route rather than inventing ground truth at arbitrary unvisited coordinates.

## Why the initial generic idea was rejected
"Predict QoS and avoid blackspots" is too close to established communication-aware radio-map planning. Gordon et al. (2026) already use estimated QoS-risk maps proactively for robot motion, and recent GP/tube-MPC work already couples radio-map uncertainty to robust motion. Real-data vehicular predictive-QoS work also exists. The defensible gap is therefore not prediction, uncertainty, or communication-aware planning in isolation.

The selected contribution is an **evidence-validity layer for measured-QoS motion decisions**: drive-grouped anti-leakage splits, strong causal persistence baselines, horizon-dependent predictive value, spatial-support diagnostics, distribution-shift-aware uncertainty reporting, and measured-support route replay.

## Evidence-driven hypothesis revision
The original H1 stated that a lightweight learned predictor would improve one-step delay MAE over persistence. This was falsified on the primary grouped split: persistence was stronger than spatial KNN and tree ensembles. The project was therefore not allowed to preserve that hypothesis by changing the split or hiding the negative result.

The revised predictive hypothesis is:

**H1-R:** learned spatial/context information has incremental value over current-value persistence at sufficiently long planning horizons, and that value must be demonstrated across grouped run splits.

Five grouped split seeds support H1-R at the longer tested horizons: every split improved at roughly 1.1 s, 2.8 s and 5.5 s horizons using calibration-only context-adaptive fusion.

The original uncertainty hypothesis expected near-nominal split-conformal coverage. Coverage was below nominal under some grouped splits and degraded with measurement-support distance. The revised uncertainty hypothesis is:

**H2-R:** empirical support distance and grouped distribution shift reveal when nominal marginal uncertainty guarantees are unreliable; support should therefore be exposed to the planner rather than hidden inside a single confidence interval.

The decision hypothesis remains prospective until the measured replay result is complete:

**H3:** support-aware predictive decisions reduce measured high-delay exposure relative to reactive persistence at a measurable mobility cost without relying on unmeasured counterfactual ground truth.

## Primary endpoints
1. Run-level predictive MAE relative to persistence at each horizon.
2. Run-level measured delay-violation fraction selected by P0/P1/P2/P3 in route-constrained held-out replay.
3. Fraction of selected decisions outside configured empirical support.

## Secondary endpoints
RMSE, interval coverage/width, support-stratified error, measured delay, selected-horizon/mobility deviation, SINR diagnostics, decision compute time and failure cases.

## Relationship to PC-FMCW
The existing PC-FMCW branch remains the technology-specific model-based optical experiment. The measured CICV5G branch tests the general decision-layer principle under real communication traces. No 5G measurement is relabeled as PC-FMCW, and no real-data result is presented as optical-channel validation.

## Falsification discipline
If the replay shows that P2 or P3 do not improve measured outcomes over P1, that is the reported result. If P3 adds only conservatism without QoS benefit, uncertainty-aware planning will not be claimed as superior. If strict support gating prevents meaningful alternatives, the conclusion will be that this dataset is insufficient for that claim rather than manufacturing unsupported trajectories.
