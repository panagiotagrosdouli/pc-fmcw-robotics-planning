# Paper Experiment Reporting Checklist

Use this checklist when converting the reproducible simulation outputs into paper tables, figures, and claims. It is deliberately conservative: the repository implements a PC-FMCW-informed controlled simulation, not measured optical-link or real-vehicle validation.

## Reproducibility gate

Before reporting numerical results, record the exact Git commit, Python/platform metadata, seed count, P3 Monte Carlo sample count, paired-analysis bootstrap sample count, and robustness bootstrap seed/sample count from the generated reproducibility metadata. Do not combine outputs from different commits into one comparison unless the paper explicitly labels them as separate experiments.

## Fair-comparison gate

For every P0-P4 comparison, verify that the same scenario and seed realizations are paired. All planners must use the same vehicle model, road/static-obstacle constraints, configured collision-clearance radius, and common mean target prediction for dynamic safety. P4 may use simulator future target truth only for connectivity forecasting; it must not receive oracle future truth for collision avoidance. P3 must retain the same mean target predictor and PC-FMCW-informed link model as P2, adding only the declared Monte Carlo uncertainty/risk treatment.

## Metrics to report

Connectivity metrics are modeled quantities: mean outage probability, modeled SNR, modeled BER, and modeled goodput. Mobility/safety diagnostics include path length, progress, minimum target distance, collision indicator/rate, collision-boundary realized TTC, and no-candidate steps. Infinite realized TTC values are retained in raw episode outputs; the inferential analysis may cap them at the episode-duration boundary solely to permit finite paired statistics.

## Statistical reporting

Report paired comparisons by scenario and seed. For each declared comparison, report the effect direction and magnitude, the 95% paired-bootstrap interval, paired Wilcoxon p-value, and Holm-adjusted p-value. Do not describe a small p-value as practical superiority without also discussing the effect magnitude and safety/mobility trade-off. Robustness-plot 95% bootstrap intervals describe variability across simulated episodes, not physical measurement uncertainty.

## Robustness reporting

Report sensitivity to observation noise, target-prediction uncertainty, planning horizon, and connectivity-objective weight. A conclusion should be described as robust only over the parameter range actually swept. Do not extrapolate beyond those ranges.

## Claim boundary

Allowed framing includes: controlled model-based simulation, PC-FMCW-informed analytical connectivity model, predictive connectivity-aware motion planning, closed-loop receding-horizon evaluation, and comparative behavior under the implemented scenarios and assumptions.

Do not claim measured PC-FMCW channel accuracy, hardware validation, real-road safety, real-world generalization, or empirical superiority outside the tested simulation. Do not call synthetic observation/prediction perturbations measurement noise unless a corresponding measurement model is explicitly defined and justified.

## Figure and table integrity

Every numerical table or chart must be generated from saved experiment outputs. Do not manually invent, smooth, or alter numerical results for presentation. Captions should state the number of seeds/episodes, whether intervals are bootstrap intervals, and that results are from controlled simulation. P4 should be labeled as an oracle connectivity reference rather than a deployable planner.

## Minimum result package before paper claims

A paper-ready result package should contain the benchmark `episodes.csv`, planner summary, aggregate and per-scenario paired-effects tables, scenario summary, the safety/prediction diagnostics under `diagnostics/`, robustness episode/summary outputs, robustness figures, and reproducibility metadata. Collision interpretation must use the per-scenario collision timing and candidate-rejection outputs rather than the aggregate collision rate alone. If any component is missing or a CI/full-workflow run fails, numerical conclusions should remain provisional until the reproducible run is complete.
