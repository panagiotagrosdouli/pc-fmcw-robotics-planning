# Paper 3 annotated bibliography and citation map

Audit date: 2026-09-25

Purpose: provide a reviewer-facing literature structure while preserving claim boundaries. The references below position the study or document measured-data provenance; they are not evidence for the frozen C0-C4 numerical results unless explicitly identified as measured-support data.

## 1. Dual control, active learning, and value of probing

| Key | Reference / DOI | Why it is cited | What it does not support |
|---|---|---|---|
| `barshalom1974` | Bar-Shalom & Tse, IEEE TAC 19(5), 494-500. DOI `10.1109/TAC.1974.1100635` | Classical dual-effect foundation: an action can influence both physical state and future uncertainty. | Does not validate the implemented C3 approximation or any optical model. |
| `heirung2015` | Heirung, Foss & Ydstie, Journal of Process Control 32, 64-76. DOI `10.1016/j.jprocont.2015.04.012` | Online experiment design inside MPC; precedent for deliberate excitation and reducing excitation when information is adequate. | Does not establish decision-relevance gating or vehicular validity. |
| `klenske2016` | Klenske & Hennig, JMLR 17(127), 1-30 | Approximate Bayesian dual control and exploration/exploitation framing. | Not a safety or vehicular-optical reference. |
| `mesbah2018` | Mesbah, Annual Reviews in Control 45, 107-117. DOI `10.1016/j.arcontrol.2017.11.001` | Survey of stochastic MPC with active uncertainty learning; motivates approximate dual-control methods. | Does not imply that the Paper-3 information proxy is optimal. |
| `li2025` | Li, Chen, Yang & Yan, IEEE T-ASE 22, 2145-2158. DOI `10.1109/TASE.2024.3375373` | Contemporary dual control of exploration/exploitation with active learning. | Does not support a first-of-kind claim for Paper 3. |
| `hu2024` | Hu, Isele, Bae & Fisac, IJRR 43(9), 1382-1408. DOI `10.1177/02783649231215371` | Safe dual-control-style interaction planning; important autonomous-driving neighbor. | Does not validate the Paper-3 safety benchmark or optical mechanism. |
| `pashupathy2026` | Pashupathy et al., IEEE T-ASE 23, 8046-8058. DOI `10.1109/TASE.2026.3679278` | Active estimation and path planning in robotics. | Different task, sensing model, and hardware; no direct quantitative comparison. |

### Positioning consequence
The manuscript must not claim that active probing, dual control, or safe information-seeking motion is novel in general. Its narrower contribution is the downstream decision-relevance gate in the frozen PC-FMCW-informed vehicular benchmark.

## 2. Informative motion and calibration trajectory design

| Key | Reference / DOI | Why it is cited | Claim boundary |
|---|---|---|---|
| `hitz2017` | Hitz et al., Journal of Field Robotics 34(8), 1427-1449. DOI `10.1002/rob.21722` | Informative path planning as measurement-rich motion under constraints. | Environmental monitoring, not communication calibration. |
| `popovic2020` | Popovic et al., ICRA 2020, 10751-10757. DOI `10.1109/ICRA40945.2020.9197034` | Information gathering with explicit localization uncertainty. | Does not establish decision-regret gating. |
| `lv2022` | Lv et al., IEEE T-RO 38(6), 3734-3753. DOI `10.1109/TRO.2022.3174476` | Observability-aware calibration and treatment of non-identifiable directions. | Different sensors and calibration target. |
| `amersdorfer2025` | Amersdorfer & Meurer, IEEE T-ASE 22, 24152-24163. DOI `10.1109/TASE.2025.3632764` | Robot trajectory design as an optimal calibration experiment. | Does not imply that Paper-3 latent parameters are physically identifiable. |

### Positioning consequence
Paper 3 evaluates information by downstream trajectory-selection regret rather than parameter RMSE alone. This is a decision-level emphasis, not a claim that informative calibration motion is new.

## 3. Communication-aware planning and vehicular ISAC

