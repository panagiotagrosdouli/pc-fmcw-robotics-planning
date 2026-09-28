# Paper 2 — Formal Mathematical Formulation

This file freezes the notation for the decision-validity version of the measured-V2X paper. It is aligned with the implemented pipeline and archived evidence.

## 1. Logged field measurements

For acquisition run \(r\) and chronological sample \(t\),

\[
z_{r,t}=(x_{r,t},c_{r,t},y_{r,t}),
\]

where \(x_{r,t}\in\mathbb{R}^2\) is position, \(c_{r,t}\) is causally available vehicle/network context, and \(y_{r,t}\) is measured communication delay.

At horizon \(h\),

\[
y^{(h)}_{r,t}=y_{r,t+h}.
\]

No feature generated after time \(t\) may be used by a deployable query evaluated at \(t\).

## 2. Whole-run anti-leakage partition

\[
\mathcal R=
\mathcal R_{\mathrm{tr}}
\dot\cup
\mathcal R_{\mathrm{cal}}
\dot\cup
\mathcal R_{\mathrm{te}}.
\]

All samples from one acquisition run inherit the same partition.

- \(\mathcal R_{\mathrm{tr}}\): predictor fitting and empirical-support fitting.
- \(\mathcal R_{\mathrm{cal}}\): fusion/model selection and residual uncertainty calibration.
- \(\mathcal R_{\mathrm{te}}\): final prediction and decision replay evaluation.

Alternative grouped assignments reuse runs and are descriptive sensitivity analyses, not independent experiments.

## 3. Decision-validity layer I: predictive value

Persistence is the mandatory causal baseline:

\[
\hat y^{\mathrm{pers}}_{r,t+h\mid t}=y_{r,t}.
\]

A learned predictor is

\[
\hat y^{\mathrm{learn}}_{r,t+h\mid t}
=f_h(x_{r,t+h}^{\mathrm{cand}},c_{r,t}),
\]

where all context is available at decision time.

The calibration-gated fusion is

\[
\hat y^{\mathrm{fuse}}_{r,t+h\mid t}
=(1-\alpha_h)\hat y^{\mathrm{pers}}_{r,t+h\mid t}
+\alpha_h\hat y^{\mathrm{learn}}_{r,t+h\mid t},
\qquad
\alpha_h\in[0,1],
\]

with \(\alpha_h\) selected only on calibration runs.

Predictive validity is therefore horizon-specific: a learned component receives decision credit only where it adds held-out value beyond persistence.

## 4. Residual uncertainty

For calibration residuals

\[
e_i=|y_i-\hat y_i|,
\]

let \(q_{1-\gamma}\) be the empirical conformal quantile. Then

\[
\mathcal I(x)=
[\hat y(x)-q_{1-\gamma},\hat y(x)+q_{1-\gamma}].
\]

These intervals are empirical residual diagnostics. Under grouped distribution shift they are not interpreted as guaranteed event probabilities.

## 5. Decision-validity layer II: empirical support

Let

\[
\mathcal X_{\mathrm{tr}}=
\{x_i:i\in\mathcal R_{\mathrm{tr}}\}.
\]

Nearest training distance:

\[
d_{\min}(x)=
\min_{x_i\in\mathcal X_{\mathrm{tr}}}
\|x-x_i\|_2.
\]

Local measurement density:

\[
n_\rho(x)=
\sum_{x_i\in\mathcal X_{\mathrm{tr}}}
\mathbf 1\{\|x-x_i\|_2\le\rho\}.
\]

Frozen unsupported-query indicator:

\[
u(x)=
\mathbf 1\{
d_{\min}(x)>d_{\max}
\lor
n_\rho(x)<n_{\min}
\}.
\]

The thresholds are empirical validity controls, not propagation constants. Predictive uncertainty and empirical support remain separate objects.

## 6. Decision-validity layer III: measured evaluability

For held-out run \(r\) and time \(t\), MSCR restricts evaluation candidates to later states actually recorded in the same run:

\[
\mathcal A_{r,t}=
\{a_{r,t}^{(1)},\ldots,a_{r,t}^{(K)}\}.
\]

Candidate \(a_{r,t}^{(k)}\) maps to a future logged state \(x_{r,t+h_k}\).

The associated future measured delay \(y_{r,t+h_k}\):

1. exists in the held-out log,
2. is unavailable during planner scoring,
3. is revealed only after selection.

Thus the predictor cannot define its own post-decision ground truth.

MSCR is an offline route-supported evaluation protocol. It does not identify the causal outcome of an arbitrary physical route intervention.

## 7. Planner objectives

Let \(J_{\mathrm{mob}}(a)\) denote mobility cost.

### P0 — mobility/reference

\[
a^\star_{P0}=
\arg\min_{a\in\mathcal A_{r,t}}
J_{\mathrm{mob}}(a).
\]

### P1 — reactive/current QoS

\[
a^\star_{P1}=
\arg\min_{a\in\mathcal A_{r,t}}
[J_{\mathrm{mob}}(a)+
\lambda_c\hat y^{\mathrm{pers}}(a)].
\]

### P2 — predictive QoS

\[
a^\star_{P2}=
\arg\min_{a\in\mathcal A_{r,t}}
[J_{\mathrm{mob}}(a)+
\lambda_c\hat y^{\mathrm{fuse}}(a)].
\]

P2 tests predictive decision utility.

### P3 — predictive QoS with empirical-support control

\[
a^\star_{P3}=
\arg\min_{a\in\mathcal A_{r,t}}
[J_{\mathrm{mob}}(a)+
\lambda_c\hat y^{\mathrm{fuse}}(a)+
\lambda_s u(a)].
\]

P3 tests willingness to act on weakly supported predictions. It is not defined as a guaranteed QoS improvement.

## 8. Post-selection measured outcome

If planner \(P\) selects a candidate corresponding to future index \(t+h^\star\),

\[
y^{\mathrm{meas}}_{P,r,t}
=y_{r,t+h^\star}.
\]

For experimental threshold \(\tau=50\,\mathrm{ms}\),

\[
v_{P,r,t}
=\mathbf 1\{
y^{\mathrm{meas}}_{P,r,t}>\tau
\}.
\]

Unsupported-selection indicator:

\[
s_{P,r,t}
=u(x(a^\star_P)).
\]

## 9. Run-level inference

For metric \(m\), planners \(A,B\), and held-out run \(r\),

\[
\Delta_{m,r}
=m_{B,r}-m_{A,r}.
\]

Primary-split inference uses the run-level paired effects with deterministic paired bootstrap confidence intervals and paired Wilcoxon tests. Holm correction is applied across the declared comparison/metric family.

Timestamps are not treated as independent subjects.

## 10. Repeated grouped splits

For split assignment \(s\),

\[
\Delta^{(s)}
\]

is dependent across \(s\) because drives recur. Reported summaries may include

\[
\bar\Delta=
\frac{1}{S}\sum_s\Delta^{(s)}
\]

and the fraction of assignments with favorable direction, but \(S\) is not treated as an independent sample size.

## 11. Interpretation boundary

The formalism intentionally distinguishes:

- regression accuracy from decision utility;
- short-horizon persistence from planning-horizon predictive value;
- residual uncertainty from empirical support;
- model-generated counterfactual values from measured post-selection outcomes;
- descriptive split robustness from independent replication;
- offline route-supported replay from physical intervention;
- measured 5G evidence from the separate modeled PC-FMCW optical branch.
