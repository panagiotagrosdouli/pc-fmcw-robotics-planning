# Paper 2 — Literature Audit for Decision Calibration

**Date:** 2026-09-30  
**Purpose:** prevent novelty inflation before the matched-field direction is promoted to a manuscript claim.

## Prior art that must be conceded

### Communication-aware motion planning

Communication quality has influenced robot/vehicle motion for many years. The paper cannot claim novelty for coupling mobility and connectivity.

Representative foundation:
- Ghaffarkhah & Mostofi, *Communication-Aware Motion Planning in Mobile Networks*.

### Predictive QoS for automotive systems

Predictive QoS is already explicitly motivated as a mechanism for proactive adaptation in automotive and teleoperated-driving applications.

Representative examples:
- NordicDat, cross-border predictive-QoS dataset;
- PRATA, predictive-QoS framework for teleoperated driving;
- existing vehicular QoS prediction and field-measurement studies already cited by Paper 2.

Therefore the paper cannot claim that future QoS prediction for vehicle adaptation is new.

### Decision-focused / predict-then-optimize learning

Training or judging predictors according to downstream optimization loss is an established general field.

Representative work:
- Elmachtoub & Grigas, *Smart Predict, then Optimize*;
- Mandi et al., *Decision-Focused Learning: Foundations, State of the Art, Benchmark and Future Opportunities*;
- subsequent task-aware and regret-weighted prediction methods.

Therefore "prediction error is not decision error" is not a standalone novelty claim.

### Regret-aware vehicular decision diagnostics

Vehicular communication papers now explicitly use oracle-referenced regret diagnostics.

Badshah et al., *Decision-Stability and Regret Diagnostics for Reinforcement Learning Based Handover in Vehicular Mobility*, IET Communications, first published 15 April 2026, evaluates a vehicular handover policy with oracle-referenced regret and decision-stability diagnostics in DriveNetSim.

Therefore the paper cannot claim the first use of regret, oracle comparison, or decision-stability analysis in vehicular communication decisions.

### QoS prediction linked to policy evaluation

A September 2026 IETF Internet-Draft, *QoSformer: A Framework for Learning-Based QoS Prediction and Policy Evaluation*, explicitly connects learned QoS prediction with evaluation of candidate network-policy configurations and separates prediction from post-change observation.

Therefore the paper cannot claim novelty for the generic idea that QoS prediction should be linked to downstream policy evaluation or decision traceability.

The distinction remains the vehicular-motion evidence substrate: physically interpretable speed actions, repeated measured drives, disjoint train/donor/query acquisition-run roles, finite action support, and donor-aware inference.

### Task-aware radio world models

RMWorld (2026) explicitly argues that globally accurate radio models can fail at decision-sensitive regions where rate errors reverse control decisions, and it learns/calibrates the model according to downstream task relevance.

Therefore the paper cannot claim the first task-aware or decision-relevant communication model.

## Remaining non-overlap

The defensible distinction is the **evaluation substrate** and evidence boundary.

The proposed Paper 2 asks:

> When a vehicle-motion action is selected from a field-trained communication model, can the resulting decision be evaluated using a measured outcome from disjoint repeated drives, while enforcing finite action overlap and refusing unsupported counterfactual claims?

The specific combination is:

1. repeated real vehicular communication drives;
2. physically interpretable motion action (30 vs 50 km/h);
3. disjoint training / donor-outcome / query-run roles;
4. exact communication/motion context matching plus spatial support;
5. donor measurement hidden during selection;
6. measured action-ranking regret against a support-bounded matched oracle;
7. explicit abstention when action support or decision confidence is inadequate.

The novelty should be framed as a **field-evidence protocol and empirical study of decision reliability**, not as a new general learning paradigm.

## Closest-concept comparison

| Area | Existing work already establishes | Paper-2 distinction if validated |
|---|---|---|
| Communication-aware planning | communication can alter motion | field-log evidential validity of a motion action |
| Predictive QoS | future connectivity can guide proactive adaptation | downstream action ranking is evaluated with separate measured drives |
| Decision-focused learning | prediction objectives can be aligned to optimization loss | field-supported action-margin calibration under finite repeated-drive overlap |
| Regret-aware vehicular decisions | oracle regret can diagnose handover policies | regret from matched measured action outcomes rather than simulator truth |
| Radio world models / RMWorld | task-relevant radio-model error and counterfactual credibility matter | no learned world model is promoted to measured counterfactual ground truth |
| Generic off-policy evaluation | overlap/confounding matter for logged-policy evaluation | acquisition-run role separation for repeated vehicular field experiments |

## Language rule

Use:
- "we operationalize";
- "we evaluate";
- "we construct a support-bounded measured replay";
- "we separate regression accuracy from measured action reliability";
- "we quantify the effect of donor/action support".

Avoid:
- "we are the first";
- "novel decision-focused learning";
- "true counterfactual QoS";
- "causal speed optimization";
- "real-world oracle";
- "field-proven autonomous speed controller".

## Publication condition

The non-overlap is credible only if the final experiment demonstrates that the measured replay protocol materially changes what conclusions would be drawn from prediction accuracy alone.

If the final paper reduces to "a different loss improves speed selection," it is too close to generic decision-focused learning.

If it shows that field action support, donor-run variation, and decision calibration alter the evidential validity of communication-aware vehicle decisions, the methodological distinction is substantially stronger.
