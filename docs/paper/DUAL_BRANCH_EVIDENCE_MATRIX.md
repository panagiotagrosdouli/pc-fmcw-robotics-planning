# Dual-branch evidence matrix

| Question | PC-FMCW-informed branch | Field-measured V2X branch | Cross-branch conclusion |
|---|---|---|---|
| Communication source | Analytical/model-based optical PC-FMCW-informed link | CICV5G field-measured 5G V2N2V traces | Complementary evidence sources, not interchangeable channels |
| Main QoS quantities | SNR, BER, outage, goodput | Delay, SINR, support distance/density | Planner must operate on a generic QoS/risk abstraction rather than one technology-specific scalar |
| Reactive baseline | P1 current connectivity-aware | P1 persistence/current delay | Strong baseline is mandatory |
| Predictive planner | P2 future trajectory-conditioned connectivity | P2 horizon-adaptive causal QoS prediction | Predictive information has decision value in both branches |
| Risk/support planner | P3 Monte Carlo/risk-sensitive | P3 uncertainty + empirical-support penalty | Risk awareness is best framed as robustness/validity control |
| Oracle | P4 simulator truth for connectivity only | Omitted for arbitrary positions | Real observational data do not justify a free oracle |
| Strongest positive result | P2 improves link metrics vs P1 | P2 reduces measured replay delay vs P1 | Predictive-versus-reactive contrast replicates qualitatively |
| P3 vs P2 | Small, non-significant link gains | No delay gain; lower unsupported exposure | Do not claim risk-awareness automatically improves QoS |
| Safety result | No planner-level collision-rate difference in verified baseline | Route replay is not a safety-validation experiment | No cross-branch safety improvement claim |
| Real measurements? | No | Yes, communication traces only | Measurement realism belongs to V2X decision validation, not PC-FMCW channel validation |
| Counterfactual validity | Simulator supplies model value at arbitrary candidates | Restricted/audited because measurements exist only on visited states | Explicit distinction is a methodological contribution |
| Main limitation | model calibration / optical realism | observational support / route coverage / distribution shift | The limitations are different and therefore complementary |

## Evidence hierarchy

### Level 1 — directly measured

Only the CICV5G communication records are directly measured in the real-data branch. Measured future delay is revealed after a route-replay choice and is never a causal planner input.

### Level 2 — model-derived

PC-FMCW SNR, BER, outage and goodput are outputs of the controlled analytical simulation bridge. They must always be labeled modeled quantities.

### Level 3 — learned prediction

The real-V2X future QoS estimates are learned from run-disjoint training data. Their validity depends on prediction horizon, context and empirical support.

### Level 4 — decision-derived

Planner effects such as selected trajectory, mobility deviation and unsupported-selection fraction are decision outcomes conditioned on the corresponding communication model/predictor.

## Claim map

### Supported now

- predictive P2 materially improves the controlled PC-FMCW-informed link result relative to reactive P1;
- one-step measured V2X delay is strongly persistent and naive learned spatial models are not automatically superior;
- calibrated context/spatial information has incremental value at longer planning horizons across the five tested grouped splits;
- in route-constrained held-out replay, P2 lowers mean measured delay relative to P1;
- P3 reduces reliance on empirically unsupported selections in measured replay, at additional mobility cost;
- the same predictive-connectivity decision abstraction can be instantiated with technology-specific modeled optical QoS and with field-measured V2X data without conflating the two channels.

### Partially supported / needs closure

- robustness of PC-FMCW effects across observation noise, target-prediction uncertainty, horizon and connectivity-weight sweeps;
- robustness of route-replay P2/P1 and P3/P2 results across multiple grouped split seeds;
- real-time suitability on target vehicle hardware;
- optical-specific superiority of angular/pointing-aware modeling over distance-only connectivity.

### Do not claim

- first communication-aware planner;
- first predictive communication-aware planner;
- first uncertainty-aware communication planner;
- first use of real V2X data in trajectory/QoS research;
- real measured PC-FMCW link validation;
- improved collision safety;
- P3 QoS superiority over P2;
- arbitrary off-route measured counterfactual validity.

## Closest contemporary work and differentiation

### Ullah et al., IEEE Access 2025

Trajectory planning of autonomous vehicles to ensure target QoS requirements in 6G mobile networks optimizes vehicle routes over a modeled mmWave/6G coverage graph using spectral-efficiency-based edge weights. This makes generic QoS-aware AV route planning non-novel. The present work differs by studying predictive-versus-reactive decision information, field-measured QoS generalization, empirical support validity and a separate PC-FMCW ISCAI-to-action branch.

DOI: 10.1109/ACCESS.2025.3543204

### Gordon et al., IEEE INFOCOM NetRobiCS 2026

Communication-aware robot motion planning via online radio-map estimation proactively avoids low-QoS regions using estimated service-specific risk maps. This makes generic proactive radio-map planning non-novel. The differentiation here is whole-drive anti-leakage measured-data evaluation, planning-horizon analysis and explicit support auditing rather than treating every queried map location as equally defensible.

DOI: 10.1109/INFOCOM59046.2026.11571354

### GP-driven adaptive tube MPC, Sensors 2026

Recent work combines Gaussian-process RSSI maps with uncertainty-aware tube MPC and validates the radio-prediction layer with real RSSI. Therefore uncertainty-aware communication-preserving motion itself is not novel. The present real-data branch should emphasize empirical-support validity and route-constrained measured decision replay rather than claiming uncertainty-aware motion as a first.

DOI: 10.3390/s26133981

### Decision-consistent online control for UAV-enabled ISAC, Vehicular Communications 2026

Recent ISAC work explicitly couples motion and post-motion sensing/communication resource decisions for UAV systems. Therefore the combined paper should not claim that mobility/control integration with ISAC is unprecedented. The PC-FMCW contribution is narrower: bridging a specific phase-coded FMCW vehicular ISCAI architecture through tracking/prediction into autonomous ego-motion planning, followed by a separate measured-V2X stress test of the decision principle.

DOI: 10.1016/j.vehcom.2026.101061

## Recommended claim sentence

> We do not propose communication-aware motion planning as a new problem. Instead, we study when predictive communication information is useful at the autonomous decision horizon, first through a PC-FMCW-specific model-based perception-to-action chain and then through leakage-safe, support-audited field-measured vehicular QoS replay.
