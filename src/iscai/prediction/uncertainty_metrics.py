"""Calibration metrics and validation-only scaling for probabilistic trajectories."""
from __future__ import annotations
import numpy as np

def _arrays(pred_mean,pred_sigma,truth):
 mean=np.asarray(pred_mean,float);sigma=np.asarray(pred_sigma,float);truth=np.asarray(truth,float)
 if mean.shape!=sigma.shape or mean.shape!=truth.shape:raise ValueError('mean, sigma and truth must have identical shape')
 return mean,np.maximum(sigma,1e-9),truth

def gaussian_coverage(pred_mean,pred_sigma,truth,k=1.0):
 mean,sigma,truth=_arrays(pred_mean,pred_sigma,truth);return float(np.mean(np.abs(truth-mean)<=k*sigma))

def gaussian_nll_numpy(pred_mean,pred_sigma,truth):
 mean,sigma,truth=_arrays(pred_mean,pred_sigma,truth);z2=((truth-mean)/sigma)**2;return float(np.mean(.5*z2+np.log(sigma)+.5*np.log(2.*np.pi)))

def sharpness(pred_sigma):return float(np.mean(np.asarray(pred_sigma,float)))

def optimal_sigma_scale(pred_mean,pred_sigma,truth):
 """MLE scalar sigma multiplier fitted on a calibration/validation split only.

 For a diagonal Gaussian with fixed means and base sigmas, minimizing NLL over
 a positive global scale c has the closed form c=sqrt(mean(z^2)).  The caller
 is responsible for never fitting this factor on the held-out test set.
 """
 mean,sigma,truth=_arrays(pred_mean,pred_sigma,truth);z=(truth-mean)/sigma;return float(max(np.sqrt(np.mean(z*z)),1e-9))

def apply_sigma_scale(pred_sigma,scale):
 if not np.isfinite(scale) or scale<=0:raise ValueError('scale must be positive and finite')
 return np.asarray(pred_sigma,float)*float(scale)
