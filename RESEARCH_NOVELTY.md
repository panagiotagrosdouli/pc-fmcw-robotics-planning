# Research Novelty and Defensible Contribution Boundary

**Repository:** `panagiotagrosdouli/pc-fmcw-robotics-planning`  
**Assessment date:** 2026-09-30  
**Repository state assessed:** `main` after commit `60fbd567c8354f041d5666077ffa809f79badc02`  
**Purpose:** define the research novelty that is defensible in a paper, separate it from established prior art, and connect each novelty claim to the frozen evidence already present in the repository.

---

## Executive assessment

This repository is scientifically mature enough to support **three distinct papers with bounded claims**.

The publishable novelty is **not** that communication-aware planning, optical-aware motion control, predictive QoS, ISAC-aware planning, informative path planning, or decision-relevant channel learning are new in general. Those areas already have substantial prior art.

The research contribution is narrower and stronger:

1. **Paper 1:** experimentally isolate the value of **future directional connectivity geometry** downstream of a PC-FMCW-informed sensing stack while holding the candidate set and safety interface fixed.
2. **Paper 2:** treat logged field-measured connectivity planning as a **decision-validity problem**, separating predictive validity, empirical-support validity, and measured post-selection outcome validity through measurement-supported counterfactual replay.
3. **Paper 3:** study when a vehicle's own **safe motion should become a channel-learning intervention**, using downstream trajectory disagreement and expected regret to suppress unnecessary active probing.

These are three different research objects with different evidence, inferential units, limitations, and reviewer risks. They should remain separate.

---

# Unifying research thesis

The common research question across the repository is:

> **When should communication information be allowed to change a vehicle's motion decision, and what evidence is required before that decision is scientifically credible?**

The three papers answer different parts of that question:

| Paper | Decision-level question | Main evidence |
|---|---|---|
| Paper 1 | Does future directional link geometry improve the decision relative to current/reactive geometry? | Frozen controlled simulation |
| Paper 2 | When can logged field measurements support a claim about an alternative motion decision? | Held-out field-measured V2X replay |
| Paper 3 | When is it worth moving partly to learn an uncertain link model? | Frozen active-calibration simulation with negative controls |

This decision-level framing is the coherent research program. The novelty is in the **controlled interfaces, evidential discipline, and mechanism isolation**, not in claiming ownership of the broader communication-aware robotics field.

---

# Paper 1 — Predictive directional connectivity downstream of PC-FMCW

## Research gap

Communication-aware motion planning, optical/FSO-aware control, QoS-aware vehicle planning, proactive radio-map planning, and planning-oriented ISAC already exist.

The remaining question is more specific:

> If a PC-FMCW-informed architecture provides target-state information, does using **future candidate-dependent directional connectivity geometry** improve modeled communication outcomes over reactive/current-geometry scoring when both planners share the same motion candidates and safety information?

## Defensible novelty

The research novelty is the **controlled isolation of predictive directional connectivity as a downstream planning mechanism**.

The design makes the P1-versus-P2 comparison interpretable:

- the same target predictor is used;
- the same candidate generator is used;
- the same dynamic-safety information is used;
- P1 uses present/myopic communication geometry;
- P2 uses future trajectory-conditioned communication geometry;
- a directional-versus-distance-only ablation tests whether the observed benefit actually depends on angular link geometry.

This is stronger than showing that a communication-weighted planner can behave differently from a mobility-only planner, because the experiment isolates the predictive geometric mechanism itself.

## Evidence that supports the claim

The frozen V7 confirmation uses 50 untouched confirmatory seeds, with scenario effects aggregated within seed before inference.

P2 improves all five declared modeled communication endpoints relative to P1 after Holm correction:

- lower mean outage probability;
- higher mean SNR;
- higher minimum SNR;
- lower modeled BER;
- higher modeled goodput.

The independent directional mechanism study shows that the P2-P1 outage effect is present with directional attenuation and approximately collapses when the angular term is removed.

## Paper-level contribution statement

> We isolate the downstream value of future directional connectivity prediction in a PC-FMCW-informed vehicular planning stack under a common motion and safety interface, and show through a distance-only ablation that the modeled predictive benefit depends on angular link geometry.

## Claim boundary

This paper does **not** establish:

- measured PC-FMCW optical propagation;
- physical calibration of the directional surrogate;
- real-road closed-loop benefit;
- a general safety guarantee;
- novelty of communication-aware planning itself;
- novelty of optical/FSO-aware control itself;
- superiority of the implemented P3 risk formulation.

The correct positioning is a **controlled algorithmic/mechanism study**.

---

# Paper 2 — Decision validity from logged field measurements

## Research gap

A logged vehicular dataset records communication quality along the trajectory that was actually driven.

A motion planner asks a different question:

