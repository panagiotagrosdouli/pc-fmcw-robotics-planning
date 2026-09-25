# When Should a Vehicle Move to Learn the Channel?
## Decision-Triggered Active Self-Calibration for Vehicular Optical Planning

> Manuscript status: frozen confirmatory experiment completed. Numerical claims below are restricted to the frozen synthetic study and the separately scoped measured-data support studies.

## 1. Introduction

Directional optical planning depends on parameters that may be uncertain or mismatched. Ordinary communication-aware motion planning assumes a usable link model and then optimizes motion. This work instead asks when the vehicle should deliberately choose a safe motion whose communication observation is useful for resolving uncertainty that matters to the next control decision.

The investigated principle is: **motion is simultaneously a control action and, only when decision-relevant, an experiment for learning the communication model.**

The implemented contributions are:
1. a small interpretable latent PC-FMCW-informed directional link model;
2. causal Bayesian online parameter belief;
3. a decision-relevance gate separating parameter uncertainty from control-relevant uncertainty;
4. a safe information-seeking planner and C0-C4 ablation family;
5. a prospective paired-seed protocol centered on downstream decision regret.

No claim is made that dual control, active learning, communication-aware planning, optical planning, or their broad combination is universally first-of-kind.

## 2. Related Work

Discuss dual control, active perception/active learning, adaptive model-based planning, communication-aware robotics, optical/FSO/VLC planning, and ISAC/PC-FMCW context. State the narrower research gap at their intersection rather than asserting broad novelty.

## 3. PC-FMCW-Informed Planning Model

Describe the existing downstream planning interface, candidate trajectories, common hard safety filter, target prediction and analytical optical-link quantities. Preserve the boundary that this is a PC-FMCW-informed model, not a measured optical calibration.

## 4. Latent Communication-Model Uncertainty

Define `phi=[alpha_loss, delta_beam, k_angular]`, distinguish nominal model, simulator truth and planner belief, and state why three parameters are used. Describe where identifiability may fail.

## 5. Passive and Active Calibration

Define the modeled SNR observation, Bayesian grid update and causal information boundary. Introduce the predictive-information approximation and its limitations.

## 6. Decision-Triggered Dual-Control Planner

Define posterior expected candidate cost, decision disagreement probability, expected decision regret, trigger threshold, probing cost and gated information term. State explicitly that hard safety precedes all scoring.

Contrast:
- C0 nominal/no calibration;
- C1 passive;
- C2 always information-seeking;
- C3 decision-triggered;
- C4 oracle parameter reference.

## 7. Experimental Protocol

Six scenarios (A-F) were evaluated. Development used seeds `31000..31019`; the predeclared grid contained 27 settings. All 27 settings and the common C0/C1/C4 baseline completed before selection. The deterministic selection rule chose `dev_t010_i025_p020`, corresponding to `decision_threshold=0.10`, `information_weight=0.25`, `probe_weight=0.20`, and `min_expected_regret=0`.

The protocol was frozen at `2026-09-25T07:28:10.141950+00:00`. Confirmatory execution began only afterward and used untouched seeds `32000..32049`. The confirmatory artifact contains 1,500 episode rows (50 seeds x 6 scenarios x 5 planners) and 45,000 timestep rows with no duplicate planner/scenario/seed episodes.

The independent inferential unit is the seed after averaging the six declared scenarios within seed. Timesteps are diagnostic only. The predeclared primary comparisons are C0-C1, C1-C2, C2-C3 and C3-C4. Each comparison family reports deterministic paired bootstrap 95% intervals, paired Wilcoxon tests, paired effect sizes and Holm adjustment across the seven declared metrics.

Primary outcome: cumulative decision regret relative to the oracle-parameter candidate choice. Secondary outcomes: oracle agreement, probing burden, parameter error, communication metrics, progress and safety diagnostics.

## 8. Frozen Confirmatory Results

### 8.1 Decision quality

Across 300 scenario-seed episodes per planner, mean cumulative decision regret was:

