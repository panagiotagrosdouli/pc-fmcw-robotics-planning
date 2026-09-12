# Dual-branch evidence matrix

| Question | PC-FMCW-informed branch | Field-measured V2X branch | Cross-branch conclusion |
|---|---|---|---|
| Communication source | Analytical/model-based optical PC-FMCW-informed link | CICV5G field-measured 5G V2N2V traces | Complementary evidence sources, not interchangeable channels |
| Main QoS quantities | SNR, BER, outage, goodput | Delay, SINR, support distance/density | Planner must operate on a generic QoS/risk abstraction rather than one technology-specific scalar |
| Reactive baseline | P1 current connectivity-aware | P1 persistence/current delay | Strong baseline is mandatory |
| Predictive planner | P2 future trajectory-conditioned connectivity | P2 horizon-adaptive causal QoS prediction | Predictive information has decision value in both branches |
| Risk/support planner | P3 Monte Carlo/risk-sensitive | P3 uncertainty + empirical-support penalty | Risk awareness is best framed as robustness/validity control |
| Oracle | P4 simulator truth for connectivity only | Omitted for arbitrary positions | Real observational data do not justify a free oracle |
| Strongest positive result | P2 improves link metrics vs P1 in the verified historical baseline | Primary split shows lower measured replay delay for P2 vs P1; grouped multi-split robustness is being executed | Predictive-versus-reactive contrast is the cross-branch hypothesis, but each branch keeps its own evidence level |
| P3 vs P2 | Small, non-significant link gains in the historical baseline | No delay gain; lower unsupported exposure in the primary split | Do not claim risk-awareness automatically improves QoS |
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

- the historical 20-seed PC-FMCW-informed baseline supports a P2-versus-P1 modeled-connectivity advantage;
- one-step measured V2X delay is strongly persistent and naive learned spatial models are not automatically superior;
- calibrated context/spatial information has incremental value at longer planning horizons across the five tested grouped split assignments;
- the primary route-constrained held-out replay shows a lower-delay direction for P2 relative to P1 at a small mobility cost;
- the primary replay shows that P3 can reduce reliance on empirically unsupported selections, but does not improve measured delay relative to P2;
- the same predictive-connectivity decision abstraction can be instantiated with technology-specific modeled optical QoS and with field-measured V2X data without conflating the two channels.

### Partially supported / needs closure

- the frozen 50-seed Part-B-final-v1 confirmatory PC-FMCW result;
- robustness of PC-FMCW effects across observation noise, target-prediction uncertainty, horizon, link-model mismatch and connectivity-weight sweeps;
- robustness of route-replay P2/P1 and P3/P2 effects across multiple grouped split assignments;
- real-time suitability on target vehicle hardware;
- optical-specific superiority of angular/pointing-aware modeling over distance-only connectivity.

### Do not claim

- first communication-aware planner;
- first predictive communication-aware planner;
- first uncertainty-aware communication planner;
- first optical/FSO trajectory optimizer;
- first optical-ISAC mobility optimizer;
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

### Nafees et al., IEEE WCNC 2025 — optical ISAC trajectory optimization

Integrated Sensing and Communication for UAV Trajectory Optimization in Mixed FSO-RF Networks in Dynamic Weather Conditions uses back-scattered optical/FSO sensing information to estimate channel conditions and dynamically optimize UAV trajectory, with evaluation incorporating real hourly visibility/weather data. This is important prior art because it shows that **optical ISAC plus mobility optimization is already established**. The PC-FMCW branch must therefore differentiate through the specific vehicular laser-headlamp architecture, PC-FMCW sensing/tracking chain, ego-vehicle motion decision layer and predictive-vs-reactive information study rather than through the generic phrase "optical ISAC trajectory optimization."

DOI: 10.1109/WCNC61545.2025.10978163

### FSO trajectory and pointing-error optimization literature

FSO communication has an established UAV trajectory-optimization literature, including multi-UAV service-time optimization, cloud/attenuation-aware trajectories, hybrid RF/FSO relay optimization and explicit pointing-error-aware trajectory design. Accordingly, directional optical geometry and pointing loss are important mechanisms to model, but their mere inclusion is not a novelty claim.

Representative recent work includes:

- Moon et al., generalized pointing-error model and trajectory optimization for fixed-wing UAV FSO links, IEEE Transactions on Wireless Communications, 2025, DOI 10.1109/TWC.2025.3549062.
- Hybrid RF/FSO UAV trajectory/resource optimization studies published in 2026.

### Visible-light robot path planning prior art

Visible-light-communication-aware robot path planning also exists, including work that fuses illumination-intensity and obstacle maps into path costs. Therefore a claim such as "first robot path planner considering optical communication" would be indefensible. The present work should instead focus on predictive closed-loop vehicular planning from a PC-FMCW sensing/tracking architecture, not generic VLC path planning.

## Recommended claim sentence

> We do not propose communication-aware, optical-aware, or ISAC-aware motion planning as new problems. Instead, we study when predictive communication information is useful at the autonomous decision horizon, first through a PC-FMCW-specific vehicular perception-to-action chain and then through leakage-safe, support-audited field-measured vehicular QoS replay.
