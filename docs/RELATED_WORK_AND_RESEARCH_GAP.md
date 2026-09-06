# Related Work, Research Gap, and Proposed Paper Idea

## Quick explanation for a reader

This repository is intended to support a possible research paper on **predictive connectivity-aware motion planning for autonomous vehicles using PC-FMCW-informed sensing and communication information**.

The paper idea is not to invent communication-aware motion planning or PC-FMCW itself. Instead, the idea is to connect the two in a specific closed-loop decision problem:

> **Can an autonomous vehicle make better motion decisions if it predicts how each possible future trajectory will affect its future communication link, instead of reacting only to the link quality observed now?**

The planned study uses PC-FMCW-informed target tracking/prediction, evaluates alternative ego-vehicle trajectories, predicts the future communication quality associated with each trajectory, and lets the planner use that information when selecting the next motion.

---

## What we propose to do

At every planning step, the system will:

```text
1. Observe / track the target using PC-FMCW-informed sensing information
                       |
                       v
2. Predict the target's future motion
                       |
                       v
3. Generate several feasible future trajectories for the ego vehicle
                       |
                       v
4. For every candidate trajectory, calculate the future ego-target geometry
                       |
                       v
5. Predict the communication quality along that candidate trajectory
   (modeled SNR / outage / BER / goodput)
                       |
                       v
6. Reject trajectories violating vehicle, road, obstacle, or target-safety constraints
                       |
                       v
7. Score the remaining trajectories using mobility + connectivity objectives
                       |
                       v
8. Select a trajectory, execute only its first control action, observe again, and replan
```

Therefore the vehicle is not simply asking:

```text
How good is my communication link now?
```

It is asking:

```text
If I choose trajectory A, what is my predicted future link?
If I choose trajectory B, what is my predicted future link?
If I choose trajectory C, what is my predicted future link?

Which safe trajectory gives the best mobility/connectivity trade-off?
```

That is the central idea of the proposed paper.

---

## Main paper idea

A possible working title is:

> **PC-FMCW-Informed Predictive Connectivity-Aware Motion Planning for Autonomous Vehicles**

A more question-driven title could be:

> **Does Future Link Prediction Improve Connectivity-Aware Motion Planning? A PC-FMCW-Informed Autonomous-Vehicle Study**

The main research question is:

> **Does forecasting the future communication state induced by alternative ego trajectories provide a measurable advantage over reacting to the current communication state?**

The paper would answer this using a controlled closed-loop simulation in which the planners are deliberately constructed to isolate the effect of future connectivity prediction.

---

## The planners we compare

### P0 — Mobility-only baseline

P0 plans vehicle motion without optimizing communication quality.

Purpose:

```text
What happens if connectivity is ignored?
```

### P1 — Reactive connectivity-aware planner

P1 considers communication quality, but does so myopically/reactively.

Conceptually:

```text
current link state
      -> motion decision
```

Purpose:

```text
Is reacting to current connectivity enough?
```

### P2 — Predictive connectivity-aware planner — main proposed method

P2 predicts the future target motion and evaluates future communication quality along every candidate ego trajectory.

Conceptually:

```text
predicted target motion
        +
candidate ego trajectory
        |
        v
predicted future relative geometry
        |
        v
predicted future communication quality
        |
        v
motion decision
```

Purpose:

```text
Does future connectivity prediction improve the decision compared with P1?
```

**P1 versus P2 is the central experiment of the paper.**

### P3 — Risk-aware predictive planner

P3 extends P2 by propagating uncertainty in the target prediction and using a risk-sensitive connectivity score.

Purpose:

```text
Does explicitly modeling prediction uncertainty provide additional benefit beyond P2?
```

### P4 — Oracle connectivity reference

P4 is not a deployable planner. It is allowed to use simulator ground-truth future target motion only when forecasting connectivity. It does not receive an oracle safety advantage.

Purpose:

```text
How much additional performance would perfect future connectivity information provide?
```

This gives an approximate upper reference against which P2 can be interpreted.

---

## What would be new in our paper

The proposed contribution is **not** any individual component in isolation.

Communication-aware motion planning already exists. Predictive/network-aware planning already exists. Optical communication-aware MPC exists. PC-FMCW sensing and communication exist. Recent ISAC work also connects sensing/communication design with vehicle planning.

