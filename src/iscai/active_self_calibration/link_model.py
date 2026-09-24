"""Modeled latent optical-link parameters for active self-calibration experiments.

The latent parameters in this module are simulation variables. They are not
measured optical calibration constants. The equations deliberately reuse the
existing PC-FMCW-informed analytical geometry model while exposing only a small
number of interpretable mismatch parameters.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from iscai.connectivity.pc_fmcw_bridge import OpticalGeometryAssumptions,PCFMCWReferenceParameters
from iscai.prediction.link_predictor import LinkForecast


@dataclass(frozen=True)
class LatentLinkParameters:
    """Small modeled latent parameter vector used by the new study."""
    alpha_loss: float=1.0
    delta_beam_rad: float=0.0
    k_angular: float=1.0

    def __post_init__(self):
        values=np.array([self.alpha_loss,self.delta_beam_rad,self.k_angular],dtype=float)
        if not np.all(np.isfinite(values)): raise ValueError("latent link parameters must be finite")
        if self.alpha_loss<=0.0: raise ValueError("alpha_loss must be positive")
        if self.k_angular<=0.0: raise ValueError("k_angular must be positive")

    def as_array(self):
        return np.array([self.alpha_loss,self.delta_beam_rad,self.k_angular],dtype=float)


NOMINAL_LATENT_PARAMETERS=LatentLinkParameters()


class ParameterizedPCFMCWLinkModel:
    """Analytical link model with modeled latent mismatch.

    `directional=False` is the declared distance-only mechanism ablation. In
    that mode boresight and angular-width latents have no observation effect,
    which is intentional and exposes their non-identifiability under a
    distance-only model.
    """
    def __init__(self,reference=None,geometry=None,*,directional: bool=True):
        self.reference=reference or PCFMCWReferenceParameters()
        self.geometry=geometry or OpticalGeometryAssumptions()
        self.directional=bool(directional)

    @staticmethod
    def _states(value):
        array=np.asarray(value.states if hasattr(value,"states") else value,dtype=float)
        if array.ndim!=2 or array.shape[1]<3:
            raise ValueError("trajectory/state array must have shape (N, >=3)")
        return array

    def predict(self,ego_trajectory,target_prediction,parameters=None,link_history=None):
        del link_history
        phi=parameters or NOMINAL_LATENT_PARAMETERS
        ego=self._states(ego_trajectory);target=np.asarray(target_prediction,dtype=float)
        if target.ndim!=2 or target.shape[1]<2:
            raise ValueError("target_prediction must have shape (N, >=2)")
        n=min(len(ego),len(target))
        if n==0:
            empty=np.empty(0,dtype=float);return LinkForecast(empty,empty,empty,empty,1.0)
        ego=ego[:n];target=target[:n];delta=target[:,:2]-ego[:,:2]
        distance=np.maximum(np.linalg.norm(delta,axis=1),0.1)
        g=self.geometry
        distance_loss_db=10.0*g.pathloss_exponent*phi.alpha_loss*np.log10(distance/g.reference_distance_m)
        if self.directional:
            bearing=np.arctan2(delta[:,1],delta[:,0])
            raw_error=bearing-ego[:,2]-phi.delta_beam_rad
            angle_error=np.arctan2(np.sin(raw_error),np.cos(raw_error))
            angular_gain=np.exp(-0.5*phi.k_angular*(angle_error/max(g.beam_sigma_rad,1e-12))**2)
            angular_loss_db=-10.0*np.log10(np.maximum(angular_gain,1e-12))
        else:
            angular_loss_db=np.zeros_like(distance_loss_db)
        snr_db=g.reference_snr_db-distance_loss_db-angular_loss_db
        z=np.clip((g.outage_threshold_db-snr_db)/max(g.outage_softness_db,1e-12),-60.0,60.0)
        outage=1.0/(1.0+np.exp(-z))
        snr_linear=10.0**(snr_db/10.0);ber=0.5*np.exp(-np.maximum(snr_linear,0.0))
        goodput=self.reference.data_rate_bps*(1.0-np.clip(ber,0.0,1.0))
        survival=float(np.prod(1.0-np.clip(outage,0.0,1.0)))
        return LinkForecast(snr_db,ber,outage,goodput,survival)

    def snr_at_state(self,ego_state,target_state,parameters=None):
        ego=np.asarray(ego_state,dtype=float).reshape(1,-1)
        target=np.asarray(target_state,dtype=float).reshape(1,-1)
        return float(self.predict(ego,target,parameters).snr_db[0])

    def provenance(self):
        return {
            "study_scope":"active_self_calibration",
            "model_family":"PC-FMCW-informed analytical optical surrogate",
            "geometry_mode":"directional" if self.directional else "distance_only_ablation",
            "latent_parameters":["alpha_loss","delta_beam_rad","k_angular"],
            "latent_parameter_status":"MODELED",
            "measured_optical_calibration":False,
            "real_world_validation":False,
            "nominal_parameters":NOMINAL_LATENT_PARAMETERS.as_array().tolist(),
        }
