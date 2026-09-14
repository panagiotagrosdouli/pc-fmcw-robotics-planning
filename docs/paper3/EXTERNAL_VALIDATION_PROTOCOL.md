# Paper 3 external scenario-shift validation protocol

## Status

Eligibility rules were committed before planner outcomes from the non-W2S cohort are inspected. The existing W2S analysis remains retrospective development evidence and is not relabeled confirmatory.

## Motivation

Paper 3 asks when a communication forecast is sufficiently supported and decision-relevant to justify altering motion. The development study uses the CICV5G W2S subset. Because those drives have already participated in prior Paper-2/Paper-3 analyses, a new split of W2S cannot create independent confirmation.

The upstream CICV5G repository also contains Urban road, Arterial road, and Rural/off-road field measurements. These are treated only as a candidate external scenario-shift cohort. Eligibility is determined from scenario, sampling, schema, and route-continuity information, not from delay outcomes or planner performance.

## Frozen eligibility rule

An external run is eligible only if all of the following hold:

1. it is outside W2S;
2. it belongs to Urban road, Arterial road, or Rural/off-road;
3. it is a standard 20-Hz run;
4. it contains publish/receive timestamps, measured delay, UTM position, heading, and velocity;
5. it is a continuous route trace suitable for route-supported future candidates;
6. the replay can reveal realized delay only after the action is selected.

Runs must not be included or excluded because their delay distribution or A1/A2 result looks favorable.

## Frozen planner operating point

The external run uses the development-selected operating point without retuning: nominal horizon 20 steps; candidate offsets 0.5x, 1.0x, and 1.5x; conformal alpha 0.1; support radius 1 m; minimum support neighbors 5; mobility scale 1 ms; minimum net gain 0 ms; 50-ms violation threshold as an experimental operating point only.

## Evidence interpretation

The external cohort tests scenario-shift transport of the selective communication-forecast intervention behavior. It does not establish arbitrary counterfactual trajectory validity, closed-loop driving safety, optical PC-FMCW validation, or a universal 50-ms requirement.

If the external cohort fails schema or route-validity checks, that is a data-limit result. If it passes but the development effect does not transport, that is a valid boundary-of-generalization result. Parameters must not be retuned to rescue the external result.
