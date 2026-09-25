# Paper 3 — T-IV Regular Paper submission checklist

**Preferred target:** IEEE Transactions on Intelligent Vehicles (T-IV), Regular Paper — conditional  
**Verification date:** 2026-09-25

Official sources checked:
- https://ieee-itss.org/pub/t-iv/
- https://ieee-itss.org/pub/t-iv/author/
- https://ieee-itss.org/wp-content/uploads/IEEE-TIV-Checklist.pdf

## Scope fit

The current T-IV scope explicitly includes automated vehicles, autonomous/intelligent robotic vehicles, information fusion, vehicle control, collision avoidance, and vehicle-environment perception. Paper 3 addresses a safety-constrained intelligent-vehicle motion planner whose communication-model uncertainty can influence vehicle-control decisions.

## Manuscript-format checks

- [x] IEEE double-column journal format.
- [x] Regular Paper is the preferred T-IV category.
- [ ] T-IV target freeze pending public-repository-policy clarification.
- [x] Current abstract length is 220 words; current T-IV guidance is 150–250 words.
- [x] Figures and tables are embedded in the manuscript and generated from frozen evidence.
- [x] Final 8-page IEEE double-column PDF compiled successfully in Manuscript PDF CI.
- [x] Final 8-page PDF visually inspected for clipping, overlap, broken glyphs, architecture routing, figure/table readability, and bibliography rendering.
- [x] Author line contains the author name without affiliation or email under the title.
- [x] Scientific claim/evidence boundaries remain unchanged by venue formatting.

## T-IV policy blocker

The current official T-IV checklist states that the submitted work should not be deposited in a publicly accessible repository (with arXiv given as an example). The Paper-3 manuscript source is already publicly accessible in this GitHub repository and its commit history. Deleting the current copy would not erase that history.

- [ ] Obtain written clarification from the T-IV office (`tiv-eic@ieee.org`) that the existing public GitHub manuscript history is acceptable before portal submission.
- [ ] If it is not acceptable, select and re-audit a policy-compatible fallback venue rather than attempting to hide or rewrite the public record.

## T-IV author/portal items still requiring author input

- [ ] Verified institutional email address.
- [ ] Verified affiliation and postal address for submission metadata.
- [ ] Short author biography for the Regular Paper.
- [ ] Conflict-of-interest disclosure.
- [ ] Funding and acknowledgements statement, including an explicit no-funding statement if appropriate.
- [ ] ORCID for the author (required by the current T-IV checklist).
- [ ] Traditional-access versus Open Access choice.
- [ ] Author-portal account/login availability.
- [ ] Final approval of title, author list, and corresponding-author designation.

## Scientific no-change gate

Before portal upload:
- do not alter frozen seeds, selected hyperparameters, primary comparison families, or archived result values;
- do not claim C3 superiority over passive C1;
- retain the Scenario-F negative result;
- retain the measured V-VLC null directional result;
- keep CICV5G explicitly separate from optical calibration;
- describe C4 only as a model-relative oracle;
- describe zero sampled safety failures only as benchmark outcomes, not a safety guarantee.

## Final portal package

After the manual author fields above are supplied, regenerate publication assets, compile the manuscript, visually inspect the final PDF, rebuild the Paper-3 supplementary reproducibility ZIP, and record the final release/tag/DOI decision in `docs/SUBMISSION_RELEASE_MANIFEST.md`.
