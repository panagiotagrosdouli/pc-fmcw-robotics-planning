# Senior researcher report — real-measurement V2X extension

## A. Final research question
Can field-measured vehicular communication traces provide useful predictive information for autonomous motion decisions **without silently trusting QoS predictions outside their empirical measurement support**?

The initial generic idea — predict QoS and avoid blackspots — was rejected as insufficiently novel after literature review.

## B. Gap selected
The selected gap is the validity bridge between logged communication measurements and counterfactual motion decisions. The study focuses on five linked issues: whole-drive leakage, the strength of causal persistence, horizon-dependent predictive value, empirical spatial support, and uncertainty under grouped distribution shift. Decision value is evaluated only where measured replay can provide an outcome without fabricating QoS ground truth.

## C. Closest competing work and differentiation
- Ghaffarkhah & Mostofi (2011): foundational probabilistic communication-aware motion planning.
- Gordon et al. (INFOCOM 2026): proactive service-specific QoS-risk maps and robot motion planning.
- Ullah et al. (IEEE Access 2025): QoS-aware autonomous-vehicle route selection in simulated 6G/mmWave coverage.
- Kim et al. (Sensors 2026): GPR radio-map uncertainty coupled with robust tube MPC.
- Real-data vehicular predictive-QoS studies: show that field-trace QoS prediction itself is established.
- RMWorld (2026 preprint): explicitly filters counterfactual radio-model trials, weakening any generic counterfactual-awareness claim.

Our differentiation is the combined field-measured vehicular protocol: complete-run anti-leakage splitting, causal persistence baseline, multi-horizon fusion, empirical support diagnostics, grouped-shift uncertainty audit, and route-constrained measured outcome replay.

## D. Real dataset
CICV5G was selected because it is public, recent, directly downloadable, and contains repeated real 5G V2N2V measurements with position, heading, velocity, SINR, RSRP and end-to-end delay. The automated study downloaded 38 run files / 43,045 samples.

## E. Implemented research stack
The branch contains:
- public CICV5G acquisition/provenance;
- robust parsing and run metadata;
- whole-run train/calibration/test split;
- persistence, spatial KNN, Random Forest, Extra Trees and conditioned-spatial predictors;
- multi-horizon causal evaluation;
- calibration-only persistence/spatial fusion;
- residual conformal uncertainty;
- nearest-training-distance/local-density support diagnostics;
- P0–P3 communication decision adapter;
- route-constrained measured-support replay;
- run-level bootstrap/Wilcoxon statistics;
- robustness across five split seeds;
- plots/results artifacts;
- unit tests and GitHub Actions research workflow;
- literature matrix, gap analysis, research log, claim audit and paper-ready sections.

## F. Experiments actually run
1. Real-data parser/download verification.
2. One-step delay and SINR predictor comparison.
3. Support-stratified error/coverage analysis.
4. Split-conformal held-out coverage evaluation.
5. Multi-horizon delay/SINR prediction from 55 ms to ~5.5 s.
6. Calibration-only context-adaptive fusion.
7. Five grouped split seeds.
8. Route-constrained P0/P1/P2/P3 measured replay.
9. Paired run-level bootstrap confidence intervals and Wilcoxon tests.
10. CI runtime measurement for the implemented decision loop.

## G. Main quantitative results
### One-step prediction
Persistence delay MAE: 5.576 ms.
Spatial KNN: 10.862 ms.
Extra Trees: 6.659 ms.
Random Forest: 7.150 ms.

Thus the initial "generic ML beats reactive" hypothesis was falsified.

### Spatial support
Primary-split delay MAE rises from ~5.33 ms (<=1 m from training support) to ~9.58 ms (5–15 m). Interval coverage falls from ~0.888 to ~0.761 across those strata.

### Horizon robustness
Across five grouped split seeds, fusion improves over persistence in every seed at 20/50/100 samples (~1.1/2.8/5.5 s). Mean MAE improvements are approximately 1.46, 2.51 and 2.62 ms respectively.

### Measured replay
P1 mean measured delay: 23.318 ms.
P2: 22.526 ms.
P3: 22.598 ms.

P2-P1 run-level measured-delay effect: -0.792 ms; 95% bootstrap CI [-1.723,-0.138]; paired Wilcoxon p=0.0469.

P3-P2 delay effect: +0.073 ms; p=0.742 — no QoS superiority.

P3-P2 unsupported-selection effect: -0.01836 absolute; 95% CI [-0.03214,-0.00603]; p=0.03125, with additional mobility deviation.

