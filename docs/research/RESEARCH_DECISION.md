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

The completed route-constrained replay resolves the decision hypothesis:

**H3-R:** predictive P2 reduces mean measured delay relative to reactive P1 on the primary held-out replay, while support-aware P3 trades additional mobility deviation for significantly lower unsupported decision exposure rather than additional QoS gain.

Across 9 held-out runs, P2-P1 mean measured delay is **-0.792 ms** with 95% paired bootstrap CI **[-1.723, -0.138] ms** and paired Wilcoxon **p=0.0469**. The delay-threshold violation-fraction change is -0.00279 with p=0.0625, so a statistically significant reduction in violation fraction is **not** claimed from this split alone.

P3 does not improve measured delay over P2: P3-P2 is +0.073 ms (p=0.742), and the threshold-violation fraction changes by +0.00034 (p=0.50). However, P3 reduces the selected unsupported fraction relative to P2 by **0.01836 absolute** with 95% bootstrap CI **[-0.03214, -0.00603]** and paired Wilcoxon **p=0.03125**, while adding mobility deviation of +0.01052 (p=0.0078). This is therefore an inference-validity/support trade-off, not a QoS-superiority result.

## Primary endpoints
1. Run-level predictive MAE relative to persistence at each horizon.
2. Run-level mean measured delay and measured delay-violation fraction selected by P0/P1/P2/P3 in route-constrained held-out replay.
3. Fraction of selected decisions outside configured empirical support.

## Secondary endpoints
RMSE, interval coverage/width, support-stratified error, selected-horizon/mobility deviation, changed-decision fraction, SINR diagnostics, decision compute time and failure cases.

## Computational result
The replay implementation measured approximately **8.63 ms mean** and **8.85 ms p95** decision computation on the hosted CI runner. This supports only an implementation-level computational-practicality statement. It is not end-to-end embedded or vehicle real-time validation.

## Relationship to PC-FMCW
The existing PC-FMCW branch remains the technology-specific model-based optical experiment. The measured CICV5G branch tests the general decision-layer principle under real communication traces. No 5G measurement is relabeled as PC-FMCW, and no real-data result is presented as optical-channel validation.

## Final claim boundary
Measured communication samples are real 5G V2N2V field data. Planning remains offline and route-constrained; future measured QoS is revealed only as an outcome after action selection. The results do not validate arbitrary off-route counterfactuals, PC-FMCW optical hardware, vehicle safety, or real-road closed-loop autonomous-driving operation.

## Falsification discipline
The final interpretation retains the negative results: generic learned predictors do not beat persistence at one-step prediction, nominal conformal coverage is not uniformly reliable under grouped shift, and P3 is not superior to P2 on QoS. Those failures are part of the contribution because they motivate and delimit the measurement-support-aware formulation.
