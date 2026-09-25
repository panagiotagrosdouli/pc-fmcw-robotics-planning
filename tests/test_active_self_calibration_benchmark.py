import pandas as pd

from iscai.active_self_calibration.benchmark import CalibrationBenchmarkSettings,_active_prediction,_make_planner,run_study
from iscai.active_self_calibration.link_model import ParameterizedPCFMCWLinkModel
from iscai.active_self_calibration.scenarios import CalibrationScenario,make_identifiability_scenarios
from iscai.planning.dynamics import VehicleParams


def _tiny_scenario():
    base=make_identifiability_scenarios(steps=6,dt=0.1)[0]
    return CalibrationScenario(
        name=base.name,scenario=base.scenario,true_parameters=base.true_parameters,
        prior_axes={"alpha_loss_values":(0.9,1.1),"delta_beam_values_rad":(0.0,),
                    "k_angular_values":(1.0,)},mechanism=base.mechanism,
    )


def _settings():
    return CalibrationBenchmarkSettings(
        history_steps=2,horizon_steps=4,target_observation_sigma_m=0.0,
        communication_observation_sigma_db=0.5,information_horizon_steps=2,
        planning_safety_margin_m=0.0,candidate_lateral_offsets=(0.0,),
        candidate_horizons=(1.0,),candidate_speed_offsets=(0.0,),
        require_static_stop_viability=False,bounded_brake_steer=False,
        time_aligned_dynamic=False,require_dynamic_stop_viability=False,
        hierarchical_clearance=False,damped_lateral_prediction=False,
        endpoint_anchored_lateral=False,
    )


def test_oracle_parameters_are_restricted_to_c4():
    scenario=_tiny_scenario();settings=_settings();model=ParameterizedPCFMCWLinkModel()
    params=VehicleParams(dt=settings.dt)
    for mode in ("C0","C1","C2","C3"):
        assert _make_planner(mode,scenario,settings,model,params)._oracle_parameters is None
    assert _make_planner("C4",scenario,settings,model,params)._oracle_parameters==scenario.true_parameters


def test_small_study_is_deterministic_and_updates_only_calibrating_planners():
    kwargs=dict(seeds=[7],settings=_settings(),scenarios=[_tiny_scenario()],planners=("C0","C1","C3","C4"))
    a=run_study(**kwargs);b=run_study(**kwargs)
    pd.testing.assert_frame_equal(pd.DataFrame(a["episodes"]),pd.DataFrame(b["episodes"]))
    episodes=pd.DataFrame(a["episodes"]).set_index("planner")
    assert episodes.loc["C0","calibration_updates"]==0
    assert episodes.loc["C4","calibration_updates"]==0
    assert episodes.loc["C1","calibration_updates"]==episodes.loc["C1","steps"]
    assert episodes.loc["C3","calibration_updates"]==episodes.loc["C3","steps"]
    assert episodes.loc["C4","final_parameter_error_normalized"]==0.0
    assert (episodes["measured_optical_calibration"]==False).all()  # noqa: E712


def test_active_prediction_holds_position_until_three_observations():
    settings=CalibrationBenchmarkSettings(horizon_steps=4,prediction_min_history_steps=3)
    history=[[16.0809584,0.0054],[15.9659921,0.0200]]
    pred=_active_prediction(history,settings)
    assert pred.shape==(4,4)
    assert (pred[:,:2]==pred[0,:2]).all()
    assert abs(pred[0,0]-15.9659921)<1e-9


def test_active_prediction_switches_to_existing_predictor_at_minimum_history():
    settings=CalibrationBenchmarkSettings(dt=0.1,horizon_steps=3,prediction_min_history_steps=3,
                                          damped_lateral_prediction=False,
                                          endpoint_anchored_lateral=False)
    history=[[0.0,0.0],[0.5,0.0],[1.0,0.0]]
    pred=_active_prediction(history,settings)
    assert pred.shape==(3,4)
    assert pred[0,0]>1.0
