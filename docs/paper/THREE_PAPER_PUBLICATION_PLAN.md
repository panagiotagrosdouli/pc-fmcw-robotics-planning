# Three-Paper Publication Plan — September 2026

## Purpose

The repository supports three scientifically distinct manuscripts. They share a decision-layer architecture but answer different questions with different evidence sources.

The publication order is now:

1. **Paper 2 — field-measured decision validity**
2. **Paper 3 — decision-triggered active calibration**
3. **Paper 1 — PC-FMCW directional predictive-planning mechanism**

This order is based on evidential strength and reviewer risk, not on the chronological order in which the branches were developed.

---

## Paper 2 — From QoS Prediction to Decision Validity

### Proposed title

**From QoS Prediction to Decision Validity: Measurement-Supported Counterfactual Replay for Communication-Aware Vehicle Planning**

### Primary scientific question

When a motion planner uses QoS prediction learned from logged field measurements, what evidence is required before that prediction can support a counterfactual motion decision?

### Distinct contribution

The paper is no longer positioned as another communication-aware planner.

It separates:

1. predictive validity at the motion-decision horizon;
2. empirical training-measurement support;
3. measured post-selection evaluability.

The core evaluation protocol is **measurement-supported counterfactual replay (MSCR)**: candidate actions are restricted to future states that were actually measured later in the held-out route, but the measured future QoS is hidden until after planner selection.

### Primary evidence

- CICV5G field measurements;
- 38 acquisition runs / 43,045 samples in the repository subset;
- whole-run train/calibration/test separation;
- persistence and learned predictors over multiple horizons;
- empirical support diagnostics;
- route-constrained measured replay;
- five grouped split assignments used as dependent robustness checks.

### Main result boundary

P2 has a favorable measured-delay effect relative to P1 on all five grouped assignments, but the primary raw Wilcoxon result does not survive the declared Holm family correction.

Therefore the paper reports effect sizes, bootstrap intervals, and directional robustness, with no confirmatory superiority claim.

P3 consistently reduces unsupported selections but does not show a stable additional QoS benefit.

### Closest prior art explicitly conceded

- communication-aware motion planning;
- field-measured predictive QoS;
- QoS-aware AV trajectory planning;
- online/predictive radio maps;
- uncertainty-aware communication MPC;
- task-aware radio-world-model counterfactual reasoning.

### Current branch / review package

- canonical manuscript changes are now on `main`
- core reframe PR **#39: merged**
- follow-up submission/layout PR **#43: merged**
- manuscript PDF CI: **passed**, including the table-width correction
- CI-generated 7-page PDF: **visually inspected; no remaining clipping/overlap detected**

### Venue fit

**Primary target: IEEE Transactions on Vehicular Technology (TVT).**

Rationale: the paper lies directly at the intersection of vehicular wireless communication and connected/autonomous-vehicle decision algorithms. The current manuscript is 7 IEEE-style pages; current TVT instructions allow up to 14 pages for an initial regular-paper submission.

**Alternative: IEEE Open Journal of Vehicular Technology (OJVT)** if open-access funding and a fully OA route are preferred.

**Additional alternative: IEEE Transactions on Intelligent Vehicles (T-IV)** if the final presentation emphasizes the vehicle-decision methodology more than the communication-prediction methodology.

### Remaining blockers before submission

- final author affiliation/corresponding-author metadata;
- venue-specific template/page-limit check;
- final PDF visual inspection;
- cover letter;
- final release tag/archive;
- author approval of declarations.

No new experiment is required to make the current claims internally consistent.

---

## Paper 3 — When Should a Vehicle Move to Learn the Channel?

### Proposed title

**When Should a Vehicle Move to Learn the Channel? Decision-Triggered Active Self-Calibration for PC-FMCW-Informed Vehicular Optical Planning**

### Primary scientific question

When should the vehicle's own safe motion be used as a physical information-gathering action for learning an uncertain directional link model?

### Distinct contribution

Dual control, informative motion, calibration trajectories, communication-aware motion, optical communication-aware control, and decision-relevant channel learning are all prior art.

