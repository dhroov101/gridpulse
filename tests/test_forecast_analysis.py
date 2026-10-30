import pandas as pd
import pytest

from gridpulse.forecast_analysis import (
    calculate_forecast_metrics,
    compare_forecast_with_actual,
)


def test_compare_forecast_with_actual():
    actual = pd.DataFrame({
        "timestamp_utc": pd.to_datetime(
            ["2026-01-01T10:00:00Z", "2026-01-01T10:15:00Z"],
            utc=True,
        ),
        "load_mw": [100.0, 120.0],
    })

    forecast = pd.DataFrame({
        "timestamp_utc": pd.to_datetime(
            ["2026-01-01T10:15:00Z", "2026-01-01T10:00:00Z"],
            utc=True,
        ),
        "forecast_load_mw": [130.0, 110.0],
    })

    result = compare_forecast_with_actual(actual, forecast)

    assert len(result) == 2
    assert result["error_mw"].tolist() == [10.0, 10.0]
    assert result["timestamp_utc"].is_monotonic_increasing


def test_calculate_forecast_metrics():
    actual = pd.DataFrame({
        "timestamp_utc": pd.to_datetime(
            ["2026-01-01T10:00:00Z", "2026-01-01T10:15:00Z"],
            utc=True,
        ),
        "load_mw": [100.0, 120.0],
    })

    forecast = pd.DataFrame({
        "timestamp_utc": pd.to_datetime(
            ["2026-01-01T10:00:00Z", "2026-01-01T10:15:00Z"],
            utc=True,
        ),
        "forecast_load_mw": [110.0, 130.0],
    })

    comparison = compare_forecast_with_actual(actual, forecast)
    metrics = calculate_forecast_metrics(comparison)

    assert metrics["matched_records"] == 2
    assert metrics["mae_mw"] == pytest.approx(10.0)
    assert metrics["rmse_mw"] == pytest.approx(10.0)
    assert metrics["mean_error_mw"] == pytest.approx(10.0)
