"""Trainable trajectory predictor baseline using scikit-learn.

The model predicts future x/y displacement from a fixed history window. It is
intentionally lightweight so experiments can run on CPU before moving to a
sequence model. Evaluation must use scene/time-based splits to avoid leakage.
"""

from __future__ import annotations

import numpy as np
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import HistGradientBoostingRegressor


class HistoryGradientBoosting:
    def __init__(self, random_state=0, max_iter=250):
        self.model = MultiOutputRegressor(
            HistGradientBoostingRegressor(max_iter=max_iter, random_state=random_state)
        )
        self.history = None
        self.horizon = None

    def _features(self, histories):
        x = np.asarray(histories, dtype=float)
        if x.ndim != 3 or x.shape[-1] != 2:
            raise ValueError("histories must have shape (N, history, 2)")
        origin = x[:, -1:, :]
        return (x - origin).reshape(len(x), -1)

    def fit(self, histories, futures):
        histories = np.asarray(histories, dtype=float)
        futures = np.asarray(futures, dtype=float)
        if futures.ndim != 3 or futures.shape[-1] != 2:
            raise ValueError("futures must have shape (N, horizon, 2)")
        self.history, self.horizon = histories.shape[1], futures.shape[1]
        self.model.fit(self._features(histories), (futures - histories[:, -1:, :]).reshape(len(histories), -1))
        return self

    def predict(self, histories):
        histories = np.asarray(histories, dtype=float)
        if self.history is None:
            raise RuntimeError("fit() must be called first")
        if histories.shape[1] != self.history:
            raise ValueError("history length differs from fitted model")
        delta = self.model.predict(self._features(histories)).reshape(len(histories), self.horizon, 2)
        return histories[:, -1:, :] + delta
