# Active Self-Calibration Research Plan

## Scope and scientific boundary

This is a new research scope: **Decision-Triggered Active Self-Calibration for PC-FMCW-Informed Vehicular Optical Planning**. It does not modify, reinterpret, or provide new evidence for the frozen Paper 1 or Paper 2 studies.

The research question is: **when should safe ego motion also be used as an experiment for learning uncertain modeled optical-link parameters because that information could improve a downstream motion decision?**

The implemented contribution investigates a specific intersection of dual-control / active-learning ideas and PC-FMCW-informed directional vehicular optical planning. It is not described as universally first-of-kind.

All uncertain optical parameters in this study are **MODELED latent parameters**. This is not real-world optical calibration and not measured PC-FMCW link validation.

## Reused infrastructure

The extension reuses the repository's tested:
- vehicle dynamics and candidate trajectory generation;
- road, speed, static-obstacle, dynamic-target and stop-viability hard filters;
- causal target prediction;
- PC-FMCW-informed analytical link equations;
- deterministic seeded simulation patterns;
- paired bootstrap, Wilcoxon, effect-size and Holm utilities.

The extension does not modify the frozen P0-P4 benchmark, V7 protocol, Paper-1 results, Paper-2 results, or canonical manuscript evidence.

## Latent link model

The latent vector is deliberately small:

[
\phi=[\alpha_{loss},\delta_{beam},k_{angular}].
]

- `alpha_loss`: multiplicative scaling of the existing distance-loss exponent.
- `delta_beam_rad`: modeled boresight angular offset.
- `k_angular`: multiplicative scaling of Gaussian angular attenuation.

The nominal vector is `[1, 0, 1]`. Simulator truth, nominal parameters, and planner belief are distinct objects. C0-C3 never receive simulator truth. C4 receives true latent link parameters only for its non-deployable connectivity reference.

## Observation and belief model

The communication observation is modeled SNR plus declared Gaussian observation noise. The planner maintains a small Bayesian grid over `phi`. The update uses a Gaussian SNR likelihood and is performed only after an action is executed and its communication observation is realized.

This estimator was chosen because the state dimension is only three, posterior mass is directly inspectable, deterministic reproduction is straightforward, and multi-modality can be represented without forcing a Gaussian approximation.

The information score uses the short-horizon approximation

[
G(\tau)=\sum_j \tfrac{1}{2}\log\left(1+
\frac{\mathrm{Var}_{\phi}[\mu_z(\phi,\tau,j)]}{\sigma_z^2}\right).
]

It is a transparent predictive-information proxy, not a claim of exact mutual information or a physically calibrated Fisher-information matrix.

## Planner family

### C0 — Nominal / no calibration
Uses the nominal latent vector permanently. It performs no online parameter update.

### C1 — Passive calibration
Uses the posterior-expected task-plus-connectivity cost. It updates the Bayesian grid from measurements obtained along the selected trajectory but never rewards information gain.

### C2 — Always-information active calibration
Uses the same belief as C1 but always permits the information-gain reward in safe planning. It is an ablation for quantifying unnecessary probing and mobility cost.

### C3 — Decision-triggered active self-calibration
Uses information value only when uncertainty is decision-relevant. For candidate costs `J(tau, phi)`, let the posterior-expected best candidate be `tau_bar`. Define

[
U_D=P_{\phi}[\arg\min_{\tau}J(\tau,\phi)\ne\tau_{bar}]
]

and expected decision regret

[
R_D=E_{\phi}[J(\tau_{bar},\phi)-\min_{\tau}J(\tau,\phi)].
]

The information term is enabled only when `U_D > threshold` and `R_D > minimum regret`. When enabled, safe candidates are scored using posterior expected task/connectivity cost, a probing-motion penalty, and the decision-relevance-weighted information proxy.

### C4 — Oracle parameter reference
Uses simulator latent link parameters for connectivity scoring only. It remains non-deployable and receives the same causal target prediction, candidate generator, obstacles, physical limits, and hard safety filters as C0-C3.

## Safety

Safety remains a hard filter before any calibration or information score. Every planner variant uses the same:
- vehicle dynamics and candidate lattice;
- road and speed bounds;
- static obstacle clearance;
- time-aligned dynamic target clearance;
- terminal static and dynamic stop-viability checks;
- optional hierarchical clearance fallback to the same physical target boundary.

Information gain can never make a hard-infeasible candidate feasible.