Our proposed contribution is the specific closed-loop combination:

```text
PC-FMCW-informed sensing / tracking
              +
target-motion prediction
              +
candidate ego trajectories
              +
trajectory-conditioned future communication prediction
              +
safety-constrained closed-loop motion selection
              +
controlled reactive-vs-predictive evaluation
```

In other words, we investigate whether **PC-FMCW-informed future information can be converted into an actual motion-planning advantage**.

The novelty should therefore be presented as the combination, system coupling, and controlled scientific question—not as the invention of communication-aware planning itself.

---

## Why this is different from simply doing PC-FMCW

Existing PC-FMCW research primarily establishes the physical-layer capability to combine sensing and communication.

A simplified representation is:

```text
PC-FMCW waveform/system
       |
       +----> sensing / ranging / tracking
       |
       +----> communication
```

For example, experimental PC-FMCW work has demonstrated joint sensing and communication properties and practical automotive-radar relevance. Optical PC-FMCW work has also proposed integrated sensing, communication, and illumination for intelligent vehicles.

Our robotics paper starts **after** this upstream capability:

```text
PC-FMCW-informed sensing
        |
        v
target state / target prediction
        |
        v
What should the autonomous vehicle DO with this information?
        |
        v
motion planning
```

The paper therefore moves the problem from the PHY/sensing layer into the autonomous decision layer.

---

## Why this is different from ordinary communication-aware planning

Communication-aware robotics is already an established field. Prior work has used wireless connectivity constraints, spatial channel maps, time-varying communication maps, and predicted communication conditions when planning robot trajectories.

Therefore we cannot claim:

> "We are the first to use communication information in robot motion planning."

Nor can we claim:

> "We are the first to predict future connectivity during planning."

Our narrower distinction is that the predicted communication state is conditioned jointly on:

```text
predicted motion of the tracked target
                 +
future candidate motion of the ego vehicle
```

so each possible ego trajectory produces a different predicted future relative geometry and therefore a different modeled future PC-FMCW link.

---

## Closely related work

### 1. Communication-aware motion planning

Ghaffarkhah and Mostofi and related communication-aware robotics literature established that robot trajectories can account for wireless communication quality and connectivity.

Related work has also considered time-dependent spatial communication-quality maps for network-aware planning.

**What it establishes:**

```text
communication information -> robot motion planning
```

**What we investigate instead:**

```text
PC-FMCW-informed target prediction
        + candidate ego motion
        -> trajectory-conditioned future link prediction
        -> closed-loop ego-motion selection
```

Thus, communication-aware planning itself is not our novelty.

---

### 2. Planning-Oriented Integrated Sensing and Communication (PISAC)

A particularly important nearby work is:

**X. Jin et al., “Planning Oriented Integrated Sensing and Communication,” IEEE ICC 2026.**

DOI: `10.1109/ICC59461.2026.11587040`

Preprint: <https://arxiv.org/abs/2510.23021>

This work connects ISAC physical-layer resource allocation with autonomous-vehicle planning. Its simplified coupling is:

```text
ISAC resource allocation
        -> sensing uncertainty
        -> obstacle representation / safe navigable space
        -> motion planning
```

This is important because it means we cannot claim that ISAC and vehicle planning have never been connected.

**Our direction is different:**

```text
PC-FMCW-informed target state/prediction
        -> candidate-dependent future communication forecast
        -> ego-motion selection
```

PISAC asks, roughly:

```text
How should ISAC resources be adapted to improve information useful for planning?
```

Our paper asks:

```text
How should vehicle motion be adapted when future communication quality can be predicted?
```

---

### 3. Free-Space Optical communication-driven NMPC

Another close work is:

**G. Silano, D. Bonilla Licea, H. El Hammouti, and M. Saska, “Free-Space Optical Communication-Driven NMPC Framework for Multi-Rotor Aerial Vehicles in Structured Inspection Scenarios,” IEEE SMC 2025.**

DOI: `10.1109/SMC58881.2025.11343117`

Preprint: <https://arxiv.org/abs/2507.04443>

This work incorporates FSO connectivity/alignment requirements into nonlinear model predictive control for aerial vehicles.

Simplified:

```text
FSO link/alignment constraints
        -> NMPC
        -> communication-aware motion
```

It demonstrates that optical communication-aware MPC/NMPC is not new in general.

Our proposed study differs because its core question is not merely maintaining an optical-link constraint. It uses predicted target motion and alternative ego trajectories to forecast future link metrics and explicitly compares reactive versus predictive connectivity-aware decisions.

---

### 4. PC-FMCW sensing and communications

PC-FMCW literature provides the upstream technical motivation. Examples include experimental studies of phase-coded FMCW for joint sensing and communications, phase-coded FMCW RadCom systems, and optical PC-FMCW integrated sensing/communication/illumination concepts for intelligent vehicles.

These studies primarily investigate questions such as:

```text
Can PC-FMCW sense and communicate simultaneously?
How accurately can it range/detect targets?
What communication performance can it provide?
What waveform/receiver trade-offs arise?
```

Our proposed robotics study asks the next decision-level question:

```text
Once PC-FMCW-informed target/link information is available,
how should an autonomous vehicle change its motion?
```

---

## The research gap we can reasonably claim

A conservative formulation is:

> **Prior work has established communication-aware motion planning, prospective connectivity-aware planning, optical communication-constrained control, and more recently the coupling of ISAC resource allocation with autonomous-vehicle planning. Comparatively less attention has been given to using PC-FMCW-informed target prediction to forecast the communication consequences of alternative future ego motions and directly incorporate those trajectory-conditioned forecasts into closed-loop vehicle motion selection.**

The paper then investigates this gap experimentally rather than merely asserting it.

The central test is:

```text
Reactive connectivity knowledge (P1)
                 vs.
Predictive trajectory-conditioned connectivity (P2)
```

under otherwise common planning and safety mechanisms.

---

## Why P1 versus P2 is the key scientific experiment

The comparison is designed so that P1 and P2 are not two unrelated algorithms.

They share the basic vehicle model, candidate generation, target prediction used for safety, road/static-obstacle constraints, and dynamic-target safety mechanisms.

The important difference is how connectivity information enters the decision:

```text
P1:
current / myopic connectivity
        -> score candidate motion

P2:
predicted target motion
        + future candidate ego motion
        -> future relative geometry
        -> future connectivity
        -> score candidate motion
```

Therefore, if P2 systematically outperforms P1 in communication outcomes while mobility and safety mechanisms remain common, we have evidence specifically for the **value of future connectivity prediction**.

This is stronger scientifically than comparing a complete proposed system against an unrelated baseline where many components change simultaneously.

---

## What the current experiment already suggests

The verified 20-seed controlled baseline currently gives:

```text
Mean modeled outage
P1 reactive:    ~0.07977
P2 predictive:  ~0.06220
```

This is an absolute reduction of approximately `0.01757`, corresponding to roughly a **22% relative reduction in modeled outage** from P1 to P2.

The paired 95% bootstrap interval is approximately:

```text
[-0.02516, -0.01066]
```

and the Holm-corrected paired Wilcoxon result is:

```text
p = 0.000501
```

The current baseline also shows improvements in modeled SNR, BER, and goodput for P2 relative to P1.

Therefore the current evidence supports the narrow statement:

> **Under the tested controlled model-based conditions, predictive connectivity-aware planning produces significantly better modeled communication outcomes than the reactive connectivity-aware planner.**

This is currently the strongest result around which the paper can be organized.

---

## Why P3 and P4 still matter

The current baseline does not show a statistically significant P2-to-P3 improvement after multiplicity correction. The P4 oracle reference also gives only small additional numerical improvements over P2.

If this remains true after robustness testing, an interesting scientific result may emerge:

```text
P1 reactive
     |
     | large benefit from useful future prediction
     v
P2 predictive
     |
     | small additional benefit from more/perfect future information
     v
P3 risk-aware / P4 oracle
```

One hypothesis to test is that, under some operating regimes, practical prediction already captures most of the connectivity-relevant future information needed for motion planning.

This must be tested through robustness experiments rather than assumed from the baseline alone.

---

## What still needs to be done for the paper

### 1. Complete and aggregate robustness experiments

We need to determine whether the P2-over-P1 result persists when varying:

- target observation noise,
- prediction uncertainty,
- planning horizon,
- connectivity-objective weight,
- scenario/seed realizations.

