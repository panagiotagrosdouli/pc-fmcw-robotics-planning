# Paper 2 — Reviewer-Style Go/No-Go Verdict After Frozen Decision-Margin Audit

**Date:** 2026-09-30  
**Branch:** `research/paper2-matched-speed-replay`  
**Frozen audit workflow:** Decision Margin Audit, run `36744390669`  
**Frozen-code commit:** `8dbd7a5289f5e855c572da65935acac75ceea1f5`  
**Artifact:** `decision-margin-audit`, artifact ID `11111858311`

## Bottom-line scientific verdict

**GO for a methodology / failure-boundary paper.**  
**NO-GO for a "new planner outperforms baseline" paper.**

The measured repeated-drive experiment shows a stable and substantial action-value opportunity, but neither the independent absolute-QoS predictor nor the frozen pairwise decision-margin predictor recovers that opportunity reliably across whole-run splits and spatial-support settings.

That mismatch is the scientifically defensible result.

---

## What remained stable

Across the 15 support-balanced development configurations (5 whole-run split seeds × 3 spatial calipers), the nondeployable matched measured oracle is favorable relative to FAST in:

- **15/15 configurations for mean matched delay**;
- **15/15 configurations for matched p95 delay**.

Mean oracle headroom across configurations:

- mean-delay difference: approximately **-4.63 ms** versus FAST;
- matched-p95 difference: approximately **-29.08 ms** versus FAST.

The magnitude varies substantially across run-role assignments, which is itself evidence that acquisition-run variation matters and that row-level inference would be misleading.

The correct conclusion is not that a causal speed effect has been identified. The correct conclusion is that the repeated field data contain **support-bounded measured action heterogeneity** large enough to matter for downstream decision evaluation.

---

## What the ordinary predictive policy achieved

For the support-balanced W2S design:

### Mean matched delay

`PRED - FAST`:

- favorable in **9/15** configurations;
- unfavorable in **6/15**;
- average development delta approximately **-0.78 ms**;
- range approximately **-3.42 to +1.05 ms**.

### Matched p95 delay

`PRED - FAST`:

- favorable in **8/15** configurations;
- unfavorable in **7/15**;
- average delta approximately **-3.36 ms**;
- range approximately **-29.09 to +9.91 ms**.

The support-gated absolute-QoS policy is essentially the same qualitatively.

Therefore absolute QoS prediction does not yield a robust downstream speed-decision claim.

---

## Frozen pairwise decision-margin hypothesis

The pairwise model was frozen before the audit results were inspected.

Predeclared condition:

> A pairwise model trained directly on measured action margins would be considered promising only if it was favorable more consistently than the absolute-QoS predictor across multiple budgets, without simply spending more intervention budget.

It failed this condition.

### 1% intervention budget

Mean-delay comparison versus FAST:

- `MARGIN_BUDGET`: favorable **5/15**, unfavorable **10/15**, mean delta **+0.032 ms**;
- `PRED_BUDGET`: favorable **4/15**, unfavorable **11/15**, mean delta **-0.154 ms**;
- `ORACLE_BUDGET`: favorable **15/15**, mean delta **-1.706 ms**.

The pairwise model does not establish a useful reliability advantage.

### 5% intervention budget

- `MARGIN_BUDGET`: favorable **7/15**, unfavorable **8/15**, mean delta approximately **-0.006 ms**;
- `PRED_BUDGET`: favorable **9/15**, unfavorable **6/15**, mean delta approximately **-0.381 ms**;
- `ORACLE_BUDGET`: favorable **15/15**, mean delta approximately **-4.266 ms**.

The pairwise model is less reliable than the ordinary predicted-gain ranking.

### 10% intervention budget

- `MARGIN_BUDGET`: favorable **6/15**, unfavorable **9/15**, mean delta approximately **-0.198 ms**;
- `PRED_BUDGET`: favorable **9/15**, unfavorable **6/15**, mean delta approximately **-1.012 ms**;
- `ORACLE_BUDGET`: favorable **15/15**, mean delta approximately **-4.961 ms**.

Again, the pairwise model fails the frozen promising-method criterion.

### Conservative lower-margin rule

The lower-quantile decision rule also fails:

- it frequently abstains;
- when it acts, it does not demonstrate improved reliability;
- its average mean-delay effect is unfavorable at all three tested budgets.

It must be retained as a negative development result, not retuned after inspection.

---

# The actual research finding

The strongest scientific observation is now:

> **The field data contain substantial measured action-value heterogeneity, but models that appear useful at the QoS-prediction level do not reliably recover the downstream motion-action ranking under disjoint acquisition-run evaluation.**

This is different from a generic statement that "prediction error is not decision error."

The empirical contribution is that the failure is demonstrated under a specific evidence discipline:

