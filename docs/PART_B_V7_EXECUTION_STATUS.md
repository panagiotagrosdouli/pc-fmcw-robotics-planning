# Paper 1 V7 endpoint-anchored forecast protocol

## Boundary

V6 selected a 0.5 m planning margin in development but failed its independent confirmatory gate. Seed 16030 produced one no-candidate step for P0, P1, and P3 in `following_lateral_offset`; realized collisions and modeled static-envelope violations remained zero. These V6 rows are used only for diagnosis and never as V7 evidence.

## Frozen diagnosis and intervention

At the failing step, the damped lateral forecast used the least-squares fitted endpoint as its initial lateral position. For the final eight noisy observations this endpoint was approximately 4.6 cm away from the latest observation. That small discontinuity moved the predicted target toward the ego lane and eliminated the entire physical candidate set.

V7 changes exactly one estimator detail: the damped lateral displacement starts from the latest observed lateral position while retaining the same least-squares slope and fixed 0.5 s exponential decay. The correction is shared by P0–P4, uses no future target truth, and does not alter collision distance, candidate generation, margin hierarchy, static viability, dynamic-stop viability, or communication scoring.

As a development-only diagnostic, replaying V6 seed 16030 restores physical candidates for P0, P1, and P3 with zero no-candidate steps and zero collisions. This historical replay is not V7 evidence.

## Frozen V7 gate

V7 uses previously untouched, disjoint ranges:

- development: seeds 18000–18019 across margins 0.0–3.0 m;
- confirmatory: seeds 19000–19049 only after selection;
- geometry: seeds 20000–20019 only after the confirmatory hard gate passes.

The selector and hard gate remain unchanged: zero realized collision episodes, zero no-candidate episodes, and zero modeled static-envelope violations. A valid negative result is recorded as `gate_passes=false`; communication inference and geometry are then skipped without converting the scientific stop decision into an infrastructure failure.

## Status

Protocol frozen before inspection of any V7 seed. Claims remain limited to the analytical simulator and do not constitute optical measurements or real-vehicle safety validation.