| Key | Reference / DOI | Why it is cited | Claim boundary |
|---|---|---|---|
| `ghaffarkhah2011` | Ghaffarkhah & Mostofi, IEEE TAC 56(10), 2478-2485. DOI `10.1109/TAC.2011.2164033` | Foundational communication-aware robot motion planning. | Rules out generic novelty claims for communication-aware planning. |
| `gordon2026` | Gordon et al., IEEE INFOCOM 2026, 1-6. DOI `10.1109/INFOCOM59046.2026.11571354` | Contemporary radio-map-aware robot motion planning. | RF/network risk maps, not optical self-calibration. |
| `ullah2025` | Ullah et al., IEEE Access 13, 37361-37369. DOI `10.1109/ACCESS.2025.3543204` | Autonomous-vehicle trajectory planning around communication QoS. | Does not validate the Paper-3 link model. |
| `cheng2022` | Cheng et al., IEEE IoT Journal 9(23), 23441-23451. DOI `10.1109/JIOT.2022.3191386` | Vehicular ISAC context and sensing/communication coupling. | Broad context, not planner evidence. |
| `jin2026` | Jin et al., ICC 2026. DOI `10.1109/ICC59461.2026.11587040` | Planning-oriented ISAC connects sensing uncertainty/resource allocation to vehicle planning. | Different physical-layer problem and uncertainty model. |
| `silano2025` | Silano et al., IEEE SMC 2025, 6641-6646. DOI `10.1109/SMC58881.2025.11343117` | Optical-communication-driven NMPC in robotics. | Aerial FSO control, not vehicular PC-FMCW calibration. |

## 4. Vehicular optical / visible-light communication

| Key | Reference / DOI | Why it is cited | Claim boundary |
|---|---|---|---|
| `takai2014` | Takai et al., IEEE Photonics Journal 6(5), 1-14. DOI `10.1109/JPHOT.2014.2352620` | Demonstrated optical V2V system and real driving/outdoor optical communication context. | Does not calibrate the analytical surrogate. |
| `karbalayghareh2020` | Karbalayghareh et al., IEEE TVT 69(7), 6891-6901. DOI `10.1109/TVT.2020.2993294` | Shows vehicular VLC path loss depends on distance, lateral geometry, weather, and receiver properties. | Does not validate the three Paper-3 latents. |
| `turan2021` | Turan & Coleri, IEEE TVT 70(10), 9659-9672. DOI `10.1109/TVT.2021.3107835` | Source paper for measured V-VLC data used by the separate support study. | Measured support only; not PC-FMCW waveform calibration. |
| `turan2022nlos` | Turan et al., IEEE TVT 71(9), 10110-10114. DOI `10.1109/TVT.2022.3181160` | Measurement-based reflected/NLoS V-VLC characterization. | Does not imply NLoS effects are modeled in Paper 3. |
| `mohamed2023` | Mohamed, Elamassie & Uysal, IEEE TVT 72(8), 9692-9703. DOI `10.1109/TVT.2023.3253762` | Measurement-based evidence that vehicle geometry/oscillation affects VLC path loss. | Different optical geometry and link model. |
| `cailean2024` | Cailean, Avatamanitei & Beguni, Sensors 24(9), 2814. DOI `10.3390/s24092814` | Adaptive field-of-view receiver prior art; reinforces directionality/FoV as practical issues. | Receiver-design prior art, not model validation. |

## 5. Measured 5G support data

| Key | Reference / DOI | Role | Claim boundary |
|---|---|---|---|
| `zhang2026` | Zhang et al., Scientific Data 13, 878. DOI `10.1038/s41597-026-07239-7` | Provenance for CICV5G measured delay/pose data used in the separately scoped QoS prediction and replay study. | 5G data are not optical data and cannot validate optical calibration. |

## Metadata correction recorded during this audit

The repository previously associated the 2024 Sensors paper *Driving toward Connectivity...* with an incorrect four-author list. Publisher metadata shows three authors in this order: Alin-Mihai Cailean, Sebastian-Andrei Avatamanitei, and Catalin Beguni. The Paper-3 bibliography uses the corrected metadata; the Paper-1 BibTeX entry is corrected in the same publication-only branch.

## Citation policy

1. Numerical C0-C4 results are supported by frozen repository artifacts, not by external literature.
2. External citations establish prior art, motivate design choices, and bound novelty.
3. Measured V-VLC and CICV5G references are explicitly separated from simulator confirmation.
4. No citation is used to imply a real-road safety guarantee, measured PC-FMCW calibration, or universal first-of-kind status.
5. This is a targeted reviewer-oriented literature audit, not a systematic review or exhaustive priority search.
