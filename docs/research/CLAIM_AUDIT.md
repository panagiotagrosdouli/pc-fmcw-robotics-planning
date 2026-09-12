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
| Real-data planner is real-world autonomous-driving validation | DO NOT CLAIM | Planner evaluation remains offline/counterfactual. |
| Support-aware P3 improves QoS over P2/P1 | NOT YET SUPPORTED | Requires completed real-data planner experiment and paired statistics. |
| Method is real-time capable | NOT YET SUPPORTED | Must report measured decision latency. |
