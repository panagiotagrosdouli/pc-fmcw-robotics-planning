# Paper readiness audit

Audit date: 2026-09-25  
Audited state: frozen Paper-1 V7, verified Paper-2 measured-data evidence, and completed Paper-3 active self-calibration study.

## Executive status

| Paper | Status | Submission interpretation |
|---|---|---|
| Paper 1 — PC-FMCW predictive connectivity-aware robotics | **PASS WITH EXPLICIT LIMITATIONS** | Frozen V7 supports predictive-vs-reactive modeled-connectivity claims under a controlled analytical link. It is not measured optical validation or a safety guarantee. |
| Paper 2 — field-measured V2X predictive planning | **PASS WITH EXPLICIT LIMITATIONS** | Whole-drive measured-data prediction/replay and support analysis are reproducible. P2 evidence remains exploratory/descriptive after multiplicity correction; reused grouped splits are sensitivity analyses. |
| Paper 3 — decision-triggered active self-calibration | **PASS WITH EXPLICIT LIMITATIONS** | Frozen 50-seed C0-C4 confirmation supports strong suppression of unconditional probing cost, but does **not** establish superiority over passive C1. Scenario F is a retained null/negative mechanism result. |

## Repository-wide audit method

The audit covers canonical manuscripts, source/configuration boundaries, GitHub Actions workflows, frozen protocol records, compact archived evidence, paired statistical outputs, safety gates, measured-data support studies, bibliography positioning, and post-merge CI. Frozen scientific evidence is distinguished from development, mechanism ablation, and measured support studies.

## Internal evidence map

| Claim | Experiment/source | Independent unit | Canonical evidence | Supported conclusion | Limitation |
|---|---|---|---|---|---|
| Paper 1 P2 improves modeled connectivity vs P1 | Frozen V7 confirmation, seeds 19000–19049 | Seed after scenario aggregation | `manuscripts/paper1_pc_fmcw/results_archive/` | Supported across declared communication endpoints after Holm correction | Analytical uncalibrated link; simulated motion |
| Paper 1 directional geometry is operative | Authorized V7 geometry study | Seed | Full Actions geometry artifact plus archived summaries | Supported as simulator mechanism evidence | One no-candidate episode; not safety evidence |
| Paper 2 one-step generic learned V2X models beat persistence | CICV5G grouped primary split | Held-out run | Paper-2 archive | **Not supported; persistence is stronger** | Dataset-specific |
| Paper 2 P2 lowers measured replay delay vs P1 | Route-constrained replay | Held-out run | Paper-2 archive | Directionally favorable; primary raw p does not survive declared Holm family | Offline replay, route constrained |
| Paper 2 P3 improves QoS vs P2 | Same | Held-out run | Paper-2 archive | **Not supported**; stable role is reduced unsupported exposure | Validity/mobility trade-off |
| Paper 3 C1 improves decision regret vs C0 | Frozen confirmation, seeds 32000–32049 | Seed after six-scenario aggregation | `manuscripts/paper3_active_self_calibration/results_archive/primary_regret_effects.csv` | Mean delta -0.001646; bootstrap CI excludes zero | Holm-adjusted p=0.05765, so no multiplicity-adjusted confirmatory significance |
| Paper 3 unconditional C2 is worse than passive C1 | Same | Seed | Same | Regret delta +0.083290, Holm p≈1.24e-14 | Model-relative endpoint |
| Paper 3 C3 suppresses unconditional probing penalty | Same | Seed | Same plus planner summary | C3-C2 regret delta -0.082211 and probe-fraction delta -0.037444 | Does not imply C3 > C1 |
| Paper 3 C3 beats passive C1 | Frozen confirmation | Not a predeclared primary pair | Descriptive planner/scenario summaries | **Not established**; overall C1 regret is lower descriptively and F favors C1 | No post-hoc superiority inference |
| Paper 3 Scenario E suppresses irrelevant probing | Scenario E | Seed/scenario diagnostic | `scenario_EF.csv` | C3 regret=0 and probe fraction=0; C2 probes and incurs regret | Mechanism diagnostic, not separate confirmatory family |
| Paper 3 Scenario F converts active probing into lower regret than C1 | Scenario F | Seed/scenario diagnostic | `scenario_EF.csv` | **Not supported**; C3 probes but mean regret 0.034416 vs C1 0.028037 | Retained null/negative result |
| Paper 3 directionality is necessary for nontrivial active behavior | Distance-only development ablation, seeds 31000–31019 | Seed | `distance_only_summary.csv` | Regret/probing collapse to zero across C0-C4 while distance-loss learning remains | Development mechanism ablation; not primary confirmatory evidence |
| Measured V-VLC validates directional Paper-3 mechanism | Held-out spatial-group V-VLC support study | Spatial group | `support_studies_summary.csv` | **Not supported**; directional-minus-distance-only error effect is essentially null | Not PC-FMCW waveform calibration |
| CICV5G validates optical self-calibration | Measured 5G W2S support/replay | Held-out run / descriptive split | Paper-2/3 support summaries | **Not supported**; only QoS/pose transfer and offline replay evidence | Different radio modality |

