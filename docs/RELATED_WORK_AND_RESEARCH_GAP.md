# Related Work and Research Gap

## Why this document exists

This note explains how the PC-FMCW robotics-planning project relates to nearby research areas, what has already been established in the literature, and what the defensible research gap is for a possible paper.

The goal is **not** to claim that communication-aware motion planning, predictive connectivity planning, or ISAC-assisted planning are new by themselves. All of those directions already have relevant prior work. The narrower question investigated here is how **PC-FMCW-informed target prediction and future link forecasting can be coupled to closed-loop ego-motion selection**, and whether predictive connectivity information provides a measurable advantage over reactive connectivity-aware planning under otherwise identical planning and safety mechanisms.

---

## Project in one picture

The intended closed-loop chain is:

```text
PC-FMCW sensing / tracking
          |
          v
Target-state history and prediction
          |
          v
Candidate future ego trajectories
          |
          v
Future relative ego-target geometry
          |
          v
PC-FMCW-informed future link prediction
(SNR / outage / BER / goodput)
          |
          v
Safety + mobility + connectivity scoring
          |
          v
Ego-motion decision
          |
          v
Execute first control and replan
```

The important coupling is therefore not merely

```text
communication -> motion
```

but

```text
sensing/prediction -> alternative future ego motions
                   -> trajectory-conditioned future link state
                   -> motion decision
                   -> closed-loop replanning
```

---

## Closely related research directions

### 1. Communication-aware motion planning

Communication-aware robotics is an established research direction. Prior work has shown that robot motion can be planned while accounting for wireless connectivity, communication constraints, spatial channel models, and communication-quality maps.

A representative early direction is the work of Ghaffarkhah and Mostofi on communication-aware motion planning in mobile networks. Related work has also considered time-dependent spatial maps of communication quality for network-aware multi-robot path planning.

**What this means for our claims:**

We must **not** claim that incorporating communication quality into motion planning is new.

Likewise, the general idea of reasoning about prospective or future communication quality during planning is not new by itself.

**Difference from this project:**

The present project is specifically concerned with a PC-FMCW-informed autonomous-vehicle setting in which target-state prediction and each candidate ego trajectory jointly determine the predicted future relative geometry and, consequently, the modeled future link state.

---

### 2. Recent communication-aware planning using radio maps

Recent work continues to develop communication-aware robot planning using online estimates of radio conditions and QoS/risk maps. Such methods reinforce the point that connectivity-aware planning is already a mature broader concept.

**Difference from this project:**

The source of predictive information here is not primarily a learned or estimated static/spatial radio map. Instead, connectivity is conditioned on the **predicted motion of a tracked target and the candidate future motion of the ego vehicle**. The link forecast therefore changes with the candidate trajectory evaluated by the planner.

---

### 3. Planning-Oriented Integrated Sensing and Communication (PISAC)

A particularly important nearby paper is:

**X. Jin et al., “Planning Oriented Integrated Sensing and Communication,” IEEE ICC 2026.**

DOI: `10.1109/ICC59461.2026.11587040`

Preprint: <https://arxiv.org/abs/2510.23021>

This work explicitly bridges ISAC physical-layer design and autonomous-vehicle motion planning. Its key idea is to allocate ISAC resources so that sensing uncertainty is reduced for planning-critical obstacles, which in turn expands the safe navigable region available to the ego vehicle.

A simplified view of that coupling is:

```text
ISAC resource allocation
        -> sensing uncertainty
        -> obstacle representation / safe space
        -> motion planning
```

**Why it is important:**

This paper means we cannot claim that connecting ISAC and vehicle motion planning is itself unexplored.

**Difference from this project:**

The causal direction studied here is different:

```text
PC-FMCW-informed target state/prediction
        -> candidate-dependent future link forecast
        -> ego-motion selection
```

Rather than optimizing communication/sensing resources so that planning becomes easier, this project asks whether the **vehicle should change its motion because different candidate motions imply different future communication states**.

---

### 4. Free-Space Optical communication-driven NMPC

Another especially close work is:

**G. Silano, D. Bonilla Licea, H. El Hammouti, and M. Saska, “Free-Space Optical Communication-Driven NMPC Framework for Multi-Rotor Aerial Vehicles in Structured Inspection Scenarios,” IEEE SMC 2025.**

DOI: `10.1109/SMC58881.2025.11343117`

Preprint: <https://arxiv.org/abs/2507.04443>

This work integrates Free-Space Optical (FSO) connectivity constraints into nonlinear model predictive control for aerial vehicles. It considers beam alignment, minimum link quality, mobile-relay tracking, and obstacle avoidance.

A simplified view is:

```text
FSO link/alignment constraints
        -> NMPC
        -> communication-aware vehicle motion
```

**Why it is important:**

This is strong evidence that **optical communication-aware model-predictive motion planning cannot be claimed as new in general**.

**Difference from this project:**

