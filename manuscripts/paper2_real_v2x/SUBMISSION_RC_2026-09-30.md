# Paper 2 — Submission Release Candidate

**Release-candidate date:** 2026-09-30  
**Branch:** `research/paper2-matched-speed-replay`  
**Release-candidate commit:** `e389155f956146afc60bee89d5b9f78bb4523444`

## Canonical manuscript

**Title:** *From QoS Prediction to Measured Decision Validity: Support-Bounded Matched Field Replay for Vehicular Speed Decisions*

Canonical source:

`manuscripts/paper2_real_v2x/paper2.tex`

## CI gates

Latest head:

`e389155f956146afc60bee89d5b9f78bb4523444`

- Manuscript PDF CI: run `36755292291` — **success**
- Full CI: run `36755292339` — **success**
- Publication artifact ID: `11117202141`
- Publication artifact digest: `sha256:70abdc5577416fbc2e5df11cf2b163831f062731ab85ce8a5c1acd8b5b964c6f`

## Rendered manuscript QA

- PDF pages: **5**
- Page size: IEEE-style US Letter, 612 × 792 pt
- Fonts: embedded
- Page-3 long policy-label overlap: **fixed**
- Latest page-3 visual QA: **pass**
- Latest provenance-updated page-5 visual QA: **pass**
- Clipped text: **none observed**
- Broken glyphs: **none observed**
- Table overflow: **none observed**
- Unresolved-reference build gate: **pass**

Canonical PDF SHA256:

`a959be264efddf25919b58e0ed57c56d11e0fdeb01f4d26c5bf26c22d1d34172`

## Supplementary reproducibility bundle

Bundle:

`paper2_supplementary_reproducibility.zip`

SHA256:

`0120fac3dd8f8dac4c897b5e4a5bd9e7efdc662ab6ff36937da061892902b683`

Archive entries:

**103 files**

Duplicate archive paths:

**0**

Confirmed contents include:

- canonical manuscript source and bibliography;
- claim-evidence and readiness documents;
- W2S frozen protocol and result;
- arterial frozen protocol and result;
- cross-scenario synthesis;
- compact non-expiring W2S evidence snapshot;
- compact non-expiring arterial evidence snapshot;
- exact train/donor/query split metadata;
- workflow-head and executed-checkout provenance;
- matched replay implementation;
- pairwise decision-margin implementation;
- confirmatory analysis scripts;
- relevant tests;
- GitHub Actions workflow definitions.

## Scientific release-candidate claim

The release candidate supports the following bounded statement:

> Across two pre-frozen repeated-field evaluations with different speed-action pairs, support-bounded measured action-value headroom exists, while frozen prediction-based rankings fail to recover that opportunity reliably. Superiority over FAST is unconfirmed in W2S, and the same frozen predictive intervention is measurably worse than FAST in the arterial confirmation.

The release candidate does not claim:

- a causal speed effect;
- a universally superior or harmful speed policy;
- arbitrary field counterfactual ground truth;
- a deployable measured oracle;
- novelty for generic communication-aware planning, predictive QoS, regret, or decision-focused learning;
- generalization outside CICV5G.

## Provenance distinction

Because the confirmation workflows were triggered by pull requests, two SHAs are recorded for each frozen experiment.

### W2S

- workflow head SHA: `a056d46a5579032d10f51a1d6e90d800d3d017b4`
- executed checkout SHA recorded by artifact: `e4f6430f8b6368f64edee421b827895b11280115`

### Arterial

- workflow head SHA: `5a98d2e8ea1a948d5cc1d0586d4d63b402a715a7`
- executed checkout SHA recorded by artifact: `3df3a7b4479f7b1e9d6019497b4a5e9ecbb12586`

This distinction is publication-relevant provenance only; it does not change the reported numerical results.

## Remaining blockers

No additional scientific experiment is required for the current bounded manuscript claim.

External submission still requires author-owned information:

1. final author list and order;
2. affiliation(s);
3. corresponding-author institutional email;
4. funding and acknowledgments;
5. conflict-of-interest declaration;
6. ORCID / portal metadata;
7. related-manuscript, preprint, and repository disclosures;
8. author approval of the AI-assisted language-editing disclosure;
9. final immutable submission tag/release after the above metadata are inserted.

Until those items are confirmed, this state is a **submission release candidate**, not the final submission release.
