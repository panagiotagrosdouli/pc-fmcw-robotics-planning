#!/usr/bin/env bash
set -euo pipefail

# CMHT multimodal repackaging (~61.8 GB). Keep data outside Git.
# Requires: pip install huggingface_hub
#
# Run from repository root:
#   python -c 'from huggingface_hub import snapshot_download; snapshot_download(repo_id="Voxel51/cmht-autonomous-driving", repo_type="dataset", local_dir="data/raw/cmht")'

mkdir -p data/raw/cmht
python -c 'from huggingface_hub import snapshot_download; snapshot_download(repo_id="Voxel51/cmht-autonomous-driving", repo_type="dataset", local_dir="data/raw/cmht")'
echo "CMHT dataset downloaded to data/raw/cmht"
