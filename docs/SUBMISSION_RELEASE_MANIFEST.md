# Submission release manifest

The repository contains three canonical manuscript packages.

- Paper 1 source: `manuscripts/paper1_pc_fmcw/paper1.tex`.
- Paper 2 source: `manuscripts/paper2_real_v2x/paper2.tex`.
- Paper 3 source: `manuscripts/paper3_active_self_calibration/paper3.tex`.
- Paper 3 preferred venue: **IEEE Transactions on Intelligent Vehicles (T-IV), Regular Paper**, conditional pending clarification of the journal's public-repository checklist item.
- Machine-generated/build assets are validated by `.github/workflows/manuscript_ci.yml`.
- Supplementary reproducibility archives are produced by `scripts/build_submission_package.py` for `paper1`, `paper2`, and `paper3`.
- Scientific status is governed by `PAPER_READINESS_AUDIT.md` plus the paper-specific frozen protocol/evidence files.

## Paper-3 immutable evidence references

- Primary full-research run: `36105008882`.
- Confirmatory artifact: `asc-confirmatory`, artifact ID `10852339416`, digest `sha256:04acd4a427092897f5d13da6c41be8c2c51195adec2de8250a5f11d45098a3f0`.
- Development/freeze artifact: `asc-development-frozen`, artifact ID `10851144697`.
- Distance-only mechanism ablation run: `36110361343`.
- Distance-only artifact: artifact ID `10853600391`, digest `sha256:415d4d4d80697bdef3c35475773139a7fc07ce1f8435d38d0d1143bbacc8e0c5`.
- Frozen confirmatory seed range: `32000..32049`.
- Development seed range: `31000..31019`.
- Selected setting: `dev_t010_i025_p020`.

## Frozen scientific boundaries

Release work may correct wording, formatting, citation metadata, or reproducibility packaging. It may not change protocol choices, tune after confirmatory outcomes, omit negative results, relabel development/mechanism evidence as primary confirmation, or strengthen claims beyond archived evidence.

## Publication-asset state

The Paper-3 manuscript is generated from compact frozen evidence using `scripts/build_paper3_publication_assets.py`. The final merged manuscript is an 8-page IEEE double-column PDF with a 220-word abstract and 24 cited bibliography entries. Manuscript PDF CI compiled the source successfully with generated vector figures and LaTeX tables, and the resulting PDF was visually inspected for clipping, overlap, glyph rendering, architecture routing, figure/table readability, and bibliography layout.

## Venue-policy blocker

T-IV is not yet frozen for portal submission. Its current official checklist states that the submitted work should not be deposited in a publicly accessible repository. Because the canonical Paper-3 manuscript already exists in this public GitHub history, written editorial clarification is required before treating T-IV as compliant. ORCID is also listed as required for all authors.

## Release/tag state

The historical intended tag `paper-submission-v1.0` predates the Paper-3 package and should not be minted from an earlier two-paper state. A new final release tag should be chosen only after author metadata is inserted and the repository owner confirms the intended submission set.

## Zenodo

No repository DOI is claimed until the repository owner enables an archival integration and archives a release. Once minted, add the DOI to this manifest and the relevant code-availability statements without changing scientific content.
