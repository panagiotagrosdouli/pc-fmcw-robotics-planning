# Experimental setup — real V2X branch

## Data
Primary dataset: CICV5G public field measurements. The automated downloader used in CI retrieves 38 repeated-run files used by this study, totaling 43,045 synchronized observations. Available fields include millisecond timestamps, UTM position, heading, velocity, Cell ID, SINR, RSRP and V2N2V delay.

## Split protocol
All learning/evaluation splits are grouped by complete run. The primary seed produces 22,441 training, 8,846 calibration and 11,758 test samples. No timestamps from a held-out run are placed in training or calibration. Five split seeds are used for the multi-horizon robustness study.

## Predictors
The evaluation includes current-value persistence, spatial KNN, Random Forest, Extra Trees, and a context-conditioned spatial KNN. Context is defined by network band, driving direction and nominal speed where supported. A calibration-only fusion weight combines persistence and spatial prediction; unseen/insufficient calibration contexts fall back to persistence.

## Uncertainty and support
Residual split-conformal intervals are fitted on the calibration partition. Their coverage is measured on held-out runs; no universal calibration claim is assumed. Spatial support is fitted using training coordinates only and reports nearest-training distance/local density. The route replay uses a strict 1 m support radius with at least five neighbors for the P3 support penalty.

## Horizon evaluation
Forecast offsets are evaluated from 1 to 100 samples, corresponding approximately to median horizons 55 ms, 276 ms, 552 ms, 1.106 s, 2.766 s and 5.534 s in the tested data.

## Route-constrained replay
The replay does not invent alternative geographic paths. At each state from a held-out run, the planner ranks measured future states at candidate offsets 10, 20 and 30 samples. The nominal mobility choice is 20 samples. Future measured delay is hidden during scoring and revealed only after candidate selection as the outcome.

Planner variants:

- P0: mobility-only nominal choice.
- P1: reactive reference; under this route-offset replay current QoS is common to the candidate alternatives, so it retains the nominal choice.
- P2: predicted-delay-aware scoring plus mobility cost.
- P3: P2 plus interval-risk and empirical-support penalties.

Default weights are 0.15 mobility, 0.35 communication, 0.20 risk and 0.50 unsupported-support penalty. These are experiment parameters rather than universal control constants.

## Primary metrics
Prediction: MAE/RMSE, interval coverage/width, support-stratified error.

Decision replay: measured selected delay, fraction exceeding the 50 ms experimental threshold, changed-choice fraction, unsupported-selection fraction and mobility deviation.

## Statistics
The independent paired unit is the held-out run, not the individual timestamp. Primary comparisons use paired run-level effect estimates, deterministic bootstrap 95% confidence intervals and paired Wilcoxon tests. Timestamp counts are used only for descriptive summaries.

## Compute
CI experiments run on GitHub-hosted Ubuntu with Python 3.11 and lightweight NumPy/Pandas/SciPy/scikit-learn/Matplotlib dependencies. The replay implementation records decision runtime on that host, but the reported timing is not extrapolated to embedded vehicle hardware.
