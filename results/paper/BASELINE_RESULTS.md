# Verified 20-seed baseline results

These results are from the controlled model-based PC-FMCW robotics simulation in GitHub Actions Paper Experiments run #3 (commit `eef500666646dd4525e238a0d2f3f27a54ef68f5`). They are **not real-world or measured optical-hardware validation**.

## Planner summary

| Planner | Mean outage | Mean SNR (dB) | BER model | Goodput model (bps) | Progress (m) | Collision rate |
|---|---:|---:|---:|---:|---:|---:|
| P0 mobility-only | 0.061750 | 15.651580 | 0.019946 | 9.800543e8 | 44.694793 | 0.40 |
| P1 reactive connectivity-aware | 0.079767 | 13.984878 | 0.028753 | 9.712470e8 | 44.959847 | 0.40 |
| P2 predictive connectivity-aware | 0.062199 | 15.622639 | 0.020368 | 9.796324e8 | 44.699780 | 0.40 |
| P3 stochastic/risk-sensitive | 0.061545 | 15.688970 | 0.019818 | 9.801821e8 | 44.685380 | 0.40 |
| P4 oracle connectivity reference | 0.061374 | 15.678035 | 0.019793 | 9.802072e8 | 44.685700 | 0.40 |

## Paired statistical conclusions

The main positive result is **P1 vs P2**. Predictive connectivity-aware planning reduces mean outage from `0.07976655` to `0.06219851`, a paired mean change of `-0.01756804` (95% paired-bootstrap CI `[-0.02516075, -0.01066253]`; Holm-corrected Wilcoxon `p=0.000501`). It also increases SNR by about `1.638 dB`, reduces modeled BER by about `0.00839`, and increases modeled goodput by about `8.39 Mbps`; these link improvements remain significant after Holm correction.

For **P2 vs P3**, the numerical link improvements are small and none remain statistically significant after Holm correction. For **P2 vs P4**, the oracle connectivity forecast likewise provides only small numerical improvements and no Holm-significant advantage. **P0 vs P2** is statistically indistinguishable on the tested link metrics after correction in the present baseline.

## Safety interpretation

All five planners have collision rate `0.40` in this benchmark. Therefore these results do **not** support a claim that predictive planning improves collision safety. The defensible conclusion is narrower: relative to the reactive P1 planner, P2 significantly improves the modeled optical-connectivity metrics in this controlled simulation, while no planner-level difference in collision rate is observed.

The common collision rate should be analyzed per scenario before making stronger safety claims; it may reflect difficult/infeasible scenario structure or limitations of the current candidate/safety setup.

## Robustness status

The full robustness experiment was successfully executed as 20 independent one-seed GitHub Actions jobs (seeds 0–19), each producing its own artifact. The seed artifacts must be aggregated before reporting final robustness curves, confidence intervals, or robustness conclusions. No robustness numbers should be quoted from this document until that aggregation is complete.
