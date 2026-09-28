# Paper 1 — 2026 Novelty Audit

Date: 2026-09-28

## Reviewer-style challenge

**Why is this not redundant with communication-aware motion planning, FSO-aware control, or planning-oriented ISAC?**

## Prior art that must be conceded

| Literature | What it already establishes |
|---|---|
| Ghaffarkhah & Mostofi 2011 | communication-aware motion planning using learned wireless-channel structure |
| Muralidharan & Mostofi 2021 | communication-aware robotics as a mature research field |
| Hurst et al. 2021 | obstacle-aware communication-aware RRT* |
| Cai & Mostofi 2022 | joint motion, communication, and sensing optimization |
| Ullah et al. 2025 | QoS-aware autonomous-vehicle trajectory optimization |
| Gordon et al. 2026 | proactive online radio-map robot planning |
| Silano et al. 2025 | optical/FSO communication constraints integrated into NMPC |
| Jin et al. 2026 | planning-oriented ISAC coupling sensing uncertainty/resources to vehicle motion |
| Vehicular VLC literature | directional, orientation-sensitive optical vehicle channels |

## Upstream PC-FMCW source

Liu et al. introduce the phase-coded FMCW laser-headlamp architecture for integrated sensing, communication, and illumination.

Our paper must cite this as the upstream system and must not imply that the downstream analytical channel is part of their experimentally validated channel model.

## Narrow non-overlap

This paper studies a controlled downstream mechanism:

1. target-state information is available from the upstream sensing/tracking concept;
2. one common predictor produces future target positions;
3. all planners share candidate generation and safety information;
4. P1 evaluates communication using present/myopic geometry;
5. P2 evaluates communication using future candidate-dependent geometry;
6. a directional-vs-distance-only ablation tests whether the effect depends on the angular optical mechanism.

The strongest novelty is therefore **experimental isolation of predictive directional connectivity as a downstream mechanism**, not generic communication-aware planning.

## Claims that are safe

- P2 improves all five declared modeled communication endpoints relative to P1 in the frozen V7 simulator.
- The independent unit is the seed after scenario aggregation.
- P3 is worse than P2 under the implemented risk formulation.
- P4 does not show a supported additional communication benefit.
- The directional P2-P1 effect collapses when angular attenuation is removed.
- The evidence is model-relative.

## Claims that are unsafe

Do not claim communication-aware planning is new, optical communication-aware control is new, ISAC-to-planning coupling is new, PC-FMCW optical propagation is measured or calibrated here, the directional surrogate is physically validated, zero sampled collisions prove safety, 193.4 THz is a blue-light headlamp carrier, P3 is a superior risk-aware planner, or P4 proves global optimality.

## Main reviewer risk

The main weakness remains external validity: all primary PC-FMCW planning evidence is simulation/model based.

The paper should therefore be submitted as a **controlled algorithmic/mechanism study**. A venue expecting hardware optical validation will likely require additional evidence.

## Recommended one-sentence positioning

> We isolate the downstream value of future directional connectivity prediction in a PC-FMCW-informed vehicular planning stack under a common safety interface and show through a distance-only ablation that the modeled benefit depends on angular link geometry.