> What would communication quality be if a different future state or trajectory were selected?

A learned predictor can return a value for that alternative state, but a model prediction is not automatically a measured counterfactual outcome.

This creates an evidential gap between **prediction accuracy** and **decision-level validity**.

## Defensible novelty

Paper 2 operationalizes a three-layer validity framework:

### 1. Predictive validity

The future-QoS model is tested against a strong causal baseline at the horizon where vehicle motion can still respond.

The repository correctly retains the negative result that one-step persistence is stronger than the tested naive learned predictors, while longer-horizon spatial/context prediction becomes useful.

### 2. Empirical-support validity

Candidate states are audited against the actual training measurements using spatial support diagnostics.

This quantity is intentionally kept separate from residual predictive uncertainty.

### 3. Outcome validity

The selected alternative must have a future field measurement that:

- exists in the held-out trajectory;
- is hidden while the planner scores alternatives;
- is revealed only after selection for evaluation.

The repository calls this protocol **measurement-supported counterfactual replay (MSCR)**.

The key methodological contribution is not a new generic QoS predictor. It is a stricter rule for deciding **what may legitimately count as measured evidence for a planner's counterfactual decision**.

## Why MSCR is scientifically useful

Without a measured-outcome constraint, an offline evaluation can become circular:

```text
learn a communication model
        ↓
select an action using that model
        ↓
evaluate the selected action using the same model as "truth"
```

MSCR changes the last step:

```text
learn a communication model
        ↓
select among route-supported alternatives without seeing their future measurement
        ↓
reveal the withheld field measurement only after selection
```

This does not identify arbitrary off-route causal effects. It instead creates a defensible evidential boundary for logged-data planning studies.

## Evidence that supports the claim

The study uses 38 measured CICV5G runs and 43,045 synchronized samples with whole-run separation.

The main evidence is deliberately mixed rather than overclaimed:

- one-step persistence is a strong baseline;
- longer-horizon prediction becomes useful;
- P2-P1 measured delay is directionally favorable across all five grouped split assignments;
- the primary P2-P1 raw test does not survive the declared Holm family;
- P3 reduces unsupported-selection exposure but does not provide a stable QoS gain;
- grouped split assignments are sensitivity analyses, not independent replications.

That result profile supports a **methodology/evidence paper**, not a generic planner-superiority paper.

## Paper-level contribution statement

> We formulate logged field-measured communication planning as a decision-validity problem and separate predictive validity, empirical measurement support, and post-selection measured outcome validity using measurement-supported counterfactual replay.

## Claim boundary

This paper does **not** establish:

- a first communication-aware planner;
- a first predictive-QoS model;
- a first radio map;
- multiplicity-corrected P2 superiority;
- stable P3-over-P2 QoS improvement;
- physical execution of alternative routes;
- causal effects for arbitrary off-route interventions;
- optical or PC-FMCW validation from the 5G dataset.

A strong wording choice is **"we operationalize"** or **"we introduce an evaluation protocol"**, not an unsupported universal **"first"** claim.

---

# Paper 3 — Decision-triggered active self-calibration through safe motion

## Research gap

Dual control, informative path planning, observability-aware calibration trajectories, active uncertainty reduction, communication-aware motion planning, and value-of-information channel calibration are established research areas.

The August-2026 RMWorld preprint is an especially important contemporary comparison because it already couples downstream task relevance with value-of-information channel calibration and credibility-aware counterfactual rollouts.

Therefore the paper must not claim that **decision-relevant channel learning** is new in general.

The narrower question is:

> Should a vehicle deliberately use one of its own safe motion candidates as an information-gathering intervention only when channel uncertainty can change the downstream trajectory decision?

## Defensible novelty

The distinctive research object is the **online motion-probing gate**:

- the information-gathering action is the vehicle's own safe candidate motion;
- passive, unconditional-active, decision-triggered, and oracle-reference planners share the same candidate and hard-safety machinery;
- the information reward is enabled only when posterior uncertainty produces meaningful trajectory-ranking disagreement and expected decision regret;
- development and confirmation are separated;
- the C1/C2/C3 mechanism decomposition is frozen before untouched confirmatory seeds are opened.

The novelty is not "active learning improves planning." The contribution is a mechanism study of **when active physical probing should be suppressed**.

## Evidence that supports the claim

The frozen confirmation contains 50 confirmatory seeds across six scenarios and five planners.

The central result is deliberately not a superiority claim:

- unconditional active probing C2 substantially worsens decision regret relative to passive C1;
- decision-triggered C3 removes most of the C2 regret and probing penalty;
- C3 does not establish superiority over passive C1;
- Scenario E shows successful suppression of irrelevant probing;
- Scenario F is a retained failure case in which C3 probes but does not outperform passive C1;
- a distance-only ablation collapses the nontrivial probing/regret behavior, tying the mechanism to directional geometry inside the model.

