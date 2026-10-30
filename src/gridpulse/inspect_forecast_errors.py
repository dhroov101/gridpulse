
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE = PROJECT_ROOT / "data" / "gold" / "forecast_comparison.parquet"


def main():
    df = pd.read_parquet(FILE)

    print("Largest absolute errors:")
    print(
        df.assign(abs_error=df["error_mw"].abs())
        .nlargest(10, "abs_error")[
            [
                "timestamp_utc",
                "load_mw",
                "forecast_load_mw",
                "error_mw",
            ]
        ]
        .to_string(index=False)
    )

    print("\nError distribution:")
    print(df["error_mw"].describe().round(2).to_string())

    print("\nForecast vs actual summary:")
    print(
        df[["load_mw", "forecast_load_mw"]]
        .agg(["mean", "min", "max"])
        .round(2)
        .to_string()
    )


if __name__ == "__main__":
    main()
