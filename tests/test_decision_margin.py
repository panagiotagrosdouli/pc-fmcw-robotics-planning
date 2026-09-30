import pandas as pd

from iscai.connectivity.real_v2x.decision_margin import (
    ConditionedMarginKNN,
    build_matched_margin_table,
)


def test_margin_model_predicts_positive_gain_for_positive_training_margin():
    df = pd.DataFrame({
        "network": ["n8"] * 60,
        "direction": ["w2s"] * 60,
        "utm_x_m": [float(i) for i in range(60)],
        "utm_y_m": [0.0] * 60,
        "fast_minus_slow_delay_gain_ms": [5.0 + 0.1 * i for i in range(60)],
    })
    model = ConditionedMarginKNN(n_neighbors=10, min_group_samples=20).fit(df)
    stats = model.predict_stats({
        "network": "n8",
        "direction": "w2s",
        "utm_x_m": 20.0,
        "utm_y_m": 0.0,
    })
    assert stats is not None
    assert stats["mean_gain_ms"] > 0
    assert stats["lower_gain_ms"] > 0
    assert stats["n_margin_neighbors"] == 10


def test_margin_model_refuses_unseen_context():
    df = pd.DataFrame({
        "network": ["n8"] * 20,
        "direction": ["w2s"] * 20,
        "utm_x_m": [float(i) for i in range(20)],
        "utm_y_m": [0.0] * 20,
        "fast_minus_slow_delay_gain_ms": [1.0] * 20,
    })
    model = ConditionedMarginKNN(n_neighbors=5, min_group_samples=10).fit(df)
    assert model.predict_stats({
        "network": "n78",
        "direction": "w2s",
        "utm_x_m": 1.0,
        "utm_y_m": 0.0,
    }) is None


def test_build_margin_table_uses_cross_run_outcomes():
    rows = []
    for speed, base in ((30.0, 10.0), (50.0, 20.0)):
        for run in ("a", "b"):
            for i in range(5):
                rows.append({
                    "run_id": f"{run}_{int(speed)}",
                    "network": "n8",
                    "direction": "w2s",
                    "nominal_speed_kmh": speed,
                    "utm_x_m": float(i),
                    "utm_y_m": 0.0,
                    "delay_ms": base + i,
                    "pub_time_ms": float(i),
                })
    df = pd.DataFrame(rows)
    out = build_matched_margin_table(
        df,
        slow_speed_kmh=30.0,
        fast_speed_kmh=50.0,
        caliper_m=0.25,
        k_donors=1,
        anchor_spacing_m=1.0,
    )
    assert not out.empty
    # FAST is constructed 10 ms worse than SLOW everywhere.
    assert (out["fast_minus_slow_delay_gain_ms"] == 10.0).all()
