# Results — field-measured V2X validation

## Dataset and protocol
The measured-data study downloaded 38 public CICV5G run files containing 43,045 synchronized V2N2V observations. The primary whole-run split contained 22,441 training, 8,846 calibration and 11,758 held-out test samples. Runs rather than individual timestamps were assigned to splits to avoid temporal/route leakage.

The 50 ms delay threshold used in the replay study is an experimental operating point and is not presented as a universal V2X requirement.

## One-step prediction: persistence is the baseline to beat
On the primary held-out split, current-value persistence achieved a delay MAE of 5.576 ms. Generic learned alternatives were worse: spatial KNN 10.862 ms, Extra Trees 6.659 ms and Random Forest 7.150 ms. At the run level, the Extra-Trees-minus-persistence MAE difference was +1.532 ms (95% bootstrap CI 0.049 to 3.525 ms; paired Wilcoxon raw p=0.129), Random-Forest-minus-persistence +1.869 ms (0.458 to 3.532 ms; raw p=0.039), and spatial-KNN-minus-persistence +5.067 ms (3.974 to 6.310 ms; raw p=0.0039).

The one-step SINR result was even more persistence-dominated: persistence MAE was approximately 0.028 dB, whereas spatial models had substantially larger errors. Consequently, the study rejects the simplistic claim that a generic spatial/ensemble predictor is superior to reactive QoS information.

## Measurement support and context
Aggregate support strata deteriorate as test samples enter sparse regions: on the primary split, delay MAE rises from approximately 5.33 ms within 1 m of training support to 9.58 ms in the 5–15 m stratum, while marginal interval coverage decreases from about 0.888 to 0.761.

A deeper audit shows that this aggregate relationship is not universally monotonic within every drive. The strongest sparse-support failures are concentrated in `n8` contexts, whereas the observed `n78` test runs are substantially easier to predict. Empirical support is therefore treated as a context-conditioned validity diagnostic, not as a universal scalar error law.

## Uncertainty under grouped distribution shift
A nominal 90% split-conformal residual interval achieved 0.884 coverage on the primary test split. Across five grouped split assignments, mean global coverage varied around the mid-0.8 range rather than remaining at 0.9. This is reported as a limitation, not as successful universal calibration. Ordinary split-conformal marginal guarantees should not be assumed to survive arbitrary drive-level distribution shift.

## Planning-horizon study
Prediction value was strongly horizon-dependent. The causal context-adaptive fusion selected persistence/spatial weights using calibration runs only and defaulted to persistence for unsupported contexts.

Across five alternative grouped split assignments, the mean fusion-minus-persistence delay-MAE differences were:

| Horizon | Median physical horizon | Mean ΔMAE (fusion − persistence) | Fraction of split assignments improved |
|---:|---:|---:|---:|
| 1 step | 55 ms | -0.042 ms | 0.8 |
| 5 steps | 276 ms | -0.286 ms | 0.8 |
| 10 steps | 552 ms | -0.720 ms | 0.8 |
| 20 steps | 1.106 s | -1.460 ms | 1.0 |
| 50 steps | 2.766 s | -2.506 ms | 1.0 |
| 100 steps | 5.534 s | -2.622 ms | 1.0 |

Thus, learned spatial/context information is not a universal substitute for persistence, but it has consistent incremental value at the longer planning horizons tested here. Because the alternative splits reuse the same finite set of drives, this is descriptive partition-robustness evidence rather than five independent inferential replications.

## Route-constrained measured replay
To avoid fabricating QoS ground truth at arbitrary unvisited coordinates, the decision-value study restricts candidate choices to measured future states from the same held-out run. Future measured delay is never provided to P0–P3; it is exposed only after a candidate has been selected and is used as the measured outcome.

Across nine held-out runs in the primary split:

| Planner | Mean measured delay | >50 ms fraction | Changed from nominal | Unsupported selected | Mobility deviation |
|---|---:|---:|---:|---:|---:|
| P0 | 23.318 ms | 0.02179 | 0 | 0.15616 | 0 |
| P1 | 23.318 ms | 0.02179 | 0 | 0.15616 | 0 |
| P2 | 22.526 ms | 0.01900 | 0.02508 | 0.15634 | 0.01254 |
| P3 | 22.598 ms | 0.01934 | 0.04611 | 0.13798 | 0.02305 |

