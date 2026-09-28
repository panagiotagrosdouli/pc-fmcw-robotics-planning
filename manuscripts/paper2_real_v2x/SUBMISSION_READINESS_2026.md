# Paper 2 — Submission Readiness 2026

## Scientific status

**Research question:** stable.

**Frozen evidence:** complete for the current claims.

**Literature positioning:** updated through September 2026, including communication-aware planning, field-measured predictive QoS, predictive radio maps, uncertainty-aware communication control, and RMWorld.

**Central contribution:** decision validity under logged field measurements, operationalized through predictive-horizon validation, empirical-support auditing, and measurement-supported counterfactual replay (MSCR).

## Evidence checks

- Whole-run train/calibration/test separation: complete.
- Primary held-out replay: complete.
- Five grouped split sensitivity assignments: complete.
- Run-level inferential unit: preserved.
- Multiplicity correction: preserved.
- Negative P3 QoS result: retained.
- P2 primary Holm-adjusted non-significance: retained.
- Off-route ground truth is not fabricated.
- CICV5G is not relabeled as optical evidence.

## Manuscript checks

- Canonical source: `paper2.tex`.
- Bibliography: 15 entries, all cited.
- Missing citation keys: none.
- Unused citation keys: none.
- Manuscript PDF CI: passed on the Paper-2 branch, including the post-merge layout-fix build.
- CI-generated 7-page PDF rendered and visually inspected: the previously overflowing positioning table now fits within the page; no remaining clipping/overlap was detected.
- General repository CI: passed on PR #39.
- Novelty audit: present.
- Claim-evidence matrix: present.
- Formal mathematical formulation: present.
- Cover-letter draft: present.

## Recommended first target

**IEEE Transactions on Vehicular Technology (TVT).**

Alternative paths:
- IEEE Open Journal of Vehicular Technology for a fully open-access route.
- IEEE Transactions on Intelligent Vehicles if the final editorial emphasis shifts toward decision methodology.

## Genuine blockers before external submission

1. Confirm complete author list and ordering.
2. Confirm affiliations and corresponding-author email.
3. Confirm funding and conflict-of-interest statements.
4. Confirm whether any related manuscript/preprint must be disclosed to the target journal.
5. Apply the target journal's current submission template and page rules.
6. Re-run one final visual inspection after venue-template conversion.
7. Produce final source/supplementary archive and immutable release tag.
8. Approve the cover letter and declarations.

## What must not be changed merely to improve acceptance odds

- Do not convert the Holm-adjusted non-significant primary comparison into a significance claim.
- Do not treat five grouped assignments as five independent experiments.
- Do not remove the negative P3 result.
- Do not expand MSCR into a claim of real physical intervention.
