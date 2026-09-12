# Dual-branch analytical synthesis

## 1. Purpose

This repository now contains two deliberately different communication-validation branches that share a common autonomous decision layer:

1. **PC-FMCW-informed model-based branch** — technology-specific optical connectivity evaluation built around the original phase-coded FMCW ISCAI architecture.
2. **Field-measured V2X branch** — real communication measurements from CICV5G used to test whether the predictive-connectivity decision principle survives under measured, non-optical vehicular communication conditions.

These branches must not be collapsed into a single communication model. Their scientific value comes from complementarity: one provides technology specificity, the other provides measurement realism at the decision layer.

---

## 2. Common decision abstraction

Both branches instantiate the same high-level control question:

> Given several safe future ego-motion candidates, can future communication quality be predicted well enough to change the chosen motion before a reactive planner would respond?

The shared abstraction is:

`candidate ego motion -> future communication state -> communication cost/risk -> trajectory ranking`

Hard vehicle/road/obstacle safety remains external to the communication objective and common across planners.

The two branches differ only in how the future communication state is obtained.

### PC-FMCW branch

`future relative geometry -> PC-FMCW-informed analytical optical link -> SNR/BER/outage/goodput`

### Real-V2X branch

`future measured-route state + causal QoS context -> learned measured-data predictor -> delay/SINR + support/uncertainty diagnostics`

This common abstraction is the main bridge that allows cross-technology reasoning without falsely claiming that 5G measurements validate PC-FMCW propagation.

---

## 3. PC-FMCW branch: analytical interpretation

### 3.1 What the branch tests

The PC-FMCW branch asks whether an ego planner can exploit a directional, geometry-sensitive communication model associated with the upstream PC-FMCW ISCAI system.

The planner variants are interpreted as an information ladder:

- **P0**: mobility-only; communication ignored.
- **P1**: reactive communication-aware; current communication state influences motion but no predictive future communication forecast is used.
- **P2**: predictive communication-aware; candidate trajectories are scored using predicted future connectivity.
- **P3**: stochastic/risk-sensitive predictive planner.
- **P4**: oracle connectivity reference using simulator future truth for connectivity only, never for safety.

### 3.2 Verified baseline evidence

The verified 20-seed controlled simulation reports:

| Planner | Mean outage | Mean SNR dB | BER model | Goodput model bps | Progress m | Collision rate |
|---|---:|---:|---:|---:|---:|---:|
| P0 | 0.061750 | 15.651580 | 0.019946 | 9.800543e8 | 44.694793 | 0.40 |
| P1 | 0.079767 | 13.984878 | 0.028753 | 9.712470e8 | 44.959847 | 0.40 |
| P2 | 0.062199 | 15.622639 | 0.020368 | 9.796324e8 | 44.699780 | 0.40 |
| P3 | 0.061545 | 15.688970 | 0.019818 | 9.801821e8 | 44.685380 | 0.40 |
| P4 | 0.061374 | 15.678035 | 0.019793 | 9.802072e8 | 44.685700 | 0.40 |

The strongest supported comparison is **P2 versus P1**:

- outage decreases by approximately **0.01757 absolute**, about **22.0% relative to P1**;
- SNR increases by approximately **1.64 dB**;
- modeled BER decreases by approximately **0.00839**;
- modeled goodput increases by approximately **8.39 Mbit/s**;
- the outage improvement has a paired-bootstrap 95% CI approximately `[-0.0252, -0.0107]` and remains significant after Holm correction.

The important scientific interpretation is not that P2 beats every planner. It does not. P0, P2, P3 and P4 are numerically close on the baseline link metrics. The robust statement is narrower:

> **Predictive connectivity forecasting prevents the degradation observed in the reactive P1 planner under the tested PC-FMCW-informed scenarios.**

This is a more defensible and more interesting statement than claiming generic superiority of predictive planning.

### 3.3 Why P1 can be worse than P0

The baseline result P1 < P0 on communication metrics is scientifically useful rather than embarrassing. It implies that a reactive connectivity term can steer the vehicle based on a communication state that is already stale relative to future geometry. In a directional/geometry-sensitive link, local improvement can create a worse future state.

The key mechanism to test in scenario traces is therefore:

`current-link reaction -> short-sighted maneuver -> future geometry degradation`

versus

`future-link prediction -> anticipatory maneuver -> avoided degradation`.

This mechanism should be illustrated with at least one representative trajectory/time-series figure before publication.

### 3.4 What the branch does not establish

The current baseline does **not** show:

- improved collision safety;
- measured optical-channel performance;
- real-road autonomous-driving validation;
- a statistically meaningful P3 advantage over P2;
- a statistically meaningful P4 oracle advantage over P2.

The common collision rate of 0.40 makes any safety-improvement claim invalid. The safety result should be reported as neutral: the communication policy changes did not create a planner-level collision-rate difference in this benchmark, but the benchmark itself contains difficult/infeasible scenario structure that requires per-scenario interpretation.

### 3.5 PC-FMCW-specific novelty opportunity

The technology-specific contribution is strongest when the communication objective is explicitly tied to mechanisms generic RF planners do not normally contain, especially:

