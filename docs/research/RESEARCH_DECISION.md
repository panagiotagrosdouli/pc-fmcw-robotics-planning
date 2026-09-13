# Research decision

## Primary question
Can a lightweight autonomous planner extract useful future QoS information from **field-measured vehicular communication data** while explicitly respecting **empirical measurement support and grouped distribution shift**, rather than trusting an unconstrained learned radio/QoS map?

## Final selected direction
Use CICV5G repeated field runs as the primary measured-data benchmark. Train, calibrate, and test on disjoint whole runs. Treat current-value persistence as a serious baseline. Evaluate prediction at planning-relevant horizons. Add spatial/context information only when calibration data show value over persistence. Audit every queried future state against training-coordinate support. Evaluate uncertainty on genuinely held-out runs. For decision-value testing, restrict replay choices to measured future states on the same held-out route rather than inventing ground truth at arbitrary unvisited coordinates.

## Why the initial generic idea was rejected
“Predict QoS and avoid blackspots” is too close to established communication-aware radio-map planning. Gordon et al. (INFOCOM/NetRobiCS 2026) already use estimated QoS-risk maps proactively for robot motion; Ullah et al. (IEEE Access 2025) optimize AV trajectories using communication QoS; recent GP/tube-MPC work couples radio-map prediction uncertainty to robust communication-preserving motion; and optical/FSO/ISAC trajectory optimization also has direct prior art. The defensible gap is therefore not prediction, uncertainty, communication-aware planning, or optical trajectory optimization in isolation.

The selected contribution is an **evidence-validity layer for measured-QoS motion decisions**: drive-grouped anti-leakage splits, strong causal persistence baselines, horizon-dependent predictive value, spatial-support diagnostics, distribution-shift-aware uncertainty reporting, and measured-support route replay.

## Evidence-driven hypothesis revision
The original H1 stated that a lightweight learned predictor would improve one-step delay MAE over persistence. This was falsified on the primary grouped split. The project was not allowed to preserve that hypothesis by changing the split or hiding the negative result.

**H1-R:** learned spatial/context information has incremental value over current-value persistence at sufficiently long planning horizons.

Across five grouped split assignments, calibration-only horizon-adaptive fusion improves delay MAE over persistence in all five assignments at roughly 1.1 s, 2.8 s, and 5.5 s horizons. The assignments reuse the same 38 drives, so this is descriptive robustness evidence rather than five independent replications.

The original uncertainty hypothesis expected near-nominal split-conformal coverage. Coverage is below nominal under some grouped shifts and degrades in low-support strata in the primary analysis. Deeper inspection shows the support/error relationship is context-dependent rather than universally monotone.

**H2-R:** empirical measurement support and grouped distribution shift expose reliability risks that should be visible to the planner rather than hidden behind a single uncertainty interval.

The route-constrained replay motivates the decision hypothesis:

**H3-R:** predictive P2 should provide favorable measured-outcome decision value relative to reactive P1, while support-aware P3 should reduce unsupported decision exposure even if it does not provide additional QoS gain.

On the primary nine-run split, P2-P1 mean measured-delay delta is about **-0.792 ms**, with 95% paired-bootstrap CI approximately **[-1.723, -0.138] ms** and raw paired Wilcoxon **p=0.046875**. After Holm correction across the declared 12 replay comparison/metric tests, the adjusted p-value is about **0.28125**. The result is therefore exploratory effect-size evidence, not multiplicity-corrected confirmatory significance.

P3 does not improve measured delay over P2: the primary P3-P2 delay effect is about +0.073 ms and cross-split effects are mixed. P3 reduces unsupported selection exposure in the primary split by about 0.01836 absolute, but its raw p=0.03125 becomes about **0.25 after Holm correction**. Across five grouped split assignments, however, the unsupported-fraction delta is negative in all 5/5 assignments (descriptive mean about -0.02795). P3 is therefore interpreted as an inference-validity/support-control mechanism with a mobility trade-off, not a QoS-superiority result.

## Primary endpoints
1. Run-level predictive MAE relative to persistence at each horizon.
2. Run-level mean measured delay and measured delay-violation fraction selected by P0/P1/P2/P3 in route-constrained held-out replay.
3. Fraction of selected decisions outside configured empirical support.

## Secondary endpoints
RMSE, interval coverage/width, support-stratified error, selected-horizon/mobility deviation, changed-decision fraction, SINR diagnostics, decision compute time, and failure cases.

## Computational result
The later vectorized replay implementation demonstrates microsecond-scale batched QoS/support evaluation and candidate scoring on hosted CI, with occasional outliers. This supports only an implementation-level computational-practicality statement. It is not end-to-end embedded or vehicle real-time validation.

## Relationship to PC-FMCW
The PC-FMCW branch remains the technology-specific model-based optical experiment. The CICV5G branch tests the decision-layer principle under real communication traces. No 5G measurement is relabeled as PC-FMCW and no real-data result is presented as optical-channel validation.

## Final claim boundary
Measured communication samples are real 5G V2N2V field data. Planning remains offline and route-constrained; future measured QoS is revealed only as an outcome after action selection. The results do not validate arbitrary off-route counterfactuals, PC-FMCW optical hardware, vehicle safety, or real-road closed-loop autonomous-driving operation.

## Falsification discipline
The interpretation retains negative results: generic learned predictors do not beat persistence at one-step prediction, ordinary conformal coverage is not uniformly reliable under grouped shift, raw primary-split p-values do not survive the declared multiplicity correction, and P3 is not superior to P2 on measured QoS. These failures motivate and delimit the measurement-support-aware formulation.
