# PC-FMCW Robotics Planning

Predictive connectivity-aware autonomous motion planning from a PC-FMCW integrated sensing/communication architecture, complemented by a separate field-measured vehicular-QoS research branch.

![Project overview](docs/project_overview.jpg)

## Research program

This repository now contains two deliberately separated studies that share one decision-layer question: **when is future communication information useful enough, and trustworthy enough, to influence autonomous vehicle motion?**

1. **Paper 1 — PC-FMCW perception-to-action robotics:** a technology-specific, model-based extension downstream of PC-FMCW sensing/tracking.
2. **Paper 2 — Measurement-support-aware V2X planning:** field-measured vehicular QoS with whole-drive anti-leakage evaluation, horizon-dependent prediction, empirical-support auditing, and route-constrained offline replay.

The evidence is not interchangeable. CICV5G 5G measurements are never presented as PC-FMCW optical measurements or as validation of the analytical optical surrogate.

The canonical claim status is tracked in [`docs/research/EVIDENCE_LEDGER.md`](docs/research/EVIDENCE_LEDGER.md) and [`docs/research/CLAIM_AUDIT.md`](docs/research/CLAIM_AUDIT.md).

---

# Paper 1 — Predictive Connectivity-Aware PC-FMCW Robotics

## Research question

Can prediction of future modeled PC-FMCW link quality beneficially influence vehicle motion before a reactive planner responds to connectivity degradation, while preserving a common hard safety envelope?

## Perception-to-action bridge

```text
PC-FMCW waveform / sensing / communication
        ↓
Target detection and tracking
        ↓
Target-state history
        ↓
Future target prediction
        ↓
Candidate ego trajectories
        ↓
Common hard safety filtering
        ↓
Trajectory-conditioned future link prediction
        ↓
Mobility + connectivity + risk evaluation
        ↓
Receding-horizon ego-motion decision
```

The robotics contribution begins at the sensing/tracking-to-motion bridge. It does not redesign the upstream waveform, DPSK coding, coherent receiver, or tracking front end.

## Planner ladder

- **P0 — Mobility only:** communication ignored in the objective.
- **P1 — Reactive:** uses current/myopic communication information.
- **P2 — Predictive:** evaluates future modeled link quality along candidate trajectories.
- **P3 — Predictive risk-aware:** augments P2 with uncertainty/risk-sensitive scoring.
- **P4 — Simulator oracle reference:** may use simulator future truth for connectivity only; it receives no privileged collision-avoidance information.

All planners share vehicle limits, candidate-generation rules, road/static-obstacle constraints, and dynamic-target safety logic.

## PC-FMCW-informed link model

The planner evaluates an analytical/surrogate link model from future relative ego/target geometry and derives modeled quantities such as SNR, BER, outage probability, and goodput. Distance loss and directional/angular loss are represented separately.

This model is **not experimentally calibrated optical hardware**. Robotics-side parameters such as reference SNR, path-loss exponent, angular width, outage threshold, softness, and uncertainty scale are model assumptions unless independent calibration evidence is supplied.

The upstream source reports a nominal carrier near 193.4 THz, corresponding approximately to 1550 nm, despite “blue laser” terminology. The repository preserves that provenance inconsistency rather than silently inferring visible-blue photometry, eye safety, detector responsivity, or atmospheric behavior from it. See [`docs/PC_FMCW_PARAMETER_AUDIT.md`](docs/PC_FMCW_PARAMETER_AUDIT.md).

## Safety-first experiment history

### V1 — invalidated as confirmatory

The first 50-seed confirmatory attempt used seeds `1000..1049`. It produced interesting communication diagnostics but **failed the robotics safety requirements**: collision/no-candidate behavior was substantial and the captured artifact also omitted the frozen `min_snr_db` endpoint. V1 communication outcomes are therefore historical exploratory evidence only.

### V2 — development safety gate failed

V2 added common straight maximum-braking candidates and used separate development data. The development gate still did not establish the required zero-collision / zero-no-candidate protocol, so V2 communication outcomes are not promoted as confirmatory evidence.

### V3 — active frozen protocol

V3 adds communication-agnostic braking-plus-lateral-evasion emergency candidates shared identically by P0–P4 and separates the physical collision definition from a planning-only prediction margin.

Development seeds: `6000..6019`.

Predeclared planning-margin candidates:

```text
0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 m
```

The selector chooses the **minimum** margin for which every development episode satisfies:

- zero collision episodes;
- zero episodes with `no_candidate_steps > 0`.

Communication performance is not used to select the margin.

If no development margin passes, V3 confirmation is scientifically blocked and the reserved confirmatory seeds must not be used for tuning.

If development passes, the selected margin is frozen and fresh confirmatory seeds `7000..7049` run. Communication inference is permitted only if the fresh confirmatory set itself passes the hard gate:

- zero collision episodes across every scenario/planner;
- zero episodes with no-candidate steps.

The five frozen primary communication endpoints are:

- `mean_outage_probability`
- `mean_snr_db`
- `min_snr_db`
- `mean_ber_model`
- `mean_goodput_bps_model`