## Identifiability scenarios

Six prospective mechanism scenarios are declared:

- **A — Angular bias:** nonzero modeled boresight offset.
- **B — Distance-loss mismatch:** non-nominal distance-loss scaling.
- **C — Combined ambiguity:** multiple latent mismatches whose predictions become distinguishable only under changing geometry.
- **D — Model already accurate:** nominal truth and a narrow prior; probing should have limited value.
- **E — Uncertainty exists but is decision-irrelevant:** broad latent uncertainty under a mobility-dominant common decision; C3 should suppress active probing.
- **F — Decision-critical uncertainty:** competing safe trajectories whose communication ranking can change across plausible latent models.

These scenarios test mechanism and decision relevance. They do not establish physical optical parameter identifiability in real vehicles.

## Metrics

Safety/mobility: collision indicator, no-candidate steps, minimum target distance, realized TTC diagnostic, static clearance, progress, path length, margin-relaxation use.

Communication: modeled SNR, outage probability, BER and goodput.

Calibration: normalized latent-parameter error, per-parameter error, belief entropy reduction, convergence slope, update count.

Active behavior: information-active steps, probe steps/fraction, probe cost, information gained per probe, unnecessary-probe rate.

Decision quality: oracle-parameter trajectory-selection agreement, cumulative oracle-parameter decision regret, and time to consistent oracle agreement.

The primary scientific endpoint is downstream decision regret, not parameter-estimation RMSE alone.

## Prospective protocol

Development seeds are `31000..31019`. They may be used for debugging, mechanism inspection and selection of the declared decision threshold, information weight and probe weight grid.

A freeze script records the selected development setting, config SHA-256, development-manifest SHA-256 and the confirmatory seed range.

Confirmatory seeds are `32000..32049`. Confirmatory execution requires the frozen protocol file and refuses CLI hyperparameter overrides. Choices must not be retuned after opening confirmatory seeds.

The independent inferential unit is a scenario seed after aggregating repeated declared scenarios within seed. Timesteps are diagnostics, never independent confirmatory samples. Primary paired comparisons are C0-C1, C1-C2, C2-C3 and C3-C4. The analysis reports deterministic paired bootstrap intervals, paired Wilcoxon tests, paired effect sizes and Holm adjustment within each declared comparison family.

## Ablations

The C0-C4 family directly supplies:
- no calibration vs passive calibration;
- passive vs always-active;
- always-active vs decision-triggered;
- decision-trigger removal (C2);
- information-gain removal while retaining belief updates (C1);
- oracle parameter gap (C4).

A directional-vs-distance-only mechanism ablation is implemented through `--link-model distance_only`. It removes angular attenuation while retaining the same planner/safety machinery and records the geometry mode in provenance. It is explicitly marked as a development mechanism ablation, not part of the primary frozen confirmatory protocol; under this ablation, `delta_beam_rad` and `k_angular` are intentionally non-identifiable from link observations.

## Provenance and artifacts

The isolated root is `artifacts/active_self_calibration/`. Each executed scope records the full config digest, Git commit SHA, seed values, software information, link provenance, planner/oracle boundary, selected hyperparameters, raw episode rows and timestep diagnostics.

Smoke outputs are engineering-only. Development outputs are not confirmatory evidence. Historical exploratory outputs must never be relabeled as confirmatory.

## Known scientific limitations requiring review

1. **Observation model:** Gaussian modeled-SNR noise is a simulation assumption, not a measured receiver-noise distribution.
2. **Local identifiability:** distance-loss, beam offset and angular-width effects can remain confounded under poor geometry. The study must report posterior ambiguity rather than force convergence.
3. **Information approximation:** the implemented information score assumes additive local measurement value and does not integrate the full posterior over future closed-loop state transitions.
4. **Candidate-lattice dependence:** information value is defined relative to the safe trajectory set exposed by the existing planner. A richer action set may alter identifiability.
5. **Oracle regret:** C4 is an evaluation/reference device, not a deployable controller and not evidence of real-world optimality.
6. **Model mismatch:** a low latent-parameter error inside this three-parameter family does not imply that the analytical optical model is physically complete.
7. **Negative findings:** a result in which C3 does not outperform passive calibration, or in which active probing is inefficient, is a valid outcome of the study.

The experiment is scientifically meaningful only if these assumptions remain explicit and the frozen confirmatory protocol is respected.