Our focus is not simply maintaining an optical constraint or alignment condition. The planner uses a PC-FMCW-informed target prediction and evaluates how alternative ego trajectories change future relative geometry and modeled future communication quantities. The experimental question also explicitly isolates **reactive versus predictive connectivity-aware planning**.

---

### 5. PC-FMCW sensing and communications

PC-FMCW research establishes the upstream motivation for using a phase-coded FMCW architecture for integrated sensing and communications. Existing experimental and system-oriented PC-FMCW studies focus primarily on waveform, sensing, ranging/radar, communications, interference, and related physical-layer properties.

In optical/intelligent-vehicle settings, related PC-FMCW concepts have also been proposed for integrated sensing, communication, and illumination.

A simplified view of much of this literature is:

```text
PC-FMCW waveform/system
        -> sensing
        + communication
```

**Difference from this project:**

The robotics question begins after the upstream system has provided target-state information. The contribution is not a redesign of the PC-FMCW waveform or PHY. Instead, it asks what an autonomous motion planner should do with the predicted sensing/communication state.

The additional loop is:

```text
PC-FMCW-informed sensing
        -> target prediction
        -> future link consequences of ego motion
        -> autonomous motion decision
```

---

## What we should NOT claim

The following claims would be too broad and should not be used in a paper:

> “Communication-aware motion planning has not previously been studied.”

False: there is substantial prior literature.

> “Predicting future communication quality for robot planning is new.”

Too broad: prospective/time-dependent connectivity has already appeared in communication-aware planning.

> “ISAC has not previously been integrated with autonomous motion planning.”

False: recent work such as PISAC explicitly couples ISAC and vehicle planning.

> “Optical communication has not previously been incorporated into MPC/NMPC motion planning.”

False: FSO communication-driven NMPC provides a clear counterexample.

> “This work validates real PC-FMCW optical performance or real autonomous-driving safety.”

Not supported by the current benchmark. The current study is a controlled, PC-FMCW-informed, model-based simulation.

---

## The defensible research gap

The gap is narrower and lies at the intersection of these areas.

A conservative formulation is:

> **Prior work has established communication-aware motion planning, prospective connectivity-aware planning, optical communication-constrained control, and more recently the coupling of ISAC resource allocation with autonomous-vehicle planning. Comparatively less attention has been given to using PC-FMCW-informed target prediction to forecast the communication consequences of alternative future ego motions and directly incorporate those trajectory-conditioned forecasts into closed-loop vehicle motion selection.**

The project therefore investigates the following specific question:

> **Does forecasting the future communication state induced by alternative ego trajectories provide a measurable advantage over reacting to the current communication state in a PC-FMCW-informed autonomous-driving setting?**

This is deliberately narrower than claiming a new field of communication-aware planning.

---

## Why P1 versus P2 is scientifically important

The benchmark is designed so that the main comparison can isolate the value of predictive connectivity information.

### P1 — Reactive connectivity-aware planner

P1 uses current/myopic link information for connectivity scoring while using the common predicted target trajectory for safety.

Conceptually:

```text
current link state -> motion decision
```

### P2 — Predictive connectivity-aware planner

P2 evaluates future connectivity along each candidate trajectory using predicted target motion.

Conceptually:

```text
predicted target motion
        + candidate ego trajectory
        -> predicted future relative geometry
        -> predicted future link
        -> motion decision
```

P1 and P2 share the same basic motion-generation and safety framework. This is important because it makes the experiment more informative than simply comparing two unrelated planners.

The central scientific comparison becomes:

```text
Reactive knowledge of connectivity
              vs.
Predictive trajectory-conditioned connectivity
```

rather than:

```text
our complete system vs. an unrelated baseline
```

---

## Current baseline evidence

The verified 20-seed controlled simulation currently shows a clear P1-to-P2 improvement in the modeled communication metrics.

Mean modeled outage changes approximately from:

```text
P1: 0.07977
P2: 0.06220
```

corresponding to an absolute reduction of about `0.01757` and a relative reduction of roughly 22% from the P1 value.

The paired analysis currently reports a 95% paired-bootstrap interval of approximately:

```text
[-0.02516, -0.01066]
```

with Holm-corrected paired Wilcoxon `p = 0.000501` for the outage comparison.

The same baseline also shows improvements in modeled SNR, BER, and goodput for P2 relative to P1.

These results support a **narrow comparative simulation claim**: predictive connectivity-aware planning improves modeled link outcomes relative to the reactive P1 planner under the tested controlled conditions.

They do **not** establish real-world optical-link performance or real-road autonomous-driving superiority.

---

## P3 and P4 are useful even when they do not win

The current baseline does not show statistically significant improvements from P2 to the risk-sensitive P3 planner after multiplicity correction. Likewise, the oracle-connectivity P4 reference currently provides only small additional numerical improvements over P2.

This is scientifically useful rather than necessarily a negative result.

If the observation remains stable under robustness experiments, it may indicate a regime in which useful future prediction captures most of the connectivity-relevant benefit:

