# Archived Paper 2 result snapshots

This directory now contains two evidence generations.

## Legacy route-constrained replay snapshot

The root-level CSV/JSON files preserve the earlier Paper-2 predictor/support/MSCR study. They remain useful historical and background evidence, but they are no longer the primary basis for the canonical manuscript's planner claim.

Legacy artifact SHA-256:

`1d4f655bb52d0321deecb153e934b1f6166c9a4cbc08d96d85054dc98b768bf6`

Legacy artifact ID: `10613267659`; workflow run: `35537024339`; source branch head: `0b112e2a46d55bd8f993a2cd6a8ea2b1388a1df3`.

Do not treat historical split-seed p-values as independent-replicate evidence.

## Locked W2S confirmation

Directory: `confirmed_w2s/`

This is the compact, non-expiring snapshot of the locked 30/50-km/h support-bounded matched-field confirmation.

It includes:

- exact train/donor/query acquisition-run assignment;
- frozen action/support parameters;
- policy point estimates;
- two-way query-run × donor-run bootstrap summary;
- workflow-head and executed-checkout provenance;
- upstream CICV5G tree and manifest hashes.

The full row-level artifact remains reproducible from the pinned public dataset and frozen scripts and is intentionally not committed.

## Locked arterial confirmation

Directory: `confirmed_arterial/`

This is the compact, non-expiring snapshot of the separately pre-frozen arterial n8 50/80-km/h confirmation, with the same classes of metadata and inference summary.

## Publication rule

The canonical manuscript's primary numerical claims must be checked against:

- `confirmed_w2s/confirmatory_two_way_bootstrap.csv`;
- `confirmed_w2s/confirmatory_policy_point_estimates.csv`;
- `confirmed_arterial/confirmatory_two_way_bootstrap.csv`;
- `confirmed_arterial/confirmatory_policy_point_estimates.csv`;
- `CLAIM_EVIDENCE.md`.

Full timestamp/query rows are not inferential replicates.
