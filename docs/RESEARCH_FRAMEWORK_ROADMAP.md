# Robotics Under Communication Uncertainty: Research Framework Roadmap

This document defines the implementation plan for extending the existing predictive connectivity-aware planning benchmark into a broader robotics-under-communication-uncertainty research framework.

## Scientific question

How much future communication information does an autonomous robot need to make robust motion-planning decisions under uncertain connectivity, and how should that information be incorporated when predictions are uncertain or shifted?

## Framework additions

1. Risk-aware connectivity planning using tail-risk objectives (CVaR).
2. Chance-constrained connectivity planning with explicit outage-risk constraints.
3. Adaptive connectivity weighting driven by predicted outage risk while preserving the common motion/safety cost interface.
4. Prediction-horizon sweeps to quantify saturation of causal foresight.
5. Value-of-information analysis across reactive, predictive, uncertainty-aware, and oracle planners.
6. Distribution-shift stress tests including bias, noise, delay, and link-model mismatch.
7. Controlled communication-blackout scenarios: sudden blockage, persistent NLOS, intermittent links, and rapid degradation.
8. Reliability-mobility Pareto analysis over connectivity weighting.
9. Counterfactual trajectory exports for matched initial conditions.
10. Safety/connectivity decoupling diagnostics and constrained-safety variants where methodologically justified.
11. Stronger planning baselines under matched dynamics, candidate budgets, and information constraints.
12. Compute-performance analysis over horizon, Monte-Carlo budget, and planner variant.

## Experimental principles

- Existing frozen P0-P4 experiments remain a baseline snapshot and are not overwritten by retrospective tuning.
- New methods are evaluated under a new protocol version with fixed seeds/configuration before confirmatory analysis.
- Planner comparisons must use matched dynamics, candidate generation, safety filters, and compute-budget reporting.
- Statistical units are episodes/paired scenario-seed units as defined by the benchmark design; candidate evaluations are diagnostics, not independent samples.
- New risk/chance/adaptive planners are hypotheses until their controlled experiments are complete.
- Negative and null results are retained.
- Safety claims remain separate from connectivity/reliability claims.

## Intended outputs

The codebase should support a reproducible chain from method definition to benchmark execution, stress testing, statistical inference, and final publication figures/tables. No single analysis script is considered the contribution; the contribution is the integrated planning-and-evaluation framework.
