# PC-FMCW Robotics Planning

Predictive connectivity-aware autonomous motion planning for vehicles using a dataset-free PC-FMCW-informed simulation model.

## Research objective

This repository implements the robotics extension of the PC-FMCW predictive-communications pipeline. The core idea is a closed-loop planner that evaluates candidate ego trajectories using predicted future communication quality and selects motion under hard vehicle, road, static-obstacle, and dynamic-target safety constraints.

The upstream PC-FMCW/communications model is treated as frozen as far as possible. The new contribution is the **ego motion decision layer**, not scheduling or a redesign of the PHY.

## Planning pipeline

1. PC-FMCW sensing and tracking model
2. Target-motion prediction
3. Candidate ego-trajectory generation
4. Hard static- and dynamic-obstacle filtering
5. Trajectory-conditioned future link prediction
6. Safety / mobility / connectivity evaluation
7. Receding-horizon motion selection
8. Execute the first control and replan

## Planners

- **P0 — Mobility-only:** no connectivity objective, but uses the common predicted target mean for safety filtering
- **P1 — Reactive connectivity-aware:** current/myopic link scoring with the common predicted target safety trajectory
- **P2 — Predictive connectivity-aware:** common predicted target motion + predicted future link state
- **P3 — Predictive risk-aware:** same mean target prediction and link model as P2 plus Monte-Carlo uncertainty propagation
- **P4 — Oracle connectivity reference:** simulator ground-truth future target motion is used only for connectivity forecasting; dynamic safety still uses the same predicted target mean as the deployable planners

All planners use the same candidate generator, vehicle limits, road/static-obstacle filters, and time-aligned dynamic-target safety layer. Future simulator truth is never used to give P4 an oracle collision-avoidance advantage.

## Dataset-free benchmark

The core paper study no longer requires CMHT/Rad-R. It is a controlled, reproducible closed-loop simulation with seeded target observations and parameterized target motion. The main benchmark is:

```bash
pip install -r requirements.txt
python scripts/run_pc_fmcw_robotics_benchmark.py --seeds 10
```

Outputs are written under `results/pc_fmcw_sim/` and include per-episode CSV rows, planner summaries, and a provenance manifest.

The robotics study uses a **PC-FMCW-informed analytical connectivity model** coupled to future relative ego/target geometry. Parameters intended to represent the upstream Part-A PC-FMCW system are kept explicit in the bridge, while the range/pointing-to-SNR mapping is a declared simulation assumption rather than a measured optical-channel calibration. Consequently, results must be reported as **controlled model-based / PC-FMCW-informed simulation**, not measured optical-link performance or real-world autonomous-driving validation.

## Scientific comparison

The experimental story is P0/P1/P2/P3/P4 under identical scenario realizations and seeds. Primary outcomes are modeled outage/SNR/BER/goodput, path length/progress, target/static-obstacle clearance, collision rate, collision-boundary realized TTC, and no-candidate rate. Statistical analysis uses independent simulation episode/seed units and paired comparisons, especially P2 vs P1 and P3 vs P2, with bootstrap effect intervals, paired Wilcoxon tests, and Holm multiplicity correction.

Robustness figures can be generated from episode-level outputs with deterministic 95% bootstrap confidence intervals. These intervals quantify variability across simulated episodes; they are not measurement-error bars from a physical optical experiment.

## Repository structure

```text
pc-fmcw-robotics-planning/
├── src/iscai/
│   ├── connectivity/
│   │   └── pc_fmcw_bridge.py
│   ├── planning/
│   ├── prediction/
│   ├── simulation/
│   │   └── pc_fmcw_benchmark.py
│   └── evaluation/
├── configs/
├── scripts/
├── tests/
├── docs/
└── requirements.txt
```

## Reproducibility

Fixed configurations, seeded scenarios, machine-readable provenance, P0–P4 fairness rules, unit tests, CI smoke benchmarks, and figure/statistics scripts are maintained in the repository. The legacy CMHT/Rad-R utilities remain optional extensions and are not prerequisites for the core dataset-free paper.

## Status

🚧 **Dataset-free PC-FMCW-informed closed-loop P0–P4 benchmark implemented with common dynamic-target safety, connectivity-only oracle fairness, collision-boundary TTC diagnostics, paired statistical analysis, robustness sweeps with bootstrap uncertainty, and reproducibility/CI integration. Remaining paper work is large-seed execution and reporting of the resulting tables/figures without extrapolating beyond the controlled simulation study.**
