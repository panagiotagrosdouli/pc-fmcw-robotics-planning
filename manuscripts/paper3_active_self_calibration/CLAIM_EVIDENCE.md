# Paper 3 claim-evidence map

| Claim | Evidence | Status | Prohibited extension |
|---|---|---|---|
| C3 strongly improves over unconditional C2 on decision regret | Frozen 50-seed C3-C2 delta -0.082211, 95% CI [-0.092695,-0.072358], Holm p≈1.24e-14 | Supported | Do not reinterpret as C3 superiority over C1 |
| C3 suppresses unnecessary probing relative to C2 | Probe-fraction delta -0.037444; cumulative-probe-cost delta -0.020332, both multiplicity-adjusted significant | Supported | Do not claim probing is always harmful |
| C1 regret improves over C0 | Delta -0.001646; CI excludes zero; Holm p=0.05765 | Effect supported descriptively; not multiplicity-adjusted confirmation | Do not call statistically significant after Holm |
| C3 beats passive calibration | Not a predeclared primary pair; overall C1 mean regret 0.004786 vs C3 0.005865; F favors C1 | **Not established** | No post-hoc superiority claim |
| Decision-irrelevant uncertainty should not trigger C3 | Scenario E: C3 probe fraction 0, regret 0; C2 probes and incurs regret | Supported mechanism diagnostic | Do not treat scenario row as independent confirmatory sample |
| Decision-critical F validates useful active probing | C3 probes, but regret 0.034416 vs C1 0.028037 | **Not supported / negative result** | Do not retune away or omit |
| Directional geometry drives nontrivial active behavior | Distance-only development ablation collapses regret/probing across C0-C4 | Supported as model mechanism | Not physical optical validation |
| Measured V-VLC supports directional gain | Directional-minus-distance-only absolute-error delta -0.005031 dB, CI crosses zero, p=0.375269 | **Not supported / null** | Do not claim measured directional advantage |
| CICV5G validates optical calibration | Different measured 5G modality | **Not supported** | QoS/pose/replay support only |
| Hard safety is guaranteed | Zero sampled failures in frozen benchmark | **Not established** | No real-world safety guarantee |

## Authoritative artifacts

- Full primary run: GitHub Actions `36105008882`.
- Confirmatory artifact: ID `10852339416`, digest `sha256:04acd4a427092897f5d13da6c41be8c2c51195adec2de8250a5f11d45098a3f0`.
- Frozen development/protocol artifact: ID `10851144697`.
- Distance-only ablation run: `36110361343`.
- Distance-only artifact: ID `10853600391`, digest `sha256:415d4d4d80697bdef3c35475773139a7fc07ce1f8435d38d0d1143bbacc8e0c5`.
- V-VLC artifact: ID `10850843212`.
- CICV5G artifact: ID `10850854673`.

No compact archive in this directory replaces the full immutable Actions artifacts; it exists for manuscript traceability and regeneration checks.
