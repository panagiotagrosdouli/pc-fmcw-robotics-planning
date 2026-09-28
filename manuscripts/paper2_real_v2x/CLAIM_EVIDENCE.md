# Paper 2 Claim-Evidence Matrix — decision-validity framing

| Claim | Evidence | Statistical support | Boundary | Status |
|---|---|---|---|---|
| One-step persistence is stronger than the tested naive learned spatial/tree baselines | Primary grouped split predictor study | Direct held-out metric comparison | CICV5G subset-specific | SUPPORTED |
| Learned spatial/context information gains value at longer planning horizons | Five grouped split assignments at 20/50/100 steps | 5/5 directional improvement over persistence | Split assignments reuse drives | SUPPORTED DESCRIPTIVELY |
| Whole-run splitting is necessary to avoid optimistic row-level leakage in this evaluation design | Implemented split protocol + prior PQoS literature on split sensitivity | Methodological/related-work support | Not claimed as a universal first | SUPPORTED |
| Empirical measurement support and predictive uncertainty are distinct diagnostics | Implemented support audit + grouped-shift coverage behavior | Conceptual + empirical diagnostics | Current support model is simple | SUPPORTED |
| MSCR evaluates selected actions using future measurements hidden during scoring | Replay implementation and archived outcome artifacts | Protocol property | Route-constrained offline replay only | SUPPORTED |
| P2 reduces measured delay relative to P1 on the primary replay | Nine-run paired replay | Bootstrap CI excludes 0; raw Wilcoxon 0.046875; Holm about 0.28125 | Not multiplicity-corrected confirmatory | EXPLORATORY |
| P2 delay-effect direction is robust across grouped split assignments | Effects -0.792, -1.253, -0.069, -0.263, -0.130 ms | 5/5 directional consistency | Not an independent n=5 sample | SUPPORTED DESCRIPTIVELY |
| P3 reduces unsupported selection exposure relative to P2 | Primary replay + five grouped split assignments | 5/5 descriptive direction | Additional mobility cost | SUPPORTED DESCRIPTIVELY |
| P3 improves QoS over P2 | Mixed-sign measured-delay effects | Not supported | -- | NOT SUPPORTED |
| The work is a new generic communication-aware planner | Extensive prior literature | Contradicted as a novelty claim | Use decision-validity framing instead | DO NOT CLAIM |
| The work is the first use of field-measured PQoS | Existing field-measured PQoS literature | Contradicted as a novelty claim | -- | DO NOT CLAIM |
| MSCR proves the causal effect of physically driving an alternate route | Offline log replay only | No intervention experiment | Different motion could change the environment/network | DO NOT CLAIM |
| CICV5G validates PC-FMCW optical communication | None | None | Cross-technology invalid inference | DO NOT CLAIM |

## Submission rule

Every strong statement in the submission must map to this matrix, an archived artifact, or a verified external source. A literature comparison may establish non-overlap, but it must not be converted into an unsupported universal first-of-kind claim.

The primary novelty story is:

**PQoS regression -> causal horizon -> empirical support -> measured counterfactual evaluability -> decision evidence.**
