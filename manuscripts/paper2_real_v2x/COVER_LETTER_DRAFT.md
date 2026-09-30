# Draft Cover Letter — Paper 2

**Target journal:** IEEE Transactions on Vehicular Technology

**Manuscript title:** *From QoS Prediction to Measured Decision Validity: Support-Bounded Matched Field Replay for Vehicular Speed Decisions*

Dear Editor,

Please consider the manuscript *From QoS Prediction to Measured Decision Validity: Support-Bounded Matched Field Replay for Vehicular Speed Decisions* for publication in IEEE Transactions on Vehicular Technology.

The manuscript addresses a methodological problem at the intersection of vehicular communications and automated-vehicle decision making. Predictive QoS, communication-aware motion planning, decision-focused learning, and regret-based policy diagnostics are established research areas. Our contribution is therefore not another generic connectivity-aware planner or a claim that a new learning loss universally improves motion decisions. Instead, we ask what measured evidence is required before a QoS predictor learned from logged field measurements can justify a different vehicle-motion action.

We introduce a support-bounded matched field replay protocol using repeated CICV5G acquisition runs. Complete drives are assigned disjoint roles for predictor training, measured action-outcome donation, and decision queries. At a supported query location, a candidate speed action is evaluated only when separate donor drives contain measurements under the same communication/action context within a frozen spatial caliper. Donor outcomes are hidden while deployable policies rank actions and are revealed only for post-selection evaluation.

The primary confirmation uses W2S measurements and a 30/50-km/h action pair. A protocol-fixed two-way acquisition-run bootstrap resamples both query and donor drives. It shows support-bounded measured oracle headroom of -4.177 ms relative to always selecting 50 km/h, with 95% interval [-13.659, -2.137] ms. The frozen absolute-QoS ranking retains +2.704 ms regret relative to this upper-bound diagnostic, with interval [+1.457, +5.832] ms. Its comparison with the FAST baseline is -1.473 ms with interval [-8.167, +0.657] ms, so we do not claim confirmatory predictive-policy superiority.

A separately pre-frozen arterial-road n8 confirmation uses a different 50/80-km/h action pair. Measured oracle headroom is again present (-0.590 ms, 95% interval [-1.431, -0.250] ms), but the same frozen predictive intervention is now worse than the FAST baseline (+0.156 ms, 95% interval [+0.038, +0.258] ms). A separately frozen pairwise action-margin model also fails to close the measured decision gap. These cross-scenario results support the manuscript's central conclusion: useful predictive structure does not automatically constitute reliable motion-decision evidence.

The statistical design treats acquisition runs, not timestamps, as the relevant evidence clusters and explicitly accounts for reuse of donor drives. Negative and non-confirmatory results are retained. The manuscript does not claim causal speed effects, arbitrary field counterfactual ground truth, a deployable measured oracle, closed-loop autonomous-vehicle validation, or novelty for generic decision-focused learning.

The work is accompanied by reproducible code, frozen protocol documents, donor-outcome provenance, immutable workflow artifacts, claim-evidence documentation, and CI-verified manuscript builds.

Before submission, replace this paragraph with confirmed statements regarding authorship, prior publication, conflicts of interest, funding, AI-assisted language-editing disclosure, and corresponding-author contact information. No such metadata are inferred from the repository.

Sincerely,

Panagiota Grosdouli  
[CONFIRMED AFFILIATION]  
[CONFIRMED CORRESPONDING EMAIL]
