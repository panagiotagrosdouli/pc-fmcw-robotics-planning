# Part B Execution Status

## Current status: final-v1 executed, but NOT manuscript-confirmatory

GitHub Actions run `34709571593` completed all five 10-seed shards (seeds 1000–1049), the 50-seed aggregate job, and the 20-seed directional-vs-distance-only optical-geometry mechanism ablation. The artifacts are reproducible and scientifically useful, but `part-b-final-v1` must **not** be presented as a passed autonomous-motion confirmatory experiment.

Two post-run audit findings prevent that interpretation.

## 1. Frozen endpoint capture mismatch

`configs/experiments/part_b_final.yaml` predeclared five primary communication endpoints: `mean_outage_probability`, `mean_snr_db`, `min_snr_db`, `mean_ber_model`, and `mean_goodput_bps_model`.

The executed benchmark episode writer did not record `min_snr_db`. An interim analyzer substituted `path_length_m` for the missing endpoint. That substitution is invalid because path length is a robotics metric and was not part of the frozen five-endpoint communication multiplicity family. The code has now been corrected so future executions record `min_snr_db`, and the seed-level analyzer again matches the frozen protocol exactly. The already-produced final-v1 artifact remains an audited exploratory artifact: its four captured communication endpoints can be reported descriptively, but the substituted five-endpoint family is not final confirmatory evidence.

## 2. Safety gate failed

The aggregate diagnostics show collision rate 1.0 for every planner in `following_lateral_offset` and `overtake`, yielding overall collision rate 0.4 for every planner. This is a failure of the intended robotics safety gate. The failure is shared across P0–P4 and therefore does not explain the relative communication effect, but it prevents claims of safe autonomous motion under the current benchmark configuration.

Several scenarios also contain substantial zero-feasible-candidate periods. Per the frozen protocol, no-candidate counts remain diagnostics rather than confirmatory communication endpoints; nevertheless, they show that the present dynamic-safety formulation/scenario combination requires remediation before the robotics system can be described as safely validated.

## Evidence that remains useful from final-v1

With 50 independent simulation seeds and repeated scenarios averaged within each seed, the captured model-based communication outcomes strongly favor P2 over P1:

| Endpoint | Mean P2−P1 effect | Bootstrap 95% CI |
|---|---:|---:|
| Mean outage probability | -0.01738 | [-0.01860, -0.01617] |
| Mean SNR | +1.596 dB | [+1.479, +1.713] |
| Modeled BER | -0.00834 | [-0.00888, -0.00779] |
| Modeled goodput | +8.337 Mbit/s | [+7.793, +8.883] |

These are **controlled model-based communication effects**. They are not measured optical performance and, because the safety gate failed, they are not evidence of successful safe autonomous driving.

The final-v1 artifact also shows smaller modeled communication changes for P3 versus P2 and the expected oracle-connectivity comparison P4 versus P2. Those effects remain secondary until the robotics benchmark is repaired and re-frozen.

## Optical-geometry mechanism ablation

The separate 20-seed mechanism ablation completed successfully. For P2−P1 under the directional model, the mean effects were approximately -0.01657 outage, +1.544 dB SNR, -0.00825 modeled BER, and +8.254 Mbit/s modeled goodput.

Under the distance-only variant, the same P2−P1 benefit disappears: outage changes by only about +2.9e-5, SNR changes by -0.310 dB, modeled BER is effectively unchanged, and modeled goodput change is zero. The directional-minus-distance-only interaction is approximately -0.01660 outage, +1.854 dB SNR, -0.00825 BER, and +8.254 Mbit/s goodput, with the bootstrap intervals for these interaction endpoints excluding zero.

This supports the narrow mechanism statement that the simulated P2 advantage is tied to the **modeled directional geometry term** rather than generic distance-only planning. It is not physical optical validation.

## Required remediation before a new confirmatory run

1. Preserve the corrected `min_snr_db` endpoint capture and exact frozen communication metric family.
2. Preserve final-v1 as a failed safety-gate run; never overwrite or relabel it as successful.
3. Diagnose why shared dynamic-safety filtering permits realized collisions in `following_lateral_offset` and `overtake` under prediction error.
4. Introduce a scientifically motivated prediction-error-aware safety treatment, evaluate/tune it only in a separate development seed set, then freeze it.
5. Add an executable CI gate that fails a confirmatory run if any final confirmatory episode has `collision_indicator != 0`.
6. Use a fresh confirmatory seed range after safety remediation, rather than reusing seeds 1000–1049 for post-tuning confirmation.

## Claim boundary

Until a remediated run passes the safety gate, Paper 1 may report the final-v1 communication effect as exploratory/model-based evidence and may report the directional-geometry mechanism ablation with its explicit simulation boundary. It must not claim a successful safety-constrained autonomous-motion validation from final-v1.
