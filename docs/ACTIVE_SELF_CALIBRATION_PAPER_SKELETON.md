# When Should a Vehicle Move to Learn the Channel?
## Decision-Triggered Active Self-Calibration for Vehicular Optical Planning

> Manuscript status: post-confirmatory manuscript draft; frozen confirmatory experiment completed. Numerical claims below are restricted to the frozen synthetic study and the separately scoped measured-data support studies.

## 1. Introduction

Directional optical planning depends on parameters that may be uncertain or mismatched. Ordinary communication-aware motion planning assumes a usable link model and then optimizes motion. This work instead asks when the vehicle should deliberately choose a safe motion whose communication observation is useful for resolving uncertainty that matters to the next control decision.

The investigated principle is: **motion is simultaneously a control action and, only when decision-relevant, an experiment for learning the communication model.**

The implemented contributions are:
1. a small interpretable latent PC-FMCW-informed directional link model;
2. causal Bayesian online parameter belief;
3. a decision-relevance gate separating parameter uncertainty from control-relevant uncertainty;
4. a safe information-seeking planner and C0-C4 ablation family;
5. a prospective paired-seed protocol centered on downstream decision regret.

No claim is made that dual control, active learning, communication-aware planning, optical planning, or their broad combination is universally first-of-kind.

## 2. Related Work

This study sits at the intersection of four established lines of work, and its contribution is deliberately framed more narrowly than any of them.

**Communication-aware motion planning.** Communication quality has long been incorporated into robot motion decisions; for example, Ghaffarkhah and Mostofi formalized communication-aware motion planning in mobile networks (IEEE Transactions on Automatic Control, 2011, DOI `10.1109/TAC.2011.2164033`). The present study therefore does not claim novelty for using communication state in planning.

**Informative motion and active calibration.** Robotics literature also shows that motion can be chosen to improve information quality rather than only to reach a task goal. Informative path planning has coupled robot trajectories to expected information gain, including active field mapping under localization uncertainty (ICRA 2020, DOI `10.1109/ICRA40945.2020.9197034`). Observability-aware LiDAR-IMU calibration uses information-theoretic data selection to retain informative motion segments and explicitly handles non-identifiable directions (IEEE Transactions on Robotics, 2022, DOI `10.1109/TRO.2022.3174476`). More recently, optimal-experiment-design trajectory planning has been used to generate calibration motions for robotic camera calibration (IEEE Transactions on Automation Science and Engineering, 2025, DOI `10.1109/TASE.2025.3632764`). These works establish the broader principle that robot motion can be an experiment for parameter estimation.

**Communication/ISAC coupled to planning.** Planning-Oriented Integrated Sensing and Communication (PISAC) couples ISAC resource allocation, sensing uncertainty and vehicle motion planning (ICC 2026; DOI `10.1109/ICC59461.2026.11587040`; preprint `arXiv:2510.23021`). In optical robotics, communication-driven NMPC has incorporated free-space-optical link/alignment requirements directly into multirotor motion control (IEEE SMC 2025, DOI `10.1109/SMC58881.2025.11343117`). These studies rule out broad claims that ISAC-to-planning coupling or optical communication-aware control are themselves new.

**Positioning of this study.** The narrower question here is not whether motion can gather information, whether communication can influence motion, or whether calibration trajectories can be planned. It is whether a safe vehicular planner should deliberately excite a **modeled directional optical link** only when posterior uncertainty changes the downstream trajectory decision. The experiment therefore separates passive Bayesian calibration (C1), unconditional information seeking (C2), decision-triggered information seeking (C3), and a model-relative oracle (C4), with a frozen paired-seed protocol. The contribution is this decision-relevance test and its negative boundary: the implemented gate strongly suppresses unnecessary probing, but the frozen study does not establish superiority over passive calibration.

No priority or universal first-of-kind claim is made. The literature set above is used for positioning, not as a systematic novelty review.

## 3. PC-FMCW-Informed Planning Model

