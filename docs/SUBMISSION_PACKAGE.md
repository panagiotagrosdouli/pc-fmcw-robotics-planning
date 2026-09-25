# Canonical submission package

This index distinguishes canonical submission evidence from historical planning notes. It does not introduce new scientific results.

## Repository-wide authority

- `PAPER_READINESS_AUDIT.md` — current three-paper PASS/limitations and evidence map.
- `README.md` — three-paper scope and claim boundaries.
- `docs/BIBLIOGRAPHY_AUDIT.md` — citation/positioning audit.
- `docs/VENUE_AND_SUBMISSION_PLAN.md` — venue state and unresolved author metadata.
- `docs/SUBMISSION_RELEASE_MANIFEST.md` — release/provenance boundary.

## Paper 1 — PC-FMCW predictive connectivity-aware robotics

- `manuscripts/paper1_pc_fmcw/paper1.tex`
- `manuscripts/paper1_pc_fmcw/MANUSCRIPT.md`
- `docs/PART_B_V7_EXECUTION_STATUS.md`
- `configs/experiments/part_b_final_v7.yaml`
- `manuscripts/paper1_pc_fmcw/results_archive/`

Claims are controlled analytical-simulation claims, not optical measurements, physical calibration, road validation, or a safety guarantee.

## Paper 2 — measurement-support-aware V2X planning

- `manuscripts/paper2_real_v2x/paper2.tex`
- `manuscripts/paper2_real_v2x/MANUSCRIPT.md`
- `manuscripts/paper2_real_v2x/CLAIM_EVIDENCE.md`
- `manuscripts/paper2_real_v2x/results_archive/`
- `.github/workflows/real_v2x_research.yml`

Evidence is field-measured 5G/V2N2V offline replay. The P2-P1 primary effect remains exploratory after multiplicity correction; grouped split assignments are descriptive sensitivity analyses.

## Paper 3 — decision-triggered active self-calibration

- `manuscripts/paper3_active_self_calibration/paper3.tex`
- `manuscripts/paper3_active_self_calibration/MANUSCRIPT.md`
- `manuscripts/paper3_active_self_calibration/CLAIM_EVIDENCE.md`
- `manuscripts/paper3_active_self_calibration/RESULTS_CHECKLIST.md`
- `manuscripts/paper3_active_self_calibration/results_archive/`
- `docs/ACTIVE_SELF_CALIBRATION_RESEARCH_PLAN.md`
- `configs/experiments/active_self_calibration.yaml`
- `.github/workflows/active-self-calibration-research.yml`
- `.github/workflows/active-self-calibration-ablation.yml`

The primary Paper-3 evidence is the frozen 50-seed directional confirmatory study. The distance-only run is a development mechanism ablation. Measured V-VLC and CICV5G results are separately scoped support studies and must not be relabeled as direct optical calibration or closed-loop real-vehicle validation.

## Historical files excluded from status decisions

Files explicitly labeled historical, superseded, roadmap, completion plan, or research expansion are audit trail only. In particular, `docs/paper/TWO_PAPER_PUBLICATION_PLAN.md` is superseded by `THREE_PAPER_PUBLICATION_PLAN.md`.

## Final pre-submission checks

1. Build all manuscript sources through `manuscript_ci.yml`.
2. Run the complete repository test suite.
3. Verify every numerical statement against the compact archive and authoritative Actions artifact.
4. Confirm there are no unresolved markers in manuscript sources.
5. Verify venue formatting and bibliography metadata without changing claims.
6. Confirm author affiliation/contact/ORCID/funding/competing-interest fields manually.
7. Tag/archive only after all three canonical packages are in the intended release state.
