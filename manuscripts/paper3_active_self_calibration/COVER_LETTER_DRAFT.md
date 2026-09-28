# Draft Cover Letter — Paper 3

**Target journal:** IEEE Transactions on Intelligent Vehicles

**Manuscript title:** *When Should a Vehicle Move to Learn the Channel? Decision-Triggered Active Self-Calibration for PC-FMCW-Informed Vehicular Optical Planning*

Dear Editor,

Please consider the manuscript *When Should a Vehicle Move to Learn the Channel? Decision-Triggered Active Self-Calibration for PC-FMCW-Informed Vehicular Optical Planning* for publication in IEEE Transactions on Intelligent Vehicles.

The manuscript studies a decision problem that arises when an intelligent vehicle plans with an uncertain communication model: when should a physically safe motion also be used as an information-gathering experiment? Dual control, informative motion, calibration trajectory design, communication-aware planning, and task-aware channel learning are established areas. We therefore position the contribution narrowly around an online motion-probing gate and its experimentally retained limitations.

Five planners share the same candidate lattice, causal target prediction, and hard safety filtering. C1 performs passive Bayesian calibration, C2 rewards information gain unconditionally, and C3 enables information seeking only when posterior channel hypotheses disagree about the downstream trajectory choice and the disagreement carries expected decision regret. The protocol uses a predeclared development grid on separate seeds and freezes the selected setting before 50 untouched confirmatory seeds are opened.

The primary scientific result is deliberately mixed. Unconditional information seeking substantially worsens cumulative decision regret relative to passive calibration, despite improving parameter estimation. Decision-triggered C3 removes most of that penalty and sharply reduces probing. However, C3 does not establish superiority over passive C1, and in the designated decision-critical scenario it probes without improving regret. We retain this negative result rather than retuning after confirmation.

The manuscript has also been updated against the August 2026 RMWorld preprint, which already uses task-aware value-of-information channel calibration. We therefore do not claim the first decision-relevant channel-learning method. The distinction is that our information-gathering intervention is the vehicle's own safe motion candidate and the gate is defined directly from posterior trajectory-ranking disagreement and expected decision regret, evaluated through a frozen passive/unconditional/triggered planner decomposition.

A distance-only mechanism ablation and separately scoped measured V-VLC/5G support studies bound interpretation. The main latent parameters and optical observations remain modeled; no measured PC-FMCW optical self-calibration or real-road safety guarantee is claimed.

The repository provides frozen configurations, immutable evidence references, claim-evidence documentation, literature audits, reproducible analysis, and CI-verified manuscript builds.

Before submission, replace this paragraph with confirmed authorship, affiliation, corresponding-author, funding, conflict-of-interest, and related-work disclosure statements.

Sincerely,

Panagiota Grosdouli  
[CONFIRMED AFFILIATION]  
[CONFIRMED CORRESPONDING EMAIL]