Validated replay decision computation: ~8.63 ms mean, ~8.85 ms p95 on hosted CI hardware. This is implementation timing, not a full vehicle real-time guarantee.

## H. Negative/failed results
- naive one-step spatial/tree prediction did not beat persistence;
- SINR was too persistent for the tested spatial models to add short-horizon value;
- nominal 90% conformal coverage was not stable under grouped distribution shift;
- P3 did not beat P2 on measured QoS;
- arbitrary off-route counterfactual validation was rejected because the dataset has no measured ground truth there.

These results are retained rather than hidden.

## I. Statistical evidence
Independent units are held-out runs, not timestamps. The primary replay has nine paired held-out runs. Robustness uses five grouped split seeds. Reported effects include paired bootstrap intervals and paired Wilcoxon tests. Timestamp-level sample counts are descriptive, not pseudo-replicates.

## J. Ablation/robustness findings
The strongest ablation is prediction horizon: spatial/context information has little one-step advantage but becomes useful at longer horizons. The support-stratified analysis demonstrates degradation away from training data. P2-vs-P3 isolates the support/risk layer: it improves inference support exposure but not measured QoS in the primary replay.

## K. Limitations
- one primary real dataset;
- route-constrained offline replay, not arbitrary counterfactual path ground truth;
- nine independent replay test runs;
- experimental delay threshold;
- incomplete conformal coverage under grouped shift;
- no physical PC-FMCW optical measurements;
- hosted-CI timing only.

## L. Defensible claims
- the dataset branch uses real measured V2N2V communication data;
- grouped splits avoid drive-level train/test leakage;
- short-horizon persistence is a strong baseline;
- longer-horizon calibration-gated fusion has consistent incremental value across five split seeds;
- predictive P2 produces a modest measured-delay improvement over reactive P1 in the primary route replay;
- support-aware P3 reduces unsupported decision exposure at mobility cost;
- prediction reliability deteriorates with weaker empirical spatial support.

## M. Claims that must not be made
- communication-aware planning is novel;
- proactive QoS/radio-map planning is novel;
- uncertainty-aware communication planning is novel;
- P3 improves communication QoS over P2;
- CICV5G validates PC-FMCW optical propagation;
- offline replay is real-world AV validation;
- ordinary split-conformal outputs are universally calibrated probabilities;
- this combination is proven to be the first ever in all literature.

## N. Reproduction commands
```bash
python scripts/prepare_cicv5g.py --output data/raw/cicv5g
PYTHONPATH=src python scripts/run_real_v2x_support_study.py --data data/raw/cicv5g --output results/real_v2x_support
python scripts/analyze_real_v2x_support_study.py --input results/real_v2x_support --bootstrap 1000
PYTHONPATH=src python scripts/run_real_v2x_horizon_study.py --data data/raw/cicv5g --output results/real_v2x_horizon
python scripts/analyze_real_v2x_horizon_study.py --input results/real_v2x_horizon --bootstrap 1000
PYTHONPATH=src python scripts/run_real_v2x_replay_planning.py --data data/raw/cicv5g --output results/real_v2x_replay
python scripts/analyze_real_v2x_replay_planning.py --input results/real_v2x_replay --bootstrap 2000
python -m pytest -q tests/test_real_v2x.py
```
The GitHub Actions research workflow runs the complete measured-data chain plus five grouped horizon split seeds and uploads the machine-readable artifact.

## O. Remaining work before submission
The implemented study is complete for its current scope. Before a strong journal submission, the highest-value additions would be an independent second V2X dataset / repeated-route campaign and, if the journal claim remains specifically PC-FMCW, real or calibrated optical-link evidence. These are scientific scope extensions rather than missing software plumbing.

## P. Publication-level assessment
**Current measured-data branch: solid conference/workshop-to-conference-level validation contribution, and a meaningful additional validation section for a broader paper.**

It is stronger than a toy simulation because it uses real field measurements, preserves negative results, enforces grouped evaluation and addresses counterfactual validity explicitly. By itself it is not yet a strong journal-extension claim because there is one primary dataset, only nine independent replay test runs, no full real-vehicle planning execution, and no measured PC-FMCW optical channel.

Combined with the existing PC-FMCW predictive robotics branch, it materially strengthens the paper by adding real-communication evidence and a reviewer-resistant claim boundary. A journal-level extension becomes more convincing with cross-dataset or optical measurement validation rather than additional model complexity.