The objective is to show where predictive planning helps, where it does not, and how sensitive the result is to modeling choices.

### 2. Investigate the collision result

The current baseline has collision rate `0.40` for every planner.

Therefore we **cannot claim a safety improvement**.

We need scenario-level analysis using candidate-rejection counts, no-candidate steps, minimum clearance, first collision time, realized TTC, and prediction error to determine whether collisions arise from infeasible scenarios, limitations of the candidate set, prediction errors, or another modeling/planning mechanism.

### 3. Report computational cost

A robotics/planning paper should report the computational burden of P0-P4, especially P2 and Monte-Carlo-based P3.

Useful quantities include:

```text
mean planning time / replanning step
95th-percentile planning time
number of candidate trajectories
planning horizon
P3 Monte Carlo sample count
```

This allows us to discuss whether the approach is compatible with online receding-horizon execution.

### 4. Perform final literature verification

Before submission, the related-work search should be expanded using IEEE Xplore, Google Scholar, Scopus/Web of Science where available, and recent arXiv literature.

Priority language such as `first`, `first-ever`, or `no previous work` should not be used unless a systematic literature search supports it.

### 5. Optional stronger validation

The present study is deliberately a controlled PC-FMCW-informed analytical simulation.

A later validation layer using measured link data, hardware, trace-driven connectivity, or a higher-fidelity simulator would strengthen external validity, but it should remain clearly separated from the claims supported by the present benchmark.

---

## What we should NOT claim

The following claims are too broad:

> “Communication-aware motion planning has not previously been studied.”

False.

> “Predicting future communication quality for robot planning is new.”

Too broad.

> “ISAC has never been integrated with autonomous motion planning.”

False given recent planning-oriented ISAC work.

> “Optical communication has never been incorporated into MPC/NMPC.”

False given FSO communication-driven NMPC.

> “The current results validate real PC-FMCW optical-link performance.”

Not supported.

> “The proposed predictive planner improves autonomous-driving safety.”

Not supported by the current collision results.

---

## Proposed paper contributions

If the robustness and diagnostic experiments support the current findings, the paper contributions can be framed approximately as:

1. **PC-FMCW-informed closed-loop motion planning:** a framework coupling predicted target motion and candidate ego trajectories to trajectory-conditioned future communication quality.

2. **Reactive-versus-predictive isolation:** a controlled benchmark designed to measure the value of future connectivity prediction while maintaining common vehicle dynamics, candidate generation, target prediction for safety, and hard feasibility constraints.

3. **Risk-aware and oracle-bounded analysis:** uncertainty-aware and connectivity-only oracle references that quantify the additional value of uncertainty treatment and perfect future information.

4. **Reproducible sensitivity analysis:** paired statistical evaluation and robustness sweeps identifying the operating conditions under which predictive connectivity information changes closed-loop outcomes.

The exact contribution list should be finalized only after the complete robustness and collision analyses.

---

## Paper story in one paragraph

A simple way to explain the intended paper to another researcher is:

> **PC-FMCW systems can provide sensing and communication capabilities, but our question is what an autonomous vehicle should do with predictive information from such a system. We construct a closed-loop motion planner that predicts target motion, evaluates several possible future ego trajectories, estimates the future communication quality associated with each trajectory, rejects unsafe candidates, and chooses motion using both mobility and connectivity objectives. The main experiment compares a reactive planner that uses myopic connectivity information with a predictive planner that reasons over future trajectory-conditioned connectivity. The goal is to determine whether forecasting where the link is going to be provides a measurable decision-making advantage over reacting to where the link is now.**

---

## Paper story in one sentence

> **We study whether an autonomous vehicle can use PC-FMCW-informed prediction not only to understand its environment, but also to choose motion that proactively improves its future communication state.**

---

## Bottom line

The paper is **not**:

```text
"We invented communication-aware planning."
```

It is:

```text
"Given a PC-FMCW-informed autonomous system,
can predicted future target/link information be turned into
better closed-loop motion decisions than reactive connectivity information?"
```

The current P1-versus-P2 result is the main evidence for that question. Robustness analysis, collision diagnosis, runtime evaluation, and final literature verification are the remaining major steps before turning the repository into a submission-ready paper.
