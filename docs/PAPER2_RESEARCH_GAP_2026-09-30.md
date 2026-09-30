# Paper 2 Research Gap — Cross-Run Matched Field Replay for Motion-Conditioned V2X Decisions

**Date:** 2026-09-30  
**Status:** research branch; not part of the frozen Paper-2 evidence  
**Branch:** `research/paper2-matched-speed-replay`

## Executive decision

The existing Paper-2 idea contains a publishable methodological core, but the current route-constrained replay has a reviewer-visible weakness: its candidate action is a future time offset on the same measured trajectory, and the archived P0 and P1 outcomes are identical.

The next experiment should therefore move from **future-horizon selection** to a **real motion-conditioned action** supported by repeated field measurements.

CICV5G is unusually suitable for this because the official field campaign contains repeated runs under multiple vehicle speeds, network modes, and directions. The W2S/S2W subset alone contains repeated 30-km/h and 50-km/h runs under n8/n78 conditions.

The proposed research object is:

> **Can repeated field drives be used to evaluate a communication-aware longitudinal speed decision without treating a learned QoS model as counterfactual ground truth?**

The answer will be studied through **Cross-Run Matched Speed Replay (CMSR)**.

---

## Why the current replay is not strong enough by itself

The current replay chooses among future offsets such as 10, 20, and 30 samples on the same logged route.

That is useful for studying decision-validity discipline, but it has two weaknesses.

### 1. The candidate is not a physically distinct executed trajectory

A different future offset is not the same thing as executing a different longitudinal or lateral motion policy. A reviewer can reasonably argue that the experiment demonstrates a timing/horizon-selection proxy rather than vehicle motion planning.

### 2. The current reactive baseline collapses to the mobility baseline

In `run_real_v2x_replay_planning.py`, P0 and P1 use the same mobility-only ranking. The archived primary replay confirms identical P0/P1 summary values.

That means the current P2-P1 result is effectively a predictive-QoS policy versus a mobility-only choice, despite the manuscript's reactive-baseline language.

This must not be hidden. The stronger experiment should replace the weak comparison rather than rhetorically defend it.

---

## Literature boundary

The new gap is **not** any of the following:

- QoS prediction from real V2X measurements;
- communication-aware motion planning;
- QoS-aware vehicle route/trajectory planning;
- radio-map-based planning;
- uncertainty-aware planning;
- task-aware radio world models;
- generic off-policy evaluation.

Those areas already exist.

Representative close work includes:

- CICV5G / Scientific Data 2026: real 5G V2N2V delay measurements across scenario, network, and speed conditions;
- Xu et al., Computer Networks 2023: field-tested V2X QoS prediction;
- Liu et al., JACIII 2025: route planning with predicted 5G QoS;
- Gordon et al., IEEE INFOCOM 2026: communication-aware motion planning from online radio maps;
- RMWorld, arXiv:2608.20126 (2026): task-aware radio world models with value-of-information calibration and credibility-filtered counterfactual rollouts;
- modern off-policy evaluation work: logged-data policy evaluation under limited overlap and potential confounding.

The non-overlap is the **field-evidence boundary for motion-conditioned actions**.

Existing QoS-aware planners typically evaluate actions against simulated, analytical, learned, or ray-traced communication surfaces. Generic off-policy evaluation assumes a logged behavior policy and action/propensity structure that ordinary vehicular QoS measurement campaigns do not necessarily provide.

CICV5G instead provides repeated measured runs under controlled motion/network configurations.

The research opportunity is to exploit that repeated experimental structure while refusing to invent outcomes where measured overlap is absent.

---

# Proposed method: Cross-Run Matched Speed Replay (CMSR)

## Evidence roles

Whole acquisition runs are assigned to three disjoint roles within each network/direction/speed stratum:

1. **training runs** — fit the QoS prediction model;
2. **donor runs** — provide measured candidate outcomes;
3. **query runs** — provide decision locations and contexts only.

No run may serve more than one role in one split.

## Motion action

The first protocol uses two longitudinal speed actions already present in the field data:

- 30 km/h;
- 50 km/h.

At a query position, the planner asks:

> If I choose the 30-km/h or 50-km/h operating mode for the next segment, what communication cost should I expect?

## Selection

A speed-conditioned predictor is fitted only on training runs.

For each query location, candidate scores combine:

- predicted communication delay;
- a simple normalized segment travel-time cost.

The measured donor outcomes are unavailable to the deployable policy.

## Evaluation

After speed selection, the chosen action is matched to donor measurements satisfying:

- same network mode;
- same travel direction;
- same nominal speed action;
- spatial distance below a predeclared caliper.

If both speed actions do not have measured donor support, the query is not counted as measured comparative evidence.

The measured donor outcome is revealed **only after selection**.

## Important claim boundary

CMSR is stronger than model-as-truth replay but is **not a randomized intervention**.

Different acquisition runs may differ in unobserved network load, traffic, blockage, or time-varying conditions.

Therefore:

- do not claim a causal average treatment effect of vehicle speed;
- do not call the matched donor outcome the exact physical counterfactual;
- report the estimand as a support-bounded cross-run matched field outcome;
- perform sensitivity analyses over caliper, donor composition, split assignment, and network/direction strata.

---

# Research hypotheses

