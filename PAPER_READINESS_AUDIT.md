# Paper readiness audit

Audit date: 2026-09-21  
Audited state: Paper-1 V7 plus verified Paper-2 provenance run `35537024339`.

## Executive status

| Paper | Status | Submission interpretation |
|---|---|---|
| Paper 1 — PC-FMCW predictive connectivity-aware robotics | **PASS WITH EXPLICIT LIMITATIONS** | The frozen V7 primary claim is supported as controlled analytical-simulation evidence. It is not optical validation or a safety guarantee. |
| Paper 2 — field-measured V2X predictive planning | **PASS WITH EXPLICIT LIMITATIONS** | The pinned-data provenance run reproduces the scientific outputs and records code, environment, raw-file hashes, grouped splits, and run-level inference. P2 evidence remains exploratory/descriptive after multiplicity correction. |

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
4. **Paper-2 evidence/provenance gap (resolved).** Run `35537024339` produced the full decisions, run metrics, paired effects, split records, code/environment provenance, and a 38-file raw-data manifest pinned to CICV5G tree `0ad0b8307b918b22754ff651f750e70c7960abd2`. The artifact digest is `sha256:1d4f655bb52d0321deecb153e934b1f6166c9a4cbc08d96d85054dc98b768bf6`; compact inferential/provenance files are checked in.
5. **Unstable hosted timing claim (resolved by removal).** Scientific outputs reproduced exactly, apart from a floating-point difference of `2.22e-16`; wall-clock timings varied with runner load. Exact timing values were removed from the paper claims rather than cherry-picked.
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

Paper 2 has executable acquisition/analysis scripts, a public dataset source pinned by upstream tree SHA, raw-file SHA-256 hashes, grouped split manifests, exact environment capture, compact run-level inference records, and a full reproducibility artifact. The regenerated scientific tables matched the prior evidence exactly; hosted timings are excluded from claims.

## Remaining work before submission

1. Mark remaining roadmap/gap documents as historical or exclude them from the submission package.
2. Perform venue-specific reference/style review and compile the final manuscripts.
3. Re-run the artifact-to-manuscript verification immediately before submission. No new scientific experiment is required by this audit.
