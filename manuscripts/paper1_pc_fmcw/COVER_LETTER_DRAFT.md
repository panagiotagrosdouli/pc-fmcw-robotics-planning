# Draft Cover Letter — Paper 1

**Target journal:** IEEE Open Journal of Vehicular Technology

**Manuscript title:** *Predictive Motion Planning Downstream of a PC-FMCW Laser-Headlamp ISCAI: A Controlled Directional-Connectivity Mechanism Study*

Dear Editor,

Please consider the manuscript *Predictive Motion Planning Downstream of a PC-FMCW Laser-Headlamp ISCAI: A Controlled Directional-Connectivity Mechanism Study* for publication in the IEEE Open Journal of Vehicular Technology.

The manuscript studies a downstream vehicular-planning question motivated by the recently published phase-coded FMCW laser-headlamp architecture for integrated sensing, communication, and illumination. The contribution is not a new generic communication-aware planner, nor a redesign of the PC-FMCW waveform. Instead, we isolate whether future target-relative directional communication geometry should influence ego-motion selection before connectivity degradation occurs.

Five planners share candidate generation, vehicle and road constraints, predicted dynamic-target safety, static filtering, and receding-horizon execution. The primary comparison changes only reactive/current-geometry connectivity scoring versus predictive/future-geometry scoring. A frozen development procedure selects the planning buffer before 50 untouched confirmatory seeds are opened. Confirmatory inference is performed at the seed level after within-seed scenario aggregation, with bootstrap intervals, paired Wilcoxon tests, and Holm correction across the declared communication endpoints.

Predictive scoring improves all five declared modeled communication endpoints relative to reactive scoring under the frozen analytical model. The uncertainty-aware extension performs worse than prediction alone, and the connectivity-only oracle does not show a supported additional benefit. A separately authorized directional-versus-distance-only ablation shows that the predictive outage effect collapses when angular attenuation is removed, providing mechanism-specific evidence that the result depends on directional geometry in the implemented model.

The manuscript deliberately preserves strong boundaries. The connectivity mapping is a PC-FMCW-informed analytical surrogate, not a calibrated optical channel. We explicitly discuss the unresolved interpretation of the upstream 193.4-THz parameter in relation to laser-headlamp/illumination framing. Collision-free confirmatory simulation is not presented as a real-road safety guarantee. Earlier protocol failures and the negative uncertainty-aware result remain in the record.

The repository provides frozen configurations, archived seed-level effects, reproducible analysis, claim-evidence documentation, and CI-verified manuscript builds.

Before submission, replace this paragraph with confirmed statements regarding authorship, affiliations, funding, conflicts of interest, prior dissemination, and corresponding-author contact information.

Sincerely,

Panagiota Grosdouli  
[CONFIRMED AFFILIATION]  
[CONFIRMED CORRESPONDING EMAIL]
