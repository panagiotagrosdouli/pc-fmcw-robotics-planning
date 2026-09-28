# Related-work positioning — Paper 2 decision-validity framing

## What is already prior art

The manuscript must not claim novelty for any of the following ideas by themselves:

- communication-aware motion planning;
- learning wireless-channel or radio-map structure and using it in planning;
- obstacle-aware communication planning;
- joint motion/communication/sensing optimization;
- predictive QoS from vehicular field measurements;
- connectivity maps for proactive vehicular communication;
- QoS-aware autonomous-vehicle route selection;
- predictive or spatio-temporal radio maps;
- uncertainty-aware communication-preserving MPC;
- task-aware or credibility-filtered counterfactual radio-world-model rollouts.

Representative prior work establishing these areas includes:

- Ghaffarkhah & Mostofi, IEEE TAC 2011, DOI 10.1109/TAC.2011.2164033.
- Muralidharan & Mostofi, Annual Review of Control, Robotics, and Autonomous Systems 2021, DOI 10.1146/annurev-control-071420-080708.
- Hurst, Cai & Mostofi, IEEE ICC 2021, DOI 10.1109/ICC42927.2021.9500912.
- Cai & Mostofi, IEEE TCNS 2022, DOI 10.1109/TCNS.2022.3158746.
- Sliwa et al., IEEE VTC-Fall 2018, DOI 10.1109/VTCFall.2018.8690856.
- Palaios et al., IEEE Access 2023, DOI 10.1109/ACCESS.2023.3303528.
- Hernangómez et al., VTC2023-Spring, DOI 10.1109/VTC2023-Spring57618.2023.10200750.
- Partani et al., VTC2025-Spring, DOI 10.1109/VTC2025-SPRING65109.2025.11174805.
- Ullah et al., IEEE Access 2025, DOI 10.1109/ACCESS.2025.3543204.
- Gordon et al., IEEE INFOCOM 2026, DOI 10.1109/INFOCOM59046.2026.11571354.
- Cheng et al., IEEE TCCN 2026 (RadioMapMotion), DOI 10.1109/TCCN.2026.3685413.
- Kim et al., Sensors 2026, DOI 10.3390/s26133981.
- Wang, Cheng & Huan, RMWorld, arXiv:2608.20126.
- Zou & Liu, AAAI 2024, DOI 10.1609/aaai.v38i15.29673, for the exchangeability/OOD limitation of ordinary split conformal prediction.

## The actual gap pursued here

The paper is not positioned around a new planner. It is positioned around the **decision-validity problem created when logged field measurements are used to justify counterfactual motion choices**.

A logged vehicular dataset observes communication outcomes along the trajectory that was actually driven. A planner asks what would happen for alternative future states. Those two objects are not automatically equivalent. A learned radio/QoS model can generate values at unvisited positions, but those model outputs must not be relabeled as field-measured counterfactual truth.

The manuscript therefore separates three validity layers:

1. **Predictive validity** — whether a future-QoS estimate adds information beyond a strong causal persistence baseline at the horizon where motion can act.
2. **Empirical-support validity** — whether a candidate-state query is represented by the training measurements, independently of residual predictive uncertainty.
3. **Outcome validity** — whether the selected candidate has a future field measurement that was hidden at decision time and can be revealed after selection for evaluation.

The core evaluation protocol is named **measurement-supported counterfactual replay (MSCR)**. Candidate choices are restricted to later measured states from the same held-out route, and future measured delay is hidden until after planner selection. This deliberately trades arbitrary off-route evaluation for a stronger evidential boundary: the reported post-decision QoS outcome is a measurement, not a prediction from the model being evaluated.

## Closest overlaps and explicit distinctions

### Sliwa et al. / vehicular PQoS
These works establish field-measured context-predictive vehicular communication. Our paper must not claim that field-measured PQoS is new. The distinction is that PQoS is inserted into a motion-decision replay with an explicit support audit and a measured post-selection outcome.

### Palaios et al.
This work already shows that split methodology can dramatically affect vehicular QoS prediction. Whole-drive splitting is therefore not claimed as a universal novelty by itself. In our paper it is one component of a decision-level validity pipeline.

### Ullah et al.
This work establishes QoS-aware autonomous-vehicle trajectory planning. Our distinction is not the use of QoS in the objective, but evaluation from finite field logs without assuming a complete communication map.

### Gordon et al. and Kim et al.
These works establish proactive radio-map planning and uncertainty-aware communication-preserving control. Our distinction is that empirical measurement support is audited separately from predictive uncertainty and that decision outcomes are evaluated through withheld route measurements rather than a simulated or model-complete communication field.

### RadioMapMotion
This work establishes proactive spatio-temporal radio prediction. Our paper is not a radio-map prediction benchmark; it studies whether prediction is decision-useful and evaluable from logged field outcomes.

### RMWorld
RMWorld explicitly studies task-aware, decision-relevant channel uncertainty and credibility of counterfactual model rollouts. Therefore the manuscript must not claim that decision relevance or credible counterfactual communication reasoning is new. The distinction is evidence: RMWorld operates with model-based rollouts, while our paper asks how logged field measurements can support or fail to support counterfactual motion evaluation.

## Defensible positioning sentence

A safe statement for the manuscript is:

> Rather than proposing another communication-aware planner, this study examines the evidential boundary between predictive QoS and motion decisions when only logged vehicular measurements are available, separating causal predictive value, empirical measurement support, and measured post-decision evaluability.

Do not use a universal first-of-kind claim unless a formal systematic review is completed.
