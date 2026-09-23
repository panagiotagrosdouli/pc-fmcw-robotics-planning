# Canonical submission package

This index distinguishes submission evidence from historical planning notes.
It does not introduce new results or expand either paper's scope.

## Repository-wide authority

- `PAPER_READINESS_AUDIT.md` — final PASS/limitations and evidence map.
- `README.md` — two-paper scope and claim boundaries.
- `docs/PAPER_FREEZE.md` — immutable Paper-1 V7 protocol state.
- `docs/PC_FMCW_PARAMETER_AUDIT.md` — upstream/modeled parameter boundary,
  including the unresolved carrier-frequency/headlamp interpretation.

## Paper 1

- `manuscripts/paper1_pc_fmcw/MANUSCRIPT.md`
- `docs/PART_B_V7_EXECUTION_STATUS.md`
- `configs/experiments/part_b_final_v7.yaml`
- `manuscripts/paper1_pc_fmcw/results_archive/`
- `results_archive/part_b_v7_development/`

Paper-1 claims are controlled analytical-simulation claims. They are not
optical measurements, physical calibration, road validation, or a safety
guarantee.

## Paper 2

- `manuscripts/paper2_real_v2x/paper2.tex`
- `manuscripts/paper2_real_v2x/MANUSCRIPT.md`
- `manuscripts/paper2_real_v2x/CLAIM_EVIDENCE.md`
- `manuscripts/paper2_real_v2x/results_archive/`
- `.github/workflows/real_v2x_research.yml`

Paper-2 evidence is field-measured 5G/V2N2V offline replay. The P2–P1 primary
effect is exploratory after multiplicity correction. The five grouped split
assignments are descriptive sensitivity analyses, not independent replications.
P3 reduces unsupported exposure but has no stable QoS advantage over P2.

## Historical files excluded from status decisions

Files explicitly labeled historical, superseded, roadmap, completion plan, or
research expansion are audit trail only. In particular, historical V1–V6
results cannot replace the frozen V7 result, and old timing measurements are
not paper claims.

## Final pre-submission checks

1. Build all manuscript sources through `manuscript_ci.yml`.
2. Run the complete test suite.
3. Regenerate tables/figures from archived machine-readable artifacts.
4. Confirm there are no unresolved markers in the manuscript sources.
5. Verify venue formatting and bibliography metadata without changing claims.

Venue selection, bibliography verification, and the frozen-release manifest are recorded in `VENUE_AND_SUBMISSION_PLAN.md`, `BIBLIOGRAPHY_AUDIT.md`, and `SUBMISSION_RELEASE_MANIFEST.md`.
