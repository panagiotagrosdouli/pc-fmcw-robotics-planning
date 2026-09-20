# V7 development-only safety sweep (confirmatory pass)

GitHub Actions run: `35496870246`; frozen protocol commit: `9deb72e57dc6691e6cc60b5bdade3eeacf0ee5de`; tree-identical trigger head: `409210803356640ef50caaa8c432c445abad91c7`. Execution used development seeds 18000–18019 and the endpoint-anchored V7 settings recorded in every `manifest.json`.

Each margin directory contains 500 paired episodes (20 seeds × five scenarios × five planners), its summary, and manifest. Independent verification confirmed all seven exact seed sets, unique `(seed, scenario, planner)` keys, manifest flags, and agreement between the 3,500 raw rows and the selector summary.

The predeclared minimum-passing selector chose 0.5 m. That margin had zero collisions, zero no-candidate episodes, zero modeled static-envelope violations, and seven episodes/11 steps of explicitly recorded buffer relaxation. The 0.0 m condition failed with 44 no-candidate episodes. Margins 1.0–3.0 m also passed but were not selected because the rule required the smallest passing margin.

The pass authorized confirmatory seeds 19000–19049. All 1,250 unique confirmatory rows passed the hard gate: zero collisions, zero no-candidate episodes, and zero static violations; 70 episodes used 106 buffer-relaxation steps. `safety_gate.json` authorized the prespecified communication inference and geometry mechanism study.

The geometry study used seeds 20000–20019 only after that authorization. It completed, but one of its 1,000 rows—directional link, P2, seed 20000, `following_lateral_offset`—had one no-candidate step, with zero collisions and zero static violations. Geometry effects therefore remain mechanism evidence with this explicit limitation, not additional safety validation.

Original GitHub artifact ZIP digests:

- 0.0 m: `sha256:e8f9ed9b2efd30f2f46ef5197dbd867f69ac06cbff03eefb8e8e1858a88d5b2c`
- 0.5 m: `sha256:3c1acbeedff1ec7cb0a0c402f0212d0a4dc8536f2c6191b6ec897853a33894b8`
- 1.0 m: `sha256:240314da59a89ac70da629a8c2155c6cd019675a8ee5c7ff9d8c87521cb7b666`
- 1.5 m: `sha256:db6cce9c24f9d23e2db350e72c3bf46486428fcfe7692fdfe2644c8b92348451`
- 2.0 m: `sha256:1febe7e694275a9ae19eeb52fd6648c41ce2df181419a4ad19e04cc6fbc107ac`
- 2.5 m: `sha256:d9ff01aaa18ba80900accac800778f9ef34c8f26d8e903bb3ec02156da394ef4`
- 3.0 m: `sha256:7e4d630b1f2a47d5bb3dad86d96b40ec8f6d86027358cd63e13bf6c6912525ee`
- selector: `sha256:84c4f6c73a05845411424726fb8b15c4b158137c1752296850a23b2fdfdc0d1d`
- confirmatory: `sha256:6466f73cf30d2738ed9be4cfa0fcb51d4daa443603f0c2a3f358b2724e5c863a`
- geometry: `sha256:3f9c153cb2623164bdd31b8eab10ac7c4d16222a87f1f49a02d5eb9d36ba8f23`

These are analytical simulator outputs, not optical measurements or real-vehicle validation.
