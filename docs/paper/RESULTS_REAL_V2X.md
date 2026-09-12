# Results — field-measured V2X validation

## Dataset and protocol
The measured-data study downloaded 38 public CICV5G run files containing 43,045 synchronized V2N2V observations. The primary whole-run split contained 22,441 training, 8,846 calibration and 11,758 held-out test samples. Runs rather than individual timestamps were assigned to splits to avoid temporal/route leakage.

The 50 ms delay threshold used in the replay study is an experimental operating point and is not presented as a universal V2X requirement.

## One-step prediction: persistence is the baseline to beat
On the primary held-out split, current-value persistence achieved a delay MAE of 5.576 ms. Generic learned alternatives were worse: spatial KNN 10.862 ms, Extra Trees 6.659 ms and Random Forest 7.150 ms. At the run level, the Extra-Trees-minus-persistence MAE difference was +1.532 ms (95% bootstrap CI 0.049 to 3.525 ms; paired Wilcoxon raw p=0.129), Random-Forest-minus-persistence +1.869 ms (0.458 to 3.532 ms; raw p=0.039), and spatial-KNN-minus-persistence +5.067 ms (3.974 to 6.310 ms; raw p=0.0039).

The one-step SINR result was even more persistence-dominated: persistence MAE was approximately 0.028 dB, whereas spatial models had substantially larger errors. Consequently, the study rejects the simplistic claim that a generic spatial/ensemble predictor is superior to reactive QoS information.

## Measurement support is predictive of reliability
Prediction reliability deteriorated as held-out samples moved farther from the training measurements. For the primary split, delay MAE was approximately 5.33 ms for held-out points within 1 m of training support, 7.12 ms for the 1–5 m stratum and 9.58 ms in the 5–15 m stratum. Marginal interval coverage simultaneously decreased from approximately 0.888 to 0.864 and then 0.761.

This result motivates treating empirical support as an observable validity variable rather than assuming a learned QoS map is equally trustworthy throughout the candidate state space.

## Uncertainty under grouped distribution shift
A nominal 90% split-conformal residual interval achieved 0.884 coverage on the primary test split. Across five grouped split seeds, mean global coverage varied around the mid-0.8 range rather than remaining at 0.9. This is reported as a limitation, not as successful universal calibration. The result is consistent with the fact that ordinary split-conformal guarantees depend on exchangeability and need not survive domain/distribution shift.

## Planning-horizon study
Prediction value was strongly horizon-dependent. The causal context-adaptive fusion selected persistence/spatial weights using calibration runs only and defaulted to persistence for unsupported contexts.

Across five grouped split seeds, the mean fusion-minus-persistence delay-MAE differences were:

| Horizon | Median physical horizon | Mean ΔMAE (fusion − persistence) | Fraction of split seeds improved |
|---:|---:|---:|---:|
| 1 step | 55 ms | -0.042 ms | 0.8 |
| 5 steps | 276 ms | -0.286 ms | 0.8 |
| 10 steps | 552 ms | -0.720 ms | 0.8 |
| 20 steps | 1.106 s | -1.460 ms | 1.0 |
| 50 steps | 2.766 s | -2.506 ms | 1.0 |
| 100 steps | 5.534 s | -2.622 ms | 1.0 |

Thus, learned spatial/context information is not a universal substitute for persistence, but it has consistent incremental value at the longer planning horizons tested here.

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

P3 did not improve QoS over P2: P3-P2 measured-delay difference was +0.073 ms (raw p=0.742) and the threshold-violation difference was +0.00034 (raw p=0.50). P3 reduced the unsupported-selection fraction by 0.01836 relative to P2 (95% CI -0.03214 to -0.00603; raw p=0.0313), at additional mobility deviation of 0.01052 (raw p=0.0078).

### Multiplicity correction

The replay analyzer now reports Holm-adjusted p-values across the complete declared family of P2-P1, P3-P2 and P3-P1 comparisons over the four replay endpoints. Under this conservative 12-test family, the primary-split raw p-values above must **not** be described as multiplicity-corrected confirmatory significance. The raw P2-P1 measured-delay result and the raw P3-P2 unsupported-exposure result are therefore treated as effect-size evidence from one grouped split until the multi-split replay analysis is complete.

This correction is intentional. The paper should not promote a result to confirmatory status simply because one grouped split yields raw p<0.05.

### Grouped multi-split replay

The repository now reruns the route-constrained replay over grouped split seeds 0–4 and aggregates **within-split run-level planner effects first, then split-level effects**. This is the preferred robustness analysis because it tests whether the direction and magnitude of the planner effect survive changes in which complete drives are assigned to train, calibration and test.

Until that artifact is completed and inspected, the primary-split replay supports the following descriptive interpretation only:

- P2 shows a modest lower-delay direction relative to P1 at a small mobility cost;
- P3 does not show a communication-QoS advantage over P2;
- P3 selects empirically unsupported states less often than P2 in the primary split;
- effect consistency across grouped splits determines whether these become paper-level robust conclusions.

## Computational behavior
The first unvectorized replay implementation required about 8.63 ms mean decision computation (p95 about 8.85 ms) on a hosted CI runner. That timing motivated a vectorized batched predictor/support implementation. Final timing should be taken from the validated vectorized workflow artifact. In either case, hosted-CI timing is implementation evidence only and is not a certified embedded real-time guarantee.

## Negative results retained
The following negative results are part of the contribution rather than omitted:

- generic one-step ML models do not beat persistence on this dataset;
- nominal conformal coverage is not stable across grouped distribution shifts;
- P3 does not improve QoS relative to P2 under the primary replay configuration;
- arbitrary off-route counterfactual validation is not scientifically supported by the available measurements;
- raw single-split p-values are not promoted to confirmatory claims after a broader multiplicity family is declared.
