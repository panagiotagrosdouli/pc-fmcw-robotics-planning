# Three-Paper Publication Plan

## Purpose

The repository supports three related but scientifically distinct manuscripts. The split prevents one evidence source from being used to validate a different scientific question.

## Paper 1 — PC-FMCW predictive connectivity-aware motion planning

**Question:** Does trajectory-conditioned future PC-FMCW-informed connectivity improve receding-horizon motion decisions relative to reactive connectivity scoring?

**Primary evidence:** frozen V7 controlled simulation.

**Boundary:** model-based PC-FMCW-informed robotics; no measured optical-channel validation or real-road safety claim.

## Paper 2 — measurement-support-aware predictive V2X planning

**Question:** When does field-measured future-QoS prediction provide actionable planning value, and how should decisions respond to poorly supported counterfactual regions?

**Primary evidence:** CICV5G whole-drive prediction, support analysis, and route-constrained measured replay.

**Boundary:** measured 5G/V2N2V offline replay; not PC-FMCW optical validation and not real-road closed-loop driving.

## Paper 3 — decision-triggered active self-calibration

**Working title:** *When Should a Vehicle Move to Learn the Channel? Decision-Triggered Active Self-Calibration for PC-FMCW-Informed Vehicular Optical Planning*

**Question:** When should safe ego motion also be used as an experiment for learning uncertain modeled optical-link parameters because that information can change the downstream motion decision?

**Primary evidence:** frozen 50-seed directional C0-C4 confirmatory study with six declared scenarios, development selection on separate seeds, seed-level paired inference, and a common hard-safety interface.

**Core result:** unconditional information seeking (C2) substantially increases decision regret; decision-triggering (C3) removes most of that penalty and suppresses irrelevant probing. However, C3 does not establish superiority over passive calibration (C1), and Scenario F is a retained null/negative mechanism result.

**Mechanism evidence:** a separate distance-only development ablation collapses regret/probing across C0-C4, supporting dependence on directional geometry inside the analytical model.

**Measured support:** held-out V-VLC path-loss data show essentially null directional predictive gain; CICV5G provides separate measured QoS/pose transfer and offline-replay context. Neither validates synthetic optical calibration.

## Shared architecture, separate claims

The three papers may share the generic abstraction

```
state/history -> prediction/belief -> candidate trajectories -> hard safety
              -> communication evaluation/information value -> decision -> replan
```

but must retain distinct hypotheses, experimental units, primary outcomes, and claim boundaries.

## Definition of manuscript-ready

A manuscript is ready only when the hypothesis/protocol is frozen, independent units are correct, declared comparisons are complete, multiplicity is handled, negative results are retained, numerical claims map to machine-readable evidence, bibliography positioning has been audited, the PDF builds cleanly, and required author/venue declarations are confirmed.

Paper 3 satisfies the scientific/evidence conditions. Its remaining blockers are publication operations: venue choice, author metadata, visual PDF inspection, and final release archiving.