The defensible Paper-3 contribution is narrower:

- the information-gathering intervention is the safe vehicle motion candidate itself;
- probing is gated by posterior disagreement over the optimal trajectory and expected decision regret;
- passive C1, unconditional-active C2, decision-triggered C3, and model-relative oracle C4 share one candidate/safety interface;
- the C1/C2/C3 mechanism is evaluated under a frozen confirmatory protocol;
- the negative boundary is retained.

### Critical 2026 literature boundary

RMWorld (arXiv:2608.20126, August 2026) already couples task-aware communication control with value-of-information channel calibration.

Therefore Paper 3 must not claim that decision-relevant channel learning is new in general.

Its non-overlap is the **online safe-motion probing gate** and the frozen passive/unconditional/triggered comparison.

### Primary evidence

- 20 development seeds;
- predeclared 27-setting grid;
- frozen setting before confirmation;
- 50 untouched confirmatory seeds;
- six declared scenarios;
- 1,500 planner/scenario/seed episodes;
- 45,000 timesteps;
- seed-level paired inference;
- distance-only mechanism ablation;
- separate measured V-VLC and CICV5G support studies.

### Main result boundary

C2 learns aggressively but substantially worsens decision regret.

C3 removes most of the C2 regret/probing penalty and correctly suppresses probing in the decision-irrelevant scenario.

However:
- C3 does not establish superiority over passive C1;
- overall descriptive regret favors C1 over C3;
- decision-critical Scenario F is a retained negative result.

The paper therefore owns **suppression of unnecessary probing**, not active-calibration superiority.

### Current branch / review package

- canonical manuscript changes are now on `main`
- PR **#41: merged**
- novelty audit updated against RMWorld
- upstream PC-FMCW citation added
- manuscript PDF CI: **passed**
- CI-generated 9-page PDF: **visually inspected; no clipping/overlap detected**

### Venue fit

**Primary target: IEEE Transactions on Intelligent Vehicles (T-IV).**

Rationale: the scientific object is vehicle decision-making under uncertainty, with communication-model learning embedded in the motion planner. The current manuscript is 9 IEEE-style pages, within T-IV's current suggested 10-page length for Regular Papers; short biographies for all authors are required before submission.

**Alternative: IEEE Transactions on Automation Science and Engineering (T-ASE)** if the paper is positioned more strongly around dual control, active estimation, and calibration methodology.

**Fallback/alternative: OJVT** if the vehicular communication/decision balance is emphasized and open access is desired.

### Remaining blockers before submission

- CI/PDF completion check;
- final author metadata;
- venue-specific formatting;
- cover letter;
- final visual inspection;
- release/archive;
- explicit author approval of the negative-result wording.

No post-confirmatory retuning should be performed to make C3 beat C1.

---

## Paper 1 — Predictive Motion Planning Downstream of PC-FMCW ISCAI

### Proposed title

**Predictive Motion Planning Downstream of a PC-FMCW Laser-Headlamp ISCAI: A Controlled Directional-Connectivity Mechanism Study**

### Primary scientific question

When motion and safety information are held constant, does using predicted future directional target/link geometry improve modeled connectivity relative to reactive/current-geometry scoring?

### Distinct contribution

The paper does not own generic communication-aware planning, optical communication-aware control, QoS-aware AV trajectory optimization, or planning-oriented ISAC.

It owns a narrower controlled mechanism study:

- explicit downstream bridge from the published PC-FMCW laser-headlamp ISCAI architecture;
- common candidate/safety interface;
- P1 current-geometry versus P2 future-geometry scoring;
- frozen V7 confirmation;
- directional-versus-distance-only ablation.

### Primary evidence

- frozen V7 development/confirmatory protocol;
- 50 untouched confirmatory seeds;
- five scenarios per seed;
- seed-level paired inference;
- five communication endpoints;
- 20-seed authorized directional mechanism study.

### Main result boundary

P2 improves all five declared modeled communication endpoints relative to P1 after correction.

P3 is worse than P2.

