> **Companion narrative.** The canonical IEEE submission source is `paper3.tex`. This Markdown file preserves a compact human-readable account of the frozen evidence; when wording differs, `paper3.tex`, `CLAIM_EVIDENCE.md`, and the frozen machine-readable evidence govern submission text and numerical claims.

# When Should a Vehicle Move to Learn the Channel?
## Decision-Triggered Active Self-Calibration for PC-FMCW-Informed Vehicular Optical Planning

**Canonical status:** frozen confirmatory evidence complete; manuscript package prepared for venue selection and final author metadata.

## Abstract

We study when safe vehicle motion should also act as an experiment for learning uncertain parameters of a modeled directional optical link. Five planners share the same vehicle dynamics, candidate lattice, causal target prediction, and hard safety filters: C0 uses nominal link parameters, C1 performs passive Bayesian calibration, C2 always rewards information gain, C3 activates information seeking only when posterior uncertainty changes the downstream trajectory decision, and C4 is a nondeployable true-parameter reference. Development used 20 seeds and a predeclared 27-setting grid; the selected setting was frozen before 50 untouched confirmatory seeds were opened. Across 1,500 confirmatory planner/scenario/seed episodes and 45,000 timesteps, the sampled hard gate recorded zero collision episodes, zero no-candidate steps, and zero static-clearance violations. Unconditional C2 greatly increased cumulative decision regret relative to C1 (+0.083290), whereas C3 removed most of that penalty relative to C2 (-0.082211; Holm-adjusted p≈1.24e-14) while reducing probe fraction by 0.037444. However, the study does not establish C3 superiority over passive C1: C1 had lower descriptive overall regret, and in the decision-critical Scenario F C3 probed but had higher mean regret than C1. A separate distance-only development ablation collapsed regret and probing across the planner family, supporting a directional-geometry mechanism within the model. The results support decision relevance as a guard against unnecessary active calibration, not a general claim that active probing outperforms passive Bayesian calibration.

## 1. Introduction

Communication-aware motion planning is established, as are informative path planning, calibration-oriented trajectory design, ISAC-to-planning coupling, and optical communication-aware control. The narrower question here is whether a vehicle should deliberately excite a modeled directional communication channel only when parameter uncertainty is **decision relevant**.

The study separates parameter learning from downstream decision quality. Better parameter estimation need not improve motion choice, and broad posterior uncertainty need not justify probing when all plausible models prefer the same safe trajectory.

## 2. Model and uncertainty

The modeled latent vector is `phi=[alpha_loss, delta_beam, k_angular]`: distance-loss scaling, boresight offset, and angular attenuation scaling. Simulator truth, the nominal model, and the planner belief are distinct. C0-C3 never receive simulator truth.

A discrete 3×3×3 Bayesian grid is updated causally from modeled SNR observations after the chosen action is executed. The information score is a short-horizon predictive-variance proxy and is not claimed to be exact mutual information or a calibrated Fisher-information matrix.

## 3. Planner family and safety

C0 is nominal/no calibration. C1 uses the posterior-expected task/connectivity cost and passively updates the belief. C2 always allows the information reward. C3 gates the information reward using posterior decision disagreement and expected decision regret. C4 uses true simulator link parameters only as a model-relative connectivity reference.

Hard road, speed, static-obstacle, dynamic-target, and stop-viability filters are applied before information scoring. Information value can never make an infeasible candidate feasible.

## 4. Frozen protocol

Development seeds were `31000..31019`. The declared 27-setting grid was completed before deterministic selection. The chosen setting `dev_t010_i025_p020` corresponds to decision threshold 0.10, information weight 0.25, probe weight 0.20, and minimum expected regret 0.

The protocol was frozen at `2026-09-25T07:28:10.141950+00:00`. Untouched confirmatory seeds `32000..32049` were then opened. The independent inferential unit is the seed after averaging the six declared scenarios. Timesteps are diagnostics only. Primary pairs are C0-C1, C1-C2, C2-C3, and C3-C4.

