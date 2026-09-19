import numpy as np

import iscai.planning.planners as planners
from iscai.planning.trajectory import CandidateTrajectory
from iscai.simulation.pc_fmcw_benchmark import BenchmarkSettings, run_simulated_episode
from iscai.simulation.scenario import following_lateral_offset


def _candidate():
    return CandidateTrajectory(
        states=np.array([[0., 0., 0., 1.], [0.1, 0., 0., 1.]]),
        controls=np.array([[0., 0.]]), horizon=0.1,
        lateral_offset=0., target_speed=1.,
    )


def test_planner_relaxes_buffer_but_never_physical_clearance(monkeypatch):
    monkeypatch.setattr(planners, "generate_candidates", lambda *args, **kwargs: [_candidate()])

    def fake_filter(candidates, target_clearance, **kwargs):
        del kwargs
        counts = {"generated": 1, "road": 0, "speed": 0, "static": 0,
                  "dynamic": int(target_clearance > 2.),
                  "feasible": int(target_clearance <= 2.)}
        return (candidates if target_clearance <= 2. else []), counts

    monkeypatch.setattr(planners, "filter_with_diagnostics", fake_filter)
    planner = planners.MobilityOnlyPlanner(
        target_clearance=3., physical_target_clearance=2.
    )
    result = planner.plan(np.array([0., 0., 0., 1.]), np.array([[5., 0.]]))
    assert result.candidate is not None
    assert planner.last_margin_relaxed
    assert planner.last_buffered_feasibility_counts["feasible"] == 0
    assert planner.last_feasibility_counts["feasible"] == 1


def test_historical_v5_failure_becomes_explicit_margin_relaxation():
    settings = BenchmarkSettings(
        planning_safety_margin_m=1.0,
        v4_static_viability=True,
        v5_time_aligned_dynamic=True,
        v5_dynamic_stop_viability=True,
        v5_damped_lateral_prediction=True,
        v6_hierarchical_clearance=True,
    )
    row = run_simulated_episode("P0", following_lateral_offset(), seed=12009,
                                settings=settings)
    assert row["no_candidate_steps"] == 0
    assert row["margin_relaxation_steps"] == 3
    assert row["collision_indicator"] == 0
