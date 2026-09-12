# Limitations — real V2X branch

1. **Single primary measured dataset.** CICV5G provides repeated real 5G V2N2V measurements, but the present study does not establish cross-dataset generalization.

2. **Route-constrained rather than arbitrary trajectory ground truth.** Logged measurements exist only on driven routes. The replay therefore restricts candidate choices to measured future states and cannot validate QoS at arbitrary lateral/off-route vehicle trajectories.

3. **Offline decision replay.** Communication outcomes are measured, but autonomous motion decisions are evaluated offline. The experiment is not a closed-loop full-vehicle trial.

4. **Threshold definition.** The 50 ms delay threshold is an experimental operating point, not a claim about a universal V2X standard or application requirement.

5. **Grouped distribution shift.** Nominal split-conformal coverage does not remain at 90% under all run-group splits. The intervals should not be interpreted as universally calibrated probabilities.

6. **Small independent replay sample.** The primary paired decision statistics use nine held-out runs. The large timestamp count does not increase the number of independent paired units.

7. **P3 validity/QoS distinction.** P3 reduces unsupported decision exposure but does not outperform P2 in measured delay in the primary replay. Its contribution is evidence quality/validity control, not demonstrated QoS superiority.

8. **Mobility proxy.** The route replay varies future offsets along an observed route rather than executing a full kinematic vehicle trajectory family. The existing PC-FMCW simulator remains the richer closed-loop motion-planning environment.

9. **Technology mismatch with PC-FMCW.** CICV5G is cellular 5G V2N2V data. It cannot validate optical PC-FMCW propagation, DPSK performance or laser-headlamp pointing/beam effects.

10. **Timing scope.** The ~8.6 ms replay timing is measured on a hosted CI machine for the implemented communication-query/decision loop and is not a certified embedded real-time result.

## What would close the largest gaps
The highest-value next experiments are (i) a second independent V2X dataset with repeated overlapping routes, (ii) purpose-built repeated-route measurements containing genuine route alternatives, and (iii) for a PC-FMCW-specific journal claim, measured or experimentally calibrated optical-link data. Those additions would strengthen generalization and technology-specific validity more than adding a more complex learning model to the current dataset.
