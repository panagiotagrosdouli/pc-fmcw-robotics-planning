# Discussion — what the real-data study actually shows

## Main finding
The field-measured study does not support the common simplifying narrative that a learned radio map should automatically replace reactive QoS information. CICV5G delay and especially SINR are strongly temporally persistent at short horizons. A planner that ignores persistence can therefore become more complex while becoming less accurate.

The useful predictive regime emerges at longer decision horizons. When spatial/context information is fused with persistence using calibration-only weights, prediction error decreases consistently across the five tested grouped split assignments at approximately 1.1–5.5 s horizons. This is the planning-relevant result: future communication information can add value, but its value is horizon-dependent and conditional on context. Because the split assignments reuse the same finite set of drives, their consistency is treated as descriptive robustness rather than five independent experimental replicates.

## Why empirical support matters
The real dataset contains measurements only along routes that were physically driven. Treating a learned QoS field as ground truth everywhere would silently convert extrapolation into apparent evidence. The support analysis shows that this concern is measurable, but the relationship is **context-dependent rather than universally monotonic**.

In the primary held-out split, the broad aggregate strata show increasing delay error and worsening interval coverage at larger support distances. A deeper context audit shows that this deterioration is driven especially by the `n8` measurements in sparse segments: the `n78` held-out runs remain substantially easier to predict across their observed support range, while `n8` segments several metres from training support show much larger error and lower coverage. Within individual drives, nearest-training distance is not consistently monotonic with instantaneous prediction error. Accordingly, support distance should be interpreted as an **empirical validity diagnostic conditioned by band/route/context**, not as a universal scalar uncertainty model.

The support-aware layer therefore has a different purpose from a conventional communication cost. It asks whether the communication estimate used to rank a candidate is empirically defensible. In the primary replay P3 does not beat P2 on delay, but it selects unsupported states less often while accepting additional mobility deviation. This is a validity-versus-mobility trade-off rather than a demonstrated QoS improvement.

## Why P3 not beating P2 is informative
A support/risk penalty is useful only when uncertainty identifies decisions whose avoidance changes outcomes. In the primary replay, P3 moves more often and uses better-supported queries, yet its measured delay is effectively unchanged relative to P2. This means support awareness should not be sold as a free communication-performance gain. Its supported interpretation is more conservative use of the learned communication model.

The primary-split raw paired p-value for reduced unsupported exposure is below 0.05, but the replay now declares a broader 12-test hypothesis family and applies Holm correction. Therefore the single-split result is reported as an effect with a confidence interval and raw/adjusted p-values, not as stand-alone confirmatory significance. The grouped multi-split replay is used as sensitivity analysis for direction and magnitude, not as independent inferential replication because the same drives are reused across split assignments.

## Relationship to prior communication-aware planning
Communication-aware motion planning is mature, and recent work already performs proactive QoS-risk-map navigation. Recent GP-based work also integrates radio-map uncertainty into robust MPC. Vehicular predictive-QoS models trained on real measurements are likewise established. Optical/FSO and visible-light mobility optimization also have prior art. Therefore the contribution cannot be "first predictive communication-aware planner," "first uncertainty-aware planner," "first optical communication-aware planner," or "first planner using real QoS data."

The narrower contribution is a field-data evaluation protocol that jointly enforces whole-run anti-leakage splitting, strong causal baselines, horizon-wise predictive evaluation, empirical support auditing, grouped-shift uncertainty analysis and route-constrained measured decision replay. This combination directly addresses the gap between evaluating a QoS predictor on logged samples and using that predictor to justify counterfactual motion choices.

## Relationship to the PC-FMCW branch
The real CICV5G experiment does not validate the optical PC-FMCW channel. The connection is at the decision layer:

- PC-FMCW branch: technology-specific optical geometry is mapped to modeled communication quality and used in candidate-trajectory evaluation.
- Real-V2X branch: field-measured 5G geometry/context is mapped to learned future delay and used to test whether predictive connectivity information has decision value.

The common scientific question is whether future communication information can change motion decisions usefully at the motion-planning horizon. The two branches provide complementary forms of evidence: technology-specific controlled simulation and field-measurement-informed decision replay.

## Statistical interpretation
The held-out runs in a given primary replay split are the paired experimental units. Timestamp-level observations are not treated as independent replicates. Raw single-split p-values are retained for transparency, but final interpretation also respects the declared multiplicity family. Repeated train/calibration/test split assignments are not independent because they recycle the same finite set of measured runs, so cross-split summaries are sensitivity analyses rather than a new sample size.

This distinction is important: the scientific evidence comes from run-level effects, their uncertainty, their stability to alternative grouped splits and the absence of data leakage—not from treating tens of thousands of correlated timestamps as independent trials.

## Practical implication
For a lightweight onboard implementation, the strongest design lesson is hierarchical:

1. use persistence/current QoS when the horizon is very short;
2. add learned spatial/context information only where calibration evidence shows incremental value;
3. expose support/OOD diagnostics to the planner and condition their interpretation on communication context;
4. treat uncertainty as a validity control rather than assuming it necessarily improves QoS;
5. avoid evaluating candidate trajectories in regions where the dataset cannot support counterfactual claims.

## What a stronger follow-up should do
A stronger follow-up would use at least one additional real V2X dataset or a purpose-built repeated-route measurement campaign with denser lateral/route alternatives. That would allow cross-dataset transfer tests and more genuine counterfactual route choices. For a PC-FMCW-specific journal extension, measured optical/laser communication data or a validated physical optical link model would be more valuable than simply adding another generic wireless dataset.
