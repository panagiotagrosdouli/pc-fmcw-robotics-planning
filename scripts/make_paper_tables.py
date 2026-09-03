"""Create compact paper-ready tables and Pareto figures from experiment outputs."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("results/paper_stage9"))
    a=p.parse_args()
    replay=a.root/"planner_replay.csv"
    horizon=a.root/"trajectory_horizon"/"summary.csv"
    if not replay.exists() or not horizon.exists():
        raise SystemExit("Required experiment outputs are missing; no paper tables were generated.")

    df=pd.read_csv(replay)
    table=df.groupby("planner",as_index=False).agg(
        N=("window","count"), Feasible=("feasible","mean"),
        Mean_SNR_dB=("mean_snr_db","mean"), P05_SNR_dB=("p05_snr_db","mean"),
        Outage=("outage_rate","mean"), Runtime_ms=("runtime_ms","mean"))
    table.to_csv(a.root/"table_planner_main.csv",index=False)
    (a.root/"table_planner_main.tex").write_text(table.to_latex(index=False,float_format=lambda x:f"{x:.3f}"))

    h=pd.read_csv(horizon)
    h.to_csv(a.root/"table_prediction_horizon.csv",index=False)
    (a.root/"table_prediction_horizon.tex").write_text(h.to_latex(index=False,float_format=lambda x:f"{x:.3f}"))

    plt.figure(figsize=(6.5,4.5))
    for planner,g in df.groupby("planner"):
        plt.scatter(g["runtime_ms"].mean(),g["outage_rate"].mean(),label=planner)
    plt.xlabel("Mean planning runtime (ms)")
    plt.ylabel("Mean realized outage rate")
    plt.title("Planner compute-connectivity trade-off")
    plt.legend()
    plt.tight_layout()
    plt.savefig(a.root/"pareto_runtime_outage.png",dpi=220)
    plt.close()

    plt.figure(figsize=(6.5,4.5))
    for planner,g in df.groupby("planner"):
        plt.scatter(g["terminal_x_m"].mean(),g["outage_rate"].mean(),label=planner)
    plt.xlabel("Mean terminal longitudinal position (m)")
    plt.ylabel("Mean realized outage rate")
    plt.title("Mobility-connectivity trade-off")
    plt.legend()
    plt.tight_layout()
    plt.savefig(a.root/"pareto_mobility_outage.png",dpi=220)
    plt.close()

    print(table.to_string(index=False))

if __name__=="__main__": main()
