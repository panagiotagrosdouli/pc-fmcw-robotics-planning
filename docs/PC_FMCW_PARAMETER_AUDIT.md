# PC-FMCW upstream parameter audit

## Purpose

The robotics extension inherits several numerical parameters from the upstream PC-FMCW paper/reproduction context. This file separates parameters that can be traced to the upstream study from additional analytical assumptions introduced only for planning.

The audit is intentionally conservative: a parameter copied from a paper does not automatically validate the physical realism of the downstream optical-link model.

## Upstream numerical parameters used in the research context

The upstream PC-FMCW study reports a simulation configuration including:

- carrier/laser frequency: **193.4 THz**;
- FMCW chirp bandwidth: **10 GHz**;
- chirp duration/period: **10 microseconds**;
- embedded communication rate: **1 Gbit/s**;
- DPSK/phase-coded communication embedded in the FMCW waveform.

These quantities may be cited as upstream simulation/context parameters when the source is explicitly identified.

## Important optical-interpretation issue

The same upstream work is framed as a **laser headlamp** architecture and describes a blue-laser/illumination path, while a frequency of 193.4 THz corresponds to a free-space wavelength of approximately 1550 nm, i.e. infrared rather than blue visible light.

This repository must therefore NOT silently interpret `193.4 THz` as a physically calibrated visible-blue headlamp carrier.

Possible explanations include:

1. the communication/sensing simulation carrier is an abstract coherent-optical parameter distinct from the visible illumination conversion path;
2. the value was inherited from a conventional coherent/telecom FMCW simulation;
3. the manuscript contains a simplified or inconsistent parameter description;
4. the illumination stage may involve conversion not represented by the single carrier-frequency parameter.

The current repository does not have evidence sufficient to choose among these explanations.

## Required claim boundary

Until clarified by an authoritative source or the original authors:

- use `193.4 THz` only as a **traceable upstream simulation parameter**;
- do not use it to argue visible-light propagation realism;
- do not convert it into a blue-light wavelength in figures or text;
- do not claim that the downstream planning link model is an experimentally calibrated laser-headlamp channel;
- keep additional distance/pathloss/beam-width mappings labeled as PC-FMCW-informed analytical assumptions.

## Downstream planning assumptions that are not directly validated by the upstream paper

The planning bridge introduces assumptions such as:

- reference SNR at a reference distance;
- path-loss exponent;
- angular/beam-width penalty;
- outage threshold and softness;
- mapping from geometry to communication SNR;
- BER/goodput mapping under the downstream planning abstraction.

These are useful controlled-simulation mechanisms, but they must not be described as measured values unless an external calibration source is later added.

## Publication recommendation

The methods section should use wording such as:

> The planner uses a PC-FMCW-informed analytical connectivity surrogate parameterized by upstream waveform/data-rate values where traceable. The geometry-to-link mapping is a declared controlled-simulation assumption and is not an optical-channel calibration.

If reviewers ask about the carrier-frequency/headlamp interpretation, report the numerical upstream parameter and the claim boundary rather than inventing a physical reconciliation.

## Future strengthening path

The strongest future upgrade would be one of:

1. obtain clarification or supplemental channel parameters from the upstream authors;
2. replace the generic geometry-to-SNR surrogate with a literature-grounded laser/FSO headlamp channel model;
3. calibrate the surrogate against measured optical headlamp/VLC/FSO data;
4. present a sensitivity analysis showing that the planner conclusion survives plausible optical channel parameter ranges.

Until then, the current controlled model remains suitable for algorithmic comparison but not for measured optical-performance claims.