The robotics extension begins after a target state/history is available from the upstream sensing/tracking chain. At planning step (k), the ego state is represented by position, yaw and speed, while a causal target predictor supplies a common future target-position sequence. For candidate ego trajectory (	au_i), the planner evaluates the future relative geometry between the candidate ego states and the predicted target states.

A PC-FMCW-informed analytical link surrogate maps this relative geometry to modeled communication quantities including SNR, outage probability, BER and goodput. These quantities are simulation-model outputs; they are not measured PC-FMCW channel calibration.

Candidate trajectories are generated by the common vehicle model and then passed through the same hard feasibility filters for every planner: road and speed limits, static-obstacle clearance, time-aligned dynamic-target clearance, and terminal stop-viability checks. Information gain or calibration value is evaluated **only after** this common hard-safety filter. Consequently, a candidate cannot become feasible merely because it is informative.

Planning is receding-horizon and causal. Each planner selects a candidate, executes only its first control action, receives the resulting communication observation, updates its belief if applicable, and replans. Future simulator truth is unavailable to C0-C3; C4 receives the true latent link parameters only for the declared model-relative connectivity reference.

## 4. Latent Communication-Model Uncertainty

The modeled latent parameter vector is

[
phi=[alpha_{loss},delta_{beam},k_{angular}].
]

Here, (alpha_{loss}) scales the distance-loss exponent, (delta_{beam}) is a modeled boresight angular offset, and (k_{angular}) scales Gaussian angular attenuation. The nominal vector is ([1,0,1]). Three objects are kept distinct throughout the experiment: simulator truth, the nominal model, and the planner belief. C0-C3 never receive simulator truth.

The directional model uses both distance and angular attenuation. A separate distance-only mechanism ablation removes angular attenuation while preserving the rest of the planner and safety machinery. In that ablation, (delta_{beam}) and (k_{angular}) are intentionally non-identifiable from link observations; only the remaining distance-dependent degree of freedom can be learned.

The latent family is intentionally small and interpretable. It is not claimed to be a physically complete vehicular optical-channel model. Low estimation error inside this family therefore does not imply physical model validity, and posterior ambiguity is retained rather than forced into convergence when geometry is uninformative.

## 5. Passive and Active Calibration

The communication observation is modeled SNR corrupted by declared Gaussian observation noise. C1-C3 maintain a discrete Bayesian belief over the latent parameter hypotheses. The implementation uses a small (3	imes3	imes3) grid spanning distance-loss scaling, beam offset and angular attenuation scaling. After an action is executed and its SNR observation becomes available, the posterior is updated with a Gaussian likelihood. The update is therefore causal: an observation generated by an action cannot influence selection of that same action.

For a candidate trajectory, the information score is the short-horizon predictive proxy

[
G(	au)=sum_j rac{1}{2}logleft(1+
rac{mathrm{Var}_{phi}[mu_z(phi,	au,j)]}{sigma_z^2}ight),
]

where (mu_z) is the modeled SNR prediction under latent hypothesis (phi) and (sigma_z) is the observation-noise standard deviation. This score is deliberately described as a predictive-information approximation, not exact mutual information and not a physically calibrated Fisher-information matrix.

Parameter uncertainty and decision uncertainty are treated separately. A posterior can remain broad while all plausible hypotheses prefer the same safe trajectory; in that case parameter learning may have little downstream value. Conversely, a smaller region of uncertainty can matter if it changes which candidate is optimal.

## 6. Decision-Triggered Dual-Control Planner

Let (J(	au,phi)) denote the task-plus-connectivity cost of candidate (	au) under latent hypothesis (phi), and let (ar{	au}) be the candidate minimizing posterior-expected cost. Two diagnostics quantify whether uncertainty is decision-relevant:

[
U_D=P_{phi}[argmin_{	au}J(	au,phi)
ear{	au}]
]

and

[
R_D=E_{phi}[J(ar{	au},phi)-min_{	au}J(	au,phi)].
]

