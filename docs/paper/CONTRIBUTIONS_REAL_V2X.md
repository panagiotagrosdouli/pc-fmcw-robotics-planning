# Defensible contribution statement — real V2X branch

The real-data extension should be presented with deliberately narrow claims.

## Contribution 1 — leakage-safe field-measured QoS benchmark for motion decisions
We introduce a reproducible evaluation protocol that uses whole CICV5G runs as independent train/calibration/test groups, preventing neighboring measurements from the same drive from being randomly distributed across splits. The protocol evaluates persistence and learned predictors at multiple future horizons and uses drive/run-level statistical units.

## Contribution 2 — empirical-support auditing of trajectory-conditioned QoS queries
Every future communication query can be accompanied by measurement-support diagnostics derived only from training data, including nearest-measurement distance and local density. This exposes when a trajectory-conditioned QoS estimate relies on weak empirical support instead of silently treating extrapolated predictions as equally trustworthy.

## Contribution 3 — horizon-adaptive causal communication prediction
The experiments show that one-step CICV5G QoS is strongly persistent and that naive spatial/tree models do not outperform persistence. A calibration-only context-adaptive fusion retains persistence when spatial information is unhelpful and extracts incremental delay-prediction value at longer planning horizons. Across five grouped split seeds, the fusion improves delay MAE over persistence in every seed at approximately 1.1, 2.8 and 5.5 s horizons.

## Contribution 4 — measured-support route replay with explicit validity/QoS trade-off
To avoid fabricated ground truth for unvisited positions, the decision experiment is restricted to measured future states on held-out routes. Predictive P2 reduces mean measured delay relative to reactive P1 by approximately 0.79 ms across nine held-out runs, while support-aware P3 does not further improve delay but reduces unsupported selections by approximately 1.84 percentage points at additional mobility cost. This separates predictive decision value from inference-validity control.

## Contribution 5 — cross-technology decision-layer validation without false channel claims
The existing PC-FMCW branch remains a technology-specific model-based optical study. CICV5G provides a separate field-measurement-informed test of the common predictive-connectivity decision principle. The work explicitly does not relabel 5G data as PC-FMCW measurements or claim real optical-link validation.

## Claims that must not appear in the paper
Do not claim:

- communication-aware planning is new;
- QoS-risk-map navigation is new;
- uncertainty-aware communication planning is new;
- using real V2X data for QoS prediction is new;
- P3 outperforms P2 in communication QoS;
- ordinary conformal intervals are calibrated event probabilities under distribution shift;
- the replay is closed-loop real-vehicle autonomous-driving validation;
- the 5G results validate PC-FMCW optical propagation;
- the current reviewed combination is a universal first-ever result.

A defensible novelty phrasing is:

> In the literature reviewed for this study, we found no close prior work combining field-measured vehicular QoS, whole-drive anti-leakage evaluation, horizon-dependent causal prediction, explicit empirical support auditing, and measured-support route replay for communication-aware motion decisions.
