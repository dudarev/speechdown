from typing import Protocol

from speechdown.domain.value_objects import Language


class ConfigPort(Protocol):
    languages: list[Language]

    def get_languages(self) -> list[Language]: ...

    def set_languages(self, languages: list[Language]) -> None: ...