## H1 — field-supported communication-aware speed adaptation

Within query locations having measured support for both speed actions, a speed-conditioned predictive policy can reduce matched measured delay and/or matched tail delay relative to a mobility-first fastest-speed policy.

This is the primary empirical question, not an assumed result.

## H2 — support gating

A policy that acts only when both speed candidates have adequate training support should reduce decisions driven by extrapolative QoS estimates.

Whether this improves QoS is an empirical question; a null QoS result is acceptable.

## H3 — context dependence

Any speed-conditioned communication effect is expected to vary by:

- n8 versus n78;
- W2S versus S2W;
- strong- versus weak-signal route regions.

A global average should not hide heterogeneous or null strata.

---

# Required baselines

The paper must include at least:

- **FAST:** always choose the higher-speed action;
- **SLOW:** always choose the lower-speed action;
- **PRED:** choose from the training-fitted speed-conditioned QoS prediction plus mobility cost;
- **PRED_SUPPORT:** only deviate from FAST when the candidate comparison has training support and a predeclared minimum predicted communication gain;
- **ORACLE_MATCHED:** nondeployable reference using donor measured outcomes, reported only as an upper-bound diagnostic.

A current-delay heuristic may be added later, but it should not be called a strong reactive baseline unless it produces a candidate-dependent decision using only causal information.

---

# Statistical design

## Independence

Timestamp rows are never inferential replicates.

The primary unit should remain the acquisition run.

However, query runs may share donor runs, creating dependence that ordinary paired run tests do not capture.

The final analysis should therefore use one of:

1. a cross-fitted design with disjoint query/donor fold roles and multiway cluster bootstrap over both query and donor run IDs; or
2. a conservative split-level analysis where independent split constructions form the replication unit only if run reuse is eliminated.

Until this is implemented, bootstrap intervals over query runs alone are development diagnostics, not confirmatory inference.

## Predeclared sensitivity analysis

Freeze before confirmatory evaluation:

- spatial caliper, e.g. 1, 2, 5 m;
- query spacing, e.g. 5 m;
- donor count rule;
- communication/mobility weights;
- minimum predicted gain for PRED_SUPPORT;
- split seeds;
- primary delay endpoint;
- tail-delay endpoint;
- family for multiplicity correction.

## Negative-result rule

If PRED does not improve measured outcomes over FAST, retain the result.

A valid paper can still conclude that:

> repeated field measurements reveal insufficient or context-dependent evidence for communication-aware speed adaptation, despite predictive QoS differences.

That would be a useful boundary result and stronger than tuning until a favorable planner effect appears.

---

# Why this can become a stronger paper

The paper would no longer depend on saying:

> "we predicted future QoS and changed a planner."

Instead, its core would be:

> **we construct a measured, support-bounded evaluation protocol for a physically interpretable motion variable using disjoint repeated field drives, and quantify when the field evidence is sufficient to justify a communication-aware motion decision.**

This is a narrower and more defensible research contribution.

It bridges:

- vehicular PQoS;
- communication-aware planning;
- logged-data decision evaluation;
- support/overlap diagnostics;
- real field measurements.

---

# Engineering status

Implemented on the research branch:

- `src/iscai/connectivity/real_v2x/matched_replay.py`
  - stratified run-role split;
  - cross-run spatial/speed matcher;
  - no same-run donor reuse.
- `scripts/run_real_v2x_matched_speed_replay.py`
  - 30/50-km/h speed actions;
  - training-only prediction;
  - donor-only measured outcome evaluation;
  - FAST/SLOW/PRED/PRED_SUPPORT/ORACLE_MATCHED policies.
- `scripts/analyze_real_v2x_matched_speed_replay.py`
  - run-level development summaries;
  - explicitly non-confirmatory query-run bootstrap diagnostics.
- `tests/test_matched_speed_replay.py`
  - run-role disjointness;
  - context/speed matching;
  - no same-run donor leakage.
- GitHub Actions research workflow updated to run the real-data development experiment.

---

# Go/no-go criteria for turning this into the canonical paper

## Go

Proceed to a new Paper-2 manuscript if the real-data run shows:

- substantial two-speed spatial overlap in held-out donor data;
- enough query runs in multiple network/direction strata;
- nontrivial PRED decisions;
- stable behavior under reasonable caliper/split sensitivity;
- measured outcome differences that can be reported without relying on timestamp pseudo-replication.

## Reframe

If overlap is adequate but the policy effect is null:

- publish as a measured evidence-boundary / negative-result study;
- emphasize when logged V2X data are insufficient for motion-policy claims.

## No-go for this dataset

If overlap is too sparse after honest run separation:

- do not relax matching until an effect appears;
- conclude that CICV5G is suitable for QoS modeling but not for this stronger motion-counterfactual claim;
- move the protocol to a dataset or new experiment with repeated randomized/controlled trajectory actions.

---

# Candidate paper title if CMSR succeeds

**From QoS Prediction to Measured Decision Evidence: Cross-Run Matched Replay for Communication-Aware Vehicle Speed Planning**

Alternative:

**When Can Field V2X Logs Support a Motion Decision? Matched-Speed Replay with Measured Counterfactual Support**

Avoid "causal" or "real-world counterfactual ground truth" in the title unless a stronger identification design is established.
