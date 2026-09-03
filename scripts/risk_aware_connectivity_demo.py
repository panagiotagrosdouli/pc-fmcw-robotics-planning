"""Demonstrate uncertainty-to-connectivity-risk propagation."""

import argparse
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.planning.risk_cost import snr_samples_from_prediction, outage_risk, risk_cost


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--samples", type=int, default=1024)
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()
    h = 20
    t = np.arange(h)
    mean = np.column_stack((10 + .5*t, .3*np.sin(t/3)))
    ego = np.column_stack((.5*t, np.zeros(h)))
    sigma = np.column_stack((.15 + .015*t, .10 + .01*t))
    snr = snr_samples_from_prediction(mean, sigma, ego, samples=args.samples, rng=args.seed)
    risk = outage_risk(snr)
    print({"risk_cost": risk_cost(snr), "mean_outage_probability": float(np.mean(risk)),
           "max_outage_probability": float(np.max(risk)), "min_snr_p05_db": float(np.percentile(snr, 5))})


if __name__ == "__main__":
    main()
