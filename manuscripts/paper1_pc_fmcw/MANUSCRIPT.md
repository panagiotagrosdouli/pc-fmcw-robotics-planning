# Predictive Motion Planning Downstream of a PC-FMCW Laser-Headlamp ISCAI
## A Controlled Directional-Connectivity Mechanism Study

**Canonical source:** paper1.tex. Numerical claims are governed by the frozen V7 artifacts and seed-level effect tables.

## Research question

The paper no longer asks whether communication-aware or ISAC-aware planning is new. Those are established areas.

The narrower question is:

**When a PC-FMCW-informed vehicular architecture supplies target-state information, does scoring the future directional communication geometry along candidate ego trajectories improve modeled communication outcomes relative to reactive/current-geometry scoring, under a shared motion and safety interface?**

## Upstream/downstream boundary

The upstream reference is Liu et al., *Phase-Coded FMCW Laser Headlamp for Integrated Sensing, Communication, and Illumination*, IEEE Photonics Technology Letters, DOI 10.1109/LPT.2025.3649597.

The robotics paper begins after target-state/history estimation. It does not redesign the PC-FMCW waveform, phase-coded communication, coherent reception, the upstream tracking front end, or illumination control.

The planner receives target information, predicts future target motion, generates ego candidates, applies common hard safety filters, and evaluates trajectory-conditioned future communication geometry.

## Literature boundary

The manuscript explicitly concedes prior art on communication-aware motion planning, communication-aware RRT, joint motion/communication/sensing optimization, proactive radio-map planning, QoS-aware autonomous-vehicle trajectory selection, optical/FSO communication-aware motion control, planning-oriented ISAC, and vehicular optical communication/channel modeling.

The paper therefore does not claim that optical communication can influence motion for the first time.

## Actual contribution

The contribution is a controlled downstream mechanism study with four parts:

1. a PC-FMCW-to-planning interface downstream of the published laser-headlamp ISCAI concept;
2. a P1/P2 comparison that holds candidate generation and dynamic-safety information constant while changing only current-versus-future connectivity geometry;
3. a frozen development/confirmation protocol using independent seed-level inference and retaining earlier protocol failures;
4. a directional-versus-distance-only mechanism ablation showing that the predictive effect collapses when the implemented angular attenuation mechanism is removed.

## Planner family

- **P0:** mobility only.
- **P1:** reactive communication scoring using present/myopic target geometry.
- **P2:** predictive communication scoring using future target geometry.
- **P3:** P2 plus the implemented Monte-Carlo uncertainty/risk treatment.
- **P4:** future simulator truth for connectivity scoring only; safety still uses the common predicted target.

Thus P2-P1 tests future connectivity value, P3-P2 tests the implemented risk treatment, and P4-P2 tests the model-relative connectivity oracle gap.

## Frozen V7 evidence

Development seeds: 18000-18019.

Confirmatory seeds: 19000-19049.

Directional-mechanism seeds: 20000-20019.

The predeclared minimum-passing development rule selected a 0.5-m planning buffer.

The independent confirmatory unit is the seed after averaging the five declared scenarios within seed.

The 1,250-row confirmatory artifact passed the hard gate with zero collision episodes, zero no-candidate episodes, and zero modeled static-clearance-violation episodes. These are sampled simulation results, not a safety guarantee.

## Primary P2-P1 results

| Endpoint | Mean seed effect |
|---|---:|
| Mean outage probability | -0.0173955 |
| Mean SNR | +0.2799 dB |
| Minimum SNR | +2.0097 dB |
| Modeled BER | -0.003045 |
| Modeled goodput | +3.045 Mbit/s |

Every deterministic bootstrap interval excludes zero and every Holm-adjusted p-value remains below 1e-10.

These are correlated outputs of one analytical link model. They are not five independent physical validations.

## Negative results retained

### P3

P3 is worse than P2 on all five declared communication endpoints after correction. Therefore the paper must not claim that the implemented uncertainty/risk treatment improves communication utility.

### P4

P4 does not differ significantly from P2 after correction. This is interpreted narrowly: under the tested conditions, the practical forecast captures most of the communication value of perfect future target geometry inside the declared model.

### Earlier protocol failures

V3-V5 development failures and the V6 independent confirmatory failure remain in the scientific record.

## Directional mechanism

A 20-seed ablation compares distance loss plus angular/beam attenuation against distance loss only.

The directional P2-P1 outage effect is approximately **-0.01803**. The distance-only effect is approximately zero.

This supports the claim that the implemented predictive effect depends on directional geometry. It does not prove that the angular model is a calibrated physical optical channel.

One directional/P2 mechanism episode has one no-candidate step, so the mechanism study is not additional safety evidence.

## Physical-model boundary

The link is explicitly a **PC-FMCW-informed analytical connectivity surrogate**.

The downstream path-loss, angular penalty, reference SNR, outage mapping, BER, and goodput relationships are planning-side assumptions unless separately traceable.

The upstream context contains a 193.4-THz carrier/frequency value while the architecture is described as a laser headlamp/illumination system. 193.4 THz corresponds to approximately 1550 nm, not visible blue light.

The repository does not have evidence to reconcile this. The paper therefore reports the upstream number only as provenance, does not call it a calibrated blue-light carrier, and does not claim measured PC-FMCW optical propagation.

## Supported conclusion

**Under the frozen analytical simulator, future trajectory-conditioned directional connectivity scoring improves modeled communication outcomes relative to reactive scoring while sharing the same motion candidates and safety information. The effect collapses in the distance-only mechanism ablation.**

That is the paper. It is not a real-road validation, physical optical-channel validation, or generic first-of-kind communication-aware planning claim.
