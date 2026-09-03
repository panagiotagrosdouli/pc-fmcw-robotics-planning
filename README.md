# PC-FMCW Robotics Planning

Predictive connectivity-aware autonomous motion planning for vehicles using PC-FMCW/DPSK optical-link forecasts.

## Research objective

This repository implements the robotics extension of the PC-FMCW predictive-communications pipeline. The core idea is a closed-loop planner that evaluates candidate ego trajectories using predicted future communication quality and selects motion under hard vehicle, road, collision, and safety constraints.

The upstream PC-FMCW/communications model is treated as frozen as far as possible. The new contribution is the **ego motion decision layer**, not scheduling or a redesign of the PHY.

## Planning pipeline

1. PC-FMCW sensing and tracking
2. Target-motion prediction
3. Candidate ego-trajectory generation
4. Trajectory-conditioned future link prediction
5. Safety / mobility / connectivity evaluation
6. Receding-horizon motion selection
7. Execute the first control and replan

## Planners

- **P0 — Mobility-only:** no connectivity objective
- **P1 — Reactive connectivity-aware:** current/myopic link information
- **P2 — Predictive connectivity-aware:** predicted target motion + predicted future link state
- **P3 — Predictive risk-aware:** uncertainty-aware extension point
- **P4 — Oracle:** simulator ground-truth upper bound

All planners use the same candidate generator and hard safety filters.

## Primary research questions

- Can predicted future PC-FMCW/DPSK link quality proactively improve autonomous motion decisions?
- How much mobility cost is required for a given connectivity gain?
- At what prediction horizon and prediction-error regime does proactive planning cease to be beneficial?

## Current implementation

The Stage 9 core is now executable as a deterministic simulation prototype:

- kinematic bicycle dynamics
- Frenet-inspired candidate trajectory library
- hard road/speed/obstacle filtering with obstacle radii
- trajectory-conditioned geometry-based link forecast
- P0/P1/P2/P4 planner baselines
- receding-horizon closed-loop episode runner
- five primary synthetic scenario families: following/lateral-offset, lane choice, overtake, intersection turn, and occluding cut-in
- CSV experiment output and an initial outage-vs-travel-time figure under `results/`

The geometry predictor is intentionally a configurable surrogate. It must be replaced or calibrated against the frozen PC-FMCW predictor/PHY model before making final scientific claims.

## Run the primary experiment

From the repository root:

```bash
pip install -r requirements.txt
python scripts/run_stage9.py
```

The script compares P0/P1/P2/P4 on the five deterministic scenarios and writes:

```text
results/stage9_primary.csv
results/stage9_summary.csv
results/stage9_outage_vs_travel_time.png
```

## Repository structure

```text
pc-fmcw-robotics-planning/
├── notebooks/
├── src/iscai/
│   ├── phy/
│   ├── tracking/
│   ├── prediction/
│   ├── planning/
│   ├── simulation/
│   └── evaluation/
├── configs/stage9/
├── scripts/
├── tests/
├── results/
└── requirements.txt
```

## Scientific scope

The first paper target is simulation-first and CPU-friendly. The planned experimental story is predictive versus reactive connectivity-aware motion planning, with hard safety constraints, mobility-connectivity Pareto analysis, and robustness to prediction horizon and prediction error.

Higher-fidelity CommonRoad/CARLA integration, probabilistic uncertainty, and HIL/real-world validation are later stages rather than prerequisites for the core contribution.

## Reproducibility

Experiment configurations, fixed scenarios, machine-readable results, unit tests, and figure-generation scripts are kept in the repository so that experiments can be regenerated from controlled inputs.

## Status

🚧 **Research prototype — Stage 9 closed-loop core + primary benchmark implemented; next: prediction-error/horizon sweeps and frozen PC-FMCW model integration.**
