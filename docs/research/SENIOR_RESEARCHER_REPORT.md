# Senior researcher report — dual-branch evidence audit

## A. Research questions

**Paper 1 — PC-FMCW model-based branch.** Can prediction of future modeled PC-FMCW link quality beneficially influence vehicle motion before a reactive planner responds to degradation?

**Paper 2 — field-measured branch.** When can an autonomous planner trust predicted connectivity from field measurements when evaluating counterfactual future motion?

The generic idea “predict QoS and avoid blackspots” is not a novelty claim. The repository separates a technology-specific PC-FMCW perception-to-action study from a field-measured decision-validity study.

## B. Literature/novelty boundary
Communication-aware motion planning, QoS/radio-map-aware navigation, QoS-aware AV routing, uncertainty-aware robust communication-preserving MPC, optical/FSO trajectory optimization, and optical ISAC trajectory optimization have prior art. Current examples include Gordon et al. (INFOCOM/NetRobiCS 2026) for online radio-map risk planning, Ullah et al. (IEEE Access 2025) for QoS-driven AV route selection, Kim et al. (Sensors 2026) for GP-driven adaptive tube MPC with communication constraints, and Nafees et al. (WCNC 2025) for optical ISAC UAV trajectory optimization over mixed FSO/RF links.

The defensible measured-data differentiation is the combination of whole-drive anti-leakage splitting, strong causal persistence baselines, horizon-dependent prediction, explicit empirical measurement-support auditing, grouped-shift uncertainty diagnostics, and route-constrained outcome replay without fabricated off-route QoS labels. The PC-FMCW contribution is narrower and technology-specific: a model-based sensing/tracking-to-motion bridge with explicit safety and directional-mechanism audits.

## C. Real dataset and protocol
CICV5G is the primary measured dataset. The automated study uses 38 run files / 43,045 synchronized observations. Primary evaluation uses complete-run train/calibration/test splitting rather than random rows. Spatial support is fitted from training coordinates only. Future measured delay is hidden from planners during route replay and revealed only after candidate selection.

The real-data branch is therefore field-measured communication evidence plus offline route-constrained decision replay; it is not closed-loop real-vehicle validation and does not physically validate PC-FMCW optical communication.

## D. One-step prediction: negative result retained
On the primary grouped split:

- persistence delay MAE: about **7.419 ms** (RMSE about 11.365 ms);
- conditioned spatial kNN delay MAE: about **12.344 ms**;
- Random Forest delay MAE: about **9.291 ms**;
- ExtraTrees delay MAE: about **8.950 ms**.

The hypothesis that generic learned spatial/tree predictors beat a strong causal persistence baseline at one step is not supported.

## E. Horizon-dependent predictive value
A calibration-only horizon-adaptive persistence/spatial fusion becomes useful at longer planning horizons. Across five grouped split assignments, all five show lower delay MAE than persistence at:

- 20 steps (about 1.1 s): mean improvement about **1.463 ms**;
- 50 steps (about 2.8 s): mean improvement about **2.510 ms**;
- 100 steps (about 5.5 s): mean improvement about **2.621 ms**.

The five assignments reuse the same 38 drives. They are descriptive sensitivity evidence, not five independent replicates and not a basis for an n=5 inferential test.

## F. Empirical support and uncertainty
Primary support strata show delay MAE / empirical interval coverage of approximately:

- <=1 m: **6.98 ms / 0.888**;
- 1–5 m: **8.51 ms / 0.841**;
- 5–15 m: **10.47 ms / 0.761**.

However, deeper diagnostics show that support-distance/error behavior is context-dependent rather than universally monotone within every drive; severe degradation is concentrated particularly in some n8 contexts/segments. The valid conclusion is that low empirical support is a useful reliability-risk indicator under grouped shift, not a universal distance-to-error law.

Residual split-conformal intervals are reported through empirical coverage. They are not called calibrated event probabilities, and nominal 90% coverage is not assumed to survive grouped distribution shift.

## G. Primary measured-route replay
On the primary nine-run held-out replay:

| Planner | Mean measured delay | >50 ms violation fraction | Changed from nominal | Unsupported fraction | Mobility deviation |
|---|---:|---:|---:|---:|---:|
| P0 | ~11.7659 ms | ~0.01657 | 0 | ~0.10834 | 0 |
| P1 | ~11.7659 ms | ~0.01657 | 0 | ~0.10834 | 0 |
| P2 | ~10.9737 ms | ~0.01378 | ~0.12043 | ~0.10561 | ~0.06022 |
| P3 | ~11.0468 ms | ~0.01412 | ~0.13750 | ~0.08725 | ~0.07074 |

P1 and P0 make the same route-horizon choice in this replay because current QoS is common to the candidate set at a decision instant; a reactive/current-value term therefore cannot distinguish future candidate horizons. This is a baseline property, not hidden future information.

The P2-P1 measured-delay delta is about **-0.792 ms**, with paired-bootstrap CI approximately **[-1.723, -0.138] ms** and raw paired Wilcoxon p=0.046875. The >50 ms violation delta is about -0.00279 with raw p=0.0625.

