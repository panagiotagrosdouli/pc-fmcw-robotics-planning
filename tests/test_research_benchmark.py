import numpy as np

from iscai.simulation.research_benchmark import ResearchBenchmarkSettings, run_research_benchmark
from iscai.simulation.scenario import following_lateral_offset


def test_research_benchmark_emits_paired_episode_and_trace_metrics():
    scenario = following_lateral_offset(steps=7, dt=0.1)
    settings = ResearchBenchmarkSettings(horizon_steps=4, mc_samples=1)
    episodes, traces = run_research_benchmark(
        seeds=[0],
        settings=settings,
        scenarios=[scenario],
        planners=("P1", "P2", "P2-CVaR", "P2-Adaptive"),
    )
    assert len(episodes) == 4
    assert {row["planner"] for row in episodes} == {"P1", "P2", "P2-CVaR", "P2-Adaptive"}
    assert all(row["protocol_version"] == "research-framework-v1" for row in episodes)
    assert all(np.isfinite(row["mean_planning_time_s"]) for row in episodes)
    assert traces
    assert {"ego_x_m", "ego_y_m", "realized_snr_db", "planning_time_s"} <= set(traces[0])


def test_research_benchmark_keeps_optical_claim_boundary_explicit():
    scenario = following_lateral_offset(steps=5, dt=0.1)
    settings = ResearchBenchmarkSettings(horizon_steps=3, mc_samples=1)
    episodes, _ = run_research_benchmark(
        seeds=[0], settings=settings, scenarios=[scenario], planners=("P2",)
    )
    assert episodes[0]["measured_optical_link"] is False
