# Active Self-Calibration Artifacts

This directory is reserved for the scientifically separate active-self-calibration study. Committed files here are metadata/placeholders only unless explicitly identified as executed evidence.

Expected generated structure:

- `smoke/` — engineering smoke outputs; never scientific evidence;
- `development/` — development/tuning outputs using declared development seeds;
- `frozen_protocol.json` — development-selected hyperparameter lock created before confirmatory seeds are opened;
- `confirmatory/` — frozen confirmatory outputs;
- `figures/` — figures generated from a named executed artifact scope.

Every executed scope must contain `manifest.json`, `episodes.csv`, `steps.csv`, and `summary.csv`. Confirmatory inference must be generated from independent seed-level effects, not timestep rows.
