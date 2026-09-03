# PC-FMCW Robotics Planning

Predictive connectivity-aware autonomous motion planning for vehicles using a dataset-free PC-FMCW-informed simulation model.

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/e2440283-661c-4707-b63a-d19ef3c7e6ae" />

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

- **P0 — Mobility-only:** no connectivity objective, but uses the same predicted target mean for safety filtering as P1–P3
- **P1 — Reactive connectivity-aware:** current/myopic link scoring with the same predicted target safety trajectory
- **P2 — Predictive connectivity-aware:** predicted target motion + predicted future link state
- **P3 — Predictive risk-aware:** same mean target prediction as P2 plus Monte-Carlo uncertainty propagation
- **P4 — Oracle:** simulator ground-truth future target motion; non-deployable reference

All planners use the same candidate generator, vehicle limits, road/static-obstacle filters, and time-aligned dynamic-target safety layer. P4 alone receives future simulator truth.

## Dataset-free benchmark

The core paper study no longer requires CMHT/Rad-R. It is a controlled, reproducible closed-loop simulation with seeded target observations and parameterized target motion. The main benchmark is:

```bash
pip install -r requirements.txt
python scripts/run_pc_fmcw_robotics_benchmark.py --seeds 10
```

Outputs are written under `results/pc_fmcw_sim/` and include per-episode CSV rows, planner summaries, and a provenance manifest.

The PC-FMCW bridge traces the upstream waveform constants (`fc`, `B`, chirp duration, and 1-Gbit/s data rate) to the Part-A notebook. The range/pointing-to-SNR relation remains an explicit optical-geometry simulation assumption; therefore results must be reported as **PC-FMCW-informed simulation**, not measured optical-link data or real-world autonomous-driving validation.

## Scientific comparison

The experimental story is P0/P1/P2/P3/P4 under identical scenario realizations and seeds. Primary outcomes are modeled outage/SNR/BER/goodput, path length/progress, target/static-obstacle clearance, collision rate, and no-candidate rate. Statistical analysis should use independent simulation episode/seed units and paired comparisons, especially P2 vs P1 and P3 vs P2.

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

🚧 **Dataset-free PC-FMCW-informed closed-loop P0–P4 benchmark implemented, dynamic target safety enforced, and reproducibility/CI integration active. Next research work: large-seed sweeps, uncertainty/horizon sensitivity, statistical tables, and final paper figures.**