P3-P2 measured-delay delta is about +0.073 ms and does not establish QoS superiority. P3 primarily reduces unsupported selection exposure while increasing mobility deviation.

## H. Multiplicity-corrected interpretation
The replay analysis applies Holm correction across the declared 12 planner-comparison/metric tests. The primary raw p-values do **not** remain confirmatory at 0.05 after correction:

- P2-P1 delay: raw p=0.046875 -> Holm-adjusted p about **0.28125**;
- P3-P2 unsupported fraction: raw p=0.03125 -> Holm-adjusted p about **0.25**.

These primary-split effects are therefore exploratory effect-size evidence rather than multiplicity-corrected significance claims.

## I. Grouped-split replay robustness
Because the five split assignments reuse the same drives, the repository reports descriptive robustness only.

P2-P1 measured-delay deltas by split are approximately:

`-0.791924, -1.253015, -0.069188, -0.262972, -0.129775 ms`.

All 5/5 are negative; descriptive mean is about **-0.501375 ms** and median about **-0.262972 ms**.

P2-P1 >50 ms violation-fraction deltas are also negative in all 5/5 assignments, with mean about **-0.002239**.

P3-P2 unsupported-fraction deltas are negative in all 5/5 assignments, with mean about **-0.027954**.

P3-P2 measured-delay effects have mixed sign and mean near zero, so there is no stable additional QoS advantage for P3.

Interpretation: **P2 = predictive communication utility; P3 = inference-validity/support control.**

## J. Computational interpretation
The vectorized measured-replay implementation has demonstrated microsecond-scale batched QoS/support evaluation and candidate scoring on hosted CI. This supports an implementation-level computational-practicality statement only. It does not establish embedded, end-to-end, or real-vehicle real-time performance.

## K. PC-FMCW evidence state
Historical V1 communication effects are exploratory only and the V1 run is invalidated as confirmatory robotics evidence because of collisions/no-candidate behavior and an incomplete frozen endpoint schema. V2 did not establish the required safety gate and its communication outcomes must not be promoted.

The active V3 protocol uses development seeds 6000–6019, selects the minimum predeclared planning margin in {0,0.5,1.0,1.5,2.0,2.5,3.0} m that yields zero collision episodes and zero episodes with no-candidate steps, and only then permits fresh confirmatory seeds 7000–7049 plus fresh geometry-mechanism seeds 8000–8019. The physical collision threshold remains 2.0 m.

No V3 communication claim is accepted until the fresh 50-seed hard safety gate passes and seed-level bootstrap/Wilcoxon/Holm analysis over the five frozen endpoints completes.

## L. PC-FMCW provenance boundary
The source paper reports approximately 193.4 THz, corresponding to about 1550 nm, despite “blue laser” headlamp terminology. The repository preserves that inconsistency rather than silently reconciling it. Robotics-side reference SNR, path loss, angular width, outage threshold, softness, and uncertainty parameters are surrogate modeling assumptions unless independent calibration evidence is available.

Do not claim measured blue-light photometry, eye-safety validation, calibrated atmospheric propagation, detector responsivity, or physical optical channel validation.

## M. Supported statements now
It is defensible to state that:

- the field branch uses genuine V2N2V measurements with whole-run anti-leakage splitting;
- one-step persistence is stronger than the tested naive learned predictors;
- contextual/spatial information has consistent descriptive incremental value at longer tested horizons across grouped partition sensitivity analyses;
- P2 shows a favorable measured-delay direction across all five grouped split assignments, without claiming five independent replicates;
- P3 consistently reduces unsupported decision exposure across those assignments but does not show stable QoS superiority;
- prediction reliability depends on empirical support and operating context;
- PC-FMCW results remain model-based and safety-gated.

## N. Statements that must not be made
Do not claim generic communication-aware planning, radio-map planning, optical/FSO trajectory optimization, or ISAC-aware mobility is new. Do not claim real 5G validates PC-FMCW optical propagation. Do not call the route replay closed-loop autonomy. Do not call raw primary-split p<0.05 confirmatory after Holm correction. Do not treat five split assignments as n=5 independent statistical replication. Do not claim P3 improves QoS over P2. Do not call the analytical PC-FMCW surrogate physically calibrated.

## O. Remaining closure items
1. Complete the frozen V3 development safety selector.
2. If it passes, complete fresh 7000–7049 confirmatory safety gate and communication inference.
3. Complete fresh 8000–8019 directional-versus-distance-only mechanism ablation.
4. Update the evidence ledger before manuscript numerical claims.
5. Synchronize the Paper-1 manuscript with final validated `main` evidence.
6. Keep Paper 2 separate and frame repeated grouped splits as sensitivity analyses.

## P. Publication assessment
The measured-data branch is strongest as a narrow methodological paper about when logged vehicular communication data are sufficiently supported to justify predictive motion decisions; its contribution is evidence discipline rather than spectacular ML gains.

Paper 1 can support a distinct technology-specific contribution if V3 closes the hard safety gate and fresh confirmatory evidence supports useful predictive communication effects. A null V3 communication result remains publishable evidence if the safety/statistical protocol is clean; it must not be tuned away post hoc.
