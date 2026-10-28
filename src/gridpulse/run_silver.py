from pathlib import Path

from gridpulse.silver import build_silver_dataframe, write_silver_parquet


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_FILE = PROJECT_ROOT / "data" / "silver" / "actual_load.parquet"


def main():
    xml_files = list(BRONZE_DIR.rglob("*ACTUAL_TOTAL_LOAD*.xml"))

    if len(xml_files) != 1:
        raise RuntimeError(
            f"Expected exactly one actual-load XML file, found {len(xml_files)}"
        )

    df = build_silver_dataframe(xml_files[0])
    write_silver_parquet(df, SILVER_FILE)

    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"Time range: {df['timestamp_utc'].min()} to {df['timestamp_utc'].max()}")
    print(f"Missing values: {int(df.isna().sum().sum())}")
    print(f"Saved to: {SILVER_FILE}")


if __name__ == "__main__":
    main()
