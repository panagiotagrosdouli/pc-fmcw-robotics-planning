# Paper 2 — Formal Mathematical Formulation

**Updated:** 2026-09-30

This file freezes the notation for the canonical support-bounded matched field replay paper.

## 1. Field observations

For acquisition run (r) and sample (t),

[
z_{r,t}=(x_{r,t},c_{r,t},a_r,y_{r,t}),
]

where:

- (x_{r,t}inmathbb{R}^2) is position;
- (c_{r,t}) is communication/context information;
- (a_r) is the nominal motion action represented by the run speed;
- (y_{r,t}) is measured communication delay.

## 2. Disjoint evidence roles

Within network × direction × speed strata,

[
mathcal R=
mathcal R_{mathrm{tr}}
dotcup
mathcal R_{mathrm{don}}
dotcup
mathcal R_{mathrm{qry}}.
]

- (mathcal R_{mathrm{tr}}): predictive-model fitting.
- (mathcal R_{mathrm{don}}): measured action-outcome donation.
- (mathcal R_{mathrm{qry}}): decision contexts.

No acquisition run serves more than one role in one locked analysis.

## 3. Supported motion actions

For query state (x) and action (a), define

[
mathcal D(x,a)=
left{
iinmathcal R_{mathrm{don}}:
c_i=c_x,,
a_i=a,,
|p_i-p_x|_2leho
ight}.
]

A comparative query is eligible only if both candidate actions have nonempty donor support.

The locked spatial caliper is

[
ho=2,mathrm{m}.
]

## 4. Matched measured outcome

For selected donor subset (mathcal D^star(x,a)),

[
	ilde y(x,a)=
rac{1}{|mathcal D^star(x,a)|}
sum_{iinmathcal D^star(x,a)} y_i.
]

Donor selection prefers acquisition-run diversity before repeated samples from one donor run.

The measured donor outcome is hidden from deployable policy ranking.

## 5. Action sets

Primary W2S confirmation:

[
mathcal A_{mathrm{W2S}}={30,50} mathrm{km/h}.
]

Arterial confirmation:

[
mathcal A_{mathrm{art}}={50,80} mathrm{km/h}.
]

In each pair, define (a_s) as the slower action and (a_f) as the faster action.

## 6. Absolute-QoS predictive gain

A context-conditioned predictor fitted only on (mathcal R_{mathrm{tr}}) gives

[
g_{mathrm{pred}}(x)
=
hat y(x,a_f)-hat y(x,a_s).
]

Positive (g_{mathrm{pred}}) predicts lower delay under the slower action.

## 7. Pairwise action-margin model

The frozen pairwise model estimates

[
g_{mathrm{margin}}(x)
=
widehat{
	ilde y(x,a_f)-	ilde y(x,a_s)
}.
]

It is a comparator, not the claimed contribution.

## 8. Budgeted decision rule

To avoid arbitrary scalarization between mobility time and network delay, each query run receives a maximum intervention budget

[
B=0.10.
]

FAST selects (a_f) everywhere.

PRED_BUDGET ranks locations by positive (g_{mathrm{pred}}) and may select (a_s) at at most fraction (B).

MARGIN_BUDGET applies the same budget to the frozen pairwise score.

## 9. Measured upper-bound diagnostic

Define measured action gain

[
g_{mathrm{oracle}}(x)
=
	ilde y(x,a_f)-	ilde y(x,a_s).
]

ORACLE_BUDGET ranks query locations using (g_{mathrm{oracle}}) under the same budget.

Because donor outcomes are used in ranking and evaluation, ORACLE_BUDGET is a nondeployable support-bounded upper-bound diagnostic, not an unbiased future policy estimate.

## 10. Primary estimands

Measured action opportunity:

[
E_1
=
Y_{mathrm{ORACLE}}-Y_{mathrm{FAST}}.
]

Predictive regret relative to the measured upper bound:

[
E_2
=
Y_{mathrm{PRED}}-Y_{mathrm{ORACLE}}.
]

Secondary effects:

[
Y_{mathrm{PRED}}-Y_{mathrm{FAST}},
]

[
Y_{mathrm{MARGIN}}-Y_{mathrm{FAST}},
]

[
Y_{mathrm{MARGIN}}-Y_{mathrm{ORACLE}}.
]

Lower delay is better.

## 11. Two-way acquisition-run bootstrap

Matched outcomes contain two dependence dimensions:

- query acquisition run;
- donor acquisition run.

For bootstrap replicate (b):

1. resample query runs with replacement;
2. independently resample donor runs with replacement;
3. reconstruct matched action outcomes from resampled donor contributions;
4. recompute ORACLE_BUDGET within the replicate;
5. retain frozen PRED_BUDGET and MARGIN_BUDGET rankings;
6. aggregate at the query-run level.

The locked analyses use 5,000 replicates and percentile 95% intervals.

## 12. Interpretation boundary

The formalism distinguishes:

- prediction quality from action-ranking validity;
- finite measured action support from model-generated predictions;
- measured donor outcomes from causal potential outcomes;
- deployable predictive rankings from a nondeployable measured upper bound;
- timestamp rows from independent acquisition-run evidence;
- within-dataset cross-scenario confirmation from generalization outside CICV5G.

No causal speed-effect claim follows from this formulation.
