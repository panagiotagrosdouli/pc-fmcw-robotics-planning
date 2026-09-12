# Paper 2 — Formal Mathematical Formulation

This file freezes the mathematical notation for the measured-V2X manuscript. It is intentionally aligned with the implemented pipeline and avoids claims not supported by the code/data.

## 1. Indexed field measurements

Let a measured acquisition run be indexed by \(r\), and let sample index \(t\) denote chronological order within a run. Each record is

\[
z_{r,t} = (x_{r,t}, c_{r,t}, y_{r,t}),
\]

where \(x_{r,t}\in\mathbb{R}^2\) is vehicle position, \(c_{r,t}\) denotes causally available context (e.g., radio indicators, heading, velocity, network/scenario metadata when permitted by the implemented feature set), and \(y_{r,t}\) is measured communication delay.

For a prediction horizon \(h\), the supervised target is

\[
y^{(h)}_{r,t}=y_{r,t+h}.
\]

No feature may contain information generated after time \(t\) for the query being evaluated.

## 2. Grouped anti-leakage partition

The set of complete runs \(\mathcal R\) is partitioned as

\[
\mathcal R = \mathcal R_{\mathrm{tr}} \;\dot\cup\; \mathcal R_{\mathrm{cal}} \;\dot\cup\; \mathcal R_{\mathrm{te}},
\]

with no run appearing in more than one partition. All samples of a run inherit the partition of that run. Predictors and empirical spatial support are fitted only from \(\mathcal R_{\mathrm{tr}}\); model/fusion selection and residual uncertainty calibration use \(\mathcal R_{\mathrm{cal}}\); final planning evaluation uses \(\mathcal R_{\mathrm{te}}\).

## 3. Persistence and learned spatial/context predictors

The persistence predictor for horizon \(h\) is

\[
\hat y^{\mathrm{pers}}_{r,t+h\mid t}=y_{r,t}.
\]

Let \(f_h(\cdot)\) be a learned predictor fitted only on training runs. Its forecast is

\[
\hat y^{\mathrm{learn}}_{r,t+h\mid t}=f_h(x_{r,t+h}^{\mathrm{cand}}, c_{r,t}),
\]

where \(x_{r,t+h}^{\mathrm{cand}}\) denotes the candidate future state supplied to the predictor and \(c_{r,t}\) contains only information available at decision time.

For the calibration-gated horizon-adaptive predictor, let \(\alpha_h\in[0,1]\) be chosen exclusively from calibration data. Then

\[
\hat y^{\mathrm{fuse}}_{r,t+h\mid t}
= (1-\alpha_h)\hat y^{\mathrm{pers}}_{r,t+h\mid t}
+ \alpha_h\hat y^{\mathrm{learn}}_{r,t+h\mid t}.
\]

A value \(\alpha_h\approx 0\) corresponds to a persistence-dominated short-horizon regime; larger \(\alpha_h\) is allowed only when calibration evidence supports incremental learned value.

## 4. Residual split-conformal interval

On the calibration set, define absolute residuals

\[
e_i = \left|y_i-\hat y_i\right|.
\]

Let \(q_{1-\gamma}\) be the finite-sample empirical conformal quantile for nominal miscoverage \(\gamma\). The prediction interval is

\[
\mathcal I(x)=\left[\hat y(x)-q_{1-\gamma},\;\hat y(x)+q_{1-\gamma}\right].
\]

In this paper this interval is treated as an empirical uncertainty diagnostic. It is **not** interpreted as a calibrated probability of threshold violation or outage.

## 5. Empirical measurement support

Let the training-position set be

\[
\mathcal X_{\mathrm{tr}} = \{x_i: i\in\mathcal R_{\mathrm{tr}}\}.
\]

For candidate position \(x\), define nearest-training distance

\[
d_{\min}(x)=\min_{x_i\in\mathcal X_{\mathrm{tr}}}\|x-x_i\|_2.
\]

For a support radius \(\rho\), define local measurement density

\[
n_{\rho}(x)=\sum_{x_i\in\mathcal X_{\mathrm{tr}}}\mathbf 1\{\|x-x_i\|_2\le\rho\}.
\]

A candidate is empirically unsupported under the frozen rule when

\[
u(x)=\mathbf 1\{d_{\min}(x)>d_{\max}\;\lor\;n_{\rho}(x)<n_{\min}\}.
\]

