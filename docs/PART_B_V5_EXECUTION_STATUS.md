# Paper 1 V5 development protocol and execution status

## Boundary

V4 failed its complete development gate at all seven margins; see [`PART_B_V4_EXECUTION_STATUS.md`](PART_B_V4_EXECUTION_STATUS.md). V4 development episodes are used only to diagnose the failure. The V5 development seeds 12000–12019 and confirmatory seeds 13000–13049 are disjoint from all V3/V4 development and confirmation sets. Historical V3/V4 confirmatory sets remain unused. No V4 communication result is confirmatory evidence.

## Diagnosis and intervention frozen before V5 seeds

In a V4 failing episode (`following_lateral_offset`, seed 9006, P0, 1.0 m), 152 candidate trajectories passed the static filters at the first no-candidate step, but none passed the dynamic forecast filter. The old filter compared the current ego state to the *next* target prediction, shifting the trajectories by one 0.1 s step. It also checked only the first 20 target predictions even when a candidate lasted 3–5 s. The target's lateral least-squares velocity was extrapolated for two full seconds after the true lateral motion had leveled out, causing a predicted shift from approximately 1.2 m to 0 m. These are historical development diagnostics, not V5 gate results.

V5 applies the following common changes to P0–P4 behind explicit flags, retaining the V4 static and bounded-control branch:

- Compare the first simulated ego step with the first next-step target forecast. Extend the shared mean target forecast by its terminal displacement to cover a candidate's full horizon.
- Reject a candidate if its endpoint lacks a straight maximum-braking continuation clear of the extended predicted moving target. This is a forecast-model viability witness, not a robust guarantee against target maneuvers.
- Preserve longitudinal least-squares constant velocity; damp the lateral least-squares velocity exponentially with a predeclared 0.5 s time constant. The predictor uses observed history only. No oracle target information enters P0–P3 safety; P4 shares the same safety prediction.

The physical collision threshold stays 2.0 m, the static obstacle-surface clearance stays 1.5 m, the candidate controls and fallback stay those of V4, and a no-candidate episode remains a hard failure. A diagnostic rerun on two *historical V4 development seeds* showed seed 9006 P0 at 1.0 m and seed 9010 P0 at 1.0 m without no-candidate steps or realized target collision. This does not establish performance on the fresh V5 development set.

## Frozen gate

[`part_b_final_v5.yaml`](../configs/experiments/part_b_final_v5.yaml) specifies the fixed 20-seed development range 12000–12019, five scenarios, P0–P4, and margins 0.0–3.0 m in 0.5 m increments. Each margin must have exactly 500 paired episode rows. The *minimum* margin with zero realized target collision episodes, zero no-candidate episodes, and zero modeled static-envelope violation episodes is frozen. If none passes, stop without confirmatory or geometry runs. Communication metrics on development seeds are never used to select a margin.

Only after a development pass may 50 untouched confirmatory seeds 13000–13049 run, subject to the same hard safety gate before any communication inference. The geometry mechanism seeds are 14000–14019, with the same frozen margin. All claims remain within the analytical simulation model, not measured optical or real-vehicle validation.

## Status

The complete V5 development sweep finished in GitHub Actions run [35455288436](https://github.com/panagiotagrosdouli/pc-fmcw-robotics-planning/actions/runs/35455288436) from frozen head commit `66eb475980e7c196beb6b1415cbd04529582f1dd`. All seven margin jobs completed successfully and produced 500 paired rows each. Independent artifact verification confirmed exactly 3,500 rows, seeds 12000–12019, all five scenarios and planners, no duplicate paired episode, and agreement with the selector summary.

| Margin (m) | Target collision episodes | No-candidate episodes | Static-envelope violation episodes | Minimum target separation (m) | Gate |
|---:|---:|---:|---:|---:|:---|
| 0.0 | 0 | 26 | 0 | 2.107104 | Fail |
| 0.5 | 0 | 27 | 0 | 2.494166 | Fail |
| 1.0 | 0 | 4 | 0 | 3.319654 | Fail |
| 1.5 | 0 | 35 | 0 | 4.163939 | Fail |
| 2.0 | 0 | 190 | 0 | 4.534840 | Fail |
| 2.5 | 0 | 200 | 0 | 4.970749 | Fail |
| 3.0 | 0 | 200 | 0 | 5.352434 | Fail |

The selector returned `selected_margin_m: null`, `gate_passes: false`, and `confirmatory_seeds_used: false`. V5 eliminated observed collisions and modeled static-envelope violations on the development grid, but it did not eliminate candidate-set failure; therefore no margin passed the joint gate. The minimum no-candidate count was four episodes at 1.0 m, which is still a hard failure under the frozen rule.

**Stop decision:** confirmatory seeds 13000–13049 and geometry seeds 14000–14019 were not run; GitHub marked those jobs skipped. No V5 confirmatory communication, geometry-mechanism, or safety claim is authorized. The complete artifacts and original ZIP digests are archived in [`results_archive/part_b_v5_development`](../results_archive/part_b_v5_development/). A later redesign must use a new predeclared development set and independent confirmatory holdout; this result may not be converted to a pass by relaxing the no-candidate condition.