```text
Reactive P1
    |
    | substantial benefit from future prediction
    v
Predictive P2
    |
    | relatively small additional benefit
    v
Oracle P4
```

A possible interpretation to test—not assume—is that perfect future target knowledge has diminishing value once the planner already possesses a sufficiently informative practical prediction.

This conclusion should only be made if the robustness analysis supports it.

---

## Important limitation: safety results

The current verified baseline has the same collision rate (`0.40`) for all five planners.

Therefore the current results **must not** be presented as evidence that predictive connectivity planning improves collision safety.

Before publication, the collision behavior should be analyzed by scenario using the available diagnostics, including candidate rejection causes, no-candidate steps, minimum clearances, collision timing, and realized TTC. The analysis should determine whether collisions arise from intentionally difficult/infeasible scenarios, candidate-set limitations, prediction error, or another aspect of the simulation/planning setup.

The current defensible conclusion is about **modeled connectivity improvement**, not improved safety.

---

## Proposed paper positioning

A suitable positioning statement is:

> **This work does not introduce communication-aware planning as a new concept. Instead, it studies a specific closed-loop coupling between PC-FMCW-informed target prediction, trajectory-conditioned future link forecasting, and autonomous ego-motion selection. Through controlled reactive, predictive, risk-aware, and oracle-reference planners, the study isolates whether future connectivity prediction improves motion decisions beyond reactive link-aware planning while maintaining common safety and motion-generation mechanisms.**

A concise description of the novelty is:

```text
PC-FMCW-informed prediction
          +
trajectory-conditioned future connectivity
          +
closed-loop ego-motion planning
          +
controlled reactive-vs-predictive evaluation
```

The novelty should be presented as the **combination and experimental question**, not as invention of any one of those broad components in isolation.

---

## Candidate contribution statements

For a future paper, the contributions could be framed approximately as follows:

1. **Closed-loop PC-FMCW-informed planning framework.** A motion-planning framework coupling target prediction and candidate ego trajectories to modeled future communication quality.

2. **Controlled reactive-versus-predictive study.** A benchmark designed to isolate the value of future connectivity forecasting while keeping vehicle dynamics, candidate generation, target prediction used for safety, and hard feasibility constraints common across the relevant planners.

3. **Risk-aware and oracle-bounded analysis.** Risk-sensitive and connectivity-only oracle references for studying the value of uncertainty treatment and the remaining performance gap to perfect future connectivity information.

These statements should be updated after the full robustness study and collision analysis are completed.

---

## References / starting points

The following are particularly important papers or literature directions to inspect when positioning the work. This is a working related-work list, not yet a complete systematic bibliography.

### Communication-aware robotics

- Ghaffarkhah, A. and Mostofi, Y., work on **Communication-Aware Motion Planning in Mobile Networks**.
- Related work on **time-dependent spatial maps of communication quality for network-aware multi-robot path planning**.

These works establish that communication-aware and prospective-connectivity-aware motion planning predate the present project.

### Planning-oriented ISAC

- X. Jin, G. Li, S. Wang, F. Liu, M. Wen, H. Arslan, D. W. K. Ng, and C. Xu, **“Planning Oriented Integrated Sensing and Communication,”** IEEE International Conference on Communications (ICC), 2026. DOI: `10.1109/ICC59461.2026.11587040`. Preprint: <https://arxiv.org/abs/2510.23021>

### Optical communication-aware control

- G. Silano, D. Bonilla Licea, H. El Hammouti, and M. Saska, **“Free-Space Optical Communication-Driven NMPC Framework for Multi-Rotor Aerial Vehicles in Structured Inspection Scenarios,”** IEEE International Conference on Systems, Man, and Cybernetics (SMC), 2025. DOI: `10.1109/SMC58881.2025.11343117`. Preprint: <https://arxiv.org/abs/2507.04443>

### PC-FMCW / integrated sensing and communication

- Experimental and system-level literature on phase-coded FMCW for joint sensing and communications should be cited as the upstream technical foundation.
- Optical PC-FMCW / integrated sensing-communication-illumination work for intelligent vehicles is particularly relevant when motivating the vehicle setting.

A final paper submission should perform a broader database search (IEEE Xplore, Scopus/Web of Science where available, Google Scholar, arXiv) before using priority language such as “first,” “first-ever,” or “no previous work.”

---

## Bottom line

The project should **not** be sold as “the first communication-aware planner.”

The more defensible story is:

> Communication-aware planning already exists. Predictive/network-aware planning already exists. Optical communication-aware MPC already exists. ISAC-to-planning coupling now exists. **The open question addressed here is the closed-loop use of PC-FMCW-informed target prediction to evaluate the future communication consequences of alternative ego trajectories, and whether that predictive information materially improves autonomous motion decisions compared with a reactive connectivity-aware planner.**

That is the research question the P0–P4 benchmark is designed to study.
