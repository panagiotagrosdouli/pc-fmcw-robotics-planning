# Senior researcher report — real-measurement V2X extension

## A. Final research question
Can field-measured vehicular communication traces provide useful predictive information for autonomous motion decisions **without silently trusting QoS predictions outside their empirical measurement support**?

The initial generic idea — predict QoS and avoid blackspots — was rejected as insufficiently novel after literature review.

## B. Gap selected
The selected gap is the validity bridge between logged communication measurements and counterfactual motion decisions. The study focuses on whole-drive leakage, the strength of causal persistence, horizon-dependent predictive value, empirical spatial support, uncertainty under grouped distribution shift, and decision evaluation without fabricated off-route QoS ground truth.

## C. Closest competing work and differentiation
Communication-aware planning, proactive radio-map planning, QoS-aware AV routing, robust radio-map MPC, vehicular QoS prediction, optical/FSO trajectory optimization and ISAC-aware mobility optimization all have prior art. The study therefore does **not** claim novelty for any of those generic problem classes.

The defensible differentiation is the combined field-measured vehicular protocol: complete-run anti-leakage splitting, a strong causal persistence baseline, planning-horizon analysis, calibration-gated contextual prediction, explicit empirical-support auditing and route-constrained measured-outcome replay. In the wider repository this is paired with a separate technology-specific PC-FMCW perception-to-action simulation branch rather than being mislabeled as optical measurement validation.

## D. Real dataset
CICV5G was selected because it is public, recent, directly downloadable, and contains repeated real 5G V2N2V measurements with vehicle/network state and end-to-end communication quantities. The automated study downloaded 38 run files containing 43,045 synchronized observations.

## E. Implemented research stack
The repository contains public CICV5G acquisition/provenance, robust parsing, complete-run train/calibration/test partitioning, persistence and learned QoS baselines, multi-horizon causal evaluation, calibration-only fusion, conformal residual intervals, spatial-support diagnostics, P0-P3 decision adapters, route-constrained measured replay, run-level paired statistics, grouped-split sensitivity analysis, tests, CI workflows, research logs, claim audit and paper-facing methods/results/discussion material.

## F. Experiments executed so far
The completed measured-data chain includes parser/download verification; one-step delay/SINR prediction; support-stratified error and coverage; split-conformal held-out coverage; prediction horizons from about 55 ms to 5.5 s; context-adaptive persistence/spatial fusion; five grouped split assignments for sensitivity; route-constrained P0/P1/P2/P3 measured replay on the primary split; and run-level effect estimation.

A new workflow extends the route replay across grouped split assignments and treats those assignments as **descriptive sensitivity analyses**, not independent statistical replicates, because they reuse the same finite set of measured drives.

## G. Main quantitative results
### One-step prediction
On the primary split, current-value persistence achieved delay MAE about 5.576 ms. Spatial KNN was about 10.862 ms, Extra Trees 6.659 ms and Random Forest 7.150 ms. Thus the initial “generic ML beats reactive” hypothesis was falsified.

### Spatial/context support
Aggregate support strata show worse prediction and lower interval coverage in the sparsest held-out regions, but deeper analysis shows this effect is context-dependent rather than universally monotonic within every drive. The strongest deterioration occurs in sparse `n8` segments, whereas the observed `n78` runs are substantially easier to predict. Empirical support should therefore be interpreted jointly with network/route context.

### Horizon sensitivity
Across five alternative grouped split assignments, calibration-gated fusion has lower delay MAE than persistence in every assignment at the approximately 1.1 s, 2.8 s and 5.5 s tested horizons. The corresponding mean descriptive improvements are about 1.46, 2.51 and 2.62 ms. These five assignments are a robustness check over data partitioning, not five independent experiments.

### Primary measured replay
For the primary nine-run held-out split, mean measured delay is approximately 23.318 ms for P1, 22.526 ms for P2 and 22.598 ms for P3. The run-level P2-P1 delay effect is approximately -0.792 ms with a paired-bootstrap interval [-1.723,-0.138] ms and raw paired Wilcoxon p=0.0469.

P3-P2 measured-delay effect is approximately +0.073 ms: there is no QoS superiority. P3 selects empirically unsupported states less often in the primary split, with an absolute P3-P2 unsupported-selection effect around -0.01836 and additional mobility deviation.

