"""Generate first Stage 9 paper figures from stage9_primary.csv."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"


def main():
    csv_path = RESULTS / "stage9_primary.csv"
    if not csv_path.exists():
        raise SystemExit("Run scripts/run_stage9.py first.")
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path)

    summary = df.groupby("planner", as_index=False).agg(
        outage_fraction=("outage_fraction", "mean"),
        path_length_m=("path_length_m", "mean"),
        link_lifetime_s=("link_lifetime_s", "mean"),
    )

    ax = summary.plot.bar(x="planner", y="outage_fraction", legend=False, rot=25)
    ax.set_ylabel("Mean outage fraction")
    ax.set_xlabel("")
    ax.set_title("Connectivity comparison")
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(FIGURES / "planner_outage.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots()
    for planner, group in df.groupby("planner"):
        ax.scatter(group["path_length_m"], group["outage_fraction"], label=planner)
    ax.set_xlabel("Path length (m)")
    ax.set_ylabel("Outage fraction")
    ax.set_title("Mobility-connectivity trade-off")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "mobility_connectivity_tradeoff.png", dpi=200)
    plt.close(fig)

    print(f"Saved figures to {FIGURES}")


if __name__ == "__main__":
    main()
