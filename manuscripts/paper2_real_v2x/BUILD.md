# Paper 2 build and reproducibility

The canonical submission source is `paper2.tex`. The bibliography is `references.bib`.

## Compile PDF

```bash
cd manuscripts/paper2_real_v2x
latexmk -pdf -interaction=nonstopmode -halt-on-error paper2.tex
```

## Primary confirmed evidence

The canonical paper is governed by two compact, committed result snapshots:

- `results_archive/confirmed_w2s/` — locked W2S 30/50-km/h confirmation;
- `results_archive/confirmed_arterial/` — pre-frozen arterial n8 50/80-km/h confirmation.

Each snapshot stores exact run-role metadata, point estimates, dependence-aware bootstrap summaries, and provenance.

The large row-level files are not committed because they are deterministically regenerable from the pinned public CICV5G tree and frozen scripts.

## Reproduce W2S confirmation

Use the public CICV5G W2S data and the exact parameters recorded in `results_archive/confirmed_w2s/metadata.json`.

Core scripts:

```bash
python scripts/prepare_cicv5g.py --output data/raw/cicv5g

PYTHONPATH=src python scripts/run_real_v2x_matched_speed_replay.py \
  --data data/raw/cicv5g \
  --output results/paper2_confirmatory \
  --seed 20260930 \
  --directions w2s \
  --train-fraction 0.40 \
  --donor-fraction 0.40 \
  --speeds 30,50 \
  --query-spacing-m 5.0 \
  --caliper-m 2.0 \
  --k-donors 5

python scripts/analyze_real_v2x_matched_speed_confirmatory.py \
  --input results/paper2_confirmatory \
  --budget 0.10 \
  --bootstrap 5000 \
  --bootstrap-seed 20260930
```

## Reproduce arterial confirmation

```bash
python scripts/prepare_cicv5g_arterial_confirmation.py \
  --output data/raw/cicv5g_arterial_confirmation

PYTHONPATH=src python scripts/run_real_v2x_matched_speed_replay.py \
  --data data/raw/cicv5g_arterial_confirmation \
  --output results/paper2_arterial_confirmation \
  --seed 20260930 \
  --directions unknown \
  --train-fraction 0.40 \
  --donor-fraction 0.40 \
  --speeds 50,80 \
  --query-spacing-m 5.0 \
  --caliper-m 2.0 \
  --k-donors 5

python scripts/analyze_real_v2x_matched_speed_confirmatory.py \
  --input results/paper2_arterial_confirmation \
  --budget 0.10 \
  --bootstrap 5000 \
  --bootstrap-seed 20260930
```

## Legacy publication assets

The older predictor/support figures can still be regenerated from the root `results_archive/` snapshot:

```bash
python scripts/build_paper2_publication_assets.py \
  manuscripts/paper2_real_v2x/results_archive \
  --out manuscripts/paper2_real_v2x/generated
```

These figures are background assets, not the source of the canonical confirmatory tables.

## Scientific QA

Before submission:

1. verify every manuscript number against the locked compact snapshots;
2. verify `CLAIM_EVIDENCE.md`;
3. keep the measured oracle labeled as a nondeployable support-bounded upper-bound diagnostic;
4. do not infer causal speed effects from observational repeated drives;
5. do not treat timestamp rows, bootstrap draws, or reused split configurations as independent field experiments;
6. compile and visually inspect every PDF page for clipping, overlaps, and broken glyphs;
7. verify workflow-head SHA and executed checkout SHA separately for pull-request workflows.

A successful PDF build is necessary but not sufficient for claim validity.
