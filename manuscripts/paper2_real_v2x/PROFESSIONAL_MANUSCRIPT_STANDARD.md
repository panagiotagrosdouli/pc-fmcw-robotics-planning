# Paper 2 — journal-grade manuscript standard

This file is a quality contract for the submission manuscript, not a project README.

The canonical paper must read as a self-contained scientific article. Repository implementation details belong in reproducibility material unless they are required to understand the method. The paper should not use PR numbers, CI run numbers, branch names, or development history as narrative evidence.

## Required scientific narrative

The manuscript must establish the problem in this order: vehicular motion changes wireless conditions; future-QoS prediction can therefore be decision relevant; field-measured predictors are not valid everywhere a planner can query them; row-wise validation can leak route-local information; and arbitrary counterfactual positions lack measured QoS truth. The proposed methodology addresses these issues with whole-run partitioning, causal horizon-specific prediction, calibration-only model selection, training-only empirical support, and route-constrained measured replay.

The novelty claim must remain narrow. Communication-aware planning, radio-map planning, QoS-aware trajectory optimization, predictive V2X QoS, and uncertainty-aware planning are prior art. The contribution is the combination of anti-leakage field evaluation, horizon-dependent decision relevance, explicit measurement-support auditing, and measured post-selection replay.

## Required sections

The submission version should contain a substantive Introduction; Related Work organized by communication-aware planning, predictive vehicular QoS, uncertainty/support, and counterfactual evaluation; Data and leakage-control protocol; Problem Formulation; Prediction and calibration; Empirical Measurement Support; Route-Constrained Measured Replay; Planner Definitions; Experimental Protocol and Hypotheses; Results; Discussion; Threats to Validity; Reproducibility and Data Availability; Conclusion; and verified references.

## Required hypotheses

H1: spatial/context information provides incremental predictive value over persistence only at sufficiently long decision horizons.

H2: using horizon-appropriate future-QoS estimates changes selected measured-route actions in a direction that reduces subsequently observed delay relative to reactive/current-QoS planning.

H3: explicit training-measurement support control reduces the fraction of selected actions whose predictor queries are empirically unsupported; no additional QoS gain is assumed.

Each hypothesis must be linked to a declared analysis and must be weakened or rejected when the evidence does not support it.

## Statistical language

The nine held-out acquisition runs in the primary split are the paired inferential units for replay comparisons. Bootstrap confidence intervals and paired Wilcoxon tests may be reported, with Holm adjustment over the declared family. A raw p-value below 0.05 that does not survive Holm must be described as exploratory. Five alternative grouped split assignments reuse drives and therefore provide descriptive sensitivity evidence only; they are not n=5 independent experiments.

## Claim boundaries

CICV5G provides field-measured 5G/V2N2V evidence for the decision layer. It does not validate the separate PC-FMCW optical model. Route-constrained replay is offline measured replay, not closed-loop autonomous-driving deployment. Residual split-conformal intervals are empirical uncertainty intervals, not calibrated event probabilities. The 50-ms delay threshold is an experimental operating point, not a universal networking standard. Implementation timing is not an embedded real-time guarantee.

## Presentation standard

Every central quantitative result should appear in a generated table or vector figure and be reproducible from the archived artifact snapshot. The main text should interpret effect size, uncertainty, multiplicity, and practical meaning rather than merely list numbers. Negative results must remain visible, especially the failure of naive one-step learned predictors to beat persistence and the absence of a stable P3-over-P2 QoS gain.

The final PDF should target normal full-paper density rather than a 3--4 page project summary. Page count is venue dependent, but the scientific content should be sufficient for an approximately 8--12 page IEEE-style full paper before venue-specific compression.
