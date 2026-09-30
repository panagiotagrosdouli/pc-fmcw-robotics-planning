# Paper 2 — Submission Readiness 2026

**Last scientific/submission pass:** 2026-09-30

## Current manuscript

**Title:** *From QoS Prediction to Measured Decision Validity: Support-Bounded Matched Field Replay for Vehicular Speed Decisions*

**Canonical source:** `paper2.tex`

**Primary contribution:** measured decision validity under finite repeated-drive action support, not planner superiority.

The paper separates:

1. predictor training;
2. measured action-outcome donation;
3. decision queries;
4. two-way query-run × donor-run uncertainty.

## Scientific status

**Research question:** stable.

**Frozen evidence:** complete for the current cross-scenario claims.

**Literature positioning:** updated through September 2026, including communication-aware planning, field-measured PQoS, radio-map planning, RMWorld, vehicular regret diagnostics, and the September 2026 QoSformer Internet-Draft.

**Novelty boundary:** the contribution is not generic communication-aware planning, decision-focused learning, regret analysis, or QoS policy evaluation. The defensible distinction is the combination of vehicular motion actions, repeated measured drives, disjoint train/donor/query acquisition-run roles, finite action support, donor outcome provenance, and donor-aware inference.

## Confirmed field evidence

### W2S confirmation — 30 vs 50 km/h

Frozen before outcome inspection.

- Workflow: `36747715208`
- Workflow head SHA: `a056d46a5579032d10f51a1d6e90d800d3d017b4`
- Executed checkout SHA recorded by artifact: `e4f6430f8b6368f64edee421b827895b11280115`
- Valid two-way bootstrap replicates: 4,945 / 5,000
- ORACLE − FAST: **−4.177 ms**, 95% CI **[−13.659, −2.137]**
- PRED − ORACLE: **+2.704 ms**, 95% CI **[+1.457, +5.832]**
- PRED − FAST: **−1.473 ms**, 95% CI **[−8.167, +0.657]**
- MARGIN − FAST: **−1.668 ms**, 95% CI **[−9.524, +1.180]**

Interpretation:

- measurable action-value headroom is present;
- predictor regret relative to the measured upper-bound diagnostic is present;
- PRED-over-FAST superiority is **not** confirmatory.

### Arterial n8 confirmation — 50 vs 80 km/h

Protocol frozen before outcome inspection and performed on a different scenario/action pair.

- Workflow: `36749176921`
- Workflow head SHA: `5a98d2e8ea1a948d5cc1d0586d4d63b402a715a7`
- Executed checkout SHA recorded by artifact: `3df3a7b4479f7b1e9d6019497b4a5e9ecbb12586`
- Valid two-way bootstrap replicates: 4,409 / 5,000
- ORACLE − FAST: **−0.590 ms**, 95% CI **[−1.431, −0.250]**
- PRED − ORACLE: **+0.746 ms**, 95% CI **[+0.344, +1.596]**
- PRED − FAST: **+0.156 ms**, 95% CI **[+0.038, +0.258]**
- MARGIN − FAST: **+0.032 ms**, 95% CI **[+0.007, +0.061]**

Interpretation:

- measured action-value headroom again exists;
- the frozen predictive intervention is measurably worse than FAST in this scenario;
- the frozen pairwise margin intervention is also worse than FAST.

## Cross-scenario conclusion

The supported central empirical statement is:

> Across two pre-frozen repeated-field evaluations with different speed-action pairs, support-bounded measured action-value headroom exists, while frozen prediction-based rankings fail to recover it reliably. Superiority over FAST is unconfirmed in W2S, and the same frozen prediction-derived intervention is worse than FAST in the arterial confirmation.

This is a failure-boundary / evidence-validity result, not a universal negative claim about predictive QoS.

## Statistical integrity checks

- Whole acquisition runs, not timestamp rows, define evidence roles.
- Training, donor, and query roles are disjoint within each locked configuration.
- Donor measurements are hidden during deployable policy ranking.
- Matched donor contribution provenance is exported explicitly.
- Two-way bootstrap resamples both query and donor acquisition runs.
- Development seed/caliper configurations are not treated as independent experiments.
- Negative pairwise-margin results are retained.
- No post-result method retuning was used to manufacture a positive planner effect.
- Causal speed effects are not claimed.
- The measured oracle is labeled as a nondeployable support-bounded upper-bound diagnostic.

## Manuscript checks

- Canonical TeX source: `paper2.tex`.
- Human-readable companion: `MANUSCRIPT.md`.
- Confirmatory snapshot: `MANUSCRIPT_CONFIRMED_2026.md`.
- Claim-evidence matrix: aligned with both confirmations.
- Cover letter: aligned with the cross-scenario evidence.
- Abstract: **218 words**.
- Citation keys in confirmed TeX: **14 unique, 0 missing**.
- LaTeX environment balance: no static mismatches.
- Exact confirmed TeX was compiled by Manuscript PDF CI run `36751514918`: **success**.
- Resulting confirmed PDF: **5 IEEE-style pages**.
- Unresolved manuscript-marker check: passed.
- Supplementary reproducibility packaging: passed.

The exact confirmed TeX content that passed this build was subsequently promoted to canonical `paper2.tex`.

## Recommended first target

**IEEE Transactions on Vehicular Technology (TVT).**

The current confirmed manuscript is approximately **5 IEEE-style pages**, comfortably inside the journal's current initial regular-paper page allowance.

Current TVT rules were checked on 2026-09-30 against the official Vehicular Technology Society author instructions.

Alternative paths remain:

- IEEE Open Journal of Vehicular Technology for a fully open-access route;
- IEEE Transactions on Intelligent Vehicles if the final editorial emphasis shifts more strongly toward decision methodology.

## TVT-specific editorial compliance

TVT's current author instructions state that AI tools may be used for language/grammar modification of author-generated text but that such use must be disclosed in the acknowledgments.

Suggested disclosure after author review:

> OpenAI ChatGPT was used to assist with language editing and clarity of author-prepared manuscript text. The author reviewed the final wording and remains responsible for the scientific content, analysis, interpretation, and conclusions.

Do not insert this as a factual acknowledgment until the author has reviewed and approved the final wording.

## Genuine blockers before external submission

1. Confirm complete author list and ordering.
2. Confirm affiliation(s) and corresponding-author institutional email.
3. Confirm funding/acknowledgments and conflict-of-interest statements.
4. Confirm ORCID and IEEE Author Portal metadata.
5. Confirm disclosure requirements for any related public manuscript, repository, or preprint.
6. Approve and insert the AI-assisted language-editing disclosure if applicable.
7. Run final visual inspection on the new canonical five-page PDF.
8. Decide whether the manuscript needs one compact figure explaining train/donor/query replay; do not add it merely to increase page count.
9. Produce the immutable submission source/supplement archive and release tag.
10. Approve the final cover letter and portal declarations.

## What must not be changed merely to improve acceptance odds

- Do not claim PRED superiority in W2S; its two-way interval crosses zero.
- Do not hide the arterial degradation result.
- Do not retune the pairwise margin method after its frozen negative result.
- Do not call the matched oracle deployable or unbiased.
- Do not convert observational matched outcomes into causal speed effects.
- Do not treat timestamp rows or bootstrap draws as new independent field experiments.
- Do not broaden novelty to generic PQoS, communication-aware planning, decision-focused learning, regret diagnostics, or generic QoS policy evaluation.
- Do not add experiments solely to manufacture statistical significance.
