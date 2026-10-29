
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from gridpulse.xml_loader import parse_day_ahead_forecast


FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "sample_forecast.xml"
)


def test_parse_day_ahead_forecast():
    rows = parse_day_ahead_forecast(FIXTURE)

    assert len(rows) == 3
    assert rows[0] == {
        "position": 1,
        "timestamp_utc": "2026-10-18T22:00:00+00:00",
        "forecast_load_mw": 10867.514,
    }
    assert rows[1]["forecast_load_mw"] == 10913.892
    assert rows[2]["forecast_load_mw"] == 10929.885