This negative/mixed result is scientifically valuable because it separates **learning the model better** from **making a better decision**.

## Paper-level contribution statement

> We show that downstream trajectory disagreement and expected regret can act as an online guard against unnecessary physical channel-probing motion, while also showing that decision relevance alone is insufficient to make active probing outperform passive Bayesian calibration.

## Relation to RMWorld

RMWorld (Wang, Cheng, and Huan, arXiv:2608.20126, August 2026) already studies task-aware radio-world-model calibration and value-of-information-guided learning.

The non-overlap should remain explicit:

- RMWorld values channel evidence and counterfactual trials according to downstream task risk;
- Paper 3 asks whether a **safe vehicle motion candidate itself** should become the physical information-gathering intervention;
- Paper 3's main result is a boundary result: gating suppresses harmful unconditional probing but does not prove an advantage over passive calibration.

Reference: https://arxiv.org/abs/2608.20126

## Claim boundary

This paper does **not** establish:

- the first decision-relevant channel calibration method;
- the first task-aware communication calibration method;
- active calibration superiority over passive calibration;
- measured optical self-calibration;
- physical identification of PC-FMCW channel parameters;
- a safety guarantee from collision-free modeled trials.

---

# Why the repository is paper-ready

## Scientific maturity

The repository already contains the components normally missing from early research prototypes:

- frozen development-versus-confirmation protocols;
- explicit inferential units rather than timestep pseudo-replication;
- multiplicity correction;
- retained negative results;
- claim-evidence matrices;
- contemporary novelty audits;
- literature boundaries;
- reproducible result archives;
- manuscript sources for all three studies;
- manuscript build instructions;
- venue-specific submission checklists and cover-letter drafts.

## Reproducibility status

At the assessed `main` state:

- repository CI completed successfully;
- the reproducible **Submission Bundles** workflow completed successfully;
- the workflow produced artifact `submission-bundles-2026-09-28`;
- the artifact is tied to commit `60fbd567c8354f041d5666077ffa809f79badc02`.

This is sufficient to treat the repository as a reproducible manuscript package rather than only source code.

---

# What is still missing before actual journal submission

The remaining blockers are mainly publication operations rather than new scientific experiments:

1. final author list and ordering;
2. verified affiliations and institutional email;
3. funding/acknowledgement text;
4. conflict-of-interest declarations;
5. ORCID and author-biography requirements where applicable;
6. final venue-template conversion and visual QA;
7. immutable release/source/supplement archive;
8. related-work/preprint disclosure checks for the selected venue.

For Paper 3 specifically, the documented T-IV public-repository policy issue must be resolved before treating that venue as portal-ready.

No new experiment should be added merely to manufacture significance or turn a bounded result into a stronger claim.

---

# Publication interpretation

## Paper 1

**Publishable as:** a controlled PC-FMCW-informed directional-connectivity mechanism paper.  
**Main weakness:** external validity remains model/simulation based.

## Paper 2

**Publishable as:** a field-data methodology and decision-validity paper.  
**Main strength:** it makes an underappreciated logged-data counterfactual-evaluation problem explicit and ties every reported planner outcome to an evidential support rule.  
**Main weakness:** the primary planner effect is modest and not multiplicity-confirmatory, so the methodology must remain the center of the paper.

## Paper 3

**Publishable as:** a decision-triggered active-calibration mechanism and boundary paper.  
**Main strength:** the frozen negative/mixed results make a credible scientific point about the difference between information gain and downstream decision value.  
**Main weakness:** the active-calibration evidence remains modeled, and RMWorld narrows the permissible novelty claim.

---

# Recommended novelty language for abstracts and cover letters

Use verbs such as:

- **isolate**
- **operationalize**
- **formulate**
- **evaluate**
- **separate**
- **audit**
- **demonstrate under the tested model**
- **show that the effect depends on**
- **identify a failure boundary**

Avoid unsupported formulations such as:

- "the first communication-aware planner";
- "the first decision-relevant channel-learning method";
- "proves safety";
- "physically validates PC-FMCW";
- "active calibration outperforms passive calibration";
- "real-world counterfactual ground truth" for off-route actions.

---

# Bottom line

The repository is no longer just a robotics implementation around PC-FMCW. Its defensible research contribution is a **decision-validity program for communication-aware vehicle motion**:

- Paper 1 asks whether future directional communication geometry matters;
- Paper 2 asks when field measurements can legitimately validate the resulting decision;
- Paper 3 asks when motion itself should be used to learn the uncertain communication model.

That is a coherent and publishable research arc, provided the three papers preserve their present evidence boundaries and do not broaden their novelty claims beyond what the frozen experiments and current literature support.