C3 enables the information reward only when both the decision-disagreement probability and expected decision regret exceed their declared gates. When active, candidate scoring combines posterior-expected task/connectivity cost, probing-motion cost, and the decision-relevance-weighted information proxy. Hard safety is still evaluated first.

The planner family isolates the mechanism:

- **C0 — nominal/no calibration:** fixed nominal latent parameters and no Bayesian update.
- **C1 — passive calibration:** posterior-expected task/connectivity cost with causal belief updates, but no information reward.
- **C2 — unconditional active calibration:** the same Bayesian belief as C1, with information-seeking enabled whenever safe candidates are scored.
- **C3 — decision-triggered active self-calibration:** information-seeking is gated by downstream decision disagreement and expected regret.
- **C4 — oracle-parameter reference:** true simulator latent parameters are used only for model-relative connectivity scoring; C4 is non-deployable and receives no privileged safety information.

This decomposition is essential to interpretation. C2-C1 isolates the cost of unconditional information seeking, C3-C2 tests whether decision relevance suppresses that cost, and C3-C4 reports the remaining model-relative oracle gap. C1-C3 was not a predeclared primary confirmatory comparison, so descriptive differences between them are not converted into a post-hoc superiority claim.

## 7. Experimental Protocol

Six scenarios (A-F) were evaluated. Development used seeds `31000..31019`; the predeclared grid contained 27 settings. All 27 settings and the common C0/C1/C4 baseline completed before selection. The deterministic selection rule chose `dev_t010_i025_p020`, corresponding to `decision_threshold=0.10`, `information_weight=0.25`, `probe_weight=0.20`, and `min_expected_regret=0`.

The protocol was frozen at `2026-09-25T07:28:10.141950+00:00`. Confirmatory execution began only afterward and used untouched seeds `32000..32049`. The confirmatory artifact contains 1,500 episode rows (50 seeds x 6 scenarios x 5 planners) and 45,000 timestep rows with no duplicate planner/scenario/seed episodes.

The independent inferential unit is the seed after averaging the six declared scenarios within seed. Timesteps are diagnostic only. The predeclared primary comparisons are C0-C1, C1-C2, C2-C3 and C3-C4. Each comparison family reports deterministic paired bootstrap 95% intervals, paired Wilcoxon tests, paired effect sizes and Holm adjustment across the seven declared metrics.

Primary outcome: cumulative decision regret relative to the oracle-parameter candidate choice. Secondary outcomes: oracle agreement, probing burden, parameter error, communication metrics, progress and safety diagnostics.

## 8. Frozen Confirmatory Results

### 8.1 Decision quality

Across 300 scenario-seed episodes per planner, mean cumulative decision regret was:

| Planner | Mean cumulative decision regret |
| --- | ---: |
| C0 | 0.006432 |
| C1 | 0.004786 |
| C2 | 0.088076 |
| C3 | 0.005865 |
| C4 | 0.000000 |

Passive calibration reduced regret relative to C0 by a mean seed-level delta of `-0.001646` (95% bootstrap CI `[-0.003079, -0.000578]`). The raw Wilcoxon p-value was `0.00961`, while the predeclared Holm-adjusted p-value within the seven-metric C1-C0 family was `0.05765`; therefore this comparison is not presented as multiplicity-adjusted confirmatory significance.

Unconditional information seeking was substantially worse than passive calibration: C2-C1 regret delta `+0.083290` (95% CI `[0.073641, 0.093720]`, Holm-adjusted `p=1.24e-14`).

Decision-triggering largely removed that penalty: C3-C2 regret delta `-0.082211` (95% CI `[-0.092695, -0.072358]`, Holm-adjusted `p=1.24e-14`).

C3 retained a nonzero gap to the model-relative oracle. The reported C4-C3 delta is `-0.005865` (95% CI `[-0.007628, -0.004242]`, Holm-adjusted `p=1.24e-6`). C4 is only an oracle-parameter reference inside the declared analytical model and is not evidence of real-world optimality.

C1 and C3 were not a predeclared primary pair, so no post-hoc superiority claim is made between them. Descriptively, C1 had lower overall mean regret (`0.004786`) than C3 (`0.005865`).

