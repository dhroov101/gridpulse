
from pathlib import Path

from gridpulse.xml_loader import parse_day_ahead_forecast


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"


def main():
    forecast_files = list(
        BRONZE_DIR.rglob("*DAY_AHEAD_TOTAL_LOAD_FORECAST*.xml")
    )

    if len(forecast_files) != 1:
        raise RuntimeError(
            f"Expected exactly one forecast XML file, found {len(forecast_files)}"
        )

    forecast_file = forecast_files[0]
    rows = parse_day_ahead_forecast(forecast_file)

    timestamps = [row["timestamp_utc"] for row in rows]
    positions = [row["position"] for row in rows]

    print(f"Source: {forecast_file.name}")
    print(f"Forecast records: {len(rows)}")
    print(f"First timestamp (UTC): {timestamps[0]}")
    print(f"Last timestamp (UTC): {timestamps[-1]}")
    print(f"Unique positions: {len(set(positions))}")
    print(f"Duplicate timestamps: {len(timestamps) - len(set(timestamps))}")
    print(f"First three records: {rows[:3]}")


if __name__ == "__main__":
    main()
