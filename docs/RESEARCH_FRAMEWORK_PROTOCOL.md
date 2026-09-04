# Research Framework Protocol v1

This protocol governs all experiments added after the frozen P0-P4 baseline.

## Confirmatory baseline

The existing P0-P4 benchmark remains the historical baseline snapshot. New methods do not replace or rewrite those results.

## New planner families

- Expected-connectivity planning: deterministic/mean connectivity objective.
- Tail-risk planning: expected connectivity plus CVaR of adverse connectivity cost.
- Chance-constrained planning: reject or penalize candidate trajectories whose predicted outage probability exceeds a specified tolerance.
- Adaptive-weight planning: increase connectivity importance only when predicted outage risk crosses an activation region.
- Oracle planning: privileged-information upper bound only; never presented as deployable.

## Fair-comparison constraints

All planner variants must share the same motion dynamics, trajectory candidate generator, road/speed/static/dynamic safety filters, planning timestep, scenario seed, and candidate budget unless the experiment explicitly studies one of those factors. Any deliberate difference must be recorded in the manifest.

## Information constraints

Reactive planners may use only information available at the current planning step. Predictive planners may use only causal predictions from available history. Oracle planners may use future realized information and are labeled privileged-information upper bounds.

## Stress tests

Stress-test perturbations are applied to the predictive information channel rather than silently changing the ground-truth simulation. Supported perturbation families include additive prediction bias, increased prediction noise, observation delay, propagation/link-model mismatch, sudden blockage, persistent NLOS, intermittent links, and rapid degradation.

## Statistical analysis

Primary planner comparisons are paired by scenario and seed. Report effect sizes and confidence intervals in addition to multiplicity-adjusted hypothesis tests. Non-significant differences are not interpreted as equivalence unless an explicit equivalence/non-inferiority analysis is pre-specified and performed. Candidate evaluations and filter rejection counts are diagnostic counts, not independent statistical samples.

## Safety

Collision and safety outcomes are reported independently from communication reliability. A planner that improves outage/SNR/goodput is not described as safer without direct evidence. Safety-constrained variants, if introduced, are analyzed as separate methods rather than retrospective fixes to baseline results.

## Compute reporting

Every new method reports planning runtime and the factors that materially control computation, including prediction horizon, Monte-Carlo sample count, and candidate evaluations. Performance improvements are interpreted together with their compute cost.

## Publication integrity

All new experiments retain negative/null results, use fixed pre-declared parameter grids, and export provenance sufficient to reconstruct the exact commit, configuration, seeds, dependency environment, and generated outputs.