### 8.2 Calibration and information acquisition

Mean probe fraction was `0` for C0/C1/C4, `0.038111` for C2 and `0.000667` for C3. Relative to C2, C3 reduced probe fraction by `0.037444` (C3-C2; 95% CI `[-0.039778, -0.035333]`, Holm-adjusted `p=3.10e-9`) and cumulative probe cost by `0.020332` (95% CI `[-0.025588, -0.015622]`, Holm-adjusted `p=3.10e-9`).

C1 substantially reduced normalized parameter error relative to C0 (`-0.393495`, 95% CI `[-0.423885, -0.363191]`, Holm-adjusted `p=1.24e-14`). C2 reduced parameter error further relative to C1 (`-0.053484`, 95% CI `[-0.079561, -0.026464]`, Holm-adjusted `p=1.30e-4`) even though its decision regret was much worse. Conversely, C3 had higher parameter error than C2 by `+0.046795` (95% CI `[0.020566, 0.072209]`, Holm-adjusted `p=4.24e-4`) while achieving far lower regret.

This separation is central to the mechanism result: more parameter learning did not imply better downstream decisions.

### 8.3 Safety, mobility and communication outcomes

All planners had zero collision episodes. Across all 1,500 confirmatory episodes there were also zero no-candidate steps and zero static-clearance-violation steps. The minimum recorded static-obstacle clearance was approximately `1.500003 m`.

Mean progress was nearly identical across planners (approximately `24.76 m` overall). C2 gained only `0.019755 m` relative to C1 while incurring much greater regret and probing burden. Mean outage probability increased by `0.005105` for C2 relative to C1 (95% CI `[0.002973, 0.007258]`, Holm-adjusted `p=1.91e-5`) and decreased by `0.006654` for C3 relative to C2 (95% CI `[-0.008331, -0.005156]`, Holm-adjusted `p=1.07e-13`).

C4 should not be read as an outage-minimizing controller: it is a true-parameter reference using the same mixed task/connectivity objective and hard-safety machinery.

## 9. Decision-Relevance Mechanism

Scenario E was designed to contain parameter uncertainty that should not matter to the motion decision. C3 behaved as intended there: mean probe fraction `0` and mean decision regret `0`. C2 still probed (`0.004667` mean probe fraction) and accumulated `0.008610` mean regret.

Scenario F was the deliberately decision-critical case. Here C3 did activate probing (`0.003333` mean probe fraction), but the intervention did **not** improve the primary decision metric over passive calibration. Mean F regret was:
- C0: `0.031984`
- C1: `0.028037`
- C2: `0.140882`
- C3: `0.034416`
- C4: `0`

Thus the frozen experiment supports the value of suppressing unconditional information seeking, but it does not support a claim that the implemented decision-triggered probing strategy improves over passive calibration in the canonical F case. This null/negative result is retained as part of the scientific conclusion rather than retuned away after confirmation.

## 10. Real-Data Support Studies and Claim Boundaries

### 10.1 Measured vehicular VLC path loss

A separate measured V-VLC study used the public `bugratu/ML_VVLC` dataset pinned to upstream commit `bdf38f402d67f9f1c48daea074730136cb6bef7e`. On the held-out spatial test set, distance-only MAE was `5.587261 dB` and the directional model MAE was `5.580011 dB`. The group-paired directional-minus-distance-only absolute-error effect was `-0.005031 dB`, with 95% bootstrap CI `[-0.019734, 0.010134] dB` and Wilcoxon `p=0.375269`.

This is effectively null evidence for a meaningful directional predictive gain in that measured dataset. The data support measured vehicular optical path-loss analysis; they do not provide direct PC-FMCW waveform calibration or closed-loop planning validation.

### 10.2 Measured CICV5G V2X support/replay study

