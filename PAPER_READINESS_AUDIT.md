# Paper readiness audit

Audit date: 2026-09-20  
Audited state: V7 branch at `c6bbbc5` plus the closure changes described here.

## Executive status

| Paper | Status | Submission interpretation |
|---|---|---|
| Paper 1 — PC-FMCW predictive connectivity-aware robotics | **PASS WITH EXPLICIT LIMITATIONS** | The frozen V7 primary claim is supported as controlled analytical-simulation evidence. It is not optical validation or a safety guarantee. |
| Paper 2 — field-measured V2X predictive planning | **BLOCKED** | The narrow descriptive/exploratory claims are scientifically plausible, but the checked-in compact archive is insufficient to independently reconstruct every inferential number and split/provenance claim. |

## Repository-wide audit method

The audit inspected README/documentation, source and experiment entry points, configurations, workflows, tests, frozen protocol/status files, checked-in archives, manuscripts, and relevant history from the safety-remediation and measured-V2X branches. The complete available test suite passed (183 tests). Artifact rows were checked for seed ranges, paired-unit cardinality, hard-gate fields, and consistency with reported V7 effects. No quarantined seeds were opened during this audit; only already-authorized archived V7 outputs were read.

## Internal evidence map

| Claim | Experiment/source | Independent unit | Artifact | Supported conclusion | Limitation |
|---|---|---|---|---|---|
| P2 improves modeled connectivity vs P1 | Frozen V7 confirmation, seeds 19000–19049 | Seed after averaging five scenarios | `manuscripts/paper1_pc_fmcw/results_archive/confirmatory_seed_level_effects.csv` | Supported for all five declared endpoints after Holm correction | Analytical uncalibrated link; simulated motion |
| V7 confirmatory protocol met its hard gate | Same 1,250 episodes | Episode for gate counting; seed for inference | `safety_gate.json` and full Actions artifact | Zero sampled collision, no-candidate, and static-violation episodes | Not a safety guarantee |
| P3 adds communication benefit over P2 | Frozen V7 confirmation | Seed | Same effects artifact | **Not supported; P3 is worse on all five endpoints** | Risk formulation specific |
| P4 materially improves over P2 | Frozen V7 confirmation | Seed | Same effects artifact | Not supported after Holm correction | Oracle is connectivity-only and nondeployable |
| Directionality is an operative mechanism | Authorized V7 geometry study, seeds 20000–20019 | Seed | Full Actions geometry artifact | Supported as simulator mechanism evidence | One directional/P2 no-candidate episode; no physical validation |
| One-step learned V2X predictors beat persistence | CICV5G grouped primary split | Held-out run | `predictor_metrics.csv` | **Not supported; persistence is stronger** | Dataset-specific |
| P2 lowers measured replay delay vs P1 | Primary route-constrained replay | Held-out run (n=9) | Full run34 artifact; compact summary only checked in | Exploratory: bootstrap interval excludes zero, raw Wilcoxon 0.046875, Holm ≈0.28125 | Not multiplicity-corrected confirmation |
| Direction is robust across five split assignments | Grouped split sensitivity | Split assignment is descriptive, not independent | `multisplit_horizon_summary.csv` plus numbers in manuscript | 5/5 directional consistency | Reused drives; no n=5 inference |
| P3 improves QoS over P2 in measured replay | Same | Held-out run | Full run34 artifact | **Not supported** | P3 instead reduces unsupported exposure |

## Scientific-validity findings

### Correct and retained

- P0–P4 share candidate generation and hard feasibility machinery. P4 receives truth only through its connectivity target; a regression test verifies that common predicted safety cannot be bypassed.
- V7 confirmation and geometry were opened only after the declared prerequisite gates passed.
- Paper-1 inference aggregates repeated scenarios within seed before bootstrap/Wilcoxon inference.
- Paper-2 splitting is by complete acquisition run; predictors/support use training, selection/calibration uses calibration, and held-out replay uses test runs.
- Route replay reveals measured future QoS only after selection and does not fabricate off-route ground truth.
- Split assignments that reuse drives are treated as sensitivity analyses, not independent replications.
- Negative results—V3–V6 gate failures, V7 P3 underperformance, one geometry no-candidate episode, one-step persistence strength, and unstable P3 QoS effects—are retained.

### Issues found and consequences

