# V4 development-only safety sweep (negative result)

Frozen local runner commit: `41bc5ae` (runner content published in PR #19 at `0d5e0576f244e643d180ba4769b77e434c19aecb`). The subsequently changed GitHub Actions timeout does not change these data. Execution: Python CLI with seeds 9000–9019 and the fixed arguments in each `manifest.json`, including `--v4-static-viability`. Seven predeclared margins are archived separately. Each `episodes.csv` contains 500 paired episodes (five scenarios × five planners × 20 seeds). `summary.csv` is the runner's descriptive summary. `development_safety_summary.csv` and `selection.json` are the output of `scripts/select_v4_safety_margin.py`. `SHA256SUMS.json` records the SHA-256 digest of every original artifact in this directory.

No margin passed the three-part safety gate. `selection.json` therefore has `selected_margin_m: null` and `gate_passes: false`. The selection script exits nonzero after writing these files. No confirmatory seeds or geometry mechanism seeds were run. See [`docs/PART_B_V4_EXECUTION_STATUS.md`](../../docs/PART_B_V4_EXECUTION_STATUS.md) for the stop decision and aggregate counts.

These are deterministic simulator outputs, not optical field measurements. The static metric checks the modeled obstacle surface and does not account for an ego-vehicle footprint.
