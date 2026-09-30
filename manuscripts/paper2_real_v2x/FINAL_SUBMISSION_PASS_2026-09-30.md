# Paper 2 — Final Submission Pass

**Date:** 2026-09-30  
**Target:** IEEE Transactions on Vehicular Technology (TVT)  
**Canonical manuscript:** `paper2.tex`

## Submission interpretation

Paper 2 is a **measured decision-validity / field-evidence paper**.

It is **not** a planner-superiority paper.

The central publication claim is:

> Across two pre-frozen repeated-field evaluations with different speed-action pairs, support-bounded measured action-value headroom exists, while frozen prediction-based rankings fail to recover it reliably.

## Editor-facing pitch

Predictive QoS and communication-aware motion planning are established, but logged field measurements do not provide arbitrary counterfactual outcomes for motion actions that were not executed. This paper introduces a support-bounded matched field replay protocol that separates predictor training, measured action-outcome donation, and decision queries across acquisition runs and uses two-way query-run × donor-run resampling for inference.

The empirical result is deliberately non-promotional: measurable action-value opportunity exists in both frozen confirmations, yet the tested prediction-derived rankings retain regret relative to that opportunity. PRED-over-FAST superiority is not confirmed in W2S, and the same frozen predictive intervention is measurably worse than FAST in the arterial confirmation.

## Primary confirmed evidence

### W2S, 30 vs 50 km/h

- ORACLE − FAST: **−4.177 ms**, 95% CI **[−13.659, −2.137]**
- PRED − ORACLE: **+2.704 ms**, 95% CI **[+1.457, +5.832]**
- PRED − FAST: **−1.473 ms**, 95% CI **[−8.167, +0.657]**
- MARGIN − FAST: **−1.668 ms**, 95% CI **[−9.524, +1.180]**

### Arterial n8, 50 vs 80 km/h

- ORACLE − FAST: **−0.590 ms**, 95% CI **[−1.431, −0.250]**
- PRED − ORACLE: **+0.746 ms**, 95% CI **[+0.344, +1.596]**
- PRED − FAST: **+0.156 ms**, 95% CI **[+0.038, +0.258]**
- MARGIN − FAST: **+0.032 ms**, 95% CI **[+0.007, +0.061]**

## What makes the paper publishable

The paper does not depend on a broad novelty claim.

Its contribution is the evidence discipline:

- physically interpretable speed actions;
- repeated field measurements;
- disjoint train/donor/query acquisition-run roles;
- finite measured action support;
- donor outcomes hidden during deployable ranking;
- donor contribution provenance;
- two-way query-run × donor-run bootstrap;
- negative frozen pairwise-margin result retained;
- cross-scenario confirmation with a different speed-action pair.

## Reviewer attack points and responses

### "This is just another communication-aware planner."

No. The planner is intentionally simple. The research object is whether logged field measurements justify a decision-level claim.

### "The oracle is optimistic."

Correct. It is explicitly labeled a nondeployable support-bounded upper-bound diagnostic because donor outcomes enter its ranking.

### "This is not causal."

Correct. Repeated drives are observational and can differ in latent network conditions. No causal speed-effect claim is made.

### "Why not use a decision-focused loss?"

A frozen pairwise action-margin model was tested and retained as a negative result. It does not remove the measured decision-evidence gap.

### "Could the result be route-specific?"

A separately pre-frozen arterial-road confirmation uses a different 50/80-km/h action pair. Measured headroom remains present, but the frozen predictive policy is worse than FAST.

### "Why not count thousands of matched rows?"

Because rows share query and donor acquisition runs. Inference resamples both cluster dimensions.

## Title

**From QoS Prediction to Measured Decision Validity: Support-Bounded Matched Field Replay for Vehicular Speed Decisions**

Do not add "first", "causal", "validated autonomous driving", or "superior controller" language.

## Genuine blockers before external submission

- final author list/order;
- affiliation(s);
- corresponding-author institutional email;
- funding/acknowledgments;
- conflicts of interest;
- ORCID and IEEE Author Portal metadata;
- related-manuscript/preprint/repository disclosure;
- author approval of AI-assisted language-editing disclosure;
- final canonical PDF visual QA after the policy-label layout fix;
- immutable source/supplement release tag;
- final cover-letter approval.

## Submission go/no-go

**Scientific go:** yes, as a methodology / measured decision-validity paper.

**Scientific no-go:** any universal or confirmatory "new speed planner is superior" claim.
