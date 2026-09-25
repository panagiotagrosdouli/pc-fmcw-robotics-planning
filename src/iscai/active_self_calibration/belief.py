"""Transparent Bayesian grid belief for a few modeled optical-link parameters."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np

from .link_model import LatentLinkParameters, ParameterizedPCFMCWLinkModel


def _normalized(weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    if weights.ndim != 1 or len(weights) == 0:
        raise ValueError("weights must be a non-empty 1D array")
    if np.any(~np.isfinite(weights)) or np.any(weights < 0.0):
        raise ValueError("weights must be finite and non-negative")
    total = float(weights.sum())
    if total <= 0.0:
        raise ValueError("weights must have positive mass")
    return weights / total


@dataclass
class GridBelief:
    """Discrete Bayesian belief over a small set of modeled parameter hypotheses."""

    support: tuple[LatentLinkParameters, ...]
    weights: np.ndarray
    observation_sigma_db: float = 1.0

    def __post_init__(self) -> None:
        if len(self.support) == 0:
            raise ValueError("belief support cannot be empty")
        if len(self.support) != len(self.weights):
            raise ValueError("support and weights must have equal length")
        self.weights = _normalized(self.weights)
        self.observation_sigma_db = float(self.observation_sigma_db)
        if not np.isfinite(self.observation_sigma_db) or self.observation_sigma_db <= 0.0:
            raise ValueError("observation_sigma_db must be positive and finite")

    @classmethod
    def from_axes(
        cls,
        alpha_loss_values=(0.85, 1.0, 1.15),
        delta_beam_values_rad=(-0.04, 0.0, 0.04),
        k_angular_values=(0.75, 1.0, 1.25),
        *,
        observation_sigma_db: float = 1.0,
        weights=None,
    ) -> "GridBelief":
        support = tuple(
            LatentLinkParameters(float(a), float(d), float(k))
            for a, d, k in product(alpha_loss_values, delta_beam_values_rad, k_angular_values)
        )
        prior = np.ones(len(support), dtype=float) if weights is None else np.asarray(weights, dtype=float)
        return cls(support, prior, observation_sigma_db)

    def copy(self) -> "GridBelief":
        return GridBelief(self.support, self.weights.copy(), self.observation_sigma_db)

    @property
    def entropy(self) -> float:
        positive = self.weights[self.weights > 0.0]
        return float(-np.sum(positive * np.log(positive)))

    @property
    def effective_sample_size(self) -> float:
        return float(1.0 / np.sum(self.weights**2))

    def mean_parameters(self) -> LatentLinkParameters:
        matrix = np.stack([p.as_array() for p in self.support])
        mean = self.weights @ matrix
        return LatentLinkParameters(*mean.tolist())

    def map_parameters(self) -> LatentLinkParameters:
        return self.support[int(np.argmax(self.weights))]

    def covariance(self) -> np.ndarray:
        matrix = np.stack([p.as_array() for p in self.support])
        mean = self.weights @ matrix
        centered = matrix - mean[None, :]
        return (centered * self.weights[:, None]).T @ centered

    def update_snr(
        self,
        model: ParameterizedPCFMCWLinkModel,
        ego_state,
        target_state,
        observed_snr_db: float,
    ) -> None:
        """Causal Bayes update from one realized SNR observation."""
        observation = float(observed_snr_db)
        if not np.isfinite(observation):
            raise ValueError("observed_snr_db must be finite")
        ego=np.asarray(ego_state,dtype=float).reshape(1,-1)
        target=np.asarray(target_state,dtype=float).reshape(1,-1)
        predicted=model.snr_hypotheses(ego,target,self.support)[:,0]
        sigma = self.observation_sigma_db
        log_prior = np.log(np.maximum(self.weights, 1e-300))
        log_likelihood = -0.5 * ((observation - predicted) / sigma) ** 2 - np.log(sigma)
        log_post = log_prior + log_likelihood
        log_post -= np.max(log_post)
        self.weights = _normalized(np.exp(log_post))

    def predictive_snr(self, model, ego_state, target_state) -> np.ndarray:
        ego=np.asarray(ego_state,dtype=float).reshape(1,-1)
        target=np.asarray(target_state,dtype=float).reshape(1,-1)
        return model.snr_hypotheses(ego,target,self.support)[:,0]

    def expected_information_gain(
        self,
        model,
        ego_states,
        target_states,
        *,
        max_measurements: int = 4,
    ) -> float:
        """Gaussian predictive-information approximation for a short future window."""
        ego = np.asarray(ego_states, dtype=float)
        target = np.asarray(target_states, dtype=float)
        if ego.ndim != 2 or target.ndim != 2:
            raise ValueError("ego_states and target_states must be 2D arrays")
        n = min(len(ego), len(target), int(max_measurements))
        if n <= 0:
            return 0.0
        sigma2 = self.observation_sigma_db**2
        means=model.snr_hypotheses(ego[:n],target[:n],self.support)
        predictive_mean=self.weights @ means
        centered=means-predictive_mean[None,:]
        variance=self.weights @ (centered**2)
        return float(np.sum(0.5*np.log1p(np.maximum(variance,0.0)/sigma2)))


def normalized_parameter_error(
    estimate: LatentLinkParameters,
    truth: LatentLinkParameters,
    *,
    scales=(0.20, 0.04, 0.35),
) -> float:
    """Dimensionless parameter error used only for simulator evaluation."""
    scale = np.asarray(scales, dtype=float)
    if scale.shape != (3,) or np.any(scale <= 0.0):
        raise ValueError("scales must contain three positive values")
    return float(np.linalg.norm((estimate.as_array() - truth.as_array()) / scale))
