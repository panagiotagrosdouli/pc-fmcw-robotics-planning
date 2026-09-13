# Paper 1 Claim-Evidence Matrix

| Claim | Evidence | Statistical support | Boundary | Status |
|---|---|---|---|---|
| V1 P2 improves modeled communication vs P1 | 50-seed V1 artifacts | Strong paired effects, but V1 invalidated for confirmatory robotics | Model-based; safety failed; endpoint mismatch | EXPLORATORY |
| Historical directional geometry drives the P2-P1 mechanism | 20-seed directional vs distance-only V1-era ablation | Strong paired interaction in simulator | Must be rerun after V3 trajectory/safety changes | EXPLORATORY / SUPPORTED MECHANISM |
| V1 demonstrates safe autonomous planning | Collision rate 0.4 overall; failures in following/overtake | Fails safety gate | -- | DO NOT CLAIM |
| V2 safety remediation succeeded | Seeds 3000-3019 development artifact | Gate failed: lane-choice no-candidate; overtake P1/P2 collisions | V2 confirmatory seeds were skipped | NOT SUPPORTED |
| V2 provides confirmatory communication evidence | None: fresh 4000-4049 jobs were quarantined/skipped | None | Failed development gate | DO NOT CLAIM |
| V3 provides confirmatory communication evidence | Fresh protocol: development 6000-6019; confirmation 7000-7049 | Pending minimum-passing-margin selector and hard safety gate | Must remain unchanged after development selection | PENDING |
| PC-FMCW link model is measured/calibrated | No hardware optical calibration in repository | None | Analytical surrogate | DO NOT CLAIM |
| 193.4 THz proves visible-blue behavior | Source parameter corresponds near 1550 nm and terminology is inconsistent | None | Provenance ambiguity | DO NOT CLAIM |

## Submission rule

Paper 1 is not final until the V3 development selector passes, the selected safety formulation is frozen, fresh seeds 7000–7049 pass the zero-collision/zero-no-candidate gate, all five communication endpoints undergo seed-level multiplicity-corrected inference, and fresh geometry seeds 8000–8019 complete. Historical V1 communication results may remain only when explicitly labeled exploratory/model-based. Failed V2 development evidence must remain visible as a negative safety result.
