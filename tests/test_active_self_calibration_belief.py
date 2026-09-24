import numpy as np

from iscai.active_self_calibration.belief import GridBelief
from iscai.active_self_calibration.link_model import LatentLinkParameters,ParameterizedPCFMCWLinkModel


def test_bayesian_grid_update_reduces_entropy_for_informative_measurement():
    model=ParameterizedPCFMCWLinkModel()
    belief=GridBelief.from_axes(
        alpha_loss_values=(0.8,1.2),delta_beam_values_rad=(0.0,),
        k_angular_values=(1.0,),observation_sigma_db=0.25,
    )
    truth=LatentLinkParameters(alpha_loss=1.2)
    ego=np.array([0.0,0.0,0.0,10.0]);target=np.array([35.0,0.0])
    observation=model.snr_at_state(ego,target,truth);initial=belief.entropy
    belief.update_snr(model,ego,target,observation)
    assert belief.entropy<initial
    assert belief.mean_parameters().alpha_loss>1.0


def test_information_gain_is_zero_when_all_hypotheses_predict_same_snr():
    model=ParameterizedPCFMCWLinkModel()
    belief=GridBelief.from_axes(
        alpha_loss_values=(1.0,),delta_beam_values_rad=(0.0,),
        k_angular_values=(1.0,),observation_sigma_db=1.0,
    )
    ego=np.array([[0.0,0.0,0.0,10.0],[1.0,0.0,0.0,10.0]])
    target=np.array([[20.0,0.0],[21.0,0.0]])
    assert np.isclose(belief.expected_information_gain(model,ego,target),0.0)
