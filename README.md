# PC-FMCW Robotics Planning

Predictive connectivity-aware autonomous motion planning built as a robotics extension of the upstream PC-FMCW/DPSK ISCAI study.

## End-to-end research story

`PC-FMCW sensing/communication → target tracking → target prediction → trajectory-conditioned connectivity forecast → P0–P4 ego-motion planning → receding-horizon closed-loop evaluation`

The upstream reference is `PanagiotaGr/ISCAI_pc_fmcw`. Its Module 0 parameters are explicitly bridged into this repository: 193.4 THz carrier, 10 GHz chirp bandwidth, 10 µs chirp duration and 1 Gbit/s data rate. The robotics contribution is the ego-motion decision layer, not a redesign of the PHY.

## Dataset-free core study

The primary paper experiment no longer requires CMHT, Rad-R, or another external driving dataset. Target motion and ego motion are generated in controlled parameterized simulation. This makes the benchmark reproducible and keeps the scientific question focused on predictive connectivity-aware planning.

The current geometry-to-SNR/outage model is a **PC-FMCW-informed simulation model**, not measured optical-link data. Waveform constants are traced to the upstream notebook; propagation/pointing assumptions are declared separately in `src/iscai/connectivity/pc_fmcw_bridge.py`. The benchmark must not be described as a real-world or real-vehicle validation.

## Planners

- **P0 — Mobility-only:** ignores connectivity.
- **P1 — Reactive:** uses current/myopic target geometry.
- **P2 — Predictive:** uses a future target-trajectory estimate.
- **P3 — Risk-aware predictive:** uses the same mean predictor as P2 plus explicit uncertainty propagated through the same link model.
- **P4 — Oracle:** simulation-only upper bound with access to future target truth.

P0–P3 do not receive future simulator truth. P2 and P3 share the same constant-velocity mean prediction so their comparison isolates risk treatment.

## Simulation benchmark

The repository contains five primary scenario families: following/lateral-offset, lane choice, overtake, intersection turn and occluding cut-in. Evaluation records modeled outage probability, SNR, DPSK BER/goodput model outputs, path length, progress, minimum target distance, static-obstacle clearance, collision indicator and planner feasibility failures.

Run the lightweight benchmark:

```bash
pip install -r requirements.txt
python scripts/run_pc_fmcw_robotics_benchmark.py --seeds 10
```

Run the frozen paper manifest:

```bash
python scripts/run_paper_experiments.py
```

The default paper configuration is `configs/experiments/paper.yaml` and uses 30 simulation seeds. Outputs are written under `results/pc_fmcw_sim/` with a machine-readable provenance manifest.

## Legacy / optional data integrations

CMHT and Rad-R integration code remains in the repository as optional/legacy validation infrastructure. It is not required by the dataset-free core experiment and must not be mixed into claims about measured optical PC-FMCW communication.

## Scientific scope

The core claim tested by this repository is whether **trajectory-conditioned future connectivity prediction can improve autonomous motion decisions relative to mobility-only and reactive baselines, and at what mobility/safety cost**. Synthetic observation/prediction perturbations are simulation errors, not physical sensor measurements.

See `docs/PC_FMCW_ROBOTICS_BRIDGE.md` for the complete claim boundary and integration protocol.

## Reproducibility

The repository keeps deterministic scenario generation, fixed experiment configuration, seeded uncertainty, P0–P4 baselines, unit/integration tests, CI smoke experiments, CSV outputs and provenance manifests under version control.

## Status

🚧 **Dataset-free PC-FMCW-informed P0–P4 closed-loop benchmark implemented. Numerical paper claims are only made after the configured experiment suite has actually executed successfully.**
