# Part B Execution Status

## Current status: V1 audited; V2 safety-remediation protocol launched

GitHub Actions run `34709571593` completed all five V1 shards (seeds 1000–1049), aggregation, seed-level analysis, diagnostics, and the directional-vs-distance-only mechanism ablation. V1 remains permanently classified as exploratory/diagnostic because (i) `min_snr_db` was not captured by the executed episode schema and (ii) the intended robotics safety gate failed in two scenario families.

The repository now contains a remediation that is deliberately separated from the V1 confirmatory data.

## V1 evidence retained

The captured 50-seed model-based communication outcomes strongly favor P2 over P1: mean outage effect about -0.01738, mean SNR +1.596 dB, modeled BER -0.00834, and modeled goodput +8.337 Mbit/s. These are controlled simulation effects only. V1 cannot support a safe-autonomous-motion claim.

The 20-seed mechanism ablation also showed that the P2-P1 effect is concentrated in the modeled directional geometry term rather than the distance-only variant. This is a mechanism result inside the analytical simulator, not physical optical validation.

## Root-cause finding and remediation

The nominal candidate lattice previously allowed only speed offsets `(-2, 0, +2) m/s`. In closing/following scenarios that can be insufficient to represent physically available emergency deceleration, so the hard dynamic-target filter can exhaust the lattice and the receding-horizon controller can continue into a realized collision.

The candidate generator now appends straight-line maximum-braking trajectories at every planning horizon. This is a shared safety-envelope action available identically to P0-P4; it is not communication-specific and therefore does not preferentially encode the desired P2 result. Existing road, static-obstacle, speed, and dynamic-target hard filters still decide whether each braking trajectory is feasible.

## Anti-overfitting execution design

The remediation is tested first on development-only seeds `3000..3019`. These seeds may be used to accept or reject the safety-envelope change, but their communication outcomes are not confirmatory evidence.

Only if the development safety gate passes does CI unlock a fresh V2 confirmatory range `4000..4049`. V2 therefore does not reuse V1 seeds after observing V1 failures. The directional mechanism ablation is also rerun on a fresh range `5000..5019` after the development gate.

## V2 hard gates

Before confirmatory communication inference is accepted, CI requires:

- zero collision episodes across every scenario and planner;
- zero episodes containing a no-candidate step;
- exact capture of all five predeclared communication endpoints, including `min_snr_db`;
- exactly 50 fresh confirmatory seeds, 4000 through 4049;
- seed-level inference after averaging repeated scenario effects within each independent seed;
- Holm correction within each planner comparison across the five communication endpoints.

If the development safety study fails, the V2 confirmatory shards are skipped. If the fresh confirmatory safety gate fails, the statistical analysis is not accepted as confirmatory robotics evidence.

## Claim boundary

Until V2 passes all gates, Paper 1 may report V1 only as exploratory/model-based communication evidence and may report the directional-geometry mechanism result with its explicit simulation boundary. No measured optical-performance claim or real-world autonomous-driving validation is supported.
