import importlib.util
from pathlib import Path
import pandas as pd

P = Path(__file__).resolve().parents[1] / "scripts" / "analyze_pc_fmcw_benchmark.py"
spec = importlib.util.spec_from_file_location("analysis", P)
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def test_analysis_preserves_seed_scenario_pairing():
    rows = []
    for seed in (0, 1):
        for scenario in ("a", "b"):
            for idx, planner in enumerate(("P0", "P1", "P2", "P3", "P4")):
                row = {"planner": planner, "scenario": scenario, "seed": seed}
                for metric in analysis.METRICS:
                    row[metric] = float(idx + seed)
                rows.append(row)
    out = analysis.analyze(pd.DataFrame(rows), bootstrap_samples=100)
    assert len(out) == len(analysis.PAIRINGS) * len(analysis.METRICS)
    assert set(out["n_pairs"]) == {4}
    p12 = out[(out.planner_a == "P1") & (out.planner_b == "P2")]
    assert (p12["mean_delta_b_minus_a"] == 1.0).all()
