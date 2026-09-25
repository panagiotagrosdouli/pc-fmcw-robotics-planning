#!/usr/bin/env python3
"""Build deterministic source/evidence archives for the three canonical papers."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]

COMMON = [
    "PAPER_READINESS_AUDIT.md",
    "docs/PAPER_FREEZE.md",
    "docs/BIBLIOGRAPHY_AUDIT.md",
    "docs/VENUE_AND_SUBMISSION_PLAN.md",
    "docs/SUBMISSION_RELEASE_MANIFEST.md",
    "requirements.txt",
]

PAPERS = {
    "paper1": [
        "manuscripts/paper1_pc_fmcw",
        "configs/experiments/part_b_final_v7.yaml",
        "results_archive/part_b_v7_development",
        "docs/PART_B_V7_EXECUTION_STATUS.md",
        "scripts/build_paper1_publication_assets.py",
    ],
    "paper2": [
        "manuscripts/paper2_real_v2x",
        "configs/real_v2x_support.yaml",
        ".github/workflows/real_v2x_research.yml",
        "scripts/build_paper2_publication_assets.py",
    ],
    "paper3": [
        "manuscripts/paper3_active_self_calibration",
        "configs/experiments/active_self_calibration.yaml",
        "docs/ACTIVE_SELF_CALIBRATION_RESEARCH_PLAN.md",
        ".github/workflows/active-self-calibration-research.yml",
        ".github/workflows/active-self-calibration-ablation.yml",
        "scripts/run_active_self_calibration.py",
        "scripts/analyze_active_self_calibration.py",
        "scripts/select_active_self_calibration_development.py",
        "scripts/freeze_active_self_calibration_protocol.py",
        "scripts/plot_active_self_calibration.py",
    ],
}

EXCLUDE_SUFFIXES = {".aux", ".bbl", ".blg", ".fdb_latexmk", ".fls", ".log", ".out"}


def files_for(entries: list[str]) -> list[Path]:
    found: list[Path] = []
    for entry in entries:
        path = ROOT / entry
        found.extend(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else found.append(path)
    return sorted({p for p in found if p.exists() and p.suffix not in EXCLUDE_SUFFIXES})


def build(name: str, out: Path) -> dict[str, str]:
    files = files_for(COMMON + PAPERS[name])
    archive = out / f"{name}_supplementary_reproducibility.zip"
    hashes: dict[str, str] = {}
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            hashes[rel] = hashlib.sha256(data).hexdigest()
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, data)
    return {"archive": archive.name, "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "files": hashes}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "output" / "submission")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {name: build(name, args.out) for name in PAPERS}
    (args.out / "SHA256SUMS.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
