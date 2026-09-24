#!/usr/bin/env python3
"""Freeze development-selected active-calibration hyperparameters before confirmation."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1]

def _sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",type=Path,default=Path("configs/experiments/active_self_calibration.yaml"))
    p.add_argument("--development-dir",type=Path,default=Path("artifacts/active_self_calibration/development"))
    p.add_argument("--setting-id",required=True)
    p.add_argument("--output",type=Path,default=Path("artifacts/active_self_calibration/frozen_protocol.json"))
    args=p.parse_args()
    config_path=ROOT/args.config;development_dir=ROOT/args.development_dir
    manifest_path=development_dir/"manifest.json";settings_path=development_dir/"development_settings.csv"
    if not manifest_path.exists() or not settings_path.exists():
        raise SystemExit("development manifest and development_settings.csv are required")
    config=yaml.safe_load(config_path.read_text(encoding="utf-8"))
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("phase")!="development": raise SystemExit("freeze input must be a development run")
    if manifest.get("config_sha256")!=_sha256(config_path):
        raise SystemExit("development manifest was generated from a different config")
    settings=pd.read_csv(settings_path);selected=settings[settings.setting_id==args.setting_id]
    if len(selected)!=1: raise SystemExit(f"setting_id must identify exactly one row: {args.setting_id}")
    row=selected.iloc[0]
    hyper={
        "decision_threshold":float(row.decision_threshold),
        "information_weight":float(row.information_weight),
        "probe_weight":float(row.probe_weight),
        "min_expected_regret":float(row.min_expected_regret),
    }
    frozen={
        "schema_version":1,"protocol_version":config["protocol_version"],
        "frozen_utc":datetime.now(timezone.utc).isoformat(),
        "config_sha256":_sha256(config_path),
        "development_manifest_sha256":_sha256(manifest_path),
        "development_seed_values":manifest.get("seed_values"),
        "selected_setting_id":args.setting_id,"selected_hyperparameters":hyper,
        "confirmatory_seed_range":config["confirmatory"]["seed_range"],
        "rule":"No hyperparameter changes after confirmatory seeds are opened.",
    }
    output=ROOT/args.output;output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(frozen,indent=2),encoding="utf-8")
    print(json.dumps(frozen,indent=2))

if __name__=="__main__": main()
