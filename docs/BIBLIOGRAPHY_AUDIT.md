# Bibliography audit

Audit date: 2026-09-23. Citation keys were checked against publisher or institutional metadata and matched to manuscript citation contexts.

| Key | Metadata result | DOI | Used for |
|---|---|---|---|
| `ghaffarkhah2011` | Authors, title, journal, volume, issue, pages, year verified | `10.1109/TAC.2011.2164033` | Established communication-aware motion planning |
| `gordon2026` | Seven authors, INFOCOM 2026, pages and year verified; corrected sixth author to Xueli An | `10.1109/INFOCOM59046.2026.11571354` | Contemporary online radio-map planning |
| `ullah2025` | Five authors, IEEE Access 13, pages 37361–37369, year verified | `10.1109/ACCESS.2025.3543204` | Vehicular QoS-aware trajectory planning |
| `takai2014` | Six authors, IEEE Photonics Journal 6(5), year verified | `10.1109/JPHOT.2014.2352620` | Optical V2V prior art; not surrogate calibration |
| `avatamanitei2024` | Four authors, Sensors 24(9), article 2814, year verified | `10.3390/s24092814` | Directional/FoV receiver prior art; not model validation |
| `zhang2026` | All nine authors, Scientific Data 13, article 878, publication year verified | `10.1038/s41597-026-07239-7` | CICV5G provenance and measured-variable facts |

## Citation mapping checks

- Paper 1 cites established planning work only to limit novelty claims.
- Optical/VLC citations do not support calibration of the analytical PC-FMCW-informed link.
- Paper 2 cites Zhang et al. for CICV5G acquisition and provenance; it never labels CICV5G as PC-FMCW data.
- No reference is used to support a real-road safety guarantee, measured optical validation, or state-of-the-art claim.
- BibTeX keys used in each `.tex` file resolve to the corresponding `.bib` file.

The audit is targeted to citations actually used in the two manuscripts; it is not a systematic literature review or novelty-priority search.


## Paper 3 positioning references

Audit date: 2026-09-25. These references are used only to position the active self-calibration study relative to established neighboring literatures; they do not support the frozen numerical results.

| Reference | Metadata result | DOI / identifier | Positioning role |
|---|---|---|---|
| Ghaffarkhah & Mostofi, *Communication-Aware Motion Planning in Mobile Networks* | IEEE TAC metadata and DOI verified | `10.1109/TAC.2011.2164033` | Communication-aware motion planning is established prior art |
| *Informative Path Planning for Active Field Mapping under Localization Uncertainty* | ICRA 2020 metadata and DOI verified | `10.1109/ICRA40945.2020.9197034` | Robot motion can be optimized for information gathering |
| *Observability-Aware Intrinsic and Extrinsic Calibration of LiDAR-IMU Systems* | IEEE T-RO 38(6), 2022 metadata and DOI verified | `10.1109/TRO.2022.3174476` | Calibration literature explicitly handles informative data selection and non-identifiable directions |
| *Trajectory Planning for Extrinsic Camera Calibration in Robotic Applications Using Optimal Experiment Design* | IEEE T-ASE 22, 2025 metadata and DOI verified | `10.1109/TASE.2025.3632764` | Continuous robot motion can be designed as a calibration experiment |
| Jin et al., *Planning Oriented Integrated Sensing and Communication* | ICC 2026 / arXiv metadata checked | `10.1109/ICC59461.2026.11587040`; `arXiv:2510.23021` | ISAC and vehicle planning have already been coupled |
| Silano et al., *Free-Space Optical Communication-Driven NMPC Framework for Multi-Rotor Aerial Vehicles in Structured Inspection Scenarios* | IEEE SMC 2025 / arXiv metadata checked | `10.1109/SMC58881.2025.11343117`; `arXiv:2507.04443` | Optical communication-aware predictive control is established neighboring work |

### Paper 3 citation-boundary checks

- These sources motivate and limit novelty language; none is used as evidence for the repository's frozen C0-C4 numerical results.
- The manuscript does not claim that communication-aware planning, informative motion, calibration-trajectory design, ISAC-to-planning coupling, or optical communication-aware control are individually new.
- The narrower study question is the decision-relevance gate for active learning of **modeled** directional optical-link parameters under a frozen safe-planning benchmark.
- The citation set is a targeted positioning audit, not a systematic literature review or a basis for universal priority claims.
