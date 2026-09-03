"""Run a small trajectory-conditioned connectivity experiment.

This is a software-integration test, not a real-data result. Real CMHT-derived
trajectories can be fed into the same interface after extraction.
"""

import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.connectivity.trajectory_link import predict_snr_db
from iscai.connectivity.evaluation import outage_rate, mean_snr, worst_percentile_snr


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=120)
    p.add_argument("--output", type=Path, default=Path("results/connectivity_demo.csv"))
    args = p.parse_args()
    t = np.arange(args.steps)
    ego = np.column_stack((0.8 * t, 0.2 * np.sin(t / 12)))
    target = np.column_stack((0.8 * t + 12.0, 2.0 * np.sin(t / 12 + 0.7)))
    snr = predict_snr_db(ego, target)
    df = pd.DataFrame({"step": t, "snr_db": snr})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print({"mean_snr_db": mean_snr(snr), "outage_rate": outage_rate(snr), "p05_snr_db": worst_percentile_snr(snr)})


if __name__ == "__main__":
    main()
