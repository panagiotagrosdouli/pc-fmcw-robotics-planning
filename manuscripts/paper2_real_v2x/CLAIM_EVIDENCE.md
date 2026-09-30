# Paper 2 Claim-Evidence Matrix — confirmed measured decision-validity framing

**Updated:** 2026-09-30  
**Locked confirmatory workflow:** `36747715208`  
**Workflow head SHA (frozen branch):** `a056d46a5579032d10f51a1d6e90d800d3d017b4`  
**Executed checkout SHA (artifact provenance):** `e4f6430f8b6368f64edee421b827895b11280115`

| Claim | Evidence | Statistical support | Boundary | Status |
|---|---|---|---|---|
| One-step persistence is stronger than the tested naive learned spatial/tree baselines | Original grouped-run predictor study | Direct held-out metric comparison | CICV5G subset-specific | SUPPORTED |
| Spatial/context prediction can add value at longer horizons | Five grouped predictor-split assignments | 5/5 descriptive direction at 20/50/100 steps | Dependent split sensitivity, not independent replication | SUPPORTED DESCRIPTIVELY |
| Whole acquisition-run role separation is necessary for the paper's field-evidence protocol | Train/donor/query design + prior split-sensitivity literature | Protocol property and methodological rationale | Not claimed as a universal theorem | SUPPORTED |
| Prediction uncertainty and empirical action support are distinct | Support audit + matched-action construction | Conceptual + empirical | Spatial support remains a simple finite-data diagnostic | SUPPORTED |
| The matched-speed protocol evaluates a physically interpretable motion action using separate measured donor runs | 30/50-km/h W2S replay; donor outcomes hidden from deployable ranking | Protocol property | Repeated observational field runs, not randomized speed intervention | SUPPORTED |
| The locked split contains support-bounded measured action-value headroom relative to FAST | ORACLE_BUDGET − FAST = -4.177 ms | Two-way query/donor bootstrap 95% CI [-13.659, -2.137] ms; 4,945 valid replicates; 100% below 0 | Oracle is a nondeployable measured upper-bound diagnostic | SUPPORTED |
| The frozen absolute-QoS ranking leaves material measured opportunity unused | PRED_BUDGET − ORACLE_BUDGET = +2.704 ms | Two-way bootstrap 95% CI [+1.457, +5.832] ms; 100% above 0 | Regret is relative to the support-bounded oracle diagnostic | SUPPORTED |
| PRED_BUDGET is superior to FAST | PRED_BUDGET − FAST = -1.473 ms | Two-way bootstrap 95% CI [-8.167, +0.657] ms | Interval crosses 0 | NOT CONFIRMATORY — DO NOT CLAIM |
| The frozen pairwise margin policy is superior to FAST | MARGIN_BUDGET − FAST = -1.668 ms | Two-way bootstrap 95% CI [-9.524, +1.180] ms | Interval crosses 0 | NOT CONFIRMATORY — DO NOT CLAIM |
| Direct pairwise action-margin learning removes the decision-evidence gap | MARGIN_BUDGET − ORACLE_BUDGET = +2.509 ms | Two-way bootstrap 95% CI [+1.572, +5.162] ms | Frozen model; no post-result retuning | CONTRADICTED / NEGATIVE RESULT |
| The failure-boundary pattern is robust to multiple development role assignments | 15 support-balanced seed/caliper configurations | Oracle favorable 15/15; PRED mean-delay direction favorable only 9/15; PRED p95 favorable 8/15 | Configurations reuse the finite drive pool | SUPPORTED DESCRIPTIVELY |
| Measured action-value headroom is also present in an out-of-scenario arterial n8 confirmation | 50/80-km/h arterial replay frozen before outcome inspection | ORACLE_BUDGET − FAST = -0.590 ms; two-way 95% CI [-1.431, -0.250] ms | Four query runs; finite CICV5G arterial subset | SUPPORTED |
| The frozen absolute-QoS policy can be harmful out of scenario | Arterial n8 50/80-km/h confirmation | PRED_BUDGET − FAST = +0.156 ms; two-way 95% CI [+0.038, +0.258] ms | Context-specific result, not universal harm | SUPPORTED |
| The frozen pairwise margin policy solves the out-of-scenario ranking problem | Arterial n8 confirmation | MARGIN_BUDGET − FAST = +0.032 ms; 95% CI [+0.007, +0.061] ms; MARGIN − ORACLE = +0.622 ms, 95% CI [+0.277, +1.472] | Frozen model; no retuning | CONTRADICTED / NEGATIVE RESULT |
| Timestamp/query rows may be treated as independent observations | Shared query-run and donor-run structure | Two-way cluster design explicitly rejects row independence | Acquisition run is the relevant cluster | DO NOT CLAIM |
| The measured oracle estimates a causal benefit of changing speed | Observational repeated drives only | No randomized intervention identification | Network load, time, blockage, traffic may differ across runs | DO NOT CLAIM |
| The matched donor outcome is arbitrary real counterfactual ground truth | Finite route/action overlap only | Outcome exists only where separate measured drives provide support | Unsupported actions remain unevaluable from the log | DO NOT CLAIM |
| The work introduces generic decision-focused learning | Existing predict-then-optimize / decision-focused literature | Prior art | Contribution is field-evidence protocol and empirical decision-reliability study | DO NOT CLAIM |
| The work introduces communication-aware motion planning | Extensive prior literature | Prior art | Use measured decision-validity framing | DO NOT CLAIM |
| The work is the first predictive-QoS system for vehicles | Existing automotive PQoS literature | Prior art | -- | DO NOT CLAIM |
| CICV5G validates PC-FMCW optical communication | No optical evidence in CICV5G | None | Cross-technology invalid inference | DO NOT CLAIM |

## Primary confirmed result

The paper's central result is **not** planner superiority.

It is:

> Across two pre-frozen repeated-field evaluations with different speed-action pairs, support-bounded measured action opportunity remains visible while frozen prediction-based rankings fail to recover it reliably: superiority over FAST is unconfirmed in W2S and the same predictive intervention is measurably worse than FAST in the arterial confirmation.

## Confirmed contribution chain

```text
field QoS prediction
        ↓
finite action support
        ↓
disjoint train / donor / query acquisition runs
        ↓
measured action evaluation
        ↓
query-run × donor-run dependence-aware inference
        ↓
prediction-to-decision evidence gap
```

## Submission rule

Every strong manuscript statement must map to:

- this matrix;
- `docs/PAPER2_CONFIRMATORY_RESULT_2026-09-30.md`;
- `docs/PAPER2_ARTERIAL_CONFIRMATION_RESULT_2026-09-30.md`;
- `docs/PAPER2_CROSS_SCENARIO_SYNTHESIS_2026-09-30.md`;
- an archived numerical artifact;
- or a verified external source.

Do not restore the older P2-superiority framing merely because the locked point estimate is favorable. The dependence-aware interval for PRED-versus-FAST crosses zero.
