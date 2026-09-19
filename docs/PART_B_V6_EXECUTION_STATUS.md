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

Protocol and implementation are frozen after 182 passing tests. No V6 seed has been used. The development workflow may start only from the committed V6 branch state.
