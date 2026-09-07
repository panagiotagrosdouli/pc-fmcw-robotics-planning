# Part B Execution Status

## Current status

The repository already implements the proposed Predictive Connectivity-Aware Receding-Horizon Motion Planning study and has prior verified 20-seed baseline evidence. The new `part-b-final-v1` protocol is now frozen for a larger confirmatory run, but that final large-seed run has **not yet been executed** from the current commit.

## What is already supported by checked-in evidence

The existing verified 20-seed baseline reports a statistically supported P2-versus-P1 improvement in modeled connectivity under the controlled simulation, while collision rate is identical across planners in that baseline. P3-versus-P2 and P4-versus-P2 differences were small and not Holm-significant in that prior run. These are historical verified baseline results, not the new final-v1 confirmatory release.

## What changed in the current completion pass

1. Added an explicit Part B completion/publication gate document.
2. Added directional paired win/tie/loss fractions to the research statistical analysis alongside bootstrap CIs, Wilcoxon, Holm, Cohen dz and rank-biserial effect size.
3. Added regression coverage for the new directional fractions.
4. Frozen `configs/experiments/part_b_final.yaml` with a fresh 50-seed confirmatory range, 100,000 paired-bootstrap samples, predeclared comparisons, metrics, robustness dimensions and claim boundary.

## Final-v1 confirmatory run

Frozen seed range: `1000..1049`.

Primary comparisons:

- P2 vs P1
- P3 vs P2
- P4 vs P2

Primary communication outcomes:

- modeled outage
- mean modeled SNR
- minimum modeled SNR
- modeled BER
- modeled goodput

Safety/mobility gate outcomes:

- progress
- path length
- target clearance
- static-obstacle clearance
- collision indicator
- realized TTC
- no-candidate rate

## Important execution limitation

No numerical result may be quoted for `part-b-final-v1` until the frozen 50-seed run and its robustness/ablation matrix have completed and the artifact bundle has been inspected. Existing 20-seed numbers remain historical baseline evidence only.

## Completion gate

Part B is publication-ready only after all of the following exist from one frozen commit:

- final 50-seed P0-P4 raw episode rows;
- exact paired cardinality audit;
- paired statistics with CIs/tests/effect sizes/win fractions;
- scenario-level safety/feasibility diagnostics;
- robustness and ablation aggregates;
- safety-connectivity trade-off figures;
- provenance manifest and environment lock;
- final tables/figures generated from artifacts;
- artifact-derived manuscript/report;
- final ten-point audit requested in the research brief.
