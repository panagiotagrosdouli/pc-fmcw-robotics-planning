# Paper 2 — 2026 Novelty Audit

Date of audit: 2026-09-28

## Reviewer-style question

**If communication-aware planning, predictive QoS, radio maps, uncertainty-aware MPC, and task-aware radio world models already exist, why is this paper not redundant?**

## Answer

Because the paper no longer claims novelty at any of those layers.

Its research object is the **validity of decision-level conclusions drawn from logged field measurements**.

The central mismatch is:

```
logged dataset:
observes QoS on the route that was driven

motion planner:
asks what would happen under alternative future states
```

A predictor can fill in unvisited states, but those values are model outputs. They cannot be silently promoted to measured counterfactual truth.

The paper therefore constrains the evaluation itself.

## Closest literature and non-overlap

| Prior work | What it already owns | What we must not claim | Remaining distinction in this paper |
|---|---|---|---|
| Ghaffarkhah & Mostofi 2011 | learned-channel communication-aware motion planning | adding communication to motion is new | field-log decision-validity protocol |
| Sliwa et al. 2018 | field-evaluated predictive vehicular connectivity | field-measured PQoS is new | QoS prediction is evaluated through motion decisions |
| Palaios et al. 2023 | QoS prediction workflow and split sensitivity | anti-leakage splitting alone is new | split control is tied to candidate support and measured decision replay |
| Ullah et al. 2025 | QoS-aware autonomous-vehicle route choice | QoS-aware AV trajectory planning is new | finite logged measurements rather than a complete simulated map |
| Gordon et al. 2026 | online radio-map risk planning | proactive radio-map planning is new | measured post-selection outcome rather than simulated/ray-traced truth |
| Kim et al. 2026 | probabilistic radio map + uncertainty-aware MPC | uncertainty-aware communication control is new | support is separated from predictive uncertainty; replay is field-outcome-based |
| RadioMapMotion 2026 | future radio-map prediction | proactive radio prediction is new | decision-level evidence rather than map-prediction accuracy |
| RMWorld 2026 | decision-relevant uncertainty and credible counterfactual rollouts | decision relevance/counterfactual credibility is new | logged field measurements are used to constrain what can be evaluated as measured outcome |

## The paper's distinct object

The manuscript introduces and evaluates a three-layer decision-validity audit:

### Layer 1 — predictive validity

Does future QoS beat persistence at the horizon where the vehicle can actually alter motion?

### Layer 2 — empirical-support validity

Is the candidate query represented by training measurements, independently of the predictor's residual interval?

### Layer 3 — outcome validity

Does the selected counterfactual candidate have a future field measurement that:

- exists in the held-out log,
- was hidden during action selection,
- is revealed only afterward for evaluation?

This third condition defines **measurement-supported counterfactual replay (MSCR)**.

## Why MSCR matters

Without MSCR, an offline planner can be evaluated circularly:

```
learn radio map
    ↓
choose action using radio map
    ↓
evaluate action using the same radio map as truth
```

MSCR replaces the last line with a withheld measured outcome for route-supported candidates.

It does not solve arbitrary off-route causal evaluation. It makes the limitation explicit instead of fabricating ground truth.

## Evidence boundary

The existing results are sufficient to support a methodology/empirical paper if claims remain narrow:

- one-step persistence is stronger than tested naive learned predictors;
- learned spatial/context information becomes useful at longer horizons;
- P2 has favorable measured-delay direction across all five grouped split assignments;
- the primary P2-P1 effect is not Holm-confirmatory;
- P3 reduces unsupported selection exposure but does not stably improve QoS;
- route replay is offline evidence, not a real intervention.

## Remaining reviewer risks

1. **Small primary test unit count:** nine held-out runs.
2. **Modest P2 effect size:** approximately -0.79 ms on the primary split.
3. **No multiplicity-corrected P2 discovery:** must remain explicit.
4. **Support metric simplicity:** spatial distance/density is not a complete OOD detector.
5. **Route-constrained replay:** stronger evidential discipline, but narrower action space.
6. **No closed-loop deployment:** should be stated in abstract/discussion/limitations.

These weaknesses are preferable to overstated novelty because they are transparent and scientifically defensible.
