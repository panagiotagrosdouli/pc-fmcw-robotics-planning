# V5 Emergency Receding-Horizon Safety Design

## Motivation

Canonical V4 development run `34784793373` failed the predeclared safety gate with 23 collision episodes and 100 episodes containing at least one unresolved no-candidate event. The V4 fallback still evaluates a long-horizon emergency envelope; this can remain infeasible even when an immediately safe control action exists.

## Frozen design principle

V5 must not relax physical safety constraints and must not use communication information in emergency recovery.

When the normal long-horizon candidate lattice is empty, generate a short one-control-interval emergency envelope containing maximum braking with bounded left/straight/right steering actions. Recede and replan at the next simulation step.

Every emergency action must independently satisfy:

- road bounds;
- speed bounds;
- static-obstacle clearance;
- time-aligned predicted-target clearance.

If no one-step action satisfies these hard constraints, the state is genuinely unsafe/unsatisfiable and must remain a safety failure rather than being hidden by a fabricated candidate.

## Development protocol

Use fresh development seeds only. Do not inspect or tune on reserved confirmatory seeds.

The V5 development gate remains:

- zero collision episodes;
- zero episodes with `no_candidate_steps > 0`.

Only after the development gate passes may a new, completely fresh confirmatory seed block be released.

## Scientific boundary

The emergency fallback is a structural control-safety mechanism. It is identical for P0--P4 and contains no connectivity objective, measured optical link, or planner-specific communication signal. V5 results therefore cannot be interpreted as optical physical validation.