For P2−P1, P3−P2, and P4−P2, scenario deltas are first averaged within seed. The independent inferential unit is the simulation seed. The confirmatory analysis reports seed-level effect sizes, deterministic paired-bootstrap confidence intervals, paired Wilcoxon tests where valid, and Holm correction across the five frozen endpoints within each comparison.

## Directional-geometry mechanism ablation

Fresh seeds `8000..8019` compare:

```text
directional surrogate = distance loss + angular/beam loss
distance-only surrogate = angular penalty effectively removed
```

The main mechanism question is whether the P2-vs-P1 benefit materially depends on modeled directional geometry. This is a **model-mechanism ablation**, not physical optical validation.

## Paper-1 claim boundary

Paper 1 may support a technology-specific model-based perception-to-action contribution if the V3 safety gate and frozen inference complete successfully. It must not claim measured optical validation, real-road autonomous-driving validation, generic communication-aware-planning novelty, generic optical/FSO trajectory-planning novelty, or unmeasured physical calibration.

---

# Paper 2 — Field-Measured V2X Predictive Planning

## Research question

When can an autonomous planner trust predicted connectivity from field measurements when evaluating counterfactual future motion?

A logged drive contains QoS only along the path actually traversed. The project therefore treats anti-leakage, empirical measurement support, and outcome validity as first-class variables rather than assuming arbitrary off-route ground truth.

## Dataset

The primary real dataset is CICV5G. The automated study uses:

- **38 measured runs/drives**;
- **43,045 synchronized samples**;
- measured delay and wireless/vehicle context including position, heading, velocity, SINR, RSRP, and network/context metadata.

The primary protocol uses whole-run train/calibration/test separation. Random row splitting is not an acceptable substitute.

## One-step prediction: negative result retained

On the primary grouped split, delay prediction is approximately:

| Model | MAE |
|---|---:|
| Persistence/current QoS | **7.419 ms** |
| Conditioned spatial kNN | 12.344 ms |
| Random Forest | 9.291 ms |
| ExtraTrees | 8.950 ms |

Thus the tested learned spatial/tree predictors do **not** beat persistence at one step. The research question is therefore horizon-dependent decision value, not generic ML superiority.

## Horizon-dependent predictive value

A calibration-only horizon-adaptive persistence/spatial fusion becomes useful at longer horizons. Across five grouped split assignments, all five assignments improve over persistence at:

- 20 steps (~1.1 s): mean improvement ~1.463 ms;
- 50 steps (~2.8 s): ~2.510 ms;
- 100 steps (~5.5 s): ~2.621 ms.

The same 38 drives are reused across split assignments. These are **descriptive sensitivity analyses**, not five independent replications.

## Empirical measurement support

Support is estimated from training coordinates only. Primary support-stratified delay MAE / empirical interval coverage is approximately:

| Nearest training support | Delay MAE | Coverage |
|---|---:|---:|
| <=1 m | 6.98 ms | 0.888 |
| 1–5 m | 8.51 ms | 0.841 |
| 5–15 m | 10.47 ms | 0.761 |

The relationship is context dependent rather than universally monotone within every drive. Low empirical support is treated as a reliability-risk indicator, not a universal distance-to-error law.

Residual split-conformal intervals are reported through empirical coverage. They are not described as calibrated event probabilities under grouped distribution shift.

## Route-constrained measured replay

Candidate future states correspond to states actually traversed later on the same held-out measured route. Future measured delay is hidden from P0–P3 and revealed only after candidate selection for outcome evaluation.

This avoids fabricating measured QoS at arbitrary unobserved positions. It remains **offline measured-route replay**, not closed-loop real-vehicle validation.

Measured-data planners:

- **P0:** mobility/reference baseline;
- **P1:** reactive/current-QoS baseline;
- **P2:** predictive mean-QoS utility;
- **P3:** predictive QoS with uncertainty/support-aware validity control.

P4 is not used because exact arbitrary counterfactual measured ground truth is unavailable.

## Primary replay

For the primary nine-run held-out split:

| Planner | Mean delay | >50 ms violation | Changed fraction | Unsupported fraction | Mobility deviation |
|---|---:|---:|---:|---:|---:|
| P0 | ~11.7659 ms | ~0.01657 | 0 | ~0.10834 | 0 |
| P1 | ~11.7659 ms | ~0.01657 | 0 | ~0.10834 | 0 |
| P2 | ~10.9737 ms | ~0.01378 | ~0.12043 | ~0.10561 | ~0.06022 |
| P3 | ~11.0468 ms | ~0.01412 | ~0.13750 | ~0.08725 | ~0.07074 |

P2-P1 mean measured-delay delta is about `-0.792 ms`. Its raw paired Wilcoxon p-value is `0.046875`, but after the declared Holm correction across the 12 replay comparison/metric tests the adjusted p-value is about `0.28125`. It is therefore **exploratory effect-size evidence, not confirmatory significance**.

P3-P2 does not show stable QoS superiority. Its consistent role is reducing unsupported decision exposure, at additional mobility deviation. The primary unsupported-exposure raw p-value also does not survive Holm correction.

