# Paper 3 — 2026 Novelty Audit

Date: 2026-09-28

## Closest challenge

The most important new comparison point is **RMWorld** (Wang, Cheng & Huan, arXiv:2608.20126, August 2026).

RMWorld already couples:
- task-aware communication control;
- value-of-information channel calibration;
- decision-relevant channel uncertainty;
- credibility-filtered counterfactual rollouts.

Therefore Paper 3 must **not** claim that decision-relevant channel learning or value-of-information channel calibration is new in general.

## What Paper 3 can still own

The distinctive experimental object is narrower:

1. the information-gathering intervention is the vehicle's own safe motion candidate;
2. active information seeking is gated by posterior disagreement over the optimal trajectory and expected decision regret;
3. the same candidate and hard-safety machinery is shared by passive, unconditional-active, decision-triggered, and oracle-reference variants;
4. the C1-C2-C3 decomposition is frozen before untouched confirmatory seeds;
5. the main scientific result is negative/mixed: the gate strongly suppresses harmful unconditional probing but does not establish superiority over passive calibration.

## Prior art that must be conceded

- classical and approximate dual control;
- safe active uncertainty reduction in robotic motion;
- informative path planning;
- observability-aware and optimal-experiment calibration trajectories;
- communication-aware planning;
- optical communication-aware control;
- planning-oriented ISAC;
- task-aware/value-of-information channel calibration (RMWorld).

## Strongest supported contribution

> Decision disagreement and regret are useful as an online guard against unnecessary physical probing motion in the implemented directional-link planner, but detecting decision relevance alone is not sufficient to make active probing outperform passive Bayesian calibration.

## Why the negative result helps

A weak paper would tune C3 until it beat C1.

The frozen study instead shows:
- C2 learns more aggressively but is much worse for decisions;
- C3 removes most of C2's regret/probe penalty;
- C1 remains descriptively better overall than C3;
- Scenario F is a direct failure case for useful probing.

This turns the paper from a generic "active learning improves planning" claim into a mechanism-and-boundary study.

## Remaining reviewer risks

1. all primary active-calibration evidence is modeled;
2. the V-VLC directional measured comparison is null;
3. the information proxy is approximate;
4. the candidate lattice may not contain sufficiently valuable probes;
5. the C1-C3 comparison was not a predeclared primary inferential pair;
6. RMWorld is very recent and conceptually close, so the non-overlap must remain explicit.

## Unsafe phrases

Do not write:
- first decision-relevant channel calibration;
- first task-aware communication calibration;
- active calibration outperforms passive calibration;
- measured optical self-calibration;
- PC-FMCW parameters are physically identified;
- collision-free confirmation proves safety.
