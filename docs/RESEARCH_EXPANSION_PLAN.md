# Post-Freeze Research Expansion Plan

Status: planned after validation of the canonical frozen paper experiment.

## Goal

Extend the existing connectivity-aware closed-loop planning benchmark into a rigorous study of how much future communication information an autonomous robot needs for robust motion planning under uncertain connectivity.

The canonical frozen P0-P4 benchmark remains the reference experiment. New methods and experiments below are extensions and must never overwrite or retroactively redefine the frozen result.

## Scientific questions

1. How much benefit comes from causal future connectivity prediction over reactive connectivity awareness?
2. How much additional value is provided by uncertainty information and oracle future information?
3. How much prediction horizon is required before planning benefit saturates?
4. When does prediction error or distribution shift erase the benefit of predictive planning?
5. Can explicit risk-aware or chance-constrained connectivity objectives improve tail reliability without unacceptable mobility/safety cost?
6. What is the Pareto frontier between task/mobility performance, connectivity reliability, safety, and compute?

## Work packages

### WP1 — Frozen benchmark closure

- Validate the canonical 20-seed P0-P4 experiment with 32 MC samples and 10,000 bootstrap samples.
- Produce overall and scenario-stratified P1-P2 and P2-P4 paired effects with confidence intervals.
- Aggregate the 20-seed robustness sweep.
- Diagnose collision and no-candidate behavior by scenario and rejection cause.
- Preserve commit, environment, manifest, seeds, and exact commands.

### WP2 — Information-value analysis

Treat P1/P2/P3/P4 as an information ladder: reactive current information, causal prediction, uncertainty-aware prediction, and oracle future information.

Report effect sizes and confidence intervals rather than interpreting non-significance as equivalence. Quantify the oracle gap by scenario and identify regimes in which future information changes the selected trajectory.

### WP3 — Prediction-horizon ablation

Sweep causal prediction horizon, including zero/reactive and multiple future horizons. Determine where benefit saturates and report paired effects, confidence intervals, planning cost, and prediction quality.

### WP4 — Connectivity-weight / Pareto analysis

Sweep the connectivity objective weight. Report a Pareto view covering outage/goodput, progress/path efficiency, collision/safety diagnostics, no-candidate rate, and runtime. Avoid selecting a single operating point solely after observing test results.

### WP5 — Prediction corruption and distribution shift

Stress the planner with controlled prediction noise, bias, delayed observations, uncertainty miscalibration, and link-model mismatch. Estimate the degradation curve and the crossover point at which predictive planning ceases to outperform reactive planning.

### WP6 — Structured blackout stress tests

Add reproducible controlled regimes such as sudden blockage, persistent NLOS, moving occlusion, intermittent connectivity, and rapid link degradation. These are stress tests, not replacements for the canonical benchmark.

### WP7 — Risk-aware planning

Evaluate an explicit tail-risk connectivity objective, e.g. a CVaR-style cost, under the same dynamics, candidate budget, safety constraints, and information restrictions as existing planners. Compare mean performance and lower-tail reliability.

### WP8 — Chance-constrained connectivity

Evaluate a reliability constraint of the form P(link quality below threshold) <= epsilon where the predictive distribution supports a defensible probability estimate. Sweep epsilon and report feasibility, reliability, mobility, safety, and runtime trade-offs.

### WP9 — Adaptive connectivity weighting

Evaluate state-dependent connectivity weighting driven only by causal information available to the planner, such as predicted outage risk and task/safety state. Compare against fixed-weight controls under matched compute and information budgets.

### WP10 — Strong baselines

Audit and, where methodologically fair, add stronger planning baselines. Candidate classes include connectivity-agnostic planning, reactive connectivity-aware planning, deterministic predictive planning, uncertainty/risk-aware planning, oracle planning, and a matched receding-horizon/MPC-style control. All comparisons must use matched dynamics, scenario seeds, candidate/compute budgets where possible, and explicit information constraints.

### WP11 — Compute-performance frontier

Measure planning latency/runtime against horizon, uncertainty samples, candidate count, and achieved connectivity/task performance. Establish whether predictive gains are attainable at a practical computational cost.

### WP12 — Counterfactual qualitative analysis

For identical initial conditions and seeds, visualize trajectories chosen by reactive and predictive planners together with the relevant predicted/realized connectivity context. Use these examples to explain mechanisms, not as substitutes for statistical evidence.

## Statistical rules

- Predeclare primary comparisons before inspecting extension results.
- Use paired experimental units whenever planners share scenario/seed conditions.
- Keep candidate evaluations and planning windows as diagnostics unless the design explicitly supports them as independent units.
- Report effect sizes and confidence intervals alongside corrected hypothesis tests.
- Do not infer equivalence from a non-significant difference.
- Separate safety outcomes from connectivity and planner-feasibility outcomes.
- Use seed/block-aware or hierarchical resampling when repeated scenario observations share a seed or experimental realization.
- Do not tune and evaluate a hyperparameter on the same held-out evidence without clearly labeling the analysis exploratory.

## Claim boundaries

Simulation evidence must be described as simulation evidence. No real-world, hardware, optical, or deployment claim may be made without corresponding experiments. Connectivity improvements do not imply safety improvements. New extension experiments must be clearly separated from the frozen canonical result.

## Target evidence package

The mature project should support a venue-independent evidence package: canonical benchmark, scenario analysis, robustness, horizon/weight ablations, distribution-shift stress tests, risk/reliability extensions, strong baselines, compute analysis, qualitative mechanism figures, exact provenance, and reproducible artifacts. Venue-specific manuscripts may emphasize different scientific angles, but must draw from the same traceable experimental evidence.