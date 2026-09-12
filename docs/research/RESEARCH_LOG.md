# Research log

## 2026-09-12 — baseline and gap decision
- Repository audited at architecture level: existing P0-P4 planning, prediction, PC-FMCW link bridge, robustness/statistics, and substantial test suite already exist.
- Literature check rejected generic "communication-aware planning" novelty.
- Closest current overlap identified: Gordon et al. 2026 proactive QoS risk maps; Ullah et al. 2025 AV QoS trajectory planning.
- CICV5G selected as primary real-data source because it has repeated field runs with position, motion, SINR, RSRP and V2N2V delay; W2S captures strong-to-weak coverage transitions.
- Research pivot: counterfactual-support-aware, leakage-safe, uncertainty-calibrated planning.
- Implemented robust CICV5G loader, grouped run split, persistence/KNN/tree predictors, split-conformal residual intervals, spatial support gating, planning score adapter, downloader, study runner, statistics/figures and tests.
- Local isolated unit tests: 7/7 passed.
- Full synthetic-fixture software verification passed after fixing a zero-range histogram edge case. Fixture numbers are not scientific evidence.

## Evidence gate
Run the research branch under GitHub Actions with downloaded public CICV5G W2S measurements. Report held-out predictor performance, interval coverage, spatial-support behavior and run-level paired effects. Only then decide whether a measured-data counterfactual planner comparison is sufficiently supported by route overlap; do not invent unobserved ground truth.
