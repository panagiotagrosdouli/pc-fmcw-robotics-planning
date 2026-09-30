from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


@dataclass(frozen=True)
class MatchResult:
    """Measured donor outcome for one motion-conditioned query."""

    delay_ms: float
    delay_std_ms: float
    nearest_distance_m: float
    mean_distance_m: float
    n_donors: int
    n_donor_runs: int
    donor_run_ids: tuple[str, ...]
    donor_delays_ms: tuple[float, ...]
    donor_distances_m: tuple[float, ...]


def stratified_run_split(
    df: pd.DataFrame,
    group_cols: Iterable[str] = ("network", "direction", "nominal_speed_kmh"),
    train_fraction: float = 0.50,
    donor_fraction: float = 0.25,
    seed: int = 0,
):
    """Split whole runs within communication/motion strata.

    The split is intended for matched field replay:
      * train runs fit the QoS predictor;
      * donor runs provide measured candidate outcomes;
      * query runs provide decision contexts only.

    Runs never cross partitions. Strata with fewer than three runs cannot support all
    three roles and are excluded from the returned frames and recorded in metadata.
    """
    cols = tuple(group_cols)
    missing = [c for c in ("run_id", *cols) if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")
    rng = np.random.default_rng(seed)
    assignments: dict[str, str] = {}
    excluded: dict[str, list[str]] = {}

    run_meta = df[["run_id", *cols]].drop_duplicates("run_id")
    for key, g in run_meta.groupby(list(cols), dropna=False, sort=True):
        if not isinstance(key, tuple):
            key = (key,)
        runs = sorted(g["run_id"].astype(str).tolist())
        label = "|".join(str(v) for v in key)
        if len(runs) < 3:
            excluded[label] = runs
            continue
        runs = [runs[i] for i in rng.permutation(len(runs))]
        n = len(runs)
        n_train = max(1, int(np.floor(n * train_fraction)))
        n_donor = max(1, int(np.floor(n * donor_fraction)))
        if n_train + n_donor >= n:
            n_donor = 1
            n_train = n - 2
        for r in runs[:n_train]:
            assignments[r] = "train"
        for r in runs[n_train:n_train + n_donor]:
            assignments[r] = "donor"
        for r in runs[n_train + n_donor:]:
            assignments[r] = "query"

    role = df["run_id"].map(assignments)
    train = df[role == "train"].copy()
    donor = df[role == "donor"].copy()
    query = df[role == "query"].copy()
    meta = {
        "group_cols": list(cols),
        "train_runs": sorted(r for r, v in assignments.items() if v == "train"),
        "donor_runs": sorted(r for r, v in assignments.items() if v == "donor"),
        "query_runs": sorted(r for r, v in assignments.items() if v == "query"),
        "excluded_strata": excluded,
    }
    return train, donor, query, meta


class CrossRunSpeedMatcher:
    """Nearest-neighbour measured outcomes from disjoint donor runs.

    Matching is exact in network, travel direction, and nominal speed, then spatial
    within a fixed UTM caliper. The matcher never interpolates a missing outcome.
    """

    def __init__(
        self,
        caliper_m: float = 2.0,
        k_donors: int = 5,
        max_neighbors: int = 64,
    ):
        self.caliper_m = float(caliper_m)
        self.k_donors = int(k_donors)
        self.max_neighbors = int(max_neighbors)
        self._groups: dict[tuple, tuple[pd.DataFrame, NearestNeighbors]] = {}

    @staticmethod
    def _key(network, direction, speed_kmh):
        return (str(network), str(direction), float(speed_kmh))

    def fit(self, donor_df: pd.DataFrame):
        required = {
            "network", "direction", "nominal_speed_kmh", "utm_x_m", "utm_y_m",
            "delay_ms", "run_id",
        }
        missing = required.difference(donor_df.columns)
        if missing:
            raise ValueError(f"donor dataframe missing: {sorted(missing)}")
        self._groups = {}
        for key, g in donor_df.groupby(
            ["network", "direction", "nominal_speed_kmh"], dropna=False, sort=False
        ):
            g = g.reset_index(drop=True)
            if g.empty:
                continue
            n = min(self.max_neighbors, len(g))
            nn = NearestNeighbors(n_neighbors=n).fit(
                g[["utm_x_m", "utm_y_m"]].to_numpy(float)
            )
            self._groups[self._key(*key)] = (g, nn)
        return self

    def match(self, query: pd.Series | dict, speed_kmh: float) -> MatchResult | None:
        key = self._key(query["network"], query["direction"], speed_kmh)
        payload = self._groups.get(key)
        if payload is None:
            return None
        g, nn = payload
        xy = np.asarray([[float(query["utm_x_m"]), float(query["utm_y_m"])]])
        distances, indices = nn.kneighbors(xy)
        distances = distances[0]
        indices = indices[0]

        keep = distances <= self.caliper_m
        if not np.any(keep):
            return None
        cand = g.iloc[indices[keep]].copy()
        cand["_distance_m"] = distances[keep]

        # Donor/query partitions are disjoint by construction, but this extra guard
        # prevents accidental same-run reuse if the matcher is used independently.
        query_run = str(query.get("run_id", ""))
        cand = cand[cand["run_id"].astype(str) != query_run]
        if cand.empty:
            return None

        # Prefer diversity across runs before taking repeated nearby samples.
        cand = cand.sort_values("_distance_m", kind="stable")
        selected = []
        used_runs: set[str] = set()
        for _, row in cand.iterrows():
            run_id = str(row["run_id"])
            if run_id not in used_runs:
                selected.append(row)
                used_runs.add(run_id)
            if len(selected) >= self.k_donors:
                break
        if len(selected) < self.k_donors:
            # Fill remaining slots with closest samples, while retaining the number
            # of unique donor runs as an explicit support diagnostic.
            selected_idx = {int(r.name) for r in selected}
            for idx, row in cand.iterrows():
                if int(idx) in selected_idx:
                    continue
                selected.append(row)
                if len(selected) >= self.k_donors:
                    break

        delays = np.asarray([float(r["delay_ms"]) for r in selected], float)
        dists = np.asarray([float(r["_distance_m"]) for r in selected], float)
        run_ids = tuple(str(r["run_id"]) for r in selected)
        runs = set(run_ids)
        return MatchResult(
            delay_ms=float(np.mean(delays)),
            delay_std_ms=float(np.std(delays, ddof=1)) if len(delays) > 1 else 0.0,
            nearest_distance_m=float(np.min(dists)),
            mean_distance_m=float(np.mean(dists)),
            n_donors=int(len(delays)),
            n_donor_runs=int(len(runs)),
            donor_run_ids=run_ids,
            donor_delays_ms=tuple(float(x) for x in delays),
            donor_distances_m=tuple(float(x) for x in dists),
        )
