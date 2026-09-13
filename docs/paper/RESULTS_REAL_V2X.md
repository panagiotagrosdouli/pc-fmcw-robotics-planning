# Results — field-measured V2X planning

## Dataset and protocol
The measured-data study uses 38 public CICV5G run files containing 43,045 synchronized V2N2V observations. Runs rather than individual timestamps are assigned to train/calibration/test partitions so that temporally and spatially adjacent samples from the same drive do not cross the primary split boundary.

The 50 ms delay threshold used in replay is an experimental operating point, not a universal V2X requirement.

## One-step prediction: persistence is the baseline to beat
On the audited primary grouped split, current-value persistence achieves delay MAE of approximately **7.419 ms** (RMSE approximately 11.365 ms). The tested learned alternatives are worse at one step:

| Predictor | Delay MAE |
|---|---:|
| Persistence/current QoS | **7.419 ms** |
| Conditioned spatial kNN | 12.344 ms |
| Random Forest | 9.291 ms |
| ExtraTrees | 8.950 ms |

The study therefore rejects the simplistic claim that a generic learned spatial/tree model is superior to reactive QoS information at the immediate next sample. This negative result motivates horizon-dependent evaluation rather than post-hoc model replacement.

## Measurement support and context
Primary support-stratified delay error and empirical interval coverage are approximately:

| Nearest training support | Delay MAE | Empirical coverage |
|---|---:|---:|
| <=1 m | 6.98 ms | 0.888 |
| 1–5 m | 8.51 ms | 0.841 |
| 5–15 m | 10.47 ms | 0.761 |

The aggregate trend indicates greater reliability risk in weakly supported regions, but a deeper audit shows that the relationship is **context-dependent rather than universally monotone within every drive**. Severe degradation is concentrated particularly in some `n8` contexts/segments. Empirical support is therefore treated as a reliability/validity diagnostic, not as a universal scalar law mapping distance to error.

## Uncertainty under grouped distribution shift
Residual split-conformal intervals are evaluated through empirical held-out coverage. Nominal 90% coverage is not maintained uniformly after whole-drive/grouped distribution shift, and coverage deteriorates in lower-support strata in the primary analysis. The results are therefore not described as calibrated event probabilities.

## Planning-horizon study
Prediction value is strongly horizon dependent. A causal horizon-adaptive fusion of persistence and spatial/context information chooses its weights using calibration data only.

Across five grouped split assignments, all five improve over persistence at the longer tested horizons:

| Horizon | Approximate physical horizon | Mean improvement in delay MAE vs persistence | Split assignments improved |
|---:|---:|---:|---:|
| 20 steps | ~1.1 s | ~1.463 ms | 5/5 |
| 50 steps | ~2.8 s | ~2.510 ms | 5/5 |
| 100 steps | ~5.5 s | ~2.621 ms | 5/5 |

At 1/5/10 steps, gains are smaller and not consistently present. Thus learned spatial/context information is not a universal substitute for persistence, but it becomes decision-relevant at sufficiently long tested planning horizons.

The five assignments reuse the same finite collection of 38 drives. They are reported as descriptive partition-sensitivity evidence, not as five independent statistical replications.

## Route-constrained measured replay
To avoid fabricating QoS ground truth at arbitrary unvisited coordinates, the decision-value study restricts candidate future states to states actually traversed later on the same held-out measured route. Future measured delay is hidden from P0–P3 and is revealed only after the candidate is selected for outcome evaluation.

Across the primary nine-run held-out replay:

| Planner | Mean measured delay | >50 ms fraction | Changed from nominal | Unsupported selected | Mobility deviation |
|---|---:|---:|---:|---:|---:|
| P0 | ~11.7659 ms | ~0.01657 | 0 | ~0.10834 | 0 |
| P1 | ~11.7659 ms | ~0.01657 | 0 | ~0.10834 | 0 |
| P2 | ~10.9737 ms | ~0.01378 | ~0.12043 | ~0.10561 | ~0.06022 |
| P3 | ~11.0468 ms | ~0.01412 | ~0.13750 | ~0.08725 | ~0.07074 |

