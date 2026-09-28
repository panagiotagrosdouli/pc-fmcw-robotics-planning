# Paper 2 — Verified Literature Backbone

This bibliography is a novelty and claim audit for the decision-validity manuscript. The canonical BibTeX is `references.bib`.

## A. Communication-aware motion planning is established

**Ghaffarkhah & Mostofi (2011), IEEE TAC. DOI 10.1109/TAC.2011.2164033.**  
Establishes communication-aware motion planning with learned/probabilistic channel structure.

**Muralidharan & Mostofi (2021), Annual Review of Control, Robotics, and Autonomous Systems. DOI 10.1146/annurev-control-071420-080708.**  
Use as the broad review establishing motion/communication co-optimization as a mature field.

**Hurst, Cai & Mostofi (2021), IEEE ICC. DOI 10.1109/ICC42927.2021.9500912.**  
Establishes obstacle-aware communication-aware RRT* planning.

**Cai & Mostofi (2022), IEEE TCNS. DOI 10.1109/TCNS.2022.3158746.**  
Establishes joint motion, communication, and sensing optimization in real wireless channel environments.

**Implication for our manuscript:** never claim novelty for adding connectivity to a motion objective.

## B. Field-measured predictive QoS is established

**Sliwa et al. (2018), IEEE VTC-Fall. DOI 10.1109/VTCFall.2018.8690856.**  
Uses mobility prediction and ML connectivity maps for context-predictive car-to-cloud communication with field evaluation.

**Hernangómez et al. (2023), Berlin V2X, VTC2023-Spring. DOI 10.1109/VTC2023-Spring57618.2023.10200750.**  
Provides GPS-located multi-vehicle/multi-RAT measurements for ML and proactive V2X studies.

**Palaios et al. (2023), IEEE Access. DOI 10.1109/ACCESS.2023.3303528.**  
Important for our methodology: shows strong sensitivity of vehicular QoS prediction to data splitting and warns that random splits can overestimate performance.

**Partani et al. (2025), VTC2025-Spring. DOI 10.1109/VTC2025-SPRING65109.2025.11174805.**  
Establishes further predictive QoS modeling on Berlin V2X data using lead-vehicle and historical information.

**Implication for our manuscript:** never claim novelty for PQoS or for using field measurements to predict vehicular QoS.

## C. QoS-aware vehicle/robot planning is established

**Ullah et al. (2025), IEEE Access. DOI 10.1109/ACCESS.2025.3543204.**  
Optimizes autonomous-vehicle trajectories over a simulated 6G/mmWave coverage graph using QoS/spectral-efficiency information.

**Gordon et al. (2026), IEEE INFOCOM/NetRobiCS. DOI 10.1109/INFOCOM59046.2026.11571354.**  
Builds online radio maps, converts them to service-specific communication-risk maps, and uses them in robot motion planning.

**Kim, Kim & Suh (2026), Sensors. DOI 10.3390/s26133981.**  
Combines Gaussian-process radio-map prediction with adaptive tube MPC and explicitly handles communication/motion uncertainty.

**Implication for our manuscript:** never claim novelty for proactive radio-map navigation, uncertainty-aware communication planning, or QoS-aware vehicle trajectory optimization.

## D. Predictive radio maps and task-aware counterfactual models are established

**Cheng et al. (2026), RadioMapMotion, IEEE TCCN. DOI 10.1109/TCCN.2026.3685413.**  
Establishes proactive spatio-temporal radio-map prediction as a dedicated benchmark problem.

**Wang, Cheng & Huan (2026), RMWorld, arXiv:2608.20126.**  
Very close conceptual comparison point. Explicitly studies task-aware radio world models, value-of-information-guided channel calibration, and credibility of counterfactual communication rollouts.

**Implication for our manuscript:** do not claim novelty for decision relevance, counterfactual communication modeling, or credible model rollouts in general.

## E. Distribution shift and uncertainty

**Zou & Liu (2024), AAAI. DOI 10.1609/aaai.v38i15.29673.**  
Shows that ordinary split-conformal validity depends on exchangeability and can fail in OOD settings.

**Implication for our manuscript:** conformal residual intervals are reported as empirical diagnostics, not as universal calibrated probabilities under drive-level distribution shift.

## F. Primary measured dataset

**Zhang et al. (2026), Scientific Data. DOI 10.1038/s41597-026-07239-7.**  
CICV5G field-measured 5G/V2N2V delay dataset with synchronized radio and vehicle context. The repository study uses a 38-run / 43,045-sample subset.

Archive DOI: 10.5281/zenodo.17475688.

## What is left for this paper to own

The manuscript is intentionally positioned in the intersection left after acknowledging all of the prior art above:

1. future QoS must be evaluated against a strong causal baseline at the motion-decision horizon;
2. empirical training-measurement support is audited separately from predictive uncertainty;
3. logged counterfactual decisions are evaluated only where a future measured outcome exists;
4. that future measured outcome is withheld until after the planner chooses;
5. repeated grouped splits are used as dependent sensitivity checks rather than pseudoreplication.

The core protocol name is **measurement-supported counterfactual replay (MSCR)**.

## Safe novelty sentence

> Rather than proposing another predictive communication-aware planner, we study the evidential boundary between QoS prediction and motion decisions under logged field measurements, separating causal predictive value, empirical measurement support, and measured post-selection evaluability.

## Phrases to reject during manuscript editing

Reject or rewrite any sentence that says or implies:

- first communication-aware planner;
- first predictive QoS planner;
- first field-measured vehicular QoS prediction;
- first radio-map-aware vehicle planner;
- first uncertainty-aware communication planner;
- first task-aware counterfactual radio model;
- first decision-relevant channel-learning method;
- real-world closed-loop validation;
- statistically significant P2 superiority after Holm correction;
- CICV5G validates PC-FMCW optical propagation.