### Multiplicity correction
The replay analysis now declares a 12-test family covering three planner comparisons over four replay endpoints and reports Holm-adjusted p-values. Under that family, the primary-split raw P2-P1 delay p-value and raw P3-P2 support-exposure p-value are **not** multiplicity-corrected confirmatory findings. They are reported as effect-size evidence from the primary grouped split while cross-split sensitivity is evaluated separately.

## H. Negative/failed results retained
The project retains the following negative findings:

- naive one-step spatial/tree prediction does not beat persistence;
- nominal conformal coverage is not stable under all grouped shifts;
- P3 does not beat P2 on measured QoS;
- empirical support distance is not a universal monotonic error proxy within every drive/context;
- arbitrary off-route counterfactual validation is unsupported by the available measurements;
- raw p<0.05 in one grouped split is not promoted to a confirmatory claim after multiplicity auditing.

## I. Statistical evidence
The independent paired units within the primary replay are held-out measurement runs, not timestamps. Timestamp-level observations are descriptive and are never treated as independent replicates. Alternative split seeds recycle the same 38 drives and therefore constitute sensitivity analyses rather than additional independent sample size. Raw and Holm-adjusted p-values are retained together with effect intervals.

## J. Ablation/robustness interpretation
The strongest measured-data mechanism is prediction horizon: the short-horizon process is so persistent that complex spatial prediction is unnecessary, while contextual information becomes useful at longer motion-planning horizons. The P2-versus-P3 comparison separates communication utility from model-validity control: P3 is more conservative about empirical support but does not improve measured delay in the primary replay.

## K. Limitations
The real-data branch still has one primary dataset, limited independent runs, observational route coverage, route-constrained offline replay rather than arbitrary counterfactual ground truth, an experimental delay threshold, incomplete uncertainty calibration under distribution shift, and no physical PC-FMCW optical measurements.

## L. Defensible claims
At the current evidence level it is defensible to state that:

- the data branch uses genuine field-measured V2N2V communication traces;
- whole-run grouping prevents direct drive-level train/test leakage;
- short-horizon persistence is a strong baseline;
- contextual/spatial information has consistent incremental predictive value at longer tested planning horizons across alternative grouped partitions;
- the primary route replay shows a modest lower-delay effect direction for predictive P2 relative to reactive P1 at a mobility cost;
- P3 changes empirical-support exposure rather than demonstrating superior QoS;
- prediction reliability and empirical support are context-dependent and must be reported rather than hidden.

## M. Claims that must not be made
Do not claim that communication-aware, predictive, uncertainty-aware, optical-aware, FSO-aware or ISAC-aware motion planning is itself new. Do not claim CICV5G validates PC-FMCW optical propagation, that offline replay is real-road autonomy validation, that P3 improves QoS over P2, that conformal intervals are universally calibrated under shift, or that the exact combination is proven to be a universal first.

## N. Reproduction
The repository provides scripts and GitHub Actions workflows for CICV5G download, leakage-safe predictor evaluation, multi-horizon analysis, primary route replay, grouped replay sensitivity, tests and machine-readable artifacts. The paper must use artifact-derived numbers rather than manually copied placeholders.

## O. Remaining work before submission
For the measured-data branch, the immediate closure item is inspection of the grouped route-replay sensitivity artifact and consistent reporting with multiplicity correction. A materially stronger future extension would add an independent V2X dataset or a purpose-built repeated-route campaign with denser alternative paths.

For the combined PC-FMCW paper, the higher-value outstanding evidence is the frozen 50-seed PC-FMCW confirmatory run, model-mismatch/robustness closure, and either validated optical modeling or measured optical data if physical channel claims are desired.

## P. Publication-level assessment
The real-data branch is a meaningful additional validation contribution and a plausible conference-level methodological result when framed narrowly. Its value is not a spectacular ML gain; it is the evidence discipline around when logged communication data can and cannot justify motion decisions.

Combined with the PC-FMCW robotics branch, it materially strengthens a broader paper by separating technology-specific modeled evidence from field-measured decision-layer evidence. A strong journal-level claim requires the frozen PC-FMCW confirmatory evidence plus stronger optical calibration or independent measured validation, rather than additional algorithmic complexity for its own sake.