1. repeated real V2X field drives;
2. physically interpretable motion actions (30 vs 50 km/h);
3. disjoint acquisition-run roles for training, measured outcome donation, and decision queries;
4. exact network/direction/action matching plus spatial support;
5. outcome measurements hidden during action selection;
6. measured matched oracle used only after selection;
7. whole-run sensitivity instead of timestamp pseudo-replication;
8. negative pairwise-model result retained under a pre-frozen protocol.

---

# What the paper should now claim

## Safe central claim

> We show that predictive accuracy and measured motion-action reliability can diverge substantially when vehicular QoS models are evaluated using disjoint repeated field drives. A support-bounded matched replay exposes stable action-value headroom that neither absolute-QoS prediction nor a frozen pairwise action-margin model recovers consistently.

## Strong methodological contribution

> We operationalize a measured evaluation boundary for communication-aware vehicle actions by separating model training, measured candidate outcomes, and decision queries across acquisition runs and refusing to assign model-generated truth to unsupported actions.

## Negative result worth preserving

> Directly training on an action-margin target does not automatically solve the decision-reliability problem.

This is scientifically useful because it prevents the paper from collapsing into generic "decision-focused learning improves planning."

---

# Claims that are not supported

Do not claim:

- a superior communication-aware speed controller;
- causal benefit of driving at 30 or 50 km/h;
- real counterfactual ground truth;
- a first decision-focused learning method;
- a first regret-aware vehicular decision system;
- pairwise decision-margin learning improves the policy;
- support gating solves distribution shift;
- row-level statistical significance from the 1,203 matched query locations;
- that the oracle is deployable.

---

# Reviewer-facing novelty boundary

The literature audit already establishes prior art in:

- communication-aware motion planning;
- predictive QoS for vehicular adaptation;
- decision-focused / predict-then-optimize learning;
- regret-aware vehicular decisions;
- task-aware radio world models such as RMWorld;
- generic logged-data/off-policy evaluation.

Therefore the paper's non-overlap is **not an algorithmic primitive**.

The non-overlap is the measured field-evidence question:

> **What changes when a communication-aware motion decision is evaluated only where a separate acquisition run provides measured support for that action, and prediction accuracy is not allowed to serve as its own counterfactual truth?**

The frozen results show that this evidence rule materially changes the scientific conclusion: models with apparently useful predictive structure do not support a robust planner-superiority claim.

That is exactly the condition stated in the literature-audit publication rule.

---

# Publication structure

## Proposed title

**Prediction Is Not Decision Evidence: Support-Bounded Matched Field Replay for Communication-Aware Vehicle Speed Decisions**

More conservative IEEE title:

**From QoS Prediction to Measured Decision Validity: Cross-Run Matched Replay for Vehicular Speed Decisions**

The first is more memorable. The second is safer.

## Proposed paper structure

1. **Problem statement** — logged field QoS observes executed conditions, while motion decisions require alternative-action evidence.
2. **Evidence protocol** — train/donor/query acquisition-run separation and finite action overlap.
3. **Matched speed replay** — 30/50-km/h action construction and support criteria.
4. **Prediction study** — ordinary QoS prediction and its downstream ranking.
5. **Frozen decision-margin study** — predeclared pairwise hypothesis and negative result.
6. **Measured oracle gap** — quantify available support-bounded action-value headroom.
7. **Run-role sensitivity** — demonstrate why donor/run identity matters.
8. **Limitations** — observational repeated drives, no causal speed-effect claim, limited run count, W2S focus.
9. **Conclusion** — prediction metrics alone are insufficient evidence for communication-aware motion claims from field logs.

---

# What is needed before submission

The current evidence is development evidence, not yet a clean final confirmation.

A final paper should add one **locked confirmatory layer** without algorithm retuning:

1. freeze the evaluation method and all current negative results;
2. construct a confirmatory resampling or cross-fitting scheme that accounts for both query-run and donor-run dependence;
3. predeclare the primary estimand:
   - oracle action-value headroom;
   - PRED action regret relative to the matched oracle;
   - optionally MARGIN action regret as a frozen negative comparator;
4. report network/context heterogeneity rather than only one pooled mean;
5. keep the final claims methodological even if a subset happens to look favorable.

Do **not** tune another learning model merely to obtain a positive planner result.

---

# Go/no-go decision

### As a positive new-algorithm paper
**NO-GO.**

The frozen pairwise method did not outperform the ordinary predictor robustly.

### As a measured decision-validity / evidence-boundary paper
**GO, conditional on confirmatory dependence-aware analysis.**

The reason is strong:

- measured action headroom is stable in direction;
- predictive exploitation is unstable;
- direct pairwise decision learning also fails;
- the evaluation framework explains why prediction-level evidence cannot be silently promoted to motion-decision evidence.

This is a coherent empirical contribution and is more scientifically defensible than forcing a planner-superiority story.
