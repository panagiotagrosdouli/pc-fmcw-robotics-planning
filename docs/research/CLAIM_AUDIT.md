# Claim audit

| Claim | Status | Evidence needed / boundary |
|---|---|---|
| Communication-aware motion planning is novel | DO NOT CLAIM | Field is mature since at least 2011. |
| Proactive QoS-risk-map planning is novel | DO NOT CLAIM | Closely overlaps Gordon et al., INFOCOM NetRobiCS 2026. |
| CICV5G contains real 5G V2N2V delay plus vehicle/network state | SUPPORTED | 2026 Scientific Data descriptor and public repository. |
| Our framework prevents temporal/run leakage by grouped splitting | SUPPORTED BY CODE | `blocked_run_split`; must retain in all reported experiments. |
| Our framework audits counterfactual spatial support | SUPPORTED BY CODE | nearest measured distance + local density. |
| Conformal intervals are calibrated probabilities | DO NOT CLAIM | Implemented intervals provide marginal coverage, not event probabilities. |
| Real V2X data validate PC-FMCW optical communication | DO NOT CLAIM | Different communication technology. |
| Real-data planner is real-world autonomous-driving validation | DO NOT CLAIM | Planner evaluation remains route-constrained offline measured replay; future measured QoS is outcome-only. |
| Predictive P2 improves measured delay over reactive P1 in the primary replay split | SUPPORTED, NARROW | Across 9 held-out runs, paired mean measured delay changes by -0.792 ms (95% bootstrap CI -1.723 to -0.138 ms; paired Wilcoxon p=0.0469). The violation-fraction change is -0.00279 with p=0.0625, so do not claim a statistically significant threshold-violation reduction from this split alone. |
| Support-aware P3 improves QoS over P2 | NOT SUPPORTED | P3-P2 mean measured delay is +0.073 ms (p=0.742) and threshold-violation fraction +0.00034 (p=0.50). Do not claim QoS superiority. |
| Support-aware P3 reduces unsupported decision exposure relative to P2 | SUPPORTED, NARROW | Across 9 held-out runs, unsupported fraction changes by -0.01836 (95% bootstrap CI -0.03214 to -0.00603; paired Wilcoxon p=0.03125), with additional mobility deviation +0.01052 (p=0.0078). Interpret as an inference-validity / support trade-off, not a QoS gain. |
| Lightweight route-constrained decision scoring is computationally practical in the CI implementation | SUPPORTED, IMPLEMENTATION-LEVEL | Mean decision computation was about 8.63 ms and p95 about 8.85 ms on the hosted CI runner for this replay implementation. Do not generalize this to end-to-end vehicle real-time capability or embedded hardware. |
| The strongest measured-data contribution is support-aware inference validity rather than a new radio-map predictor | SUPPORTED BY RESULTS | Persistence is a strong baseline; naive/global spatial models are often worse. Horizon-adaptive fusion improves delay MAE in all five grouped splits at 20/50/100-step horizons, while support-aware planning mainly reduces unsupported exposure. |
