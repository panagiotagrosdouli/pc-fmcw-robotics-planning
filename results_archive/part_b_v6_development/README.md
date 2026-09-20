# V6 development-only safety sweep (development pass, confirmatory stop)

GitHub Actions run: `35475847889`; frozen head commit: `4a1a1a218369f66543eccec05ef5117d3b84bc7a`. Execution used development seeds 15000–15019 and the fixed V6 hierarchical-clearance settings recorded in every `manifest.json`.

Each margin directory contains 500 paired episodes (20 seeds × five scenarios × five planners), the runner summary, and its manifest. `development_safety_summary.csv` and `selection.json` are the predeclared selector outputs. Independent verification confirmed all seven seed sets, planner and scenario cardinality, absence of duplicate `(seed, scenario, planner)` rows, and agreement between raw rows and selector summary (3,500 development rows total).

The predeclared minimum-passing rule selected 0.5 m. At that margin there were zero target-collision episodes, zero physical no-candidate episodes, and zero modeled static-envelope violations. Fourteen episodes used the hierarchical physical-clearance fallback for 27 total steps; these are explicitly recorded and are not represented as full-buffer satisfaction. The 0.0 m condition failed with 25 physical no-candidate episodes. Margins 1.0–3.0 m also passed the three hard development criteria but were not selected because the rule required the smallest passing margin.

The development pass authorized use of the previously untouched confirmatory seeds 16000–16049 and geometry seeds 17000–17019. The aggregate confirmatory hard gate subsequently failed because seed 16030 produced one no-candidate step in each of P0, P1, and P3 in `following_lateral_offset` (three episodes/steps total). Confirmatory collisions and modeled static-envelope violations were both zero. In accordance with the frozen protocol, communication inference was skipped and confirmatory/geometry outputs are not archived or used as positive evidence. V6 therefore ends in a confirmatory stop decision, not a validated safety claim.

Original GitHub development artifact ZIP digests:

- 0.0 m: `sha256:a16a9ccb8fb7c95334bcfe3457b010ad36ac7ea455860a7db9426654e0206033`
- 0.5 m: `sha256:3e555310b73748a72f0431d5a685b01c0a2309b42127526a33438ac1eedca137`
- 1.0 m: `sha256:0ef3cf65db1ec135d64b4d8fc3c4e9798cc68ad75ebde84acedc9f11712e7405`
- 1.5 m: `sha256:fec12a10d425249702b92df102d0ae710605d71e825108f7ef5f82bc9141083a`
- 2.0 m: `sha256:a17b7f156fdd7289b737a127c8ea569231cb9ca27a9dc4c5980f913e6d2fab36`
- 2.5 m: `sha256:127baa29f0046e5348521d1c4edcc7f19d8bcb29977322099fe09e0a866bb7cd`
- 3.0 m: `sha256:deb834e4fe11949d33190faeaa8144f07071b58d6fc7b42165d8c47a172e77da`
- selector: `sha256:f5388be18955d7eb5f669289f64d5b65f640065c1f3d5840c2c647db480b4c14`

These are analytical simulator outputs, not optical measurements or real-vehicle safety validation.
