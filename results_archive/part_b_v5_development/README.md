# V5 development-only safety sweep (negative result)

GitHub Actions run: `35455288436`; frozen head commit: `66eb475980e7c196beb6b1415cbd04529582f1dd`. Execution used seeds 12000–12019 and the fixed settings recorded in every `manifest.json`, including V4 bounded/static viability plus V5 time alignment, dynamic-stop viability, and damped lateral prediction.

Each margin directory contains 500 paired episodes (20 seeds × five scenarios × five planners), the runner summary, and its manifest. `development_safety_summary.csv` and `selection.json` are the selector outputs. Independent verification confirmed all seven seed sets, planners, scenario cardinality, absence of duplicate `(seed, scenario, planner)` rows, and agreement between raw-row counts and the selector summary.

No margin passed the predeclared joint gate. Every margin had zero realized target collisions and zero modeled static-envelope violations, but every margin had at least four no-candidate episodes. The minimum count occurred at 1.0 m. Consequently `selected_margin_m` is null, `gate_passes` is false, and `confirmatory_seeds_used` is false. Confirmatory seeds 13000–13049 and geometry seeds 14000–14019 were not run.

Original GitHub artifact ZIP digests:

- 0.0 m: `sha256:c6567da027563c7c6d51ad8d332e14f5f06b219719982c536e3482f9e6c8572c`
- 0.5 m: `sha256:2fcdf0edc1034ac53523c43eb84d612a8b6d068b0b5dd8221c0f75163fadbb15`
- 1.0 m: `sha256:f20804842471b38120cdc1fff9d3bf15ab8c0a9c7a51c9af88c65705ecb4b79a`
- 1.5 m: `sha256:a8f8c09753ab51b5b8afb837c674141e0a2f259e5a646b2ee8c86a392481040f`
- 2.0 m: `sha256:a1808ed5c6818443dd65219d1e756f229c287350ba89d4e850d7c3eb69dfac95`
- 2.5 m: `sha256:90b828f24fc9f88a39ff55d748d0b8302493caf5539dcd1014a28fe5ebe1d285`
- 3.0 m: `sha256:d058a07176693763b29c41e6262fa1ea5acad46c5b93efc20314a68f46c73722`
- selector: `sha256:844d701122608d3a3d3e432a953ba84dcf0ee69566274fb3f6405c0f454c6ace`

These are analytical simulator outputs, not optical measurements or real-vehicle safety validation.
