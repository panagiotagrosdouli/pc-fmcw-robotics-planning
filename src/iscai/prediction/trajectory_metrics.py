"""Metrics for real-data trajectory prediction experiments."""

from __future__ import annotations

import numpy as np


def displacement_errors(pred: np.ndarray, truth: np.ndarray) -> np.ndarray:
    pred = np.asarray(pred, dtype=float)
    truth = np.asarray(truth, dtype=float)
    if pred.shape != truth.shape or pred.ndim != 2 or pred.shape[1] < 2:
        raise ValueError("pred and truth must have identical shape (T, D), D>=2")
    return np.linalg.norm(pred[:, :2] - truth[:, :2], axis=1)


def ade(pred: np.ndarray, truth: np.ndarray) -> float:
    return float(np.mean(displacement_errors(pred, truth)))


def fde(pred: np.ndarray, truth: np.ndarray) -> float:
    return float(displacement_errors(pred, truth)[-1])


def p95_fde(predictions: list[np.ndarray], truths: list[np.ndarray]) -> float:
    values = [fde(p, t) for p, t in zip(predictions, truths)]
    if not values:
        return float("nan")
    return float(np.percentile(values, 95))
