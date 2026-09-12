# Paper 2 Claim-Evidence Matrix

| Claim | Evidence | Statistical support | Boundary | Status |
|---|---|---|---|---|
| One-step persistence is stronger than naive learned spatial/tree baselines | Primary grouped split predictor study | Direct metric comparison | Dataset-specific | SUPPORTED |
| Spatial/context information gains value at longer horizons | 5 grouped split assignments; 20/50/100-step study | Descriptive 5/5 direction at long horizons | Split assignments are dependent | SUPPORTED DESCRIPTIVELY |
| P2 reduces measured delay relative to P1 in primary replay | Run-paired replay | bootstrap CI excludes 0; raw Wilcoxon 0.046875; Holm ~0.28125 | Not multiplicity-corrected confirmatory | EXPLORATORY |
| P2 delay effect direction is robust across grouped split assignments | Effects -0.792,-1.253,-0.069,-0.263,-0.130 ms | 5/5 directional consistency | Not independent n=5 | SUPPORTED DESCRIPTIVELY |
| P3 reduces unsupported selection exposure vs P2 | Primary + 5 split assignments | Primary raw p exploratory; 5/5 descriptive direction | No stable QoS gain | SUPPORTED DESCRIPTIVELY |
| P3 improves QoS over P2 | Mixed-sign measured-delay effects | Not supported | -- | NOT SUPPORTED |
| CICV5G validates PC-FMCW optical communication | None | None | Cross-technology invalid inference | DO NOT CLAIM |
| Route replay is real closed-loop autonomous driving | Offline measured replay | None | No vehicle actuation experiment | DO NOT CLAIM |

## Submission rule

Every strong statement in `paper2.tex` must map to one row above or to a verified source/result artifact. Raw p-values that do not survive Holm correction must not be described as confirmatory discoveries.
