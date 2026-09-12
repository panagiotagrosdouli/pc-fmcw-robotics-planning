# Related-work positioning — real V2X extension

Communication-aware motion planning is not new. Foundational work learned probabilistic RF/channel structure and planned robot motion subject to connectivity objectives; subsequent work introduced online radio maps, resilient reconnection, formal temporal-logic communication constraints, joint communication-motion optimization and communication-aware UAV trajectories.

The vehicular literature is also mature enough that QoS-aware trajectory selection itself cannot be claimed as novel. Ullah et al. (IEEE Access, 2025) optimize autonomous-vehicle routes over a simulated mmWave/6G coverage graph to improve minimum spectral efficiency. Recent predictive-QoS work trains models on real V2X traces, including Berlin V2X measurements.

The closest recent conceptual overlap is proactive radio-map planning. Gordon et al. (IEEE INFOCOM NetRobiCS, 2026) estimate radio maps and convert them to service-specific communication-risk maps used by a motion planner. Kim et al. (Sensors, 2026) combine GPR radio-map uncertainty with adaptive tube MPC for communication-preserving mobile-relay navigation. Therefore proactive prediction and uncertainty-aware communication planning are both existing ideas.

Very recent radio-world-model research also evaluates credibility of counterfactual communication rollouts in multi-UAV control. This further rules out a broad claim that "counterfactual-aware communication planning" is itself new.

The present work is instead positioned around an empirical-validity problem specific to using logged field measurements for planning: measurements cover the route that was driven, while motion planning asks questions about alternative future states. The study therefore combines complete-run anti-leakage splitting, strong causal persistence baselines, horizon-specific predictive evaluation, explicit training-measurement support diagnostics, grouped-shift uncertainty analysis, and route-constrained measured outcome replay.

The intended novelty statement is deliberately scoped: in the literature reviewed here, no close prior study was found that combines these elements for field-measured vehicular QoS motion decisions. This is not presented as a universal first-ever claim.

## Core references to cite in manuscript
- Ghaffarkhah & Mostofi, IEEE TAC 2011, DOI 10.1109/TAC.2011.2164033.
- Caccamo et al., IEEE/RSJ IROS 2017, DOI 10.1109/IROS.2017.8206020.
- Oh et al., Journal of Guidance, Control, and Dynamics 2018, DOI 10.2514/1.G003099.
- Zhang et al., Applied Sciences 2022, DOI 10.3390/app12126261.
- Ullah et al., IEEE Access 2025, DOI 10.1109/ACCESS.2025.3543204.
- Gordon et al., IEEE INFOCOM 2026, DOI 10.1109/INFOCOM59046.2026.11571354.
- Kim et al., Sensors 2026, DOI 10.3390/s26133981.
- Zhang et al., Scientific Data 2026 (CICV5G), DOI 10.1038/s41597-026-07239-7.
- Zou & Liu, AAAI 2024, DOI 10.1609/aaai.v38i15.29673, for OOD limitations of ordinary split conformal prediction.
- Wang et al., RMWorld preprint, arXiv:2608.20126, as a recent counterfactual radio-world-model comparison point.
