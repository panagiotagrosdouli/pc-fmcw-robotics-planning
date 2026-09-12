# Paper 2 — Results and Evidence Checklist

## Frozen interpretation

- P2 tests predictive communication utility.
- P3 tests empirical measurement-support / inference-validity control.
- P3 is not required to outperform P2 on QoS.
- Repeated grouped splits are sensitivity analyses, not independent replicates.
- 5G field measurements do not validate the PC-FMCW optical model.
- Route-constrained replay is offline measured replay, not closed-loop road validation.

## Evidence already available

- CICV5G acquisition subset: 38 runs, 43,045 samples.
- Whole-run train/calibration/test separation.
- Persistence one-step delay MAE ~7.419 ms.
- Conditioned spatial kNN ~12.344 ms.
- Random Forest ~9.291 ms.
- Extra Trees ~8.950 ms.
- Horizon-adaptive prediction improves over persistence in 5/5 grouped assignments at 20, 50, 100 steps.
- Primary replay P2 vs P1 delay effect ~-0.792 ms; bootstrap 95% CI ~[-1.723,-0.138].
- Raw Wilcoxon P2 vs P1 delay p=0.046875; Holm-adjusted p~0.28125: exploratory, not confirmatory.
- P2 vs P1 measured delay improves in 5/5 grouped split assignments; descriptive mean ~-0.501 ms.
- P2 vs P1 >50 ms violation fraction improves in 5/5 assignments; descriptive mean ~-0.002239.
- P3 vs P2 unsupported-selection fraction improves in 5/5 assignments; descriptive mean ~-0.027954.
- P3 vs P2 measured delay has mixed sign; no stable additional QoS claim.
- Vectorized replay implementation has observed batched QoS/support evaluation on the order of ~81–96 microseconds/candidate in CI; this is implementation-level evidence only.

## Manuscript-critical remaining assets

- Generate publication figures from frozen result CSVs/artifacts.
- Generate final formatted tables with exact values and provenance.
- Verify every numerical statement against archived result artifacts before submission.
- Add formal equations for predictor fusion, support score, planner objective, and paired statistics.
- Add literature references and BibTeX with claim-by-claim citation audit.
- Decide target venue and adapt length/style only after scientific content is frozen.
- Add dataset license/access statement and code/data availability statement.
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
