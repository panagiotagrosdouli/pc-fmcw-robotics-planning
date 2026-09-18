# Paper 1 V4 safety remediation and execution status

## Trigger and historical boundary

The complete V3 development sweep failed for every predeclared margin (see [`PART_B_V3_EXECUTION_STATUS.md`](PART_B_V3_EXECUTION_STATUS.md)). V3 has no frozen margin or confirmatory communication claim. Historical V1/V2/V3 workflows are now manual reproduction only, so changes to planner source cannot automatically restart invalidated experiments.

## Deterministic failure diagnosis before V4 seeds

The `lane_choice` scenario starts the ego vehicle at 10 m/s with a static obstacle centered at x=15 m, radius 1 m, and a required additional static clearance of 1.5 m. Straight maximum braking at the existing -4 m/s² under the repository's 0.1 s discrete dynamics stops at x=13.0 m, leaving **1.0 m obstacle-surface clearance**, below the **1.5 m** hard bound. A straight emergency stop is therefore not a valid witness at the initial state. This does not establish that *every* bounded maneuver is impossible.

Before V4 seed runs, a deterministic control-space feasibility check identified an admissible path using maximum braking with a 0.5 s early steering pulse capped by the existing 3 m/s² lateral-acceleration parameter. The old zero-initial-steering quintic emergency family did not cover this short pulse. A receding-horizon planner also needs one- through four-step continuations after the first steering action; one fixed five-step pulse loses feasibility on the following step.

The old benchmark counted target-center collisions but did not include static-obstacle radius in its reported `min_static_obstacle_clearance_m`; when the candidate set emptied it applied zero acceleration, allowing coasting. V4 adds an explicitly labeled *static-envelope* violation metric (center-to-surface clearance under 1.5 m) and bounded fallback braking. No-candidate episodes remain a hard failure even if fallback avoids a violation. The new diagnostic does **not** establish physical vehicle-body collision rates because the simulation lacks an ego footprint model.

## Frozen V4 intervention

- Common to P0–P4: maximum braking plus symmetric steering pulses of one through five 0.1 s steps; every V4 nominal and emergency control is capped by the nominal 3 m/s² lateral-acceleration bound.
- Common static viability filter: every candidate endpoint must permit straight maximum braking with road and obstacle clearance. This is only a necessary static continuation check, not a proof of safety against uncertain moving targets.
- Missing candidate: maximal bounded straight braking, still counted and still disqualifying.
- Physical target collision distance remains 2.0 m. Static center-to-surface clearance remains 1.5 m. Forecast, candidates, and hard filters are identical for P0–P4; P4 retains oracle information only for connectivity scoring.
- The intervention is behind `--v4-static-viability`, preserving the historical candidate lattice when the flag is absent.

The frozen machine-readable protocol is [`part_b_final_v4.yaml`](../configs/experiments/part_b_final_v4.yaml). Development seeds are **9000–9019**, margins **0, 0.5, 1, 1.5, 2, 2.5, 3 m**, and the selector requires zero target-collision episodes, zero no-candidate episodes, and zero static-envelope-violation episodes for every planner and scenario. The smallest passing margin is selected. The selector validates the complete 500-row paired grid for each margin. Development communication values are not confirmatory evidence.

Only after a passing development result may the untouched V4 confirmatory seeds **10000–10049** run. The mechanism set is **11000–11019** using the same selected margin. V3 confirmatory seeds **7000–7049** remain unused.

## Status

The full V4 development sweep has been launched locally. Do not infer a pass from a one-seed diagnostic. The margin-selection output will be added here after the complete sweep. No V4 confirmatory communication inference is authorized until the selector returns a passing margin and the subsequent 50-seed hard safety gate passes.
