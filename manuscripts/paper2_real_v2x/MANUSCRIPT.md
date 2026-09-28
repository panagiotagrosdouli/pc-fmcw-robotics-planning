# From QoS Prediction to Decision Validity
## Measurement-Supported Counterfactual Replay for Communication-Aware Vehicle Planning

> **Canonical source:** `paper2.tex`. This Markdown document is the human-readable companion to the submission source. Numerical claims remain governed by the archived artifacts and `CLAIM_EVIDENCE.md`.

## Research question

Predictive QoS and communication-aware motion planning are established research areas. The paper therefore asks a narrower methodological question:

**When logged vehicular field measurements are used to influence motion, what evidence is required before a counterfactual QoS prediction can support a decision-level claim?**

The key problem is that the dataset measures the route that was actually driven, whereas a motion planner evaluates alternative future states. Model-generated QoS at an unvisited state is not automatically field-measured counterfactual truth.

## Core framing: three validity layers

### 1. Predictive validity

A future-QoS model must beat a strong causal baseline at the horizon where motion can act. On the primary split, one-step persistence has delay MAE **5.576 ms**, outperforming the tested spatial kNN, Random Forest, and Extra Trees baselines.

Across five grouped split assignments, calibration-gated spatial/context prediction improves over persistence in all five assignments at 20, 50, and 100 steps, with mean improvements of approximately **1.460, 2.506, and 2.622 ms**.

The result is therefore horizon-dependent rather than a generic claim that ML beats persistence.

### 2. Empirical-support validity

Each candidate query is audited against training measurements using spatial proximity and local density. This diagnostic is intentionally separate from residual predictive uncertainty.

On the primary split, delay MAE / empirical conformal coverage are approximately:

- within 1 m of training support: **5.332 ms / 0.888**;
- 1–5 m: **7.120 ms / 0.864**;
- 5–15 m: **9.579 ms / 0.761**.

The relationship is context-dependent and is not presented as a universal monotonic error law.

### 3. Outcome validity

For decision evaluation, candidate choices are restricted to later states actually recorded in the same held-out trajectory. Their future measured delay is hidden during planner scoring and revealed only after selection.

This protocol is called **measurement-supported counterfactual replay (MSCR)**.

MSCR does not prove what would happen under an arbitrary physically executed alternative route. It provides a stricter offline evidence boundary: every reported post-selection QoS outcome is an actual withheld measurement rather than a prediction from the model being evaluated.

## Dataset and anti-leakage design

The study uses a 38-run, 43,045-sample CICV5G subset.

The primary split contains:

- 22 training runs / 22,441 samples;
- 7 calibration runs / 8,846 samples;
- 9 test runs / 11,758 samples.

Complete runs are assigned to one partition only. There is no random row split. Repeated grouped split assignments reuse the same finite drives and are treated as descriptive sensitivity analyses rather than independent replications.

## Planner family

- **P0:** mobility/reference choice.
- **P1:** reactive/current-QoS persistence choice.
- **P2:** predictive future-QoS choice.
- **P3:** P2 plus an empirical-support penalty.

P2 tests predictive decision utility. P3 tests support-risk control. P3 is not assumed to improve QoS over P2.

## Primary replay results

| Planner | Mean measured delay (ms) | >50 ms fraction | Unsupported selection | Mobility deviation |
|---|---:|---:|---:|---:|
| P1 | 23.318 | 0.02179 | 0.1562 | 0 |
| P2 | 22.526 | 0.01900 | 0.1563 | 0.01254 |
| P3 | 22.598 | 0.01934 | 0.1380 | 0.02305 |

For P2 versus P1, the primary run-paired delay effect is **-0.791924 ms**, bootstrap 95% CI **[-1.723327, -0.137729] ms**. The raw Wilcoxon value is **0.046875**, but the Holm-adjusted value is approximately **0.28125** across the declared family. The paper therefore does not claim multiplicity-corrected confirmatory superiority.

Across five grouped split assignments, P2–P1 measured-delay effects are:

`[-0.791924, -1.253015, -0.069188, -0.262972, -0.129775] ms`.

All five have favorable direction. Their descriptive mean is **-0.501375 ms**.

P3 reduces unsupported-selection exposure relative to P2 in all five assignments, but its measured-delay effects have mixed sign. The supported conclusion is a **validity-versus-mobility trade-off**, not an additional QoS gain.

## Literature boundary

The paper explicitly acknowledges that the following are prior art:

- communication-aware motion planning;
- channel-learning-aware robot navigation;
- communication-aware RRT and joint motion/communication/sensing optimization;
- field-measured predictive QoS;
- QoS-aware autonomous-vehicle route planning;
- online and predictive radio maps;
- uncertainty-aware communication-preserving MPC;
- task-aware and credibility-filtered radio-world-model rollouts.

The manuscript's distinct question is the evidential boundary created by **logged field measurements**: causal horizon, training-measurement support, and whether a selected counterfactual action has a withheld measured outcome.

Representative literature now cited in the paper includes Ghaffarkhah & Mostofi (2011), Sliwa et al. (2018), Muralidharan & Mostofi (2021), Hurst et al. (2021), Cai & Mostofi (2022), Palaios et al. (2023), Berlin V2X (2023), Zou & Liu (2024), Ullah et al. (2025), Partani et al. (2025), Gordon et al. (2026), RadioMapMotion (2026), Kim et al. (2026), CICV5G (2026), and RMWorld (2026).

## Supported conclusion

The strongest paper-level conclusion is:

**Logged field-measured connectivity prediction should be evaluated as a decision-validity problem, not only a regression problem. Future QoS can become useful at planning horizons, but predictive utility, empirical support, and measured counterfactual evaluability are separate evidence requirements.**

## Boundaries

The paper does not claim:

- a new generic communication-aware planner;
- a new generic PQoS method;
- a first-ever radio map or predictive radio map;
- confirmatory P2 superiority after multiplicity correction;
- stable P3-over-P2 QoS improvement;
- real closed-loop vehicle validation;
- causal effects for arbitrary off-route interventions;
- optical or PC-FMCW validation from CICV5G.
