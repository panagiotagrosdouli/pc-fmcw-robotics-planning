# Part B V3 Execution Status

## Why V3 exists

The V2 development-only safety run (GitHub Actions run `34713826587`, seeds 3000–3019) failed the predeclared hard gate. The failure is retained as evidence rather than relabeled.

V2 development summary:

- `following_lateral_offset`: zero collisions for all P0–P4, but mean 1.50 no-candidate steps and maximum 4 for every planner.
- `intersection_turn`: zero collisions and zero no-candidate steps for all planners.
- `lane_choice`: zero collisions, but exactly 25 no-candidate steps for every planner; diagnostics identify static-obstacle rejection as the exhaustion stage.
- `occluding_cut_in`: zero collisions and zero no-candidate steps for all planners.
- `overtake`: P0/P3/P4 zero collisions; P1 collision rate 1.00 with mean 1.15 no-candidate steps (max 7); P2 collision rate 0.05; P3/P4 pass.

The V2 safety artifact was uploaded with SHA-256:

`4af3c8ad819271e655734d25afea5067650150541fafdce8bc2e7224e1491396`

Because the development gate failed, fresh V2 confirmatory seeds 4000–4049 and geometry seeds 5000–5019 were automatically skipped. No V2 communication result is accepted as fresh confirmatory evidence.

## Failure diagnosis

Two distinct failure mechanisms were identified.

1. **Static-envelope exhaustion in `lane_choice`.** The straight maximum-braking candidate introduced for V2 stops close enough to the static obstacle that the radius-plus-clearance constraint still rejects it. The physical braking limit must not be increased merely to pass the scenario. V3 instead adds maximum-braking trajectories across the already-declared lateral offsets, allowing physically bounded braking plus lateral evasion.
2. **Prediction-error safety risk in `overtake`.** P1/P2 can satisfy the hard filter against the constant-velocity mean prediction while violating the 2.0 m realized collision definition. V3 therefore separates the physical collision threshold from a planning-only predicted-target clearance margin.

## V3 anti-overfitting design

V3 does not continue tuning on seeds 3000–3019.

- Development-only seeds: **6000–6019**.
- Candidate planning margins: **0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 m**.
- Frozen selection rule: choose the **minimum** margin with zero collision episodes and zero episodes containing no-candidate steps across every scenario/planner. If no margin passes, confirmation remains blocked.
- Physical collision distance remains **2.0 m**; the selected margin changes only the predicted-target planning clearance.
- Emergency candidate family: maximum physical braking combined with every predeclared lateral offset; identical for P0–P4 and communication-agnostic.

If the development rule passes:

- Fresh confirmatory seeds: **7000–7049**.
- Fresh directional-vs-distance-only mechanism seeds: **8000–8019**.
- Exact communication endpoint family remains: `mean_outage_probability`, `mean_snr_db`, `min_snr_db`, `mean_ber_model`, `mean_goodput_bps_model`.
- Seed remains the independent inferential unit after averaging repeated scenario conditions.
- Bootstrap confidence intervals, paired Wilcoxon tests, and Holm correction remain required.
- Confirmatory communication inference is accepted only after zero collisions and zero no-candidate episodes across the full fresh run.

## V3 development result (seeds 6000–6019)

The complete predeclared margin sweep was executed from the repository `main` branch on 2026-09-18. Each margin contains 500 episode rows: 20 seeds × 5 scenarios × 5 planners. The exact development seed set was verified before aggregation. Communication columns in these development artifacts were not inspected for inferential claims.

| Planning margin (m) | Collision episodes | Episodes with no-candidate steps | Minimum realized target separation (m) | Gate |
|---:|---:|---:|---:|:---|
| 0.0 | 24 | 153 | 1.165642 | FAIL |
| 0.5 | 3 | 155 | 1.798903 | FAIL |
| 1.0 | 0 | 138 | 2.368143 | FAIL |
| 1.5 | 0 | 139 | 2.507269 | FAIL |
| 2.0 | 5 | 260 | 1.624154 | FAIL |
| 2.5 | 0 | 300 | 2.352042 | FAIL |
| 3.0 | 0 | 300 | 2.830477 | FAIL |

The machine-readable aggregate is stored in [`research/PART_B_V3_DEVELOPMENT_MARGIN_SUMMARY.csv`](research/PART_B_V3_DEVELOPMENT_MARGIN_SUMMARY.csv).

### Failure mechanisms

- `lane_choice` produced no-candidate steps in all 20 seeds for every planner at every tested margin. Its realized target separation remained large (minimum approximately 8.97–9.02 m across planners), which is consistent with candidate exhaustion driven by the static-obstacle envelope rather than a realized target collision.
- `following_lateral_offset` produced no-candidate episodes for every planner at every margin. The count per planner was 8, 10, 7, 7, 15, 20, and 20 as the margin increased from 0.0 to 3.0 m. At margin 2.0, one episode collided for each planner; this non-monotonic outcome is retained.
- `overtake` dominated the low-margin collision failures: at margin 0.0, P1 collided in all 20 seeds and P0/P2/P3/P4 collided once each. At margin 0.5, P1 collided three times. At margins 1.0 and 1.5 collisions were eliminated, but P1 still had no-candidate episodes (3 and 4, respectively). At margins 2.0–3.0, candidate exhaustion expanded across planners.
- `intersection_turn` and `occluding_cut_in` did not appear in the failure set for any tested margin.

The non-monotonic collision counts do not alter the predeclared rule: a margin must satisfy both hard conditions, and none did.

## Protocol consequence

No safety margin was selected or frozen. Therefore:

- V3 confirmatory seeds `7000–7049` were not run;
- no V3 P2-vs-P1, P3-vs-P2, or P4-vs-P2 communication inference was performed;
- geometry-mechanism seeds `8000–8019` were not run because the protocol requires a frozen V3 margin;
- physical-parameter sensitivity was not used to search for a favorable regime;
- the negative safety result is retained as the V3 research outcome.

Paper 1 remains scientifically gated. Any V4 safety change requires a new, explicitly versioned development protocol and fresh seed ranges; it must not reuse `7000–7049` for tuning.
