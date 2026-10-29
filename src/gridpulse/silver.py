from pathlib import Path

import pandas as pd

from gridpulse.xml_loader import parse_actual_load


EXPECTED_COLUMNS = ["position", "timestamp_utc", "load_mw"]


def build_silver_dataframe(xml_file: str | Path) -> pd.DataFrame:
    """Parse raw XML and return validated, analytics-ready load data."""
    records = parse_actual_load(xml_file)

    if not records:
        raise ValueError("No actual load records found")

    df = pd.DataFrame(records, columns=EXPECTED_COLUMNS)

    df["position"] = pd.to_numeric(df["position"], errors="raise").astype("int64")
    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"], utc=True, errors="raise"
    ).astype("datetime64[ns, UTC]")
    df["load_mw"] = pd.to_numeric(df["load_mw"], errors="raise")

    if df["position"].duplicated().any():
        raise ValueError("Duplicate point positions found")

    if df["timestamp_utc"].duplicated().any():
        raise ValueError("Duplicate timestamps found")

    

    if df[EXPECTED_COLUMNS].isna().any().any():
        raise ValueError("Silver data contains missing values")

    if not df["load_mw"].map(lambda value: pd.notna(value) and abs(value) != float("inf")).all():
        raise ValueError("Load values must be finite")

    return df.sort_values("timestamp_utc").reset_index(drop=True)


def write_silver_parquet(
    df: pd.DataFrame, output_file: str | Path
) -> Path:
    """Write a Silver DataFrame to Parquet and return its path."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(output_path, index=False)
    return output_path