The thresholds \(d_{\max}\), \(\rho\), and \(n_{\min}\) are experimental validity controls, not physical propagation constants.

## 6. Route-constrained measured candidate set

For a held-out run \(r\) and decision time \(t\), the candidate set is restricted to future states actually present in the same measured trajectory:

\[
\mathcal A_{r,t}=\{a_{r,t}^{(1)},\ldots,a_{r,t}^{(K)}\},
\]

where each candidate maps to a later recorded state \(x_{r,t+h_k}\). Its future measured delay \(y_{r,t+h_k}\) is hidden during planner scoring and revealed only after selection for evaluation.

This design avoids inventing communication ground truth for arbitrary off-route counterfactual positions.

## 7. Planner objective

Let \(J_{\mathrm{mob}}(a)\) denote mobility deviation/cost for candidate \(a\), and let \(\hat y(a)\) denote its predicted future communication delay.

### P0: mobility/reference planner

\[
a^{\star}_{P0}=\arg\min_{a\in\mathcal A_{r,t}} J_{\mathrm{mob}}(a).
\]

### P1: reactive/current-QoS planner

P1 uses the current communication state/persistence forecast rather than a learned future spatial prediction:

\[
a^{\star}_{P1}=\arg\min_{a\in\mathcal A_{r,t}}
\left[J_{\mathrm{mob}}(a)+\lambda_c\hat y^{\mathrm{pers}}(a)\right].
\]

### P2: predictive communication planner

\[
a^{\star}_{P2}=\arg\min_{a\in\mathcal A_{r,t}}
\left[J_{\mathrm{mob}}(a)+\lambda_c\hat y^{\mathrm{fuse}}(a)\right].
\]

P2 is the primary test of whether future QoS prediction has decision utility.

### P3: predictive planner with empirical-support control

\[
a^{\star}_{P3}=\arg\min_{a\in\mathcal A_{r,t}}
\left[J_{\mathrm{mob}}(a)+\lambda_c\hat y^{\mathrm{fuse}}(a)+\lambda_s\,u(a)\right].
\]

A continuous support penalty can be substituted if implemented, but the interpretation remains the same: \(\lambda_s\) controls willingness to act on predictions made in weakly represented regions.

## 8. Measured post-decision evaluation

If planner \(P\) selects candidate \(a^{\star}_{P}\) corresponding to a recorded future index \(t+h^{\star}\), measured evaluation uses

\[
y^{\mathrm{meas}}_{P,r,t}=y_{r,t+h^{\star}}.
\]

The threshold-violation indicator for experimental delay threshold \(\tau=50\,\mathrm{ms}\) is

\[
v_{P,r,t}=\mathbf 1\{y^{\mathrm{meas}}_{P,r,t}>\tau\}.
\]

The unsupported-selection indicator is

\[
s_{P,r,t}=u(x(a^{\star}_{P})).
\]

## 9. Paired run-level comparison

For metric \(m\) and planners \(A,B\), aggregate decisions within held-out run \(r\) to obtain \(m_{A,r}\) and \(m_{B,r}\). The paired run effect is

\[
\Delta_{m,r}=m_{B,r}-m_{A,r}.
\]

Inference on the primary split is performed on the vector \(\{\Delta_{m,r}\}\) using a paired bootstrap confidence interval and paired Wilcoxon signed-rank test. Holm correction is applied to the predeclared family of planner/metric tests.

## 10. Multi-split robustness without pseudoreplication

Let \(s\in\{1,\ldots,S\}\) index alternative grouped train/calibration/test assignments. Because the same acquisition runs can appear across different assignments, effects \(\Delta^{(s)}\) are dependent. Therefore we report descriptive quantities such as

\[
\bar\Delta=\frac{1}{S}\sum_s\Delta^{(s)},
\quad
\mathrm{median}_s\,\Delta^{(s)},
\quad
\frac{1}{S}\sum_s \mathbf 1\{\Delta^{(s)}<0\},
\]

without treating \(S\) as an independent inferential sample size.

## 11. Interpretation boundary

The formalism supports the following distinctions:

- prediction accuracy is not the same as decision utility;
- prediction uncertainty is not the same as empirical measurement support;
- repeated grouped splits are not independent subjects;
- route-constrained replay supplies measured post-decision outcomes only for actually traversed candidate states;
- CICV5G provides field-measured 5G evidence for the communication-decision branch only.
