from pathlib import Path
from typing import Protocol

from speechdown.domain.value_objects import Language


class ConfigPort(Protocol):
    languages: list[Language]
    output_dir: Path | str | None
    timestamp_extraction_enabled: bool
    timestamp_year_min: int
    timestamp_year_max: int
    timestamp_fallback_to_modification_time: bool

    def get_languages(self) -> list[Language]: ...

    def set_languages(self, languages: list[Language]) -> None: ...

    def get_output_dir(self) -> Path | None: ...

    def set_output_dir(self, output_dir: Path | str | None) -> None: ...

    def get_timestamp_extraction_enabled(self) -> bool: ...

    def set_timestamp_extraction_enabled(self, enabled: bool) -> None: ...

    def get_timestamp_year_min(self) -> int: ...

    def get_timestamp_year_max(self) -> int: ...

    def set_timestamp_year_range(self, year_min: int, year_max: int) -> None: ...