| Planner | Mean cumulative decision regret |
| --- | ---: |
| C0 | 0.006432 |
| C1 | 0.004786 |
| C2 | 0.088076 |
| C3 | 0.005865 |
| C4 | 0.000000 |

Passive calibration reduced regret relative to C0 by a mean seed-level delta of `-0.001646` (95% bootstrap CI `[-0.003079, -0.000578]`). The raw Wilcoxon p-value was `0.00961`, while the predeclared Holm-adjusted p-value within the seven-metric C1-C0 family was `0.05765`; therefore this comparison is not presented as multiplicity-adjusted confirmatory significance.

Unconditional information seeking was substantially worse than passive calibration: C2-C1 regret delta `+0.083290` (95% CI `[0.073641, 0.093720]`, Holm-adjusted `p=1.24e-14`).

Decision-triggering largely removed that penalty: C3-C2 regret delta `-0.082211` (95% CI `[-0.092695, -0.072358]`, Holm-adjusted `p=1.24e-14`).

C3 retained a nonzero gap to the model-relative oracle. The reported C4-C3 delta is `-0.005865` (95% CI `[-0.007628, -0.004242]`, Holm-adjusted `p=1.24e-6`). C4 is only an oracle-parameter reference inside the declared analytical model and is not evidence of real-world optimality.

C1 and C3 were not a predeclared primary pair, so no post-hoc superiority claim is made between them. Descriptively, C1 had lower overall mean regret (`0.004786`) than C3 (`0.005865`).

### 8.2 Calibration and information acquisition

Mean probe fraction was `0` for C0/C1/C4, `0.038111` for C2 and `0.000667` for C3. Relative to C2, C3 reduced probe fraction by `0.037444` (C3-C2; 95% CI `[-0.039778, -0.035333]`, Holm-adjusted `p=3.10e-9`) and cumulative probe cost by `0.020332` (95% CI `[-0.025588, -0.015622]`, Holm-adjusted `p=3.10e-9`).

C1 substantially reduced normalized parameter error relative to C0 (`-0.393495`, 95% CI `[-0.423885, -0.363191]`, Holm-adjusted `p=1.24e-14`). C2 reduced parameter error further relative to C1 (`-0.053484`, 95% CI `[-0.079561, -0.026464]`, Holm-adjusted `p=1.30e-4`) even though its decision regret was much worse. Conversely, C3 had higher parameter error than C2 by `+0.046795` (95% CI `[0.020566, 0.072209]`, Holm-adjusted `p=4.24e-4`) while achieving far lower regret.

This separation is central to the mechanism result: more parameter learning did not imply better downstream decisions.

### 8.3 Safety, mobility and communication outcomes

All planners had zero collision episodes. Across all 1,500 confirmatory episodes there were also zero no-candidate steps and zero static-clearance-violation steps. The minimum recorded static-obstacle clearance was approximately `1.500003 m`.

Mean progress was nearly identical across planners (approximately `24.76 m` overall). C2 gained only `0.019755 m` relative to C1 while incurring much greater regret and probing burden. Mean outage probability increased by `0.005105` for C2 relative to C1 (95% CI `[0.002973, 0.007258]`, Holm-adjusted `p=1.91e-5`) and decreased by `0.006654` for C3 relative to C2 (95% CI `[-0.008331, -0.005156]`, Holm-adjusted `p=1.07e-13`).

C4 should not be read as an outage-minimizing controller: it is a true-parameter reference using the same mixed task/connectivity objective and hard-safety machinery.

## 9. Decision-Relevance Mechanism

Scenario E was designed to contain parameter uncertainty that should not matter to the motion decision. C3 behaved as intended there: mean probe fraction `0` and mean decision regret `0`. C2 still probed (`0.004667` mean probe fraction) and accumulated `0.008610` mean regret.

Scenario F was the deliberately decision-critical case. Here C3 did activate probing (`0.003333` mean probe fraction), but the intervention did **not** improve the primary decision metric over passive calibration. Mean F regret was:
- C0: `0.031984`
- C1: `0.028037`
- C2: `0.140882`
- C3: `0.034416`
- C4: `0`

