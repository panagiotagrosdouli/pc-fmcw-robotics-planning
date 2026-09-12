# Paper 2 — Verified Literature Backbone

This is a claim-audit bibliography for the manuscript, not yet the final venue-formatted reference list. Entries below were verified against publisher/author/institutional metadata before inclusion.

## Foundational communication-aware motion planning

**A. Ghaffarkhah and Y. Mostofi, “Communication-Aware Motion Planning in Mobile Networks,” IEEE Transactions on Automatic Control, vol. 56, no. 10, pp. 2478–2485, 2011. DOI: 10.1109/TAC.2011.2164033.**

Use for: establishing that communication-aware motion planning and channel-learning-aware navigation are long-standing prior art. Do not claim that adding a communication objective to robot motion is novel.

## Contemporary radio-map-aware predictive planning

**D. Gordon, M. B. Khan, T. Zugno, Y. Wu, M. Boban, X. An, and F. Dressler, “Communication-aware Robot Motion Planning via Online Estimation of Radio Maps,” IEEE INFOCOM 2026, NetRobiCS, pp. 1–6, 2026. DOI: 10.1109/INFOCOM59046.2026.11571354.**

Use for: showing that radio-map estimation, service-aware QoS risk maps, and proactive communication-aware motion planning already exist. Their evaluation is simulation-based and uses ray-tracing-derived radio maps; this helps distinguish our field-measurement support-audit contribution.

## Autonomous-vehicle QoS-aware trajectory planning

**I. Ullah, H. El Sayed, A. A. Dowhuszko, M. A. Khan, and J. Hämäläinen, “Trajectory Planning of Autonomous Vehicles to Ensure Target QoS Requirements in 6G Mobile Networks,” IEEE Access, vol. 13, pp. 37361–37369, 2025. DOI: 10.1109/ACCESS.2025.3543204.**

Use for: establishing prior art on vehicle trajectory selection from network QoS maps. Their Manhattan-grid study optimizes trajectory using spectral-efficiency information and reports gains in simulated network performance. Therefore generic “QoS-aware AV trajectory planning” is not our novelty.

## Primary field-measurement dataset

**X. Zhang, L. Xiong, P. Zhang, et al., “5G communication delay dataset for cloud-based vehicle planning and control,” Scientific Data, vol. 13, article 878, 2026. DOI: 10.1038/s41597-026-07239-7.**

Dataset archive: Zenodo DOI 10.5281/zenodo.17475688.

Use for: CICV5G provenance, field-measured V2N2V delay, synchronized RSRP/SINR/Cell ID and vehicle motion data, public/private networks, and the intended use for communication-delay modeling and delay-aware planning/control research.

Important wording: during acquisition, the cloud service used for delay measurement did not run a planning/control solver; it performed immediate echo-back processing for delay measurement. Our planner is downstream research built on the released measurements.

## Related-work positioning text to preserve

A defensible manuscript sentence is:

> Communication-aware motion planning, radio-map-aware navigation, and QoS-based vehicle trajectory optimization are established research directions. Our contribution is therefore not the use of predicted connectivity in a motion objective. We instead study the validity of counterfactual planner queries when the predictor is learned from field measurements, combining whole-run anti-leakage evaluation, horizon-dependent prediction, explicit empirical measurement-support auditing, and route-constrained measured replay.

## Citation audit rules

- Cite Ghaffarkhah & Mostofi when stating that communication-aware motion planning predates this work.
- Cite Gordon et al. when discussing modern radio-map/risk-map robot planning.
- Cite Ullah et al. when discussing network-QoS-aware autonomous-vehicle trajectory optimization.
- Cite Zhang et al. for all CICV5G acquisition, variables, scale, testbed, license, and intended-use facts.
- Do not use any of these references to claim that the exact combination of our four methodological controls is formally unique unless a broader systematic review supports that claim.
- Do not infer physical optical/PC-FMCW validation from CICV5G.
