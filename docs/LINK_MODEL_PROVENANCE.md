# Link-model provenance and claim boundary

The planning code supports two scientifically distinct connectivity layers.

1. **Geometry surrogate.** This is useful for software integration, ablations and synthetic sensitivity studies. Results from this layer must not be described as measured PC-FMCW optical-link performance.
2. **Frozen calibrated predictor.** `CalibratedGeometryLinkPredictor` loads parameters fitted from a measurement CSV by `scripts/fit_link_calibration.py`. Calibration artifacts require explicit `source`, `measurement_type`, and `calibration_date` metadata.

## Required measurement schema

The minimal calibration CSV contains `distance_m`, `heading_error_rad`, and `snr_db`. Additional columns (BER, received power, relative speed, environmental state, run ID) should be retained when available, but are not silently synthesized.

## Claim rule

A calibration artifact may be called **PC-FMCW optical** only when its recorded source actually contains PC-FMCW optical measurements. Radar datasets such as Rad-R and autonomous-driving trajectory datasets such as CMHT do not establish that claim. CMHT is used for real target motion; Rad-R is real 77-GHz radar data; neither is treated as optical-link ground truth.

## Freeze protocol

Fit link parameters on calibration measurements before the planner benchmark, store the JSON artifact and provenance, and do not tune the link model on planner test outcomes. Report fit sample count and calibration RMSE. The final P0-P4 comparison should use the same frozen predictor instance/parameters for all connectivity-aware planners.
