"""Run the reproducible Stage-9 paper experiment suite from one manifest.

The orchestrator never fabricates missing data or calibration artifacts. It
records each command, status and scientific provenance in a run manifest.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, log_path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as f:
        proc = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, text=True)
    return proc.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiments/paper.yaml"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / args.config).read_text())
    out = ROOT / cfg["outputs"]["root"]
    out.mkdir(parents=True, exist_ok=True)
    labels = ROOT / cfg["cmht"]["labels"]
    calibration = cfg["planner_replay"].get("link_calibration")
    calibration_path = None if not calibration else ROOT / calibration

    commands = []
    horizons = [str(x) for x in cfg["cmht"]["horizons_s"]]
    commands.append(("real_horizon_sweep", [
        sys.executable, "scripts/run_real_horizon_sweep.py", "--labels", str(labels),
        "--history-s", str(cfg["cmht"]["history"] * cfg["cmht"]["dt"]),
        "--dt", str(cfg["cmht"]["dt"]), "--horizons", *horizons,
        "--output-dir", str(out / "trajectory_horizon")]))

    replay = [sys.executable, "scripts/run_cmht_planner_replay.py", "--labels", str(labels),
              "--history", str(cfg["cmht"]["history"]),
              "--horizon", str(cfg["planner_replay"]["horizon_steps"]),
              "--dt", str(cfg["cmht"]["dt"]), "--sigma-m", str(cfg["planner_replay"]["sigma_m"]),
              "--max-windows", str(cfg["cmht"]["max_windows"]),
              "--output", str(out / "planner_replay.csv")]
    if calibration_path is not None:
        replay += ["--link-calibration", str(calibration_path)]
    commands.append(("planner_replay", replay))

    manifest = {
        "experiment": cfg["name"], "started_utc": datetime.now(timezone.utc).isoformat(),
        "config": cfg, "inputs": {"cmht_labels_exists": labels.exists(),
        "link_calibration": None if calibration_path is None else str(calibration_path),
        "link_calibration_exists": None if calibration_path is None else calibration_path.exists()},
        "runs": []}

    if not labels.exists() and not args.dry_run:
        raise SystemExit(f"CMHT labels not found: {labels}. No results were generated.")
    if calibration_path is not None and not calibration_path.exists() and not args.dry_run:
        raise SystemExit(f"Configured calibration not found: {calibration_path}. No results were generated.")

    for name, cmd in commands:
        item = {"name": name, "command": cmd}
        if args.dry_run:
            item["status"] = "dry_run"
        else:
            rc = run(cmd, out / "logs" / f"{name}.log")
            item["returncode"] = rc
            item["status"] = "ok" if rc == 0 else "failed"
            if rc != 0:
                manifest["runs"].append(item)
                break
        manifest["runs"].append(item)

    manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__": main()
