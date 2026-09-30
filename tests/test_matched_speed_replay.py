import pandas as pd

from iscai.connectivity.real_v2x.matched_replay import (
    CrossRunSpeedMatcher,
    stratified_run_split,
)


def _rows():
    rows = []
    for speed in (30.0, 50.0):
        for run_i in range(3):
            run_id = f"w2s_n8_v{int(speed)}_run{run_i}"
            for j in range(3):
                rows.append({
                    "run_id": run_id,
                    "network": "n8",
                    "direction": "w2s",
                    "nominal_speed_kmh": speed,
                    "utm_x_m": float(j),
                    "utm_y_m": 0.0,
                    "delay_ms": 10.0 + speed / 10.0 + run_i + j,
                })
    return pd.DataFrame(rows)


def test_stratified_split_keeps_runs_disjoint_and_both_speeds():
    df = _rows()
    train, donor, query, meta = stratified_run_split(df, seed=0)
    train_runs = set(train.run_id.unique())
    donor_runs = set(donor.run_id.unique())
    query_runs = set(query.run_id.unique())

    assert train_runs
    assert donor_runs
    assert query_runs
    assert train_runs.isdisjoint(donor_runs)
    assert train_runs.isdisjoint(query_runs)
    assert donor_runs.isdisjoint(query_runs)
    assert set(train.nominal_speed_kmh.unique()) == {30.0, 50.0}
    assert set(donor.nominal_speed_kmh.unique()) == {30.0, 50.0}
    assert set(query.nominal_speed_kmh.unique()) == {30.0, 50.0}
    assert not meta["excluded_strata"]


def test_matcher_respects_speed_context_and_caliper():
    donor = pd.DataFrame([
        {
            "run_id": "d30",
            "network": "n8",
            "direction": "w2s",
            "nominal_speed_kmh": 30.0,
            "utm_x_m": 0.0,
            "utm_y_m": 0.0,
            "delay_ms": 30.0,
        },
        {
            "run_id": "d50",
            "network": "n8",
            "direction": "w2s",
            "nominal_speed_kmh": 50.0,
            "utm_x_m": 0.2,
            "utm_y_m": 0.0,
            "delay_ms": 50.0,
        },
    ])
    matcher = CrossRunSpeedMatcher(caliper_m=0.5, k_donors=1).fit(donor)
    query = {
        "run_id": "query",
        "network": "n8",
        "direction": "w2s",
        "utm_x_m": 0.1,
        "utm_y_m": 0.0,
    }

    m30 = matcher.match(query, 30.0)
    m50 = matcher.match(query, 50.0)
    assert m30 is not None and m30.delay_ms == 30.0
    assert m50 is not None and m50.delay_ms == 50.0

    far = dict(query, utm_x_m=10.0)
    assert matcher.match(far, 30.0) is None


def test_matcher_never_reuses_query_run():
    donor = pd.DataFrame([
        {
            "run_id": "same",
            "network": "n8",
            "direction": "w2s",
            "nominal_speed_kmh": 30.0,
            "utm_x_m": 0.0,
            "utm_y_m": 0.0,
            "delay_ms": 1.0,
        },
        {
            "run_id": "other",
            "network": "n8",
            "direction": "w2s",
            "nominal_speed_kmh": 30.0,
            "utm_x_m": 0.1,
            "utm_y_m": 0.0,
            "delay_ms": 9.0,
        },
    ])
    matcher = CrossRunSpeedMatcher(caliper_m=1.0, k_donors=1).fit(donor)
    query = {
        "run_id": "same",
        "network": "n8",
        "direction": "w2s",
        "utm_x_m": 0.0,
        "utm_y_m": 0.0,
    }
    match = matcher.match(query, 30.0)
    assert match is not None
    assert match.delay_ms == 9.0


def test_matcher_exposes_donor_provenance():
    donor = pd.DataFrame([
        {
            "run_id": "d1",
            "network": "n8",
            "direction": "w2s",
            "nominal_speed_kmh": 30.0,
            "utm_x_m": 0.0,
            "utm_y_m": 0.0,
            "delay_ms": 10.0,
        },
        {
            "run_id": "d2",
            "network": "n8",
            "direction": "w2s",
            "nominal_speed_kmh": 30.0,
            "utm_x_m": 0.1,
            "utm_y_m": 0.0,
            "delay_ms": 20.0,
        },
    ])
    matcher = CrossRunSpeedMatcher(caliper_m=1.0, k_donors=2).fit(donor)
    query = {
        "run_id": "q",
        "network": "n8",
        "direction": "w2s",
        "utm_x_m": 0.05,
        "utm_y_m": 0.0,
    }
    match = matcher.match(query, 30.0)
    assert match is not None
    assert set(match.donor_run_ids) == {"d1", "d2"}
    assert sorted(match.donor_delays_ms) == [10.0, 20.0]
    assert len(match.donor_distances_m) == 2
