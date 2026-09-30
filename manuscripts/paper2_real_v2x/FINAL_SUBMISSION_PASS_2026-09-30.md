# Paper 2 — Final Submission Pass

**Date:** 2026-09-30  
**Target:** IEEE Transactions on Vehicular Technology (TVT)  
**Canonical manuscript:** `paper2.tex`

## Submission interpretation

Paper 2 is ready to be treated as a **methodology-and-field-evidence paper**, not as a planner-superiority paper.

The central publication claim is:

> Logged field-measured connectivity prediction becomes decision evidence only when predictive validity, empirical measurement support, and post-selection measured evaluability are separated explicitly.

The manuscript operationalizes this through:

1. causal-horizon comparison against persistence;
2. empirical support auditing using training measurements only;
3. measurement-supported counterfactual replay (MSCR), where the selected route-supported candidate is evaluated using a future field measurement hidden during selection.

## Editor-facing two-sentence pitch

Predictive QoS and communication-aware vehicle planning are established, but logged field measurements create a validation mismatch because a planner evaluates alternative future states while measurements exist only along the trajectory that was actually driven. This paper introduces a three-layer decision-validity framework and MSCR protocol that separates predictive utility, empirical support, and measured post-selection evaluability without treating model-generated counterfactuals as measured truth.

## What makes the paper publishable

The paper does not depend on a broad novelty claim.

Its contribution is a controlled evidential protocol:

- whole-run separation prevents obvious temporal/route leakage;
- persistence is retained as the causal short-horizon baseline;
- support is not conflated with predictive uncertainty;
- future measured outcomes are hidden during selection;
- the run is the inferential unit;
- repeated grouped splits are not treated as independent replications;
- multiplicity correction is retained;
- negative P3 results are retained.

That combination makes the paper scientifically useful even though the primary P2-P1 planner comparison is not Holm-confirmatory.

## Primary evidence in reviewer-safe language

The primary nine-run replay gives a P2-P1 mean-delay effect of approximately **-0.792 ms**, with a bootstrap interval excluding zero.

The raw paired Wilcoxon value is **0.046875**, but the Holm-adjusted value is approximately **0.28125** across the declared family.

Therefore the correct statement is:

> P2 shows an exploratory favorable measured-delay effect on the primary split and the same effect direction across all five dependent grouped split assignments; the evidence does not establish multiplicity-corrected confirmatory superiority.

For P3:

> P3 consistently reduces unsupported-selection exposure relative to P2, but measured-delay effects are mixed and mobility deviation increases; the supported interpretation is a validity-versus-mobility trade-off rather than a QoS-performance gain.

## Likely reviewer attack points and the manuscript answer

### "The planner is simple."

That is intentional. The paper's research object is the validity of logged field evidence for decision evaluation, not a new trajectory optimizer. A more complex planner would make attribution harder.

### "This is not a true counterfactual intervention."

Correct. MSCR is explicitly route-constrained offline replay. It does not claim arbitrary off-route causal effects or physical intervention.

### "Nine test runs are too few for a strong superiority claim."

The paper does not make that claim. It reports effect sizes, bootstrap intervals, corrected inference, and dependent split sensitivity transparently.

### "Spatial support distance is a weak OOD detector."

Correct. It is presented as a simple empirical-support diagnostic, not a complete distribution-shift detector. Its role is to separate measurement support from residual uncertainty.

### "P3 does not improve QoS."

Correct and retained. The negative result demonstrates that evidential conservatism can reduce unsupported decisions while imposing mobility cost without automatic QoS benefit.

### "Communication-aware planning and predictive QoS are already known."

The manuscript explicitly concedes this prior art. Novelty is located at the decision-validity and measured-evaluation boundary.

## Abstract status

The abstract was tightened on 2026-09-30 to approximately **218 words**, within the general IEEE 150–250-word abstract guidance.

The revised abstract now includes the key inferential caveat:

> the primary paired comparison does not remain significant after the declared Holm correction.

This reduces the risk that the abstract is interpreted as claiming confirmatory P2 superiority.

## Title assessment

Current title:

**From QoS Prediction to Decision Validity: Measurement-Supported Counterfactual Replay for Communication-Aware Vehicle Planning**

Keep it.

It communicates:

- the methodological shift from regression to decisions;
- the named MSCR protocol;
- the vehicular communication/planning application.

Do not add "novel", "first", "real-world causal", or "validated autonomous driving" language.

## Contribution wording to preserve

The strongest contribution sentence is:

> We formulate logged field-measured communication planning as a decision-validity problem and separate predictive validity, empirical measurement support, and post-selection measured outcome validity using measurement-supported counterfactual replay.

The strongest conclusion sentence is:

> Field-measured connectivity prediction should influence motion only after its causal horizon, empirical support, and evaluation boundary have been made explicit.

## Submission blockers

Scientific evidence is frozen. Remaining blockers are operational:

- author list/order;
- affiliation;
- corresponding-author institutional email;
- funding/acknowledgments;
- conflicts of interest;
- ORCID and portal metadata;
- related-paper/preprint disclosure;
- final author approval of AI-assisted language-editing disclosure;
- post-edit PDF rebuild and visual QA;
- immutable submission archive/tag.

## TVT policy item added in this pass

The current TVT author instructions allow AI tools for language/grammar modification of author-generated text but require disclosure in the acknowledgments.

This submission pass used AI-assisted editing of existing manuscript wording. After final author review, the manuscript should carry a disclosure consistent with the current journal policy.

Suggested wording:

> OpenAI ChatGPT was used to assist with language editing and clarity of author-prepared manuscript text. The author reviewed the final wording and remains responsible for the scientific content, analysis, interpretation, and conclusions.

## Submission go/no-go

**Scientific go:** yes, under the current narrow methodology/evidence framing.

**Portal go:** after the remaining author metadata, disclosure, rebuild, and visual-QA items are completed.

No new experiment is required to support the current manuscript claims.
