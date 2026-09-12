# Paper 2 — Results and Evidence Checklist

## Frozen interpretation

- P2 tests predictive communication utility.
- P3 tests empirical measurement-support / inference-validity control.
- P3 is not required to outperform P2 on QoS.
- Repeated grouped splits are sensitivity analyses, not independent replicates.
- 5G field measurements do not validate the PC-FMCW optical model.
- Route-constrained replay is offline measured replay, not closed-loop road validation.

## Archived evidence source of truth

The numerical values below are reconciled to the archived `real-v2x-dual-branch-run34` artifacts. These artifacts supersede older working-note absolute values while preserving the previously reported paired planner effects.

- CICV5G acquisition subset: 38 runs, 43,045 samples.
- Primary split: 22 train runs / 22,441 samples; 7 calibration runs / 8,846 samples; 9 test runs / 11,758 samples.
- Whole-run train/calibration/test separation.
- One-step delay predictor metrics: persistence MAE 5.576 ms (RMSE 20.914 ms), spatial kNN MAE 10.862 ms, Random Forest MAE 7.150 ms, Extra Trees MAE 6.659 ms.
- Support-stratified delay MAE / empirical coverage: <=1 m: 5.332 ms / 0.888; 1–5 m: 7.120 ms / 0.864; 5–15 m: 9.579 ms / 0.761.
- Horizon-adaptive prediction improves over persistence in 5/5 grouped assignments at 20, 50, 100 steps, with mean MAE improvements about 1.460, 2.506, and 2.622 ms.
- Primary replay P1: mean measured delay 23.318 ms, >50 ms violation fraction 0.02179.
- Primary replay P2: mean measured delay 22.526 ms, violation fraction 0.01900, changed-decision fraction 0.02508, mobility deviation 0.01254.
- Primary replay P3: mean measured delay 22.598 ms, unsupported-selection fraction 0.13798, mobility deviation 0.02305.
- Primary replay P2 vs P1 delay effect -0.791924 ms; bootstrap 95% CI [-1.723327,-0.137729].
- Raw Wilcoxon P2 vs P1 delay p=0.046875; Holm-adjusted p=0.28125: exploratory, not confirmatory.
- P2 vs P1 measured delay improves in 5/5 grouped split assignments; descriptive mean effect -0.501375 ms.
- P2 vs P1 >50 ms violation fraction improves in 5/5 assignments; descriptive mean effect -0.002239.
- P3 vs P2 unsupported-selection fraction improves in 5/5 assignments; descriptive mean effect -0.027954.
- P3 vs P2 measured-delay effects have mixed sign; descriptive mean about -0.005765 ms; no stable additional QoS claim.
- Archived vectorized replay records about 83.1 microseconds/candidate for batched QoS/support evaluation and about 9.85 microseconds mean decision scoring. This is implementation-level evidence only, not embedded/end-to-end real-time validation.

## Statistical interpretation

- The primary split uses held-out runs as the paired inferential unit.
- Holm correction is required across the declared planner/metric test family.
- The five alternative grouped split assignments reuse the same finite set of runs and are dependent; use mean/median/min/max/fraction-same-sign descriptively only.
- Do not use the split-assignment Wilcoxon fields from historical multisplit CSV output as independent-sample inference.

## Manuscript-critical remaining assets

- Generate publication figures from the archived result CSVs/artifacts.
- Generate final formatted tables from artifact files rather than hand-entered numbers.
- Verify every numerical statement against archived result artifacts before submission.
- Complete venue-specific reference/style adaptation after scientific content is frozen.
- Maintain dataset license/access and code/data-availability statements.
- Run final manuscript claim audit against `docs/research/CLAIM_AUDIT.md`.

## Prohibited wording

Do not write:

- "first communication-aware autonomous planner"
- "first predictive QoS trajectory planner"
- "real-world autonomous-driving validation"
- "conformal outage probability"
- "5G validates PC-FMCW"
- "P3 significantly improves QoS over P2"
- "five independent split experiments"

Preferred wording:

- "field-measured vehicular QoS"
- "whole-run leakage-resistant evaluation"
- "route-constrained measured replay"
- "descriptive robustness across grouped split assignments"
- "empirical measurement-support control"
- "horizon-dependent predictive value"
