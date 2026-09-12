# Paper 1 — journal-grade manuscript standard

The canonical manuscript must be a self-contained scientific article rather than a repository status report. PR numbers, workflow runs, branch names, and debugging history belong in reproducibility/audit material, not the main narrative.

## Scientific story

The paper starts from the PC-FMCW integrated sensing/communication/illumination headlamp and asks what is required to close the loop from target sensing and tracking to autonomous ego-motion. The method predicts target motion, propagates candidate ego trajectories, evaluates future relative optical geometry with the analytical PC-FMCW-informed link surrogate, applies a planner-independent safety envelope, and executes the first control of the selected feasible trajectory in receding horizon.

The novelty claim is technology-specific. Communication-aware motion planning, QoS-aware trajectory planning, optical/FSO trajectory optimization, and ISAC trajectory optimization are prior art. The defensible contribution is a PC-FMCW-specific perception-to-action bridge with predictive-versus-reactive planner isolation, directional-geometry mechanism testing, explicit parameter provenance, and a safety-gated confirmatory protocol.

## Required sections

The full paper should contain: Introduction; Related Work; PC-FMCW System Context and Parameter Provenance; Vehicle/Target State Model; Prediction Model; Candidate Trajectory Generation; Analytical Directional Link Model; P0--P4 Planner Formulation; Shared Safety Envelope; Experimental Scenarios; Development-versus-Confirmation Protocol; Statistical Analysis; Communication Results; Safety/Robotics Results; Directional-versus-Distance-Only Mechanism Ablation; Discussion; Threats to Validity; Reproducibility; Conclusion; and verified references.

## Hypotheses

H1: predictive P2 improves the predeclared modeled communication endpoints relative to reactive P1 under the frozen scenario family while satisfying the shared safety gate.

H2: any P2 advantage is materially larger under directional optical geometry than under a distance-only ablation, supporting a geometry-specific mechanism inside the analytical simulator.

H3: P3 provides additional risk-sensitive value only if supported by the fresh confirmatory evidence; it must not be claimed by default.

P4 is a simulator-oracle reference, not a realizable controller.

## Safety integrity

V1 is exploratory because the executed study failed the robotics safety gate and omitted the frozen min-SNR endpoint from the captured schema. V2 development also failed, so its quarantined confirmatory seeds must not be used. V3 is the active remediation protocol. Development-only seeds 6000--6019 select the minimum predeclared prediction-safety margin that yields zero collisions and zero no-candidate episodes under the shared braking-plus-lateral safety envelope. Only then may fresh confirmatory seeds 7000--7049 and mechanism seeds 8000--8019 execute.

Physical collision clearance must not be redefined to make the gate pass. Safety changes must be common to P0--P4 and must not encode communication-specific preference.

## Statistics

The independent inferential unit is seed. Scenario effects are first aggregated within seed. For each declared planner comparison, report paired effect estimates, bootstrap 95% confidence intervals, paired Wilcoxon signed-rank tests where appropriate, and Holm correction across exactly the five frozen communication endpoints: mean outage probability, mean SNR, minimum SNR, modeled BER, and modeled goodput. Safety is a separate hard gate/diagnostic family.

## Claim boundaries

The optical link is analytical/model-based unless genuine hardware measurements are introduced. Directional-versus-distance-only results provide mechanism evidence inside the simulator, not physical channel validation. The reported 193.4-THz source parameter is preserved as provenance even though it corresponds near 1550 nm and is difficult to reconcile with blue-headlamp terminology; the manuscript must not infer visible-blue photometry, eye safety, detector response, or atmospheric behavior from it.

## Presentation standard

The final paper should include an architecture figure, planner/safety schematic, scenario trajectories, seed-level effect plots with confidence intervals, safety diagnostics, geometry-ablation interaction plot, parameter-provenance table, planner-definition table, confirmatory results table, and limitations/threats-to-validity section. Figures and tables must be generated from frozen artifacts rather than manually transcribed.

The manuscript may be expanded now, but its final Results/Abstract/Conclusion must remain gated until a fresh post-remediation confirmatory artifact passes the safety protocol. The target is a normal full-paper manuscript, approximately 8--12 IEEE-style pages before venue-specific compression, not a 3-page extended abstract.
