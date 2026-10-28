from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gridpulse.xml_loader import parse_actual_load


ACTUAL_LOAD_XML = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "sample_actual_load.xml"
)

def write_test_xml(tmp_path, points):
    points_xml = "".join(
        f"<Point><position>{position}</position><quantity>{quantity}</quantity></Point>"
        for position, quantity in points
    )

    xml_content = f"""<?xml version="1.0"?>
    <GL_MarketDocument>
      <TimeSeries>
        <Period>
          <timeInterval>
            <start>2026-10-18T22:00Z</start>
            <end>2026-10-18T22:30Z</end>
          </timeInterval>
          <resolution>PT15M</resolution>
          {points_xml}
        </Period>
      </TimeSeries>
    </GL_MarketDocument>
    """

    xml_file = tmp_path / "test_load.xml"
    xml_file.write_text(xml_content, encoding="utf-8")
    return xml_file


def test_parse_actual_load():
    rows = parse_actual_load(ACTUAL_LOAD_XML)

    assert len(rows) == 3
    assert rows[:3] == [
        {
            "position": 1,
            "timestamp_utc": "2026-10-18T22:00:00+00:00",
            "Load_mw": 9489.796,
        },
        {
            "position": 2,
            "timestamp_utc": "2026-10-18T22:15:00+00:00",
            "Load_mw": 9610.646,
        },
        {
            "position": 3,
            "timestamp_utc": "2026-10-18T22:30:00+00:00",
            "Load_mw": 9595.946,
        },
    ]
    assert rows[-1] == {
        "position": 3,
        "timestamp_utc": "2026-10-18T22:30:00+00:00",
        "Load_mw": 9595.946,
    }

def test_rejects_non_finite_load(tmp_path):
    xml_file = write_test_xml(tmp_path, [(1, "NaN")])

    with pytest.raises(ValueError, match="finite"):
        parse_actual_load(xml_file)
def test_out_of_order_positions(tmp_path):
    xml_file = write_test_xml(
        tmp_path,
        [(2, "9610.646"), (1, "9489.796")],
    )

    with pytest.raises(ValueError, match="Points must be in ascending order by position"):
        parse_actual_load(xml_file)

def test_rejects_missing_postion(tmp_path):
    xml_file = write_test_xml(
        tmp_path,
        [(1, "9489.796"), (3, "9595.946")],
    )

    with pytest.raises(ValueError, match="Missing point position"):
        parse_actual_load(xml_file)


def test_rejects_missing_positions(tmp_path):
    xml_file = write_test_xml(
        tmp_path,
        [(1, "9489.796"), (3, "9595.946")],
    )

    with pytest.raises(ValueError, match="Missing point position"):
        parse_actual_load(xml_file)


def test_rejects_duplicate_positions(tmp_path):
    xml_file = write_test_xml(
        tmp_path,
        [(1, "9489.796"), (1, "9610.646")],
    )

    with pytest.raises(ValueError, match="Duplicate point position"):
        parse_actual_load(xml_file)