The separate CICV5G track used 38 measured W2S vehicle runs containing 43,045 samples. In the basic held-out support split, persistence was the best tested delay predictor with MAE `5.576288 ms`. Across five grouped split assignments, route/horizon fusion reduced delay MAE relative to persistence at horizons 20/50/100 steps in 5/5 splits, with mean deltas approximately `-1.4597`, `-2.5060`, and `-2.6223 ms`, respectively.

In the offline route-replay analysis, P2 reduced measured delay relative to P1 in 5/5 split assignments (mean split effect approximately `-0.501375 ms`) with a small positive mobility-deviation effect (approximately `+0.008452`). The repeated split assignments reuse the same finite measured drives and are descriptive robustness configurations, not independent experimental replicates.

These results support measured 5G V2X QoS/pose transfer and offline replay analysis. They are not optical calibration and not closed-loop real-vehicle validation.

## 11. Directional vs Distance-Only Mechanism Ablation

A standalone **development-only** mechanism ablation removed angular attenuation while preserving the same planner family, candidate generation, Bayesian update machinery, hard-safety constraints, frozen-selected hyperparameters, and development seeds `31000..31019`. Its manifest explicitly labels the run `development_mechanism_ablation_not_primary_confirmatory_evidence`; it is not part of the frozen confirmatory evidence.

Under the distance-only link model, all five planners had effectively zero cumulative decision regret (C0/C4 exactly `0`; C1/C2/C3 at numerical roundoff, approximately `1.85e-18`) and all planners had probe fraction `0`. Progress and mean outage were identical across C0-C4. All 600 episode rows were collision-free and had zero no-candidate steps.

C1, C2 and C3 were behaviorally identical in this ablation. Relative to C0, C1 reduced normalized parameter error by `-0.160375` (95% CI `[-0.183166, -0.134407]`, Holm-adjusted `p=1.34e-5`), reflecting learning of the remaining distance-loss degree of freedom. C2-C1 and C3-C2 differences were exactly zero for regret, probing, progress, outage, and parameter error.

Scenario-level results showed the same collapse: regret and probe fraction were zero in A-F for every planner. The angular-bias and combined-ambiguity scenarios therefore cease to induce distinct planning behavior when angular attenuation is removed. The angular latent parameters `delta_beam_rad` and `k_angular` are intentionally non-identifiable under this model, while `alpha_loss` can still be updated from distance-dependent observations.

This ablation supports a **mechanism-specific**, not confirmatory, conclusion: the nontrivial active-calibration behavior observed in the directional study depends on directional geometry. Removing that geometry eliminates both decision-relevant disagreement and the incentive to probe under the implemented action set and information proxy. It does not establish physical identifiability or real-world optical validity.

## 12. Limitations

The latent parameters and communication observations are modeled; no real optical calibration is claimed. The information score is approximate, parameter identifiability depends on geometry/action richness, the candidate lattice limits the experiment set, and simulator oracle regret is model-relative.

The decision trigger succeeded at avoiding most unnecessary probing and strongly improved over unconditional information seeking, but it did not beat passive calibration in the decision-critical F scenario. This indicates that detecting decision relevance is not sufficient by itself: the available probing actions, short-horizon information proxy, or probe-value scaling may still be inadequate for turning information into better decisions.

The V-VLC directional comparison was null, and the CICV5G evidence concerns a different radio modality. Neither measured-data track should be used to imply direct physical validation of the synthetic latent optical calibration mechanism.

## 13. Conclusion

The frozen study provides **partial support** for the proposed decision-triggered active-calibration principle.

C3 dramatically reduced the regret and probing burden produced by unconditional information seeking (C2), while preserving hard safety. It also correctly suppressed probing in the decision-irrelevant E scenario. However, the study does not establish superiority over passive calibration: overall C1 had descriptively lower mean regret than C3, and in the canonical decision-critical F scenario C3 probed but did not improve regret over C1.

The strongest supported conclusion is therefore narrower: **decision relevance is useful for preventing unnecessary active calibration, but the implemented probing policy does not yet demonstrate a confirmatory advantage over passive Bayesian calibration.** This negative boundary is part of the result.
