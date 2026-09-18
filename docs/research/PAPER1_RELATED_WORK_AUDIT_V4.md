# Paper 1 related-work and novelty audit (V4)

Search scope checked 2026-09-18: communication-aware motion planning; predictive connectivity; V2X/vehicular QoS planning; radio maps; optical V2V/VLC receiver geometry; and PC-FMCW sensing/communication. Searches used combinations of those terms in scholarly indexes and primary publisher/author pages. This targeted audit extends [`LITERATURE_MATRIX.csv`](LITERATURE_MATRIX.csv); it is not an exhaustive systematic review or a novelty priority claim.

| Work / primary source | Prior result relevant to Paper 1 | Remaining distinction and limitation |
|---|---|---|
| [Mostofi et al., decentralized communication-aware motion planning (2009)](https://link.springer.com/article/10.1007/s10846-009-9335-9) | Robots predict link quality while selecting motion. | Predictive communication-aware planning itself is established prior art. |
| [Ghaffarkhah and Mostofi, communication-aware motion planning (2011)](https://doi.org/10.1109/TAC.2011.2164033) | Probabilistic communication-aware robot motion. | No generic novelty claim for communication objectives. |
| [Takai et al., optical vehicle-to-vehicle system (2014)](https://ieeexplore.ieee.org/document/6887317/) | Optical V2V communication and receiver geometry. | Optical vehicular communication exists; it does not calibrate our normalized PC-FMCW surrogate. |
| [Ullah et al., autonomous-vehicle QoS trajectory planning (2025)](https://doi.org/10.1109/ACCESS.2025.3543204) | QoS-aware vehicle planning. | Vehicular QoS objectives are prior art. |
| [Căilean et al., adaptive VLC receiver field of view (2024)](https://www.mdpi.com/1424-8220/24/9/2814) | Vehicular receiver directionality is hardware-dependent. | Our Gaussian beam width is an analytical mechanism, not that receiver's physical field of view. |
| [Gordon et al., online radio-map motion planning (2026)](https://doi.org/10.1109/INFOCOM59046.2026.11571354) | Future service/risk maps can influence robot motion. | Proactive radio-map planning is already studied. |
| [Upstream PC-FMCW reproduction notebook](https://github.com/PanagiotaGr/ISCAI_pc_fmcw/blob/main/notebooks/ISCAI_PC_FMCW.ipynb) | PC-FMCW waveform and tracking context. | The downstream closed-loop robotics decisions and optical-link surrogate are separate assumptions; upstream code alone does not validate them. |

The defensible Paper 1 contribution, if safety and communication evidence ultimately support it, is the **specific PC-FMCW sensing/tracking → future target state → candidate ego trajectories → trajectory-conditioned future analytical optical connectivity → common hard safety filter → closed-loop motion selection** chain. Any directional-versus-distance-only contrast is an analytical mechanism check. The evidence cannot establish measured headlamp-link calibration, real-vehicle safety, or novelty of communication-aware planning generally.

The safety gate currently dominates interpretation. A positive modeled QoS effect cannot support the Paper 1 claim when no-candidate steps or clearance violations remain. This audit should be revisited before submission with venue-specific citation search and citation-context checks.