## Multi-split replay robustness

P2-P1 measured-delay deltas across five grouped split assignments are approximately:

```text
-0.791924
-1.253015
-0.069188
-0.262972
-0.129775 ms
```

All 5/5 are negative; descriptive mean is approximately `-0.501375 ms`.

P2-P1 >50 ms violation-fraction deltas are also negative in 5/5 assignments, descriptive mean approximately `-0.002239`.

P3-P2 unsupported-fraction deltas are negative in 5/5 assignments, descriptive mean approximately `-0.027954`.

P3-P2 measured-delay effects have mixed sign and mean near zero.

Therefore the evidence-backed interpretation is:

```text
P2 → predictive communication utility
P3 → empirical-support / inference-validity control
```

No inferential test treats the five reused-drive split assignments as independent n=5 observations.

## Computational scope

The vectorized replay implementation has shown microsecond-scale batched QoS/support evaluation and candidate scoring in hosted CI. This is an implementation-level practicality result only; it is not an embedded or end-to-end real-time vehicle claim.

## Paper-2 claim boundary

Paper 2 may support field-measured, leakage-safe, horizon-dependent, support-aware predictive-planning methodology. It must not claim that CICV5G validates PC-FMCW optics, that route replay is real-road autonomy, that P3 consistently improves QoS, that split assignments are independent replication, or that generic communication-aware/radio-map planning is novel.

---

# Why two papers?

| | Paper 1 | Paper 2 |
|---|---|---|
| Domain | PC-FMCW / optical ISCAI robotics | Measured vehicular V2X |
| Evidence | Controlled seeded model-based simulation | Field-measured QoS + offline route replay |
| Main question | Does future PC-FMCW-informed connectivity improve motion decisions? | When are measured-data connectivity predictions valid enough for planning? |
| Primary validity threat | Safety + fidelity of analytical optical surrogate | Leakage + unsupported counterfactual extrapolation |
| Key mechanism | Future directional relative geometry | Horizon prediction + empirical support |
| Primary comparison | P2 vs P1; P3 vs P2; P4/reference; geometry ablation | P2 vs P1; P3 support-validity tradeoff |

The papers may cross-reference the common planning abstraction, but their hypotheses, evidence, validity threats, and conclusions remain separate.

---

# Repository-wide pipeline

```text
state / sensing history
        ↓
future state prediction
        ↓
candidate ego trajectories
        ↓
common hard safety filter
        ↓
future communication estimate
        ↓
uncertainty / empirical-support assessment
        ↓
trajectory scoring
        ↓
first-control execution
        ↓
replan
```

Communication estimation differs by branch:

- **PC-FMCW:** relative geometry → analytical PC-FMCW-informed QoS surrogate.
- **Real V2X:** causal measurement history/context → learned future QoS + empirical support.

# Reproduction

## Environment and tests

```bash
pip install -r requirements.txt
pytest -q
```

Normal CI covers Python 3.11/3.12 smoke and integration paths plus transformer import.

## PC-FMCW smoke benchmark

```bash
python scripts/run_pc_fmcw_robotics_benchmark.py --seeds 10
```

The publication protocol is defined by the V3 workflow/config and must not be replaced by ad-hoc seed selection. See `.github/workflows/part_b_v3.yml`, `configs/experiments/part_b_final_v3.yaml`, and the Paper-1 manuscript/build documentation.

## Real V2X

Key scripts include:

```text
scripts/prepare_cicv5g.py
scripts/run_real_v2x_study.py
scripts/run_real_v2x_horizon_study.py
scripts/run_real_v2x_multisplit.py
scripts/run_real_v2x_replay_planning.py
scripts/analyze_real_v2x_replay.py
scripts/analyze_real_v2x_replay_multisplit.py
```

Preserve dataset provenance and whole-run splitting when reproducing results.

# Research-integrity rules

Evidence labels must not be silently mixed:

- **UPSTREAM:** traceable to the source PC-FMCW study;
- **MODELED:** produced by the analytical/simulation branch;
- **MEASURED:** present directly in the vehicular dataset;
- **LEARNED/DERIVED:** predicted or computed from measured/model inputs.

A failed infrastructure/test job is repaired. A scientific negative result is retained. A protocol failure may be redesigned using development data only, followed by completely fresh confirmatory seeds/data. Reserved confirmatory evidence is never tuned after inspection merely to obtain significance.

# Current status

- Normal `main` CI is green after the CLI backward-compatibility repair.
- Real-V2X prediction, horizon, support, replay, multi-split sensitivity, and multiplicity-aware analyses are complete and audited.
- V1 PC-FMCW confirmatory evidence is invalidated for final claims; V2 did not close the development safety gate.
- The frozen V3 safety-selected protocol is the active Paper-1 experiment. Final Paper-1 communication claims remain gated until the development selector, fresh 7000–7049 hard safety gate, seed-level five-endpoint Holm analysis, and fresh 8000–8019 geometry ablation complete.

This repository should be read as a reproducible two-paper research program, not as a single planner demo.
