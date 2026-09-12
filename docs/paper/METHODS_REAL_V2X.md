# Methods — real-measurement V2X validation layer

We evaluate a second communication environment independently of the model-based PC-FMCW optical branch. Field-measured 5G vehicle-to-network-to-vehicle (V2N2V) records are used to learn a lightweight mapping from vehicle state, location and recent communication history to communication delay and SINR. The communication measurements are real; alternative candidate trajectories queried by the autonomous planner remain counterfactual/offline.

To prevent temporal leakage, the unit of partitioning is a complete measurement run rather than an individual timestamp. Whole runs are assigned to training, calibration and test partitions. Model selection includes a persistence baseline, spatial KNN and tree ensembles. Prediction performance is evaluated on held-out runs using MAE/RMSE and run-level paired effects.

Uncertainty is calibrated on a run-disjoint calibration partition using split-conformal absolute residuals. We report empirical held-out interval coverage and interval width. These intervals are not interpreted as calibrated event probabilities.

Counterfactual validity is audited by fitting a spatial support model exclusively to training coordinates. Each candidate query reports distance to the nearest measured training state and local measurement density. Predictions outside a predefined support radius/density are flagged; the planner can penalize trajectories whose communication score relies heavily on unsupported extrapolation.

Planner variants retain the repository's common hard-safety layer: P0 mobility-only; P1 reactive/current QoS; P2 predictive mean QoS; P3 predictive QoS with uncertainty and support penalty. An oracle P4 is omitted unless future measured QoS exists for the exact counterfactual position, which is generally not true for observational drive data.

A configured 50 ms delay threshold is treated only as an experimental operating point unless a specific application standard is cited. The real-data experiment does not validate PC-FMCW propagation and does not constitute real-world autonomous-driving validation.
