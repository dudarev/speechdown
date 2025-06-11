from pathlib import Path
from typing import Protocol
from datetime import datetime


class TimestampPort(Protocol):
    def get_timestamp(self, path: Path) -> datetime:
        """Return timestamp extracted from filename or fallback to file mtime."""
        ...
