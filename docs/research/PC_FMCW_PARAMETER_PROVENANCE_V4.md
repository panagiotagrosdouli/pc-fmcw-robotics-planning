# Paper 1 parameter provenance (V4 analytical branch)

This table records the values actually used by the simulation. The machine-readable source is [`PC_FMCW_PARAMETER_PROVENANCE_V4.csv`](PC_FMCW_PARAMETER_PROVENANCE_V4.csv). All listed values are frozen for V4; `UPSTREAM` refers to the upstream reproduction notebook, while `MODELED` denotes downstream analytical/planning choices. There are no measured PC-FMCW optical parameters in this branch. No additional parameter is classified as `LITERATURE` because a published number has not been demonstrated to transfer to this transmitter/receiver model.

| Parameter | Symbol | Value | Unit | Category | Confidence / physical interpretation |
|---|---|---:|---|---|---|
| carrier frequency | `f_c` | 193.4e12 | Hz | UPSTREAM | high (notebook); original manuscript not rechecked |
| chirp bandwidth | `B` | 10e9 | Hz | UPSTREAM | high (notebook); original manuscript not rechecked |
| chirp duration | `T_chirp` | 10e-6 | s | UPSTREAM | high (notebook); original manuscript not rechecked |
| communication data rate | `R_b` | 1e9 | bit/s | UPSTREAM | high (notebook); original manuscript not rechecked |
| carrier wavelength | `lambda_c` | 1.5501e-6 | m | UPSTREAM | high (calculation) |
| reference SNR | `SNR_ref` | 20.0 | dB | MODELED | high (implementation); low (physical calibration) |
| reference distance | `d_ref` | 10.0 | m | MODELED | high (implementation); low (physical calibration) |
| distance loss exponent | `n` | 2.0 | dimensionless | MODELED | high (implementation); low (physical calibration) |
| angular Gaussian width | `sigma_beam` | 0.12 | rad | MODELED | high (implementation); low (physical calibration) |
| outage threshold | `gamma_out` | 8.0 | dB | MODELED | high (implementation); low (physical calibration) |
| outage softness | `s_out` | 2.0 | dB | MODELED | high (implementation); low (physical calibration) |
| optical transmitter power | `P_tx` | not represented | W | MODELED | high (implementation); low (physical calibration) |
| receiver aperture/sensitivity | `A_rx` | not represented | m^2 | MODELED | high (implementation); low (physical calibration) |
| received optical power | `P_rx` | not represented | W | MODELED | high (implementation); low (physical calibration) |
| BER mapping | `BER` | 0.5 exp(-10^(SNR_dB/10)) | probability | MODELED | high (implementation); low (physical calibration) |
| goodput mapping | `G` | R_b (1-BER) | bit/s | MODELED | high (implementation); low (physical calibration) |
| wheelbase | `L` | 2.7 | m | MODELED | high (implementation); physical transfer unknown |
| maximum speed | `v_max` | 30 | m/s | MODELED | high (implementation); physical transfer unknown |
| maximum acceleration | `a_max` | 2.5 | m/s^2 | MODELED | high (implementation); physical transfer unknown |
| maximum braking | `a_min` | -4.0 | m/s^2 | MODELED | high (implementation); physical transfer unknown |
| maximum steering | `delta_max` | 0.5 | rad | MODELED | high (implementation); physical transfer unknown |
| maximum lateral acceleration for V4 pulse | `a_lat_max` | 3.0 | m/s^2 | MODELED | high (implementation); physical transfer unknown |
| planning timestep | `Delta_t` | 0.1 | s | MODELED | high (implementation); physical transfer unknown |
| candidate horizons | `H_c` | 2 3 4 5 | s | MODELED | high (implementation); physical transfer unknown |
| target prediction horizon | `H_p` | 20 | steps | MODELED | high (implementation); physical transfer unknown |
| target collision distance | `d_collision` | 2.0 | m | MODELED | high (implementation); physical transfer unknown |
| static clearance | `d_static` | 1.5 | m | MODELED | high (implementation); physical transfer unknown |
| planning safety margin candidates | `m_safety` | 0 0.5 1 1.5 2 2.5 3 | m | MODELED | high (implementation); physical transfer unknown |
| target observation uncertainty | `sigma_obs` | 0.20 | m | MODELED | high (implementation); physical transfer unknown |
| P3 reported prediction uncertainty | `sigma_pred` | 0.75 | m | MODELED | high (implementation); physical transfer unknown |

## Source and sensitivity boundary

- The upstream numerical values are verified in [the public reproduction notebook](https://github.com/PanagiotaGr/ISCAI_pc_fmcw/blob/main/notebooks/ISCAI_PC_FMCW.ipynb), cell 3. This is notebook provenance, not independent experimental verification of the original paper.
- 193.4 THz implies approximately 1550 nm. It is not a calibrated blue headlamp carrier.
- The normalized SNR model has no optical transmit power, receiver aperture, responsivity, pointing jitter measurement, or measured BER/outage calibration. A Gaussian angular width cannot be equated directly to a physical beam divergence or receiver field of view.
- Published optical V2V demonstrations and receiver designs motivate separate distance/pointing sensitivity axes, but cannot justify numerical ranges for this exact PC-FMCW surrogate without a mapping between hardware and the normalized SNR. Accordingly `unestablished` is retained in the CSV. A physically defensible sensitivity regime remains an open task, and no confirmatory seeds may be used to choose ranges.
- [Takai et al. optical V2V system](https://ieeexplore.ieee.org/document/6887317/) and [Căilean et al. field-of-view adaptive receiver](https://www.mdpi.com/1424-8220/24/9/2814) illustrate the hardware dependence. They do not calibrate this downstream link.
- The static 1.5 m clearance is center-to-obstacle-surface because obstacles include radii. It is distinct from the 2.0 m dynamic target center distance.
- V4 clips both the nominal quintic steering controls and emergency pulses to the nominal 3 m/s² lateral-acceleration bound. This remains a simple bicycle-model assumption rather than real-vehicle validation.