- directional geometry;
- optical pointing/angular offset;
- field-of-view or beam-alignment sensitivity where supported by the model;
- PC-FMCW/DPSK-derived link metrics;
- integrated sensing/tracking information feeding future geometry prediction.

The paper should avoid presenting the analytical connectivity model as measured optical calibration.

---

## 4. Real-V2X branch: analytical interpretation

### 4.1 What the branch tests

The real-V2X branch asks a harder question than whether a radio map can be learned:

> Can measured vehicular QoS provide useful future decision information without temporal leakage and without pretending that unmeasured counterfactual positions have known ground truth?

CICV5G provides field-measured communication traces. The experiment uses complete-run train/calibration/test separation so temporally adjacent samples from one drive cannot leak across partitions.

### 4.2 Predictor result: persistence is a serious baseline

The one-step result falsified the initial assumption that a learned spatial model would automatically outperform a reactive baseline.

On the primary grouped split:

- persistence is the best one-step delay predictor;
- spatial KNN is materially worse;
- Random Forest is also worse;
- Extra Trees does not establish a significant advantage over persistence.

This is an important negative result. Vehicular QoS over tens of milliseconds is strongly autocorrelated, so any method claiming predictive value must outperform current-value persistence rather than a weak mean predictor.

### 4.3 Planning horizon changes the result

The causal horizon study shows that the value of spatial/context information increases at future horizons relevant to planning.

Across five grouped split seeds, calibration-gated fusion improves delay MAE over persistence in every split at approximately:

- **1.1 s** horizon;
- **2.8 s** horizon;
- **5.5 s** horizon.

This gives a more precise research statement:

> **Measured vehicular QoS is too persistent for naive one-step ML to be meaningful, but context/spatial information becomes incrementally useful at planning-relevant horizons when it is gated against a strong causal persistence baseline.**

This horizon-dependent result is substantially more defensible than claiming that a machine-learning predictor is simply better.

### 4.4 Route-constrained measured replay

Arbitrary counterfactual path evaluation is invalid when field data only contain QoS along the route actually driven. The branch therefore restricts decision-value evaluation to measured future states on held-out routes.

This produces an outcome for each planner choice without fabricating QoS for unvisited coordinates.

Across 9 held-out runs:

- P1 mean measured delay: approximately **23.318 ms**;
- P2 mean measured delay: approximately **22.526 ms**;
- P3 mean measured delay: approximately **22.598 ms**.

For **P2 versus P1**:

- mean paired delay change: approximately **-0.792 ms**;
- 95% paired-bootstrap CI: approximately **[-1.723, -0.138] ms**;
- paired Wilcoxon p approximately **0.0469**;
- the selected motion differs from the nominal/reactive choice only modestly.

For the >50 ms experimental violation threshold:

- P2 reduces the mean violation fraction by approximately **0.00279 absolute** relative to P1;
- p approximately **0.0625**;
- this is directionally favorable but should not be presented as a statistically significant violation-rate improvement.

### 4.5 What P3 actually contributes

P3 does **not** improve measured delay over P2.

Instead, its supported role is inference-validity control:

- P3 reduces unsupported-selection exposure by approximately **0.01836 absolute** relative to P2;
- paired-bootstrap CI approximately **[-0.03214, -0.00603]**;
- Wilcoxon p approximately **0.03125**;
- this comes with additional mobility deviation.

Therefore P3 should not be described as a better QoS planner. It should be described as a **support-aware conservative planner** that spends mobility budget to rely less often on weakly supported communication predictions.

This distinction is scientifically valuable because it separates two objectives:

1. **communication utility** — lower measured delay;
2. **inference validity** — fewer decisions based on unsupported predictions.

### 4.6 Uncertainty interpretation

Split-conformal intervals provide marginal residual coverage under the calibration/test regime. They are not event probabilities and do not retain universal guarantees under grouped distribution shift.

Observed coverage degradation across grouped splits is evidence that measurement support and distribution shift must be reported explicitly rather than hidden inside a single confidence interval.

---

## 5. Cross-branch comparison

### 5.1 What replicates across technologies

The strongest cross-branch finding is qualitative but evidence-based:

**Reactive communication-awareness can be insufficient, and useful predictive information appears at the motion-planning horizon rather than necessarily at the immediate next sample.**

In the PC-FMCW branch, P2 strongly outperforms reactive P1 on modeled optical link metrics.

In the measured V2X branch, one-step persistence is extremely strong, but horizon-adaptive prediction gains value at multi-second horizons and P2 lowers measured replay delay relative to P1.

Thus both branches support the same decision-layer principle through different evidence sources.

### 5.2 What does not replicate

The role of P3 does not replicate as a simple QoS-improvement mechanism.

- In PC-FMCW simulation, P3 is only slightly better numerically than P2 and not significantly superior after correction.
- In measured V2X replay, P3 does not improve measured delay over P2 but does reduce unsupported selections.

This suggests that uncertainty/risk awareness should be framed as **robustness/validity control**, not an automatic communication-performance booster.

