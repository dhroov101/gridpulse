from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import math


def parse_actual_load(xml_file):
    """
    Parse actual electricity load points from an ENTSO-E XML file.

    Args:
        xml_file (str | Path): Path to the actual-load XML file.

    Returns:
        list[dict]: Rows with Position, Timestamp (UTC), and Load (MW) fields.
    """
    root = ET.parse(xml_file).getroot()

    def child_text(element, name):
        for child in element:
            if child.tag.rsplit("}", 1)[-1] == name:
                if child.text is None:
                    break
                return child.text.strip()
        raise ValueError(f"Missing or empty <{name}> element in {xml_file}")

    actual_load_data = []
    for period in root.iter():
        if period.tag.rsplit("}", 1)[-1] != "Period":
            continue

        interval = next(
            (
                child
                for child in period
                if child.tag.rsplit("}", 1)[-1] == "timeInterval"
            ),
            None,
        )
        if interval is None:
            raise ValueError(f"Missing <timeInterval> in a Period in {xml_file}")

        start_text = child_text(interval, "start")
        start = datetime.fromisoformat(start_text.replace("Z", "+00:00"))
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        start = start.astimezone(timezone.utc)

        resolution = child_text(period, "resolution")
        match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", resolution)
        if match is None:
            raise ValueError(f"Unsupported period resolution {resolution!r}")
        hours, minutes, seconds = (int(value or 0) for value in match.groups())
        step = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        if step <= timedelta(0):
            raise ValueError(f"Period resolution must be positive: {resolution!r}")

        seen_positions = set()

        for point in period:
            if point.tag.rsplit("}", 1)[-1] != "Point":
                continue
            position = int(child_text(point, "position"))
            if position in seen_positions:
                raise ValueError(f"Duplicate point position: {position}")
            seen_positions.add(position)
            if position < 1:
                raise ValueError(f"Point position must be positive: {position}")
            load = float(child_text(point, "quantity"))
            if not math.isfinite(load):
                raise ValueError(f"Point load must be finite: {load}")
            timestamp = start + (position - 1) * step
            actual_load_data.append(
                {
                    "position": position,
                    "timestamp_utc": timestamp.isoformat(),
                    "Load_mw": load,
                }
            )

    return actual_load_data