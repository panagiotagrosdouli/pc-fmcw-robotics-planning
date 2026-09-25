# Paper 3 — T-IV cover-letter draft

> **Use conditionally.** This draft is for IEEE Transactions on Intelligent Vehicles (T-IV) only if the journal confirms that the existing public GitHub manuscript history is acceptable under its current public-repository policy. Do not send it before that clarification.

## Suggested subject

Submission of Regular Paper: “When Should a Vehicle Move to Learn the Channel? Decision-Triggered Active Self-Calibration for PC-FMCW-Informed Vehicular Optical Planning”

## Draft

Dear Editor-in-Chief,

Please consider the manuscript entitled **“When Should a Vehicle Move to Learn the Channel? Decision-Triggered Active Self-Calibration for PC-FMCW-Informed Vehicular Optical Planning”** for publication as a Regular Paper in the *IEEE Transactions on Intelligent Vehicles*.

The manuscript studies a safety-constrained intelligent-vehicle planning problem in which uncertainty in a modeled directional optical link can influence motion decisions. The paper compares five planners that share the same candidate generation, causal target prediction, and hard feasibility filters, while differing in how they represent and exploit link-model uncertainty. The central mechanism is a decision-relevance gate that activates information-seeking only when posterior uncertainty changes the downstream trajectory decision.

The evaluation follows a frozen development/confirmatory protocol. A predeclared 27-setting development sweep was completed before 50 untouched confirmatory seeds were opened. The main finding is deliberately bounded: decision-triggered information seeking substantially reduces the regret and probing burden of unconditional active calibration, but the implemented probing policy does not establish a confirmatory advantage over passive Bayesian calibration. The manuscript retains the negative decision-critical result rather than retuning it away after confirmation.

The paper also includes a development-only distance-versus-directional mechanism ablation and two separately scoped measured-data support studies. These are used to bound interpretation rather than to claim direct physical validation of the modeled calibration mechanism. In particular, the measured vehicular visible-light comparison provides essentially null evidence for a meaningful directional predictive gain, and the 5G V2X dataset is treated only as non-optical QoS/pose support.

The contribution is therefore not a generic claim of novelty for dual control, active calibration, communication-aware planning, ISAC-aware planning, or optical communication-aware control. Instead, the manuscript evaluates whether downstream decision disagreement is a useful trigger for active calibration in a controlled vehicular planning architecture with a common hard-safety interface.

This manuscript is not under consideration by another journal. All author metadata, funding/acknowledgement information, conflict-of-interest declarations, and ORCID information will be supplied in the submission system and final source package as required.

Thank you for your consideration.

Sincerely,

Panagiota Grosdouli  
[Affiliation]  
[Institutional email]  
[ORCID]  
[Postal address, if appropriate for the journal correspondence]

## Claim-control notes

- Do not add a claim that C3 is superior to passive C1.
- Do not describe C4 as a real-world oracle; it is model-relative.
- Do not describe zero sampled failures as a safety guarantee.
- Do not describe the V-VLC study as validation of the latent optical calibration model.
- Do not describe CICV5G as optical evidence.
- Do not claim universal first-of-kind status.
