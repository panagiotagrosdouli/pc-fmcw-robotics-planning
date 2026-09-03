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
- **P3 — Predictive risk-aware:** uncertainty-aware extension
- **P4 — Oracle:** simulator ground truth upper bound

All planners use the same candidate generator and hard safety filters.

## Primary research questions

- Can predicted future PC-FMCW/DPSK link quality proactively improve autonomous motion decisions?
- How much mobility cost is required for a given connectivity gain?
- At what prediction horizon and prediction-error regime does proactive planning cease to be beneficial?

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

## Initial implementation

The first implementation is simulation-first and CPU-friendly:

- kinematic bicycle dynamics
- Frenet/sample-based candidate trajectories
- hard feasibility and collision filtering
- trajectory-conditioned link forecasting
- outage and link-survival as the primary connectivity objective
- receding-horizon planning
- deterministic synthetic scenarios
- paired evaluation and Pareto analysis

Higher-fidelity CommonRoad/CARLA integration and uncertainty-aware prediction are extensions after the core closed loop is validated.

## Reproducibility

Experiment configurations, random seeds, machine-readable results, unit tests, and figure-generation scripts are kept in the repository so that the main experiments can be regenerated from fixed configurations.

## Status

🚧 Research prototype — Stage 9 implementation in progress.
