# Draft Cover Letter — Paper 2

**Target journal:** IEEE Transactions on Vehicular Technology

**Manuscript title:** *From QoS Prediction to Decision Validity: Measurement-Supported Counterfactual Replay for Communication-Aware Vehicle Planning*

Dear Editor,

Please consider the manuscript *From QoS Prediction to Decision Validity: Measurement-Supported Counterfactual Replay for Communication-Aware Vehicle Planning* for publication in IEEE Transactions on Vehicular Technology.

The manuscript addresses a methodological problem at the intersection of vehicular communications and automated-vehicle decision making. Predictive QoS and communication-aware motion planning are established research areas; our contribution is therefore not a new generic connectivity-aware planner. Instead, we ask what evidence is required when a planner uses a QoS predictor learned from logged field measurements to justify a counterfactual vehicle-motion decision.

Using the field-measured CICV5G dataset, we separate three validity questions: whether future QoS adds information beyond a causal persistence baseline at the motion-planning horizon, whether candidate-state predictions are empirically supported by training measurements, and whether selected counterfactual actions can be evaluated using an actual withheld communication measurement rather than model-generated ground truth.

To address the third question, the manuscript introduces measurement-supported counterfactual replay (MSCR). Candidate actions are restricted to future states that were actually recorded later in a held-out drive. The corresponding future measured delay is hidden while the planner selects an action and revealed only afterward for outcome evaluation. This design avoids using the predictor under evaluation as its own counterfactual truth.

The study uses complete acquisition runs for training, calibration, and test separation and performs run-level paired analysis rather than treating correlated timestamps as independent observations. A strong persistence baseline dominates the tested learned alternatives at one step, whereas calibration-gated spatial/context information becomes useful at longer planning horizons. Predictive planning has a favorable measured-delay direction relative to the reactive baseline across all five grouped split assignments. We explicitly report that the primary Wilcoxon result does not survive the declared Holm family correction and therefore do not present it as confirmatory superiority. A support-aware planner consistently reduces unsupported selections but does not provide a stable additional QoS benefit.

The manuscript is accompanied by reproducible code, split manifests, archived result summaries, claim-evidence documentation, and CI-verified manuscript builds. The work does not claim real-road closed-loop intervention, PC-FMCW optical validation, or a universal first-of-kind result.

Before submission, replace this paragraph with confirmed statements regarding authorship, prior publication, conflicts of interest, funding, and corresponding-author contact information. No such metadata are inferred from the repository.

Sincerely,

Panagiota Grosdouli  
[CONFIRMED AFFILIATION]  
[CONFIRMED CORRESPONDING EMAIL]