## Paper-3 frozen protocol and safety

Development used seeds `31000..31019` across the declared 27-setting grid. The deterministic selection rule chose `dev_t010_i025_p020`: decision threshold 0.10, information weight 0.25, probe weight 0.20, and minimum expected regret 0. The protocol was frozen at `2026-09-25T07:28:10.141950+00:00` before untouched confirmatory seeds `32000..32049` were opened.

The confirmatory artifact contains 1,500 planner/scenario/seed episodes and 45,000 timestep rows with no duplicate episode keys. It recorded zero collision episodes, zero no-candidate steps, and zero static-clearance-violation steps. These are sampled hard-gate outcomes under the evaluated scenarios, not a real-world safety guarantee.

## Statistical validity

- Paper 1 aggregates repeated scenarios within independent simulation seed before inferential testing.
- Paper 2 uses held-out acquisition runs; reused grouped split assignments are descriptive sensitivity analyses.
- Paper 3 uses 50 independent confirmatory seeds after averaging the six declared scenarios within seed.
- Paper 3 reports deterministic paired bootstrap intervals, paired Wilcoxon tests, Cohen's dz/rank-biserial effects, and Holm correction within each declared seven-metric comparison family.
- Scenario/timestep/candidate rows are never treated as independent confirmatory replicates.
- C1-C3 was not a predeclared Paper-3 primary comparison and is not promoted to a post-hoc superiority test.

## Negative results retained

- Paper 1 historical gate failures and P3 underperformance.
- Paper 2 one-step persistence strength, imperfect grouped-shift coverage, and lack of stable P3 QoS gain.
- Paper 3 C1-C0 regret comparison does not survive Holm at 0.05.
- Paper 3 C3 does not demonstrate superiority over passive C1; Scenario F is explicitly negative.
- Measured V-VLC does not show meaningful directional predictive gain.
- CICV5G does not validate optical calibration.

## Reproducibility status

Paper 1 and Paper 2 retain their existing canonical manuscript directories and compact result archives. Paper 3 is canonicalized under `manuscripts/paper3_active_self_calibration/`, with a manuscript source, claim-evidence map, build instructions, compact confirmatory/mechanism/support summaries, and links to the immutable Actions artifacts.

The full Paper-3 primary evidence came from GitHub Actions run `36105008882` (`asc-confirmatory` artifact ID `10852339416`, digest `sha256:04acd4a427092897f5d13da6c41be8c2c51195adec2de8250a5f11d45098a3f0`). The standalone distance-only ablation came from run `36110361343` (artifact ID `10853600391`, digest `sha256:415d4d4d80697bdef3c35475773139a7fc07ce1f8435d38d0d1143bbacc8e0c5`).

## Unsupported claims prohibited

- measured or physically calibrated PC-FMCW optical validation;
- real-road closed-loop benefit or safety guarantee;
- universal novelty of communication-aware, optical-aware, ISAC-aware, informative, or calibration-aware motion planning;
- Paper-2 multiplicity-corrected P2 superiority;
- Paper-2 P3 QoS superiority;
- independent replication from reused-drive split assignments;
- Paper-3 C3 superiority over passive C1;
- physical parameter identifiability from the synthetic latent family;
- using CICV5G as optical calibration evidence.

## Remaining work before portal submission

No new scientific experiment is required by this audit. Remaining work is publication operations only: confirm author affiliation/contact/ORCID/funding/competing-interest text; freeze a venue for Paper 3; compile/visually inspect all three PDFs; regenerate/check compact evidence immediately before submission; and mint an archival release/DOI only if the repository owner chooses to do so.
