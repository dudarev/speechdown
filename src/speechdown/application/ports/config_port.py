from pathlib import Path
from typing import Protocol

from speechdown.domain.value_objects import Language


class ConfigPort(Protocol):
    languages: list[Language]
    output_dir: Path | str | None

    def get_languages(self) -> list[Language]: ...

    def set_languages(self, languages: list[Language]) -> None: ...
    
    def get_output_dir(self) -> Path | None: ...
    
    def set_output_dir(self, output_dir: Path | str | None) -> None: ...
