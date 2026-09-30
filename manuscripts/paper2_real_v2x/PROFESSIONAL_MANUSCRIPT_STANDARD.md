# Paper 2 — Journal-Grade Manuscript Standard

**Updated:** 2026-09-30

This file is the quality contract for the canonical submission manuscript.

## Required scientific narrative

The manuscript should establish the problem in this order:

1. predictive QoS and communication-aware motion planning are established prior art;
2. field logs only measure outcomes under executed acquisition conditions;
3. a motion decision asks about alternative actions;
4. model-generated action values cannot serve automatically as measured counterfactual truth;
5. repeated field drives can provide finite action support for some physically interpretable actions;
6. training, measured outcome donation, and query roles must be separated;
7. donor reuse creates a second dependence dimension beyond query-run dependence;
8. the resulting evidence can support or reject a decision claim without requiring a new planner architecture.

## Required contribution framing

The contribution is:

- support-bounded matched field replay;
- disjoint train/donor/query acquisition-run roles;
- explicit measured donor provenance;
- two-way query-run × donor-run inference;
- pre-frozen cross-scenario confirmation;
- a transparent negative result for direct pairwise action-margin modeling.

The contribution is not:

- generic communication-aware motion planning;
- generic predictive QoS;
- generic decision-focused learning;
- regret diagnostics;
- a causal speed controller;
- a universal superior planner.

## Required primary results

The paper must visibly report both frozen confirmations.

### W2S

- ORACLE − FAST interval entirely below zero;
- PRED − ORACLE interval entirely above zero;
- PRED − FAST interval crosses zero;
- MARGIN − FAST interval crosses zero.

### Arterial

- ORACLE − FAST interval entirely below zero;
- PRED − ORACLE interval entirely above zero;
- PRED − FAST interval entirely above zero;
- MARGIN − FAST interval entirely above zero.

The arterial degradation result must not be hidden.

## Required statistical language

- acquisition runs are evidence clusters;
- timestamp rows are not independent subjects;
- donor runs are resampled independently of query runs;
- bootstrap replicates are not independent experiments;
- development seed/caliper configurations are descriptive sensitivity analyses;
- the measured oracle is a nondeployable upper-bound diagnostic;
- repeated drives are observational and do not identify causal speed treatment effects.

## Required sections

The submission should contain:

- Introduction;
- Related Work and Non-Overlap;
- Field Data and Evidence Roles;
- Support-Bounded Matched Field Replay;
- Frozen Predictive Rankings;
- Budgeted Decision Policies;
- Statistical Protocol;
- W2S Results;
- Arterial Out-of-Scenario Confirmation;
- Discussion;
- Threats to Validity and Limitations;
- Reproducibility;
- Conclusion;
- verified references.

## Presentation standard

Every central number must be traceable to the compact locked snapshots and/or immutable Actions artifacts.

Negative results remain visible.

The PDF must have:

- no clipped text;
- no label/text overlap;
- no broken glyphs;
- no unresolved references;
- readable tables in two-column IEEE layout.

The current confirmed manuscript is intentionally concise; page count should not be increased merely to resemble a longer paper.

## Submission discipline

Before external submission:

1. canonical PDF build passes;
2. visual QA passes every page;
3. claim-evidence matrix agrees with manuscript and cover letter;
4. author metadata and disclosures are confirmed;
5. supplementary bundle includes frozen protocols, code, tests, compact result snapshots, and provenance;
6. immutable release/tag is created only after author metadata is final.
