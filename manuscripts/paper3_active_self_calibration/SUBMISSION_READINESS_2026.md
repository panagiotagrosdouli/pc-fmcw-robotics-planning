# Paper 3 — Submission Readiness 2026

## Scientific status

**Research question:** stable.

**Frozen primary evidence:** complete.

**Critical September-2026 literature update:** complete, including RMWorld.

**Defensible novelty:** an online safe-motion probing gate based on downstream trajectory disagreement and expected decision regret, evaluated against passive and unconditional active calibration under a frozen protocol.

## Evidence checks

- Development uses separate seeds from confirmation.
- 27-setting selection completed before untouched confirmatory seeds.
- 50 confirmatory seeds / six scenarios / five planners complete.
- Seed is the inferential unit after within-seed scenario aggregation.
- C2-C1 large regret penalty retained.
- C3-C2 large regret/probe reduction retained.
- C3-over-C1 superiority is not claimed.
- Scenario F negative result retained.
- Distance-only ablation remains mechanism evidence, not physical calibration.
- Measured V-VLC directional result remains null.
- CICV5G remains a separate radio-modality support study.
- Zero sampled failures are not a real-world safety guarantee.

## Literature checks

The manuscript explicitly acknowledges prior art in:
- dual control;
- active uncertainty reduction;
- informative path planning;
- calibration trajectory design;
- communication-aware motion planning;
- ISAC-aware planning;
- optical communication-aware control;
- task-aware/value-of-information channel calibration.

RMWorld is cited as a close contemporary comparison and prevents a broad first-of-kind decision-relevant channel-learning claim.

## Manuscript checks

- Canonical source: `paper3.tex`.
- Bibliography: 26 entries, all cited.
- Missing citation keys: none.
- Unused citation keys: none.
- Manuscript PDF CI: passed on PR #41 before submission packaging updates.
- Novelty audit: present.
- Claim-evidence map: updated.
- Annotated bibliography: updated.
- Cover-letter draft: present.

## Recommended first target

**IEEE Transactions on Intelligent Vehicles (T-IV).**

Alternative:
- IEEE Transactions on Automation Science and Engineering if reframed more toward dual control/active estimation.
- IEEE Open Journal of Vehicular Technology as a vehicular open-access alternative.

## Genuine blockers before external submission

1. Confirm complete author list/order.
2. Confirm affiliations and corresponding email.
3. Confirm funding and conflicts.
4. Confirm related-paper/preprint disclosure.
5. Apply the journal's current submission format/page policy.
6. Visually inspect every final PDF page.
7. Build final supplementary archive and immutable release.
8. Approve wording that C3 does not beat passive C1.

## Integrity locks

- Do not post-confirmation retune C3 to beat C1.
- Do not omit Scenario F.
- Do not call the modeled latents physically calibrated.
- Do not claim decision-relevant channel learning is new in general after RMWorld.
- Do not convert collision-free modeled trials into a safety guarantee.