P4 does not show a supported additional benefit.

The directional P2-P1 outage effect collapses under the distance-only model.

### Physical-model boundary

The link is a **PC-FMCW-informed analytical connectivity surrogate**, not a measured optical channel.

The upstream configuration contains a 193.4-THz carrier/frequency entry while the architecture is described as a laser headlamp. That physical interpretation is unresolved and must not be converted into a blue-light calibration claim.

### Current branch / review package

- canonical manuscript changes are now on `main`
- PR **#40: merged**
- manuscript PDF CI: **passed** after positioning-table correction
- CI-generated 5-page PDF: **visually inspected; no remaining clipping/overlap detected**
- novelty and claim-evidence audits added

### Venue fit

**Primary target: IEEE Open Journal of Vehicular Technology (OJVT)** for the present model-based mechanism version.

Rationale: OJVT explicitly accepts theoretical work in vehicular technology, while the current external-validity boundary should remain transparent. The current manuscript is 5 IEEE-style pages versus the current 14-page initial-submission limit. OJVT requires a registered ORCID.

**Higher-risk alternative: IEEE Transactions on Vehicular Technology (TVT)** if the final manuscript is judged sufficiently strong as a connected/autonomous-vehicle algorithmic contribution.

A future measured optical calibration or hardware experiment would materially strengthen the case for a more demanding optical/vehicular journal submission.

### Remaining blockers before submission

- final author metadata;
- final PDF visual inspection;
- venue formatting;
- cover letter;
- release/archive.

The main scientific limitation is external validity, not statistical execution.

---

## Shared architecture, separate claims

The three papers may share the abstraction:

    state/history
        -> prediction or belief
        -> candidate trajectories
        -> common hard safety
        -> communication evaluation / information value
        -> decision
        -> replan

They must not share evidence as if it answered the same scientific question.

### Evidence separation rule

- Paper 1: controlled PC-FMCW-informed analytical simulation.
- Paper 2: field-measured 5G/V2N2V prediction and route-supported replay.
- Paper 3: modeled directional active-calibration mechanism plus separately scoped support studies.

CICV5G must never be relabeled as PC-FMCW optical validation.

The V-VLC support study must never be relabeled as confirmation of the frozen active-calibration simulator.

---

## Submission-readiness definition

A paper is ready only when all of the following are true:

1. research question and claim boundary are stable;
2. literature novelty has been audited against current work;
3. experimental/statistical unit is correct;
4. multiplicity handling matches the declared family;
5. null and negative results are retained;
6. numerical claims map to frozen machine-readable evidence;
7. bibliography has no missing/unused keys;
8. manuscript PDF builds in clean CI;
9. CI-generated PDF is visually inspected, and re-inspected after any venue-template conversion;
10. author metadata and declarations are confirmed;
11. cover letter and venue-specific source package are prepared;
12. a final immutable release/archive is created.

Scientific retuning after frozen confirmation is not a submission-readiness step.

---

## Immediate submission sequence

The repository-side scientific and manuscript packaging work is complete and merged.

### 1. Paper 2
First external submission candidate. Remaining work is author-specific metadata, final TVT-format conversion/check, release/archive, and portal submission.

### 2. Paper 3
Second external submission candidate. Remaining work is author-specific metadata, T-IV short biographies, final venue-format conversion/check, release/archive, and portal submission.

### 3. Paper 1
Third external submission candidate. Remaining work is author-specific metadata, OJVT ORCID/APC confirmation, final venue-format conversion/check, release/archive, and portal submission. The absence of measured optical calibration remains the principal scientific limitation.

---

## Non-negotiable integrity rules

- Do not invent additional measurements.
- Do not promote model outputs to measured quantities.
- Do not treat repeated split assignments as independent subjects.
- Do not call uncorrected p-values confirmatory when the declared multiplicity family fails.
- Do not retune a frozen confirmatory study to remove a negative result.
- Do not infer author affiliation, funding, conflicts, or institutional approval from repository content.
- Do not claim real-road safety from collision-free simulation.
