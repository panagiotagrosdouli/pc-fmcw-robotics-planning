# When Should a Vehicle Move to Learn the Channel?
## Decision-Triggered Active Self-Calibration for Vehicular Optical Planning

> Manuscript status: prospective research note. Numerical claims are intentionally absent until the frozen experiment is executed.

## 1. Introduction

Directional optical planning depends on parameters that may be uncertain or mismatched. Ordinary communication-aware motion planning assumes a usable link model and then optimizes motion. This work instead asks when the vehicle should deliberately choose a safe motion whose communication observation is useful for resolving uncertainty that matters to the next control decision.

The investigated principle is: **motion is simultaneously a control action and, only when decision-relevant, an experiment for learning the communication model.**

Contributions to test:
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

Declare scenarios A-F, development seeds, frozen hyperparameter procedure, untouched confirmatory seeds, paired planner realizations, independent seed-level inference, metrics, primary comparisons and multiplicity correction.

Primary outcome: cumulative decision regret relative to the oracle-parameter candidate choice. Secondary outcomes: oracle agreement, probing burden, parameter error, communication metrics, progress and safety diagnostics.

## 8. Results

### 8.1 Frozen confirmatory decision quality
[TBD after frozen experiment]

### 8.2 Calibration and information acquisition
[TBD after frozen experiment]

### 8.3 Safety, mobility and communication outcomes
[TBD after frozen experiment]

## 9. Mechanism and Ablation Analysis

Report C0-C1, C1-C2, C2-C3 and C3-C4 paired effects. Examine E as the key decision-irrelevant uncertainty test and F as the canonical decision-critical mechanism example. Preserve null and negative findings.

[TBD after frozen experiment]

## 10. Limitations

The latent parameters and communication observations are modeled; no real optical calibration is claimed. The information score is approximate, parameter identifiability depends on geometry/action richness, the candidate lattice limits the experiment set, and simulator oracle regret is model-relative.

## 11. Conclusion

Conclude only at the level supported by frozen evidence. The intended hypothesis is that decision-triggered active self-calibration can reduce downstream model-induced planning regret more efficiently than passive calibration or unconditional information seeking. Whether the hypothesis is supported is **[TBD after frozen experiment]**.