P2 versus P1 reduced mean measured delay by 0.792 ms at run level (95% bootstrap CI -1.723 to -0.138 ms; paired Wilcoxon **raw** p=0.0469). Its delay-violation fraction changed by -0.00279 (95% CI -0.00524 to -0.00065; raw p=0.0625). P2 incurred a mean mobility-deviation increase of 0.01254 (raw p=0.0156).

P3 did not improve QoS over P2 on the primary split: P3-P2 measured-delay difference was +0.073 ms (raw p=0.742) and threshold-violation difference +0.00034 (raw p=0.50). P3 reduced unsupported-selection fraction by 0.01836 relative to P2 (95% CI -0.03214 to -0.00603; raw p=0.0313), at additional mobility deviation of 0.01052 (raw p=0.0078).

### Multiplicity correction

The replay analyzer reports Holm-adjusted p-values across the complete declared family of P2-P1, P3-P2 and P3-P1 comparisons over four replay endpoints. The primary-split P2-P1 measured-delay raw p=0.0469 adjusts to approximately **0.281**, while the P3-P2 unsupported-exposure raw p=0.0313 adjusts to **0.250**. Neither is therefore presented as multiplicity-corrected confirmatory significance. The effect estimates and intervals remain informative, but the paper does not equate a raw single-split p<0.05 with a confirmatory result.

### Completed grouped multi-split replay

The route-constrained replay was repeated for grouped split assignments 0–4. Every assignment uses complete train/calibration/test runs, but the same finite collection of 38 drives is recycled across assignments; consequently these are sensitivity analyses rather than independent experimental replicates.

The within-split mean P2-P1 measured-delay effects were:

| Split assignment | P2 − P1 mean measured delay |
|---:|---:|
| 0 | -0.792 ms |
| 1 | -1.253 ms |
| 2 | -0.069 ms |
| 3 | -0.263 ms |
| 4 | -0.130 ms |

All five assignments therefore favor P2 in direction, with a descriptive mean effect of approximately **-0.501 ms** and a range from **-1.253 to -0.069 ms**.

The >50 ms violation-fraction effect also favors P2 in all five assignments: approximately `-0.00279, -0.00453, -0.00055, -0.00115, -0.00217`, for a descriptive mean around **-0.00224 absolute**. This consistency is stronger evidence of direction than the primary split alone, but it is not converted into an artificial n=5 inferential test.

For P3 versus P2, measured-delay effects are heterogeneous (`+0.073, +0.015, +0.143, -0.031, -0.229 ms`), with mean approximately **-0.006 ms**. This confirms that P3 has no stable communication-QoS advantage over P2.

By contrast, P3 reduces unsupported-selection exposure relative to P2 in **all five** split assignments: approximately `-0.0184, -0.0153, -0.0190, -0.0562, -0.0309` absolute, with descriptive mean approximately **-0.0280**. P3 also incurs additional mobility deviation in all five assignments. The robust interpretation is therefore a repeatable **validity-versus-mobility trade-off**, not QoS superiority.

## Computational behavior
The vectorized replay implementation processed approximately 27k–34k candidate queries per split. Batched QoS/support inference required about **81–96 microseconds per candidate** across the completed split assignments on hosted GitHub Actions hardware. The lightweight decision-scoring portion was on the order of **10 microseconds mean per scoring call** in those runs, with rare timing outliers affecting the mean. These measurements demonstrate low software overhead in the benchmark implementation but are not an end-to-end embedded real-time guarantee.

## Negative results retained
The following negative results are part of the contribution rather than omitted:

- generic one-step ML models do not beat persistence on this dataset;
- nominal conformal coverage is not stable across grouped distribution shifts;
- P3 has no stable measured-QoS advantage over P2 across grouped replay assignments;
- support distance alone is not a universal monotonic error predictor within every drive/context;
- arbitrary off-route counterfactual validation is not scientifically supported by the available measurements;
- raw single-split p-values are not promoted to confirmatory claims after a broader multiplicity family is declared;
- repeated data splits are not misrepresented as independent experimental units.
