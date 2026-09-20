# Paper 1 V6 hierarchical-clearance protocol

## Boundary

V5 completed its full development sweep and failed the joint gate because four episodes at the best tested margin (1.0 m) contained no candidate. V5 confirmatory and geometry seeds were not run. The complete negative result is archived under `results_archive/part_b_v5_development/`.

V5 development rows are used only for failure diagnosis. V6 freezes fresh development seeds 15000–15019, confirmatory seeds 16000–16049, and geometry seeds 17000–17019 before any V6 execution. These ranges are disjoint from V3–V5 development and unused confirmatory ranges.

## Development-only diagnosis

All four V5 failures occurred in `following_lateral_offset`: P0 and P1 at seeds 12009 and 12016, steps 38–40. Static feasibility remained nonempty. At seed 12009, the best dynamically predicted emergency candidates had minimum separations 2.930–2.973 m: above the unchanged physical collision distance of 2.0 m but slightly below the buffered threshold of 3.0 m. The implementation therefore classified loss of the optional planning buffer as complete physical infeasibility.

## Frozen V6 intervention

V6 separates two meanings that V5 combined:

- **Physical filter:** a candidate must satisfy the unchanged 2.0 m predicted target clearance, road, speed, static obstacle, terminal static-stop, and predicted dynamic-stop checks. If no such candidate exists, the planner returns no candidate and the episode fails the gate.
- **Planning buffer:** candidates satisfying `2.0 m + planning_safety_margin_m` are preferred. Only when this preferred set is empty may the planner use a candidate that still passes the complete physical filter. Every such step is recorded as `margin_relaxation_steps` and reported by episode, planner, and scenario.

The hierarchy is common to P0–P4 and changes only candidate admissibility order, not communication scoring. The V4 bounded controls and static viability and all V5 time-alignment, forecast, and dynamic-stop rules remain unchanged. No oracle target truth enters P0–P3 safety, and P4 uses the same mean safety prediction.

Historical V5 seed 12009 changes from three no-candidate steps to three explicit buffer-relaxation steps, with zero realized collision. This is a development diagnostic, not V6 evidence.

## Frozen gate

[`part_b_final_v6.yaml`](../configs/experiments/part_b_final_v6.yaml) specifies seven margins from 0.0 through 3.0 m. Each margin must contain exactly 500 paired development episodes. The selected margin is the minimum with:

- zero realized target-collision episodes;
- zero physical no-candidate episodes; and
- zero modeled static-envelope violation episodes.

Margin-relaxation frequency is a required descriptive endpoint, not silently treated as full-buffer satisfaction. Communication endpoints cannot select the margin. If no margin passes, V6 stops and the untouched confirmatory and geometry seeds remain unused.

Only after a development pass may the workflow run the 50 confirmatory seeds. Their aggregate must pass the same physical hard gate before communication inference. All conclusions remain limited to the analytical simulator—not measured optical or real-vehicle safety validation.

## Status

The frozen workflow ran from commit `4a1a1a218369f66543eccec05ef5117d3b84bc7a`. All seven 500-episode development artifacts passed structural verification. The predeclared selector chose 0.5 m: zero collision episodes, zero physical no-candidate episodes, zero modeled static-envelope violations, and 14 episodes/27 steps of explicitly recorded buffer relaxation. The complete development evidence is archived under `results_archive/part_b_v6_development/`.

The development pass authorized the disjoint confirmatory and geometry jobs. Across the 1,250 confirmatory rows (50 seeds × five scenarios × five planners), realized collisions and modeled static-envelope violations were zero, but seed 16030 produced one no-candidate step for each of P0, P1, and P3 in `following_lateral_offset`. The aggregate hard gate therefore failed. Communication inference and safety diagnostics were skipped by the workflow; geometry output is not used as evidence. V6 terminates with a confirmatory stop decision and makes no validated safety or communication claim.

The workflow now treats that predeclared scientific rejection as a valid terminal state rather than an infrastructure failure: it writes `safety_gate.json`, reports a successful aggregate CI job, and gates communication inference and geometry on `gate_passes == true`. Schema/cardinality errors, missing endpoints, and non-finite data still fail the job. This preserves the negative result while keeping the PR operational.
