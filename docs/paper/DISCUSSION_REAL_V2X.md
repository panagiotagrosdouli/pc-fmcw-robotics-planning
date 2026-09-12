# Discussion — what the real-data study actually shows

## Main finding
The field-measured study does not support the common simplifying narrative that a learned radio map should automatically replace reactive QoS information. CICV5G delay and especially SINR are strongly temporally persistent at short horizons. A planner that ignores persistence can therefore become more complex while becoming less accurate.

The useful predictive regime emerges at longer decision horizons. When spatial/context information is fused with persistence using calibration-only weights, prediction error decreases consistently across five grouped split seeds at approximately 1.1–5.5 s horizons. This is the planning-relevant result: future communication information has value, but its value is horizon-dependent and conditional on context.

## Why empirical support matters
The real dataset contains measurements only along routes that were physically driven. Treating a learned QoS field as ground truth everywhere would silently convert extrapolation into apparent evidence. The support analysis shows that this concern is measurable: prediction error grows and uncertainty coverage deteriorates as held-out points move away from training measurements.

The support-aware layer therefore has a different purpose from a conventional communication cost. It answers whether the communication estimate used to rank a candidate is empirically defensible. In the primary replay P3 does not beat P2 on delay, but it significantly reduces selections outside the configured support region. This is a validity-versus-mobility trade-off rather than a QoS improvement and should be presented as such.

## Why P3 not beating P2 is informative
A support/risk penalty is useful only when uncertainty identifies decisions whose avoidance changes outcomes. In the primary replay, P3 moves more often and uses better-supported queries, yet its measured delay is statistically indistinguishable from P2. This means support awareness should not be sold as a free communication-performance gain. Its benefit is avoiding decisions that rely on weaker evidence.

This result also prevents an over-designed contribution: the paper does not need a more complicated risk term merely to obtain a positive table. A cleaner story is that P2 provides predictive benefit, whereas P3 exposes the cost of requiring stronger evidential validity.

## Relationship to prior communication-aware planning
Communication-aware motion planning is mature, and recent work already performs proactive QoS-risk-map navigation. Recent GP-based work also integrates radio-map uncertainty into robust MPC. Vehicular predictive-QoS models trained on real measurements are likewise established. Therefore the contribution cannot be "first predictive communication-aware planner," "first uncertainty-aware planner," or "first planner using real QoS data."

The narrower contribution is a field-data evaluation protocol that jointly enforces whole-run anti-leakage splitting, strong causal baselines, horizon-wise predictive evaluation, empirical spatial-support auditing, grouped-shift uncertainty analysis and route-constrained measured decision replay. This combination directly addresses the gap between evaluating a QoS predictor on logged samples and using that predictor to justify counterfactual motion choices.

## Relationship to the PC-FMCW branch
The real CICV5G experiment does not validate the optical PC-FMCW channel. The connection is at the decision layer:

- PC-FMCW branch: technology-specific optical geometry is mapped to modeled communication quality and used in candidate-trajectory evaluation.
- Real-V2X branch: field-measured 5G geometry/context is mapped to learned future delay and used to test whether predictive connectivity information has decision value.

The common scientific question is whether future communication information can change motion decisions safely and usefully. The two branches provide complementary forms of evidence: technology-specific controlled simulation and field-measurement-informed decision replay.

## Statistical interpretation
The nine held-out runs in the primary replay are the independent paired units. Timestamp-level observations are not treated as independent replicates. The observed P2 delay improvement is modest and should be reported with its confidence interval and paired test rather than advertised through the much larger number of individual samples. The violation-rate result is directionally favorable but does not meet p<0.05 under the paired Wilcoxon test, so a categorical "outage reduction" claim is not justified from this split alone.

## Practical implication
For a lightweight onboard implementation, the strongest design lesson is hierarchical:

1. use persistence/current QoS when the horizon is very short;
2. add learned spatial/context information only where calibration evidence shows incremental value;
3. expose support/OOD diagnostics to the planner;
4. treat uncertainty as a validity control rather than assuming it necessarily improves QoS;
5. avoid evaluating candidate trajectories in regions where the dataset cannot support counterfactual claims.

## What a stronger follow-up should do
A stronger follow-up would use at least one additional real V2X dataset or a purpose-built repeated-route measurement campaign with denser lateral/route alternatives. That would allow cross-dataset transfer tests and more genuine counterfactual route choices. For a PC-FMCW-specific journal extension, measured optical/laser communication data or a validated physical optical link model would be more valuable than simply adding another generic wireless dataset.
