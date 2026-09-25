import numpy as np
import pytest

from iscai.active_self_calibration.belief import GridBelief
from iscai.active_self_calibration.link_model import LatentLinkParameters
from iscai.active_self_calibration.planners import ActiveSelfCalibrationPlanner,decision_diagnostics
from iscai.planning.trajectory import CandidateTrajectory
from iscai.prediction.link_predictor import LinkForecast


def _candidate(y):
    states=np.array([[0.0,y,0.0,5.0],[1.0,y,0.0,5.0]],dtype=float)
    return CandidateTrajectory(states,np.zeros((1,2)),1.0,y,5.0)


class _RankingModel:
    def __init__(self,critical): self.critical=critical
    def predict(self,ego_trajectory,target_prediction,parameters=None,link_history=None):
        del target_prediction,link_history
        ego=np.asarray(ego_trajectory.states if hasattr(ego_trajectory,"states") else ego_trajectory)
        y=float(np.mean(ego[:,1]));high=parameters.alpha_loss>1.0
        if self.critical:
            outage=(0.1 if not high else 0.9) if y<0.0 else (0.9 if not high else 0.1)
        else:
            shift=0.05 if high else 0.0;outage=(0.1+shift) if y<0.0 else (0.6+shift)
        n=len(ego);arr=np.full(n,outage);snr=np.full(n,10.0*(1.0-outage))
        return LinkForecast(snr,np.zeros(n),arr,np.ones(n),1.0-outage)
    def snr_at_state(self,ego_state,target_state,parameters=None):
        del target_state
        y=float(np.asarray(ego_state)[1])
        if y<0.0:return 5.0
        return 0.0 if parameters.alpha_loss<1.0 else 10.0


def _belief():
    return GridBelief.from_axes(
        alpha_loss_values=(0.8,1.2),delta_beam_values_rad=(0.0,),
        k_angular_values=(1.0,),observation_sigma_db=1.0,
    )


def test_decision_uncertainty_distinguishes_parameter_from_decision_uncertainty():
    same=np.array([[0.0,0.2],[1.0,1.2]])
    idx,uncertainty,regret,_=decision_diagnostics(same,np.array([0.5,0.5]))
    assert idx==0 and uncertainty==0.0 and regret==0.0
    changing=np.array([[0.0,2.0],[2.0,0.0]])
    _,uncertainty,regret,_=decision_diagnostics(changing,np.array([0.5,0.5]))
    assert np.isclose(uncertainty,0.5) and regret>0.0


def test_deployable_planner_rejects_oracle_truth():
    with pytest.raises(ValueError,match="cannot receive latent true parameters"):
        ActiveSelfCalibrationPlanner(
            "C3",_RankingModel(True),belief=_belief(),
            oracle_parameters=LatentLinkParameters(alpha_loss=1.2),
        )


def test_plan_is_non_updating_and_c3_does_not_probe_when_decision_irrelevant(monkeypatch):
    candidates=[_candidate(-1.0),_candidate(1.0)]
    planner=ActiveSelfCalibrationPlanner(
        "C3",_RankingModel(False),belief=_belief(),decision_threshold=0.2,
        information_weight=10.0,probe_weight=0.0,
        require_static_stop_viability=False,bounded_brake_steer=False,
        time_aligned_dynamic=False,require_dynamic_stop_viability=False,
    )
    monkeypatch.setattr(planner,"_safe_candidates",lambda *args,**kwargs:candidates)
    before=planner.belief.weights.copy();target=np.array([[20.0,0.0],[21.0,0.0]])
    result=planner.plan(np.array([0.0,0.0,0.0,5.0]),target,reference_speed=5.0)
    np.testing.assert_allclose(planner.belief.weights,before)
    assert result.decision_uncertainty==0.0
    assert result.information_active is False and result.probe_selected is False


def test_c3_can_select_probe_when_uncertainty_changes_ranking(monkeypatch):
    candidates=[_candidate(-1.0),_candidate(1.0)]
    planner=ActiveSelfCalibrationPlanner(
        "C3",_RankingModel(True),belief=_belief(),decision_threshold=0.2,
        information_weight=10.0,probe_weight=0.0,
        require_static_stop_viability=False,bounded_brake_steer=False,
        time_aligned_dynamic=False,require_dynamic_stop_viability=False,
    )
    monkeypatch.setattr(planner,"_safe_candidates",lambda *args,**kwargs:candidates)
    target=np.array([[20.0,0.0],[21.0,0.0]])
    result=planner.plan(np.array([0.0,0.0,0.0,5.0]),target,reference_speed=5.0)
    assert result.decision_uncertainty>=0.5 and result.expected_decision_regret>0.0
    assert result.information_active is True and result.probe_selected is True
    assert result.candidate_index!=result.nominal_candidate_index