1. **Stale canonical documentation (results-affecting interpretation, not computation).** README called V3 the current protocol and `PAPER_FREEZE.md` pointed to an obsolete benchmark commit. This could cause authors to cite invalidated or incomplete evidence. They now point to V7 while retaining old failures as history.
2. **Paper-1 publication gap (presentation/reproducibility).** V7 status existed, but no complete Paper-1 manuscript or compact confirmatory snapshot was checked in. A conservative manuscript and artifact-derived summary/effects snapshot were added. Full raw artifacts remain referenced by immutable run/commit/digests.
3. **Generic Paper-2 scorer violated the documented P2/P3 semantics (latent code defect; archived results unaffected).** `score_candidates` applied the unsupported penalty to P1/P2 whenever a support model was supplied. The production replay script implements P2/P3 separately and did not use this helper, so published numbers are unaffected. The helper and regression test now reserve support penalties for P3.
4. **Paper-2 evidence archive is incomplete (submission blocker).** The repository contains publication-facing summaries but not the authoritative per-run effects, decisions, metadata, split manifests, and full provenance bundle. Consequently, the exact bootstrap/Holm statements and every sample-count/split claim cannot be regenerated solely from the checked-in snapshot.
5. **Dependencies are declared but not pinned (reproducibility blocker for exact regeneration).** Workflows install unpinned latest packages. V7 captured `pip freeze` in its full artifact, but Paper 2 lacks a checked-in environment lock tied to run34. Exact numeric reproduction must use an archived environment or a frozen lock validated by rerun.
6. **Historical claim documents remain noncanonical.** Several roadmap/gap documents discuss a historical 20-seed baseline or work “being executed.” They are useful provenance but must not be cited as current results. The canonical sources are this audit, the two manuscripts, V7 status, and manuscript claim-evidence files.
7. **No measured optical calibration.** The carrier/headlamp inconsistency remains unresolved and is explicitly preserved. No physical reconciliation was invented.

## Completed experiments

- V7 seven-margin development sweep: seeds 18000–18019.
- V7 independent 50-seed confirmation: seeds 19000–19049.
- V7 authorized directional/distance-only mechanism study: seeds 20000–20019.
- CICV5G grouped predictor, horizon, support, primary replay, and five-assignment sensitivity studies represented by the run34 archive summaries.

## Unopened or quarantined experiments

- V3 confirmatory/mechanism seeds remained quarantined after development failure.
- V4/V5 confirmatory/mechanism branches remained stopped after their declared failures.
- V6 evidence stops at the failed confirmatory gate; its communication inference and geometry output are not used as valid evidence.
- This audit did not create or inspect any new holdout range and did not tune against V7 or Paper-2 test outcomes.

## Unsupported claims removed or prohibited

- measured or physically calibrated PC-FMCW optical validation;
- real-road or closed-loop vehicle validation;
- safety improvement, guarantee, or “real-world safe” language;
- novelty of generic communication-, optical-, or ISAC-aware planning;
- multiplicity-corrected Paper-2 P2 superiority;
- P3 QoS superiority in either paper;
- independent replication from five reused-drive split assignments;
- PC-FMCW interpretation of CICV5G measurements.

## Statistical validity checks

- V7 uses 50 independent seed-level paired effects, deterministic bootstrap intervals, paired Wilcoxon tests, and Holm correction within each declared five-endpoint comparison family.
- Scenario/timestep/candidate rows are not used as independent confirmatory samples.
- Paper 2 uses held-out acquisition runs as paired units; its raw P2–P1 p-value does not survive the declared 12-test Holm family and is labeled exploratory.
- Multi-split summaries are descriptive only.

## Reproducibility status

Paper 1 has executable entry points, machine-readable protocol, deterministic seeds, source commit/run provenance, archived development evidence, compact confirmatory tables, and passing boundary tests. Exact full rerun still requires the captured full Actions artifact/environment.

Paper 2 has executable acquisition/analysis scripts and a public dataset source, but exact paper closure is blocked until the full authoritative run34 bundle (including `decisions.csv`, `run_metrics.csv`, `paired_planner_effects.csv`, split JSON files, metadata, raw-data manifest/checksums, and environment lock) is durably archived and the asset builder is run against it.

## Remaining work before submission

1. Recover and durably archive the complete Paper-2 run34 evidence bundle and its SHA-256; do not substitute hand-entered values.
2. Add the exact Paper-2 environment lock and raw-data file manifest/checksums.
3. Regenerate Paper-2 tables/figures from that recovered bundle and verify every manuscript number automatically.
4. Mark old roadmap/gap documents as historical or remove them from the submission package.
5. Compile the final manuscripts and perform a final reference/format review. No new scientific experiment is required unless the recovered Paper-2 bundle fails verification.
