# Paper 2 — Results and Evidence Checklist

**Updated:** 2026-09-30

## Primary publication evidence

The canonical manuscript is governed by:

- `results_archive/confirmed_w2s/`;
- `results_archive/confirmed_arterial/`;
- `CLAIM_EVIDENCE.md`;
- the frozen protocol/result documents under `docs/PAPER2_*.md`.

## W2S locked confirmation

Configuration:

- W2S only;
- 30 vs 50 km/h;
- split seed 20260930;
- train fraction 0.40;
- donor fraction 0.40;
- 2-m caliper;
- 5-m query thinning;
- 10% intervention budget;
- 9 query runs;
- 9 donor runs;
- 1,029 matched comparison contexts;
- 5,000 requested two-way bootstrap replicates;
- 4,945 valid replicates.

Point mean delays:

- FAST: 23.546 ms;
- PRED_BUDGET: 22.073 ms;
- MARGIN_BUDGET: 21.878 ms;
- ORACLE_BUDGET: 19.369 ms.

Effects:

- ORACLE − FAST: −4.177 ms; 95% CI [−13.659, −2.137];
- PRED − ORACLE: +2.704 ms; 95% CI [+1.457, +5.832];
- PRED − FAST: −1.473 ms; 95% CI [−8.167, +0.657];
- MARGIN − FAST: −1.668 ms; 95% CI [−9.524, +1.180];
- MARGIN − ORACLE: +2.509 ms; 95% CI [+1.572, +5.162].

Interpretation:

- measured action-value headroom: supported;
- predictor regret relative to oracle diagnostic: supported;
- PRED superiority over FAST: not confirmatory;
- MARGIN superiority over FAST: not confirmatory.

## Arterial locked confirmation

Configuration:

- arterial road;
- n8 only;
- 50 vs 80 km/h;
- split seed 20260930;
- train fraction 0.40;
- donor fraction 0.40;
- 2-m caliper;
- 5-m query thinning;
- 10% intervention budget;
- 4 query runs;
- 4 donor runs;
- 319 matched comparison contexts;
- 5,000 requested bootstrap replicates;
- 4,409 valid replicates.

Point mean delays:

- FAST: 18.871 ms;
- PRED_BUDGET: 19.026 ms;
- MARGIN_BUDGET: 18.903 ms;
- ORACLE_BUDGET: 18.281 ms.

Effects:

- ORACLE − FAST: −0.590 ms; 95% CI [−1.431, −0.250];
- PRED − ORACLE: +0.746 ms; 95% CI [+0.344, +1.596];
- PRED − FAST: +0.156 ms; 95% CI [+0.038, +0.258];
- MARGIN − FAST: +0.032 ms; 95% CI [+0.007, +0.061];
- MARGIN − ORACLE: +0.622 ms; 95% CI [+0.277, +1.472].

Interpretation:

- measured action-value headroom: supported;
- predictor regret: supported;
- PRED is worse than FAST in this frozen setting;
- MARGIN is worse than FAST in this frozen setting.

## Development robustness

Across 15 support-balanced W2S seed/caliper configurations:

- oracle mean-delay direction favorable: 15/15;
- PRED mean-delay direction favorable: 9/15;
- PRED p95 direction favorable: 8/15.

These configurations reuse the finite drive pool and are descriptive sensitivity analyses only.

## Secondary predictor background

The legacy predictor audit remains background evidence:

- one-step persistence MAE: 5.576 ms;
- spatial kNN MAE: 10.862 ms;
- Random Forest MAE: 7.150 ms;
- Extra Trees MAE: 6.659 ms;
- longer-horizon spatial/context information can improve over persistence.

These results do not establish a motion-policy benefit by themselves.

## Statistical rules

- acquisition run is the relevant evidence cluster;
- timestamp/query rows are not independent subjects;
- donor-run reuse must be accounted for;
- bootstrap draws are not independent experiments;
- measured oracle is not a deployable policy estimate;
- repeated drives do not identify causal speed effects.

## Prohibited wording

Do not write:

- "PRED significantly outperforms FAST";
- "pairwise margin solves the decision problem";
- "30 km/h causally improves communication";
- "80 km/h causally degrades communication";
- "real counterfactual ground truth";
- "first decision-focused V2X planner";
- "thousands of independent matched decisions".

Preferred wording:

- "support-bounded matched field outcome";
- "two-way acquisition-run bootstrap";
- "measured upper-bound action-value diagnostic";
- "prediction-to-decision evidence gap";
- "context-dependent decision reliability".
