# Decision-Margin Development Freeze

**Freeze date:** 2026-09-30  
**Audit code commit already running:** `8dbd7a5289f5e855c572da65935acac75ceea1f5`  
**Workflow:** `Decision Margin Audit`  
**Status:** parameters frozen before audit results are inspected.

## Scientific purpose

Test one predeclared hypothesis:

> A pairwise model trained on field-supported action margins may rank communication-beneficial speed interventions more reliably than independent absolute-QoS predictions.

This is a development test, not a confirmatory experiment.

## Data/evidence roles

- Direction: W2S only.
- Candidate actions: 30 and 50 km/h.
- Whole-run evidence-role split within network/direction/speed strata.
- Training fraction: 0.40.
- Measured donor fraction: 0.40.
- Remaining runs: query role.
- Roles are disjoint within each configuration.
- Seeds: 0, 1, 2, 3, 4.

## Matching sensitivity

Spatial calipers:

- 1 m;
- 2 m;
- 5 m.

Query/anchor spatial thinning:

- 5 m.

Matched donor count requested by the main replay:

- up to 5 samples, with donor-run diversity preferred.

Pairwise margin training:

- donor count capped at 3;
- same action/context matching machinery;
- anchor run is excluded from its own matched outcome.

## Pairwise model fixed parameters

- model: context-conditioned spatial KNN on the action margin;
- context groups: network + travel direction;
- target: measured matched `delay_50 - delay_30`;
- neighbors: 25;
- minimum context-group training rows: 50;
- conservative local lower quantile: 0.10;
- upper diagnostic quantile: 0.90.

No hyperparameter search is permitted after audit results are opened.

## Policy evaluation without arbitrary mobility/QoS unit conversion

The primary audit uses fixed maximum intervention budgets instead of a scalar travel-time/network-delay cost.

Budgets:

- 1%;
- 5%;
- 10%.

Within each query run, a policy may select SLOW for at most the declared fraction of locations.

Policies:

1. `FAST`: always 50 km/h.
2. `PRED_BUDGET`: rank by independent absolute-QoS predicted gain.
3. `PRED_SUPPORT_BUDGET`: same ranking, requiring support for both actions.
4. `MARGIN_BUDGET`: rank by pairwise predicted action margin.
5. `MARGIN_LOWER_BUDGET`: rank by the 0.10 local margin quantile.
6. `ORACLE_BUDGET`: nondeployable ranking by matched measured action gain.

Policies never spend intervention budget where their corresponding estimated gain is non-positive.

## Endpoints

Primary development endpoint:

- run-level mean matched delay difference versus FAST.

Secondary:

- run-level p95 matched delay;
- intervention/slow fraction;
- direction of effect across 15 seed/caliper configurations.

## Interpretation rules frozen before results

The pairwise hypothesis is considered promising only if:

1. `MARGIN_BUDGET` is favorable versus FAST in more configurations than `PRED_BUDGET`;
2. the advantage is not confined to one split seed;
3. performance is not obtained simply by using substantially more SLOW interventions;
4. the result is directionally credible at more than one intervention budget.

The conservative lower-margin policy is useful only if it improves reliability while using the same or less intervention budget.

A favorable development result does **not** become a paper claim. A separate untouched confirmatory protocol is still required.

If the pairwise margin policies fail these conditions, they will be retained as negative results and will not be retuned after inspection.

## Statistical boundary

All intervals/tests in this development stage are descriptive because donor acquisition runs are reused by multiple query locations.

No timestamp- or query-row-level significance claim is allowed.

Final confirmatory inference must account for both query-run and donor-run dependence.

## Novelty boundary

Even if the method works, the paper will not claim novelty for generic decision-focused learning, predict-then-optimize, regret learning, or action-margin estimation.

The intended contribution remains:

> measured, support-bounded decision evaluation and calibration for vehicle-motion actions using disjoint repeated field drives.