## 5. Frozen confirmatory results

Mean cumulative decision regret was C0 0.006432, C1 0.004786, C2 0.088076, C3 0.005865, and C4 0.

For C1-C0, the mean seed-level regret delta was -0.001646 with 95% bootstrap CI [-0.003079,-0.000578], but Holm-adjusted p=0.05765, so it is not described as multiplicity-adjusted confirmatory significance.

C2-C1 regret increased by +0.083290 (95% CI [0.073641,0.093720], Holm p≈1.24e-14). C3-C2 regret decreased by -0.082211 ([-0.092695,-0.072358], Holm p≈1.24e-14). C4-C3 was -0.005865 ([-0.007628,-0.004242], Holm p≈1.24e-6), leaving a model-relative oracle gap.

C3 reduced probe fraction relative to C2 by 0.037444 and cumulative probe cost by 0.020332. C2 nonetheless achieved lower parameter error than C1, while having much worse decision regret; C3 accepted higher parameter error than C2 while achieving much lower regret. Parameter learning and decision quality are therefore distinct endpoints.

All 1,500 confirmatory episodes were collision free, with zero no-candidate steps and zero static-clearance-violation steps under the sampled benchmark.

## 6. Decision-relevance mechanism

Scenario E contained uncertainty designed to be decision irrelevant. C3 had zero mean probe fraction and zero regret; C2 still probed (0.004667) and incurred regret (0.008610).

Scenario F was decision critical. C3 did activate probing (0.003333), but did not improve regret over passive C1. Mean regret was C0 0.031984, C1 0.028037, C2 0.140882, C3 0.034416, and C4 0. This null/negative result is retained and was not followed by post-confirmatory retuning.

## 7. Directional mechanism ablation

A separate development-only distance-only ablation used seeds `31000..31019` with the frozen-selected hyperparameters. Removing angular attenuation reduced cumulative regret to zero/numerical roundoff and probe fraction to zero for every planner. C1-C3 remained able to reduce error in the distance-loss degree of freedom, but angular latents were intentionally non-identifiable.

This supports a mechanism-specific conclusion: the nontrivial active behavior in the primary study depends on directional geometry inside the analytical model. It does not establish physical optical identifiability.

## 8. Measured support studies

A held-out spatial-group V-VLC study found distance-only MAE 5.587261 dB and directional MAE 5.580011 dB. The directional-minus-distance-only absolute-error effect was -0.005031 dB with 95% CI [-0.019734,0.010134] and Wilcoxon p=0.375269. This is effectively null evidence for meaningful directional predictive gain in that measured dataset.

A separate CICV5G study used 38 measured W2S runs and 43,045 samples. It provides measured 5G QoS/pose transfer and route-constrained replay context, not optical calibration or closed-loop real-vehicle validation.

## 9. Discussion

The strongest supported result is not that active calibration beats passive calibration. It is that decision relevance prevents a large amount of unnecessary information seeking. C2 learns aggressively but degrades decisions. C3 largely suppresses that cost and correctly stays inactive in Scenario E. Yet Scenario F shows that detecting decision relevance is insufficient by itself to guarantee useful probing.

Possible causes include limited probing actions, the short-horizon information proxy, and the value/scaling of information relative to task cost. These are hypotheses for future work, not explanations established by the frozen data.

## 10. Limitations and conclusion

The latent parameters, observation noise, and PC-FMCW-informed link quantities are modeled. C4 is a model-relative oracle. The candidate lattice constrains what can be learned through motion. The information score is approximate. The V-VLC directional comparison is null, and CICV5G concerns a different radio modality.

Accordingly, the conclusion is deliberately narrow: **decision relevance is useful for suppressing unnecessary active self-calibration, but the implemented probing policy does not demonstrate a confirmatory advantage over passive Bayesian calibration.**

## Reproducibility

The canonical frozen evidence, compact summaries, artifact IDs/digests, and build instructions are recorded in this directory and in the repository-wide readiness/release manifests.