Thus the frozen experiment supports the value of suppressing unconditional information seeking, but it does not support a claim that the implemented decision-triggered probing strategy improves over passive calibration in the canonical F case. This null/negative result is retained as part of the scientific conclusion rather than retuned away after confirmation.

## 10. Real-Data Support Studies and Claim Boundaries

### 10.1 Measured vehicular VLC path loss

A separate measured V-VLC study used the public `bugratu/ML_VVLC` dataset pinned to upstream commit `bdf38f402d67f9f1c48daea074730136cb6bef7e`. On the held-out spatial test set, distance-only MAE was `5.587261 dB` and the directional model MAE was `5.580011 dB`. The group-paired directional-minus-distance-only absolute-error effect was `-0.005031 dB`, with 95% bootstrap CI `[-0.019734, 0.010134] dB` and Wilcoxon `p=0.375269`.

This is effectively null evidence for a meaningful directional predictive gain in that measured dataset. The data support measured vehicular optical path-loss analysis; they do not provide direct PC-FMCW waveform calibration or closed-loop planning validation.

### 10.2 Measured CICV5G V2X support/replay study

The separate CICV5G track used 38 measured W2S vehicle runs containing 43,045 samples. In the basic held-out support split, persistence was the best tested delay predictor with MAE `5.576288 ms`. Across five grouped split assignments, route/horizon fusion reduced delay MAE relative to persistence at horizons 20/50/100 steps in 5/5 splits, with mean deltas approximately `-1.4597`, `-2.5060`, and `-2.6223 ms`, respectively.

In the offline route-replay analysis, P2 reduced measured delay relative to P1 in 5/5 split assignments (mean split effect approximately `-0.501375 ms`) with a small positive mobility-deviation effect (approximately `+0.008452`). The repeated split assignments reuse the same finite measured drives and are descriptive robustness configurations, not independent experimental replicates.

These results support measured 5G V2X QoS/pose transfer and offline replay analysis. They are not optical calibration and not closed-loop real-vehicle validation.

## 11. Directional vs Distance-Only Mechanism Ablation

A standalone development-only mechanism ablation removes angular attenuation while preserving the same planner and hard-safety machinery. In this ablation, `delta_beam_rad` and `k_angular` are intentionally non-identifiable from link observations.

The ablation is executed separately from the frozen primary confirmatory protocol and cannot change the selected hyperparameters or any primary conclusion.

[RESULTS TO BE INSERTED FROM THE STANDALONE DISTANCE-ONLY ABLATION ARTIFACT.]

## 12. Limitations

The latent parameters and communication observations are modeled; no real optical calibration is claimed. The information score is approximate, parameter identifiability depends on geometry/action richness, the candidate lattice limits the experiment set, and simulator oracle regret is model-relative.

The decision trigger succeeded at avoiding most unnecessary probing and strongly improved over unconditional information seeking, but it did not beat passive calibration in the decision-critical F scenario. This indicates that detecting decision relevance is not sufficient by itself: the available probing actions, short-horizon information proxy, or probe-value scaling may still be inadequate for turning information into better decisions.

The V-VLC directional comparison was null, and the CICV5G evidence concerns a different radio modality. Neither measured-data track should be used to imply direct physical validation of the synthetic latent optical calibration mechanism.

## 13. Conclusion

The frozen study provides **partial support** for the proposed decision-triggered active-calibration principle.

C3 dramatically reduced the regret and probing burden produced by unconditional information seeking (C2), while preserving hard safety. It also correctly suppressed probing in the decision-irrelevant E scenario. However, the study does not establish superiority over passive calibration: overall C1 had descriptively lower mean regret than C3, and in the canonical decision-critical F scenario C3 probed but did not improve regret over C1.

The strongest supported conclusion is therefore narrower: **decision relevance is useful for preventing unnecessary active calibration, but the implemented probing policy does not yet demonstrate a confirmatory advantage over passive Bayesian calibration.** This negative boundary is part of the result.
