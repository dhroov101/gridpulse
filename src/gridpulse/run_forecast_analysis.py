
from pathlib import Path

import pandas as pd

from gridpulse.forecast_analysis import (
    calculate_forecast_metrics,
    compare_forecast_with_actual,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_DIR = PROJECT_ROOT / "data" / "silver"
ACTUAL_FILE = SILVER_DIR / "actual_load.parquet"
FORECAST_FILE = SILVER_DIR / "day_ahead_forecast.parquet"
OUTPUT_FILE = PROJECT_ROOT / "data" / "gold" / "forecast_comparison.parquet"


def main():
    for path in (ACTUAL_FILE, FORECAST_FILE):
        if not path.exists():
            raise FileNotFoundError(
                f"Required Silver dataset not found: {path}"
            )

    actual_df = pd.read_parquet(ACTUAL_FILE)
    forecast_df = pd.read_parquet(FORECAST_FILE)

    comparison = compare_forecast_with_actual(actual_df, forecast_df)
    metrics = calculate_forecast_metrics(comparison)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_parquet(OUTPUT_FILE, index=False)

    print("\nInput datasets")
    print("--------------")
    print(f"Actual records: {len(actual_df)}")
    print(f"Forecast records: {len(forecast_df)}")
    print(f"Matched records: {len(comparison)}")

    print("\nForecast accuracy")
    print("-----------------")
    for name, value in metrics.items():
        if isinstance(value, float):
            print(f"{name}: {value:,.3f}")
        else:
            print(f"{name}: {value}")

    print(f"\nSaved comparison: {OUTPUT_FILE}")
    print("\nFirst five matched records:")
    print(comparison.head().to_string(index=False))


if __name__ == "__main__":
    main()
