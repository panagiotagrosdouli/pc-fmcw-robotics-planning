# Paper 2 — Submission Readiness 2026

**Last submission pass:** 2026-09-30

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
- Manuscript PDF CI: previously passed, including the post-merge layout-fix build.
- CI-generated 7-page PDF was previously rendered and visually inspected with no remaining clipping/overlap after the positioning-table correction.
- Novelty audit: present.
- Claim-evidence matrix: present.
- Formal mathematical formulation: present.
- Cover-letter draft: present.
- Abstract tightened on 2026-09-30 from approximately 273 words to approximately 218 words, preserving the frozen evidence and explicitly stating that the primary P2-P1 paired comparison does not remain significant after Holm correction.

## Recommended first target

**IEEE Transactions on Vehicular Technology (TVT).**

Current manuscript length before the 2026-09-30 abstract edit: **7 IEEE-style pages**.

Current TVT instructions require initial regular-paper submissions to use IEEE-style double-column formatting with font no smaller than 10 pt and allow up to **14 pages** for an initial regular paper. References and biographies count toward the page limit. The journal currently uses the IEEE Author Portal for new submissions.

Current official sources checked 2026-09-30:

- https://vtsociety.org/publication/ieee-transactions-vehicular-technology/guidelines-authors
- https://vtsociety.org/publication/ieee-transactions-vehicular-technology/guidelines-authors/instructions
- https://vtsociety.org/publication/ieee-transactions-vehicular-technology/guidelines-authors/frequently-asked-questions
- https://vtsociety.org/publication/ieee-transactions-vehicular-technology/guidelines-authors/instructions/page-charges

The current paper is comfortably inside the initial page limit. TVT currently applies a mandatory overlength charge beyond 10 printed pages for regular papers, so there is no reason to add material merely to fill the available 14-page initial-submission allowance.

Alternative paths:

- IEEE Open Journal of Vehicular Technology for a fully open-access route.
- IEEE Transactions on Intelligent Vehicles if the final editorial emphasis shifts toward decision methodology.

## TVT-specific editorial compliance

TVT's current author instructions state that AI tools may be used to modify author-generated text for purposes such as grammar/language improvement, but such use must be disclosed in the acknowledgments.

Because the 2026-09-30 submission pass used AI-assisted language editing of existing manuscript text, the final author-approved manuscript should include a disclosure consistent with the journal's policy.

Suggested disclosure after author review:

> OpenAI ChatGPT was used to assist with language editing and clarity of author-prepared manuscript text. The author reviewed the final wording and remains responsible for the scientific content, analysis, interpretation, and conclusions.

Do not insert the sentence as a factual acknowledgment until the author has reviewed and approved the final manuscript wording.

## Genuine blockers before external submission

1. Confirm complete author list and ordering.
2. Confirm affiliations and corresponding-author email.
3. Confirm funding and conflict-of-interest statements.
4. Confirm ORCID/IEEE Author Portal metadata required for the final author list.
5. Confirm whether any related manuscript, public manuscript version, or preprint must be disclosed to TVT.
6. Add the required AI-assisted language-editing disclosure after final author review.
7. Rebuild the manuscript after the 2026-09-30 abstract edit and confirm that it remains within the page limit.
8. Re-run final PDF visual inspection.
9. Produce the final source/supplementary archive and immutable release tag.
10. Approve the cover letter and all portal declarations.

## What must not be changed merely to improve acceptance odds

- Do not convert the Holm-adjusted non-significant primary comparison into a significance claim.
- Do not treat five grouped assignments as five independent experiments.
- Do not remove the negative P3 result.
- Do not expand MSCR into a claim of real physical intervention.
- Do not add experiments solely to manufacture statistical significance.
- Do not broaden the novelty claim to generic PQoS, radio-map planning, or communication-aware motion planning.
