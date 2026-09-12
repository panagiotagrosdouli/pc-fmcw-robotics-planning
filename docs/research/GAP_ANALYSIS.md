# Research gap analysis — real-measurement support-aware QoS planning

## What is not novel
Communication-aware motion planning is established at least since Ghaffarkhah & Mostofi (2011). Online radio mapping, resilient connectivity planning, formal QoS-constrained motion, joint communication-motion co-design, and QoS-aware AV route selection have also been demonstrated. A 2026 INFOCOM workshop paper already converts estimated radio maps into QoS-risk maps and proactively avoids low-quality regions. Therefore this project must not claim novelty for "predicting communication quality along trajectories" or "avoiding connectivity blackspots" alone.

## Selected gap
The strongest lightweight gap is the **scientific validity of using real measured vehicular QoS for counterfactual autonomous planning**. Real datasets only measure the actually driven path, while a planner scores paths that were not driven. A data-driven predictor can therefore appear effective while extrapolating outside measurement support or leaking temporally adjacent samples across train/test.

We target a combined contribution:

1. leakage-safe, run-grouped prediction of measured 5G V2N2V delay;
2. calibrated split-conformal uncertainty on held-out runs;
3. explicit spatial-support / extrapolation diagnostics for every queried candidate state;
4. a planner policy that can penalize or reject communication predictions outside measured support;
5. reactive vs predictive vs uncertainty/support-aware comparison under a common safety layer.

The novelty claim is the **combination and audit protocol**, not any one primitive.

## Why CICV5G first
CICV5G is public and contains field V2N2V records, synchronized vehicle position/heading/velocity plus SINR, RSRP and end-to-end delay, including a W2S strong-to-weak coverage subset. The data descriptor explicitly identifies delay modeling and delay-aware planning/control as downstream uses. This makes it a strong first dataset because the dependent variable is directly relevant to networked vehicle planning/control.

## Falsification conditions
The primary hypothesis fails if grouped held-out prediction does not improve over persistence sufficiently to alter planning decisions, or if supported counterfactual regions are too sparse to compare trajectories. The uncertainty hypothesis fails if held-out conformal intervals do not achieve near-nominal coverage or if risk-aware decisions do not improve tail QoS at acceptable mobility cost.

## Claim boundary
Field communication measurements are real. QoS models are learned. Candidate autonomous trajectories and counterfactual planner decisions remain offline/model-based unless an actual controlled vehicle experiment is later conducted. CICV5G is 5G V2N2V data and does not validate PC-FMCW optical propagation.
