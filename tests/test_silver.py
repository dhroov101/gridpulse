import sys
from pathlib import Path

import pandas as pd
import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from gridpulse.silver import build_silver_dataframe, write_silver_parquet


FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "sample_actual_load.xml"
)



def test_build_silver_dataframe():
    df = build_silver_dataframe(FIXTURE)

    assert list(df.columns) == ["position", "timestamp_utc", "load_mw"]
    assert len(df) == 3
    assert df["position"].dtype == "int64"
    assert str(df["timestamp_utc"].dtype) == "datetime64[ns, UTC]"
    assert pd.api.types.is_numeric_dtype(df["load_mw"])
    assert not df.isna().any().any()


def test_write_and_read_parquet(tmp_path):
    df = build_silver_dataframe(FIXTURE)
    output = tmp_path / "silver" / "actual_load.parquet"

    returned_path = write_silver_parquet(df, output)

    assert returned_path == output
    assert output.exists()

    restored = pd.read_parquet(output)
    pd.testing.assert_frame_equal(restored, df)
