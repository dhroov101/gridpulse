
import pandas as pd


def compare_forecast_with_actual(
    actual_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
) -> pd.DataFrame:
    """Align actual and forecast load by UTC timestamp and calculate errors."""
    actual = actual_df[["timestamp_utc", "load_mw"]].copy()
    forecast = forecast_df[["timestamp_utc", "forecast_load_mw"]].copy()

    actual["timestamp_utc"] = pd.to_datetime(
        actual["timestamp_utc"], utc=True, errors="raise"
    )
    forecast["timestamp_utc"] = pd.to_datetime(
        forecast["timestamp_utc"], utc=True, errors="raise"
    )

    if actual["timestamp_utc"].duplicated().any():
        raise ValueError("Actual data contains duplicate timestamps")

    if forecast["timestamp_utc"].duplicated().any():
        raise ValueError("Forecast data contains duplicate timestamps")

    comparison = actual.merge(
        forecast,
        on="timestamp_utc",
        how="inner",
        validate="one_to_one",
    )

    if comparison.empty:
        raise ValueError("No matching timestamps between actual and forecast data")

    if comparison[["load_mw", "forecast_load_mw"]].isna().any().any():
        raise ValueError("Comparison contains missing load values")

    comparison["error_mw"] = (
        comparison["forecast_load_mw"] - comparison["load_mw"]
    )
    comparison["absolute_error_mw"] = comparison["error_mw"].abs()
    comparison["squared_error_mw2"] = comparison["error_mw"] ** 2

    return comparison.sort_values("timestamp_utc").reset_index(drop=True)


def calculate_forecast_metrics(comparison: pd.DataFrame) -> dict:
    """Calculate standard forecast error metrics in MW."""
    if comparison.empty:
        raise ValueError("Cannot calculate metrics on an empty comparison")

    errors = comparison["error_mw"]

    return {
        "matched_records": len(comparison),
        "mae_mw": comparison["absolute_error_mw"].mean(),
        "rmse_mw": (comparison["squared_error_mw2"].mean()) ** 0.5,
        "mean_error_mw": errors.mean(),
    }
