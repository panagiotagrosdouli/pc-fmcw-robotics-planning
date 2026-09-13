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

## Current status

The V3 protocol is implemented in `.github/workflows/part_b_v3.yml` and `configs/experiments/part_b_final_v3.yaml` on branch `research/safety-remediation-v3` / PR #12. Development communication outcomes are not manuscript evidence. Paper 1 remains scientifically gated until the V3 development selector and fresh confirmatory hard gate complete.
