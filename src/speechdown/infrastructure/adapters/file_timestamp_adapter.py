import re
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from speechdown.application.ports.timestamp_port import TimestampPort


TIMESTAMP_PATTERNS = [
    {
        "regex": re.compile(
            r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"
        ),
        "is_yy": False,
        "name": "YYYYMMDD_HHMMSS",
    },
    {
        "regex": re.compile(
            r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}) (?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"
        ),
        "is_yy": False,
        "name": "YYYYMMDD HHMMSS",
    },
    {
        "regex": re.compile(
            r"(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"
        ),
        "is_yy": True,
        "name": "YYMMDD_HHMMSS",
    },
]

VALID_YEAR_RANGE = (2000, 2099)


@dataclass
class FileTimestampAdapter(TimestampPort):
    """Adapter for extracting timestamps from filenames with fallbacks."""

    def get_timestamp(self, path: Path) -> datetime:
        """Return timestamp extracted from filename or fallback to file mtime."""
        logger = logging.getLogger(__name__)

        extracted = self._extract_from_filename(path.name)
        if extracted:
            logger.debug("Extracted timestamp from filename %s: %s", path.name, extracted)
            return extracted

        fallback = self._get_file_fallback_time(path)
        logger.debug("Using fallback modification time for %s: %s", path.name, fallback)
        return fallback

    def _extract_from_filename(self, filename: str) -> Optional[datetime]:
        """Extract a timestamp from the filename using backwards search."""
        for config in TIMESTAMP_PATTERNS:
            pattern: re.Pattern[str] = config["regex"]  # type: ignore[assignment]
            is_yy = bool(config["is_yy"])
            match = self._search_pattern_backwards(filename, pattern)
            if match:
                try:
                    year, month, day, hour, minute, second = self._validate_timestamp_components(
                        match, is_yy
                    )
                    return datetime(year, month, day, hour, minute, second)
                except (ValueError, OverflowError) as e:
                    logging.getLogger(__name__).debug(
                        "Invalid date components in %s: %s", filename, e
                    )
                    continue
        return None

    def _search_pattern_backwards(self, text: str, pattern: re.Pattern) -> Optional[Dict[str, str]]:
        """Search for pattern from the end of the string backwards."""
        for i in range(len(text) - 1, -1, -1):
            match = pattern.match(text[i:])
            if match:
                return match.groupdict()
        return None

    def _validate_timestamp_components(
        self, parts: Dict[str, str], is_yy_format: bool
    ) -> tuple[int, int, int, int, int, int]:
        year_str = parts["year"]
        if is_yy_format:
            if not (0 <= int(year_str) <= 99):
                raise ValueError(f"2-digit year '{year_str}' out of 00-99 range.")
            year = int("20" + year_str)
        else:
            if not (1900 <= int(year_str) <= 2099):
                raise ValueError(f"4-digit year '{year_str}' out of 1900-2099 range.")
            year = int(year_str)

        if not (VALID_YEAR_RANGE[0] <= year <= VALID_YEAR_RANGE[1]):
            raise ValueError(f"Year {year} not in valid range {VALID_YEAR_RANGE}")

        month = int(parts["month"])
        day = int(parts["day"])
        hour = int(parts["hour"])
        minute = int(parts["minute"])
        second = int(parts["second"])

        if not (1 <= month <= 12):
            raise ValueError(f"Month {month} not in range 1-12")
        if not (1 <= day <= 31):
            raise ValueError(f"Day {day} not in range 1-31")
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour {hour} not in range 0-23")
        if not (0 <= minute <= 59):
            raise ValueError(f"Minute {minute} not in range 0-59")
        if not (0 <= second <= 59):
            raise ValueError(f"Second {second} not in range 0-59")

        return year, month, day, hour, minute, second

    def _get_file_fallback_time(self, path: Path) -> datetime:
        """Return the file modification time."""
        return datetime.fromtimestamp(path.stat().st_mtime)
