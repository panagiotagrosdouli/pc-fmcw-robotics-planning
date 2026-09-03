# Data

This directory documents local datasets used by the experiments.

## Rad-R v1.0

Public source: `radr-anon-2026/radr` on Hugging Face.

The dataset contains real 77-GHz TI MMWCAS-RF-EVM radar captures with synchronized IMU/GPS/camera metadata. The public repository is large, and the raw TI `.bin` capture directories are not redistributed through the Hugging Face repository; keep downloaded data outside Git and follow the dataset license/terms.

Download locally with:

```bash
pip install -r requirements.txt
python scripts/download_radr.py --output data/raw/radr
```

Do **not** commit the downloaded dataset. The `.gitignore` intentionally excludes `data/raw/` and `data/processed/`.

For the paper, Rad-R is used as real radar/perception data. It must not be described as real optical PC-FMCW communication measurements; the communication/link layer remains a separate model unless real optical-link measurements are added.