### 5.3 Technology-specific versus technology-independent claims

#### Technology-independent decision-layer claims

Potentially supported across both branches:

- future connectivity can matter to motion selection;
- reactive connectivity-awareness is not equivalent to predictive connectivity-awareness;
- planning-relevant communication horizons are longer than one-step prediction horizons;
- risk/support constraints can trade mobility performance for more defensible communication decisions.

#### PC-FMCW-specific claims

Supported only by the model-based optical branch:

- modeled optical SNR/BER/outage/goodput behavior;
- dependence on PC-FMCW-informed geometry assumptions;
- connection to upstream PC-FMCW sensing/tracking architecture.

#### V2X measurement-specific claims

Supported only by CICV5G:

- field-measured delay/SINR statistics;
- whole-run generalization behavior;
- measured replay decision outcomes;
- support-distance and grouped distribution-shift behavior.

---

## 6. Central paper thesis

A defensible integrated thesis is:

> **Predictive connectivity-aware motion planning should be evaluated at the decision horizon, not merely by one-step communication prediction accuracy. We demonstrate this principle first in a PC-FMCW-informed optical robotics model and then test its decision-layer generality using field-measured vehicular communication traces with explicit anti-leakage and empirical-support controls.**

This is stronger than claiming a new generic communication-aware planner because it combines:

1. a technology-specific ISCAI-to-action bridge;
2. a predictive-versus-reactive information study;
3. a measured-data decision validation layer;
4. an explicit treatment of where counterfactual communication inference is scientifically unsupported.

---

## 7. Contribution structure for a combined manuscript

### Contribution A — PC-FMCW perception-to-action extension

A closed-loop robotics layer extends PC-FMCW ISCAI sensing/tracking outputs into receding-horizon autonomous motion decisions using trajectory-conditioned connectivity forecasting under common hard safety constraints.

### Contribution B — predictive-versus-reactive connectivity evidence

A controlled P0-P4 information ladder isolates the value of future communication knowledge. In the PC-FMCW-informed benchmark, predictive P2 significantly recovers the optical-link degradation observed under reactive P1.

### Contribution C — field-measured decision validation

A second branch uses CICV5G field measurements with whole-drive leakage-safe splits and strong persistence baselines. It shows that predictive value is horizon-dependent and that P2 can reduce measured replay delay relative to P1.

### Contribution D — empirical-support-aware counterfactual discipline

Rather than assigning invented QoS ground truth to arbitrary alternative routes, the real-data evaluation audits training support and uses route-constrained measured replay. P3 is shown to reduce unsupported decision exposure, clarifying the trade-off between communication utility and inference validity.

---

## 8. Claims to avoid in the combined paper

Do not claim:

- communication-aware motion planning itself is novel;
- prediction of future SNR/QoS is novel;
- radio-map-aware planning is novel;
- uncertainty-aware planning automatically improves QoS;
- V2X data validate PC-FMCW optical propagation;
- modeled PC-FMCW results are hardware measurements;
- route-constrained replay is real-vehicle closed-loop validation;
- P3 beats P2 in QoS;
- the current benchmark shows improved collision safety;
- the exact combination is a universal first unless a broader systematic review establishes that claim.

---

## 9. Remaining analytical closure tasks

### PC-FMCW branch

1. Aggregate and report the full robustness sweep from all completed seed shards using the repository's existing merge/plot pipeline.
2. Produce per-scenario traces explaining why P1 degrades relative to P2.
3. Report candidate-rejection causes and collision timing per scenario.
4. Complete horizon and connectivity-weight ablations.
5. Add computational timing for P0-P4.
6. If possible, add an optical-specific ablation: distance-only versus distance-plus-angular/pointing dependence.

### Real-V2X branch

1. Repeat route-constrained replay across several grouped split seeds rather than a single split.
2. Report effect heterogeneity by network band, direction and nominal vehicle speed.
3. Add sensitivity to support radius/min-neighbor thresholds.
4. Add threshold sensitivity for the experimental delay operating point.
5. Report compute timing by P0/P1/P2/P3 separately.
6. Preserve the negative P3 QoS result.

### Cross-branch

1. Build a single table mapping evidence source -> communication model -> planner information -> endpoint -> supported claim.
2. Produce a conceptual figure with two communication branches feeding the same decision-layer block.
3. Report only within-branch quantitative effects; do not numerically compare optical SNR/outage to 5G delay as if they shared units or distributions.

---

## 10. Recommended manuscript framing

### Combined-paper title candidate

**From PC-FMCW ISCAI to Predictive Motion: Connectivity-Aware Planning with Model-Based Optical and Field-Measured V2X Validation**

### More methodological title

**Predict at the Decision Horizon: Support-Aware Connectivity Planning from PC-FMCW Robotics to Field-Measured V2X**

### Core message

The contribution is not a new radio-map planner. The contribution is a disciplined **perception-to-action and communication-to-motion evaluation framework** that demonstrates predictive connectivity value in a PC-FMCW-specific setting and then stress-tests the same decision principle using measured vehicular communication traces without granting the planner scientifically unjustified counterfactual knowledge.
