# Paper 3 Literature and Novelty Audit

## Scope

Paper 3 asks when a communication forecast is sufficiently reliable, empirically supported, and decision-relevant to justify changing robot motion. The contribution is deliberately narrower than communication-aware planning, predictive QoS planning, uncertainty-aware MPC, radio-map navigation, or optical/ISAC trajectory optimization.

## Closest prior art checked

1. Gordon et al., *Communication-aware Robot Motion Planning via Online Estimation of Radio Maps*, IEEE INFOCOM / NetRobiCS 2026, DOI 10.1109/INFOCOM59046.2026.11571354. This work integrates estimated radio maps with motion planning and converts QoS estimates into service-specific risk maps. It establishes that proactive communication-aware robot motion planning itself is prior art.
2. Kim et al., *GP-Driven Adaptive Tube MPC for Communication-Preserving Navigation of Mobile Relay Robots in Indoor Disaster Environments*, Sensors 2026, DOI 10.3390/s26133981. This work combines GP mean/uncertainty with a lower-confidence-bound communication constraint and adaptive tube MPC. It establishes that uncertainty-aware communication-preserving control is prior art.
3. Ullah et al., *Trajectory Planning of Autonomous Vehicles to Ensure Target QoS Requirements in 6G Mobile Networks*, IEEE Access 2025, DOI 10.1109/ACCESS.2025.3543204. This work selects AV routes according to spatial network QoS and establishes target-QoS trajectory planning as prior art.
4. Optical/FSO/ISAC trajectory-optimization literature must be treated as prior art for optimizing motion against an optical/wireless communication objective. Paper 3 therefore makes no novelty claim for optical or ISAC trajectory optimization.
5. Selective prediction, abstention/rejection, conformal uncertainty, OOD/support detection, decision-focused learning, and robust/risk-aware planning are neighboring methodological families. Paper 3 must not claim these generic concepts as new.

## Defensible novelty target

The candidate contribution is the experimental and decision-level separation of **forecast quality** from **forecast actionability** in communication-aware motion planning. A forecast is actionable only when its predicted communication advantage survives an explicitly predeclared decision rule that accounts for uncertainty, empirical measurement support, and mobility cost. The primary scientific object is therefore not the predictor alone but the chain:

`forecast -> support/uncertainty -> act/abstain decision -> realized measured outcome`.

The strongest defensible claim, if supported by frozen experiments, is that communication-forecast actionability can be evaluated as a downstream decision property and that support/uncertainty gating changes the rate and validity of motion changes. This is narrower than claiming a new communication-aware planner.

## Explicit non-claims

- Generic communication-aware planning is not new.
- Predictive communication planning is not new.
- Radio-map planning is not new.
- Uncertainty-aware or risk-aware planning is not new.
- Lower-confidence-bound planning is not new.
- Selective prediction/abstention is not new.
- Optical/FSO/ISAC trajectory optimization is not new.
- Field-measured V2X results do not validate the PC-FMCW optical model.
- Offline route-constrained replay is not real-road closed-loop autonomy.

## Novelty risk

The novelty risk is substantial if Paper 3 is framed as merely adding uncertainty to a communication-aware planner. The 2026 GP/tube-MPC literature already does that directly. The paper must instead make the empirical decision question central: when should a forecast be allowed to alter motion, how often does that decision help after outcomes are revealed, what regret is incurred, and how does empirical measurement support change the communication/mobility tradeoff?

## Go/no-go conclusion

**GO, with a narrow claim boundary.** Proceed only with the actionability/decision-validity framing. If experiments reduce to a conventional uncertainty-weighted communication objective without a distinct act/abstain evaluation, the Paper 3 novelty case should be considered weak and the contribution should be reformulated before confirmatory inference.

## Evidence discipline

This audit is pre-result. It does not imply that A1 beats A0 or that A2 beats A1. Those statements require actual frozen-protocol decision-level evidence. Negative and mixed results remain valid endpoints.