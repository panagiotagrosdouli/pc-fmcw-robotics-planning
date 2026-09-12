# Research log

## 2026-09-12 — baseline and gap decision
- Repository audited at architecture level: existing P0-P4 planning, prediction, PC-FMCW link bridge, robustness/statistics, and substantial test suite already exist.
- Literature check rejected generic "communication-aware planning" novelty.
- Closest current overlap identified: Gordon et al. 2026 proactive QoS risk maps; Ullah et al. 2025 AV QoS trajectory planning. Subsequent search also found recent uncertainty-aware GP/tube-MPC communication-preserving navigation and real-data vehicular predictive-QoS work, so neither uncertainty nor real-data prediction alone is a defensible novelty claim.
- CICV5G selected as primary real-data source because it has repeated field runs with position, motion, SINR, RSRP and V2N2V delay.
- Research pivot: empirical-support-aware, leakage-safe, horizon-aware measured-QoS planning.
- Implemented CICV5G loader/downloader, grouped run split, persistence/KNN/tree predictors, split-conformal residual intervals, spatial support diagnostics/gating, planning score adapter, study runners, statistics/figures and tests.

## 2026-09-12 — first full measured-data evidence
- GitHub Actions downloaded 38 public CICV5G run files and parsed 43,045 measured samples.
- Run-disjoint primary split: 22,441 train, 8,846 calibration, 11,758 test samples.
- Real-V2X unit tests: 10/10 passed.
- One-step delay prediction falsified the simple "ML beats reactive" hypothesis: persistence MAE was about 5.58 ms, while spatial KNN was about 10.86 ms, Extra Trees about 6.66 ms, and Random Forest about 7.15 ms on the held-out split.
- One-step SINR was even more temporally persistent; current-value persistence strongly outperformed spatial prediction.
- Spatial support was scientifically informative: delay MAE increased from about 5.33 ms for points within 1 m of training measurements to about 9.58 ms in the 5-15 m support stratum. Marginal interval coverage fell from about 0.888 to about 0.761 over the same strata.
- A nominal 90% split-conformal interval achieved about 0.884 coverage on the primary test split and materially lower coverage on some grouped robustness splits. This is treated as distribution-shift evidence, not hidden or relabeled as successful calibration.

## 2026-09-12 — causal horizon study
- Added causal multi-horizon evaluation. Future geometry is queried at horizons from roughly 55 ms to 5.5 s, while only current measured QoS is available causally.
- Pure spatial prediction remained weak. A calibration-only context-adaptive fusion of persistence and spatial information was therefore tested, with unseen contexts forced back to persistence.
- Five grouped split seeds show the key effect is horizon-dependent. At the longer tested horizons (~1.1 s, 2.8 s, 5.5 s), fusion improved delay MAE over persistence in every split seed. Mean improvement magnitude increased with horizon, reaching roughly 2.5-2.6 ms at the two longest horizons.
- This supports a narrower conclusion: spatial/context information has incremental predictive value at planning-relevant horizons, but not as a universal replacement for a strong reactive baseline.

## 2026-09-12 — counterfactual validity decision
- Arbitrary off-route trajectory replay was rejected because CICV5G does not provide measured QoS ground truth at unvisited counterfactual coordinates.
- Added a route-constrained measured-support replay experiment instead. Candidate decisions are restricted to future samples on the same measured held-out run; future delay is outcome-only and is never provided as a planner input.
- P0/P1/P2/P3 are compared with a mobility-deviation term, predictive QoS term, uncertainty term and empirical-support penalty where applicable.
- Added real decision-compute timing plus paired run-level bootstrap/Wilcoxon analysis.
- This experiment is explicitly a measured decision-value replay, not closed-loop vehicle validation.

## Evidence gate
The route-constrained replay must pass CI and its measured outcomes must determine the final P2/P3 claims. If P2/P3 do not improve measured outcomes, that result remains part of the final discussion. No arbitrary counterfactual QoS ground truth will be fabricated to rescue a positive claim.