P0 and P1 select the same candidates in this replay because current QoS is common to all candidate horizons at a decision instant and therefore does not distinguish the future alternatives. This is a property of the reactive baseline formulation, not access to hidden future measurements.

P2 versus P1 changes mean measured delay by approximately **-0.792 ms** at run level. The paired-bootstrap 95% interval is approximately **[-1.723, -0.138] ms**, and the raw paired Wilcoxon p-value is **0.046875**. The >50 ms violation-fraction effect is approximately **-0.00279**, with raw p=0.0625.

P3 does not improve QoS over P2 on the primary split: the P3-P2 measured-delay difference is approximately **+0.073 ms**, and the violation-fraction effect is approximately +0.00034. P3 instead reduces unsupported-selection exposure by approximately **-0.01836 absolute** relative to P2 while incurring additional mobility deviation of approximately +0.01052.

### Multiplicity correction
The replay analyzer defines one 12-test family: P2-P1, P3-P2, and P3-P1 across four replay endpoints. Holm correction is applied to the complete declared family.

Two raw p-values that could otherwise be overinterpreted do **not** survive multiplicity correction:

- P2-P1 measured delay: raw p=0.046875 -> Holm-adjusted p approximately **0.28125**;
- P3-P2 unsupported exposure: raw p=0.03125 -> Holm-adjusted p approximately **0.25**.

Neither is therefore presented as multiplicity-corrected confirmatory significance. Effect estimates, paired intervals, and directional robustness remain scientifically informative, but raw p<0.05 from one grouped split is not promoted to a confirmatory claim.

## Grouped multi-split replay sensitivity
The route-constrained replay is repeated under five grouped split assignments. The same 38 drives are recycled across assignments, so no inferential test treats these five assignments as independent n=5 observations.

P2-P1 measured-delay effects are approximately:

| Split assignment | P2 − P1 mean measured delay |
|---:|---:|
| 0 | -0.791924 ms |
| 1 | -1.253015 ms |
| 2 | -0.069188 ms |
| 3 | -0.262972 ms |
| 4 | -0.129775 ms |

All 5/5 are negative. The descriptive mean is approximately **-0.501375 ms**, median approximately **-0.262972 ms**, with range **[-1.253015, -0.069188] ms**.

The >50 ms violation-fraction effect is also negative in all 5/5 assignments:

`-0.002791, -0.004533, -0.000548, -0.001154, -0.002171`,

with descriptive mean approximately **-0.002239 absolute**.

For P3 versus P2, measured-delay effects are heterogeneous:

`+0.072572, +0.015114, +0.143389, -0.031090, -0.228812 ms`,

with mean approximately **-0.005765 ms**. This does not support stable additional QoS benefit for P3.

By contrast, P3-P2 unsupported-selection effects are negative in all 5/5 assignments:

`-0.018361, -0.015286, -0.019048, -0.056201, -0.030872`,

with descriptive mean approximately **-0.027954**.

The evidence-backed interpretation is therefore:

```text
P2 -> predictive communication utility
P3 -> empirical-support / inference-validity control
```

P3's support benefit comes with additional mobility deviation and should not be sold as QoS superiority.

## Computational behavior
The vectorized replay implementation processes batched QoS/support candidate queries at approximately **81–96 microseconds per candidate** across the completed grouped split runs on hosted GitHub Actions hardware. Candidate scoring is roughly **9.8–10.9 microseconds mean** in the observed runs, with rare timing outliers.

These are implementation-level software timing measurements, not an end-to-end embedded or real-vehicle real-time guarantee.

## Negative results retained
The following negative results are part of the contribution rather than omitted:

- generic one-step learned spatial/tree predictors do not beat persistence on the audited primary split;
- nominal conformal coverage is not stable under all grouped shifts;
- P3 has no stable measured-QoS advantage over P2;
- support distance alone is not a universal monotone error predictor within every drive/context;
- arbitrary off-route counterfactual validation is not scientifically supported by the available measurements;
- raw single-split p-values are not promoted after Holm multiplicity correction;
- repeated split assignments are not misrepresented as independent experimental units.
