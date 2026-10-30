
from pathlib import Path

import pandas as pd

from gridpulse.silver import write_silver_parquet
from gridpulse.xml_loader import parse_day_ahead_forecast


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
OUTPUT_FILE = PROJECT_ROOT / "data" / "silver" / "day_ahead_forecast.parquet"


def main():
    forecast_files = list(
        BRONZE_DIR.rglob("*DAY_AHEAD_TOTAL_LOAD_FORECAST*.xml")
    )

    if len(forecast_files) != 1:
        raise RuntimeError(
            f"Expected exactly one forecast XML file, found {len(forecast_files)}"
        )

    rows = parse_day_ahead_forecast(forecast_files[0])

    if not rows:
        raise ValueError("No forecast records found")

    df = pd.DataFrame(rows)
    df["position"] = pd.to_numeric(
        df["position"], errors="raise"
    ).astype("int64")
    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"], utc=True, errors="raise"
    ).astype("datetime64[ns, UTC]")
    df["forecast_load_mw"] = pd.to_numeric(
        df["forecast_load_mw"], errors="raise"
    )

    if df.isna().any().any():
        raise ValueError("Forecast data contains missing values")

    if not df["forecast_load_mw"].map(
        lambda value: pd.notna(value) and abs(value) != float("inf")
    ).all():
        raise ValueError("Forecast load values must be finite")

    if df["timestamp_utc"].duplicated().any():
        raise ValueError("Forecast data contains duplicate timestamps")

    df = df.sort_values("timestamp_utc").reset_index(drop=True)
    write_silver_parquet(df, OUTPUT_FILE)

    print(f"Forecast records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"First timestamp: {df['timestamp_utc'].min()}")
    print(f"Last timestamp: {df['timestamp_utc'].max()}")
    print(f"Missing values: {int(df.isna().sum().sum())}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
