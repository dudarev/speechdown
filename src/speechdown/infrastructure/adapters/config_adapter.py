from dataclasses import dataclass
import json
from pathlib import Path
from speechdown.application.ports.config_port import ConfigPort
from speechdown.domain.value_objects import Language


DEFAULT_LANGUAGES = [Language("en"), Language("uk"), Language("ru")]


@dataclass
class ConfigAdapter(ConfigPort):
    languages: list[Language]
    path: Path

    def get_languages(self) -> list[Language]:
        return self.languages

    def set_languages(self, languages: list[Language]) -> None:
        self.languages = languages
        with self.path.open("w") as file:
            config_data = {
                "languages": [language.code for language in languages],
            }
            json.dump(config_data, file)

    @classmethod
    def load_config_from_path(cls, path: Path, create=False) -> "ConfigAdapter":
        if not path.exists() and not create:
            raise FileNotFoundError(f"Config file not found at {path}")
        if create:
            with path.open("w") as file:
                json.dump({"languages": []}, file)
        with path.open("r") as file:
            config_data = json.load(file)
        languages = [Language(language) for language in config_data["languages"]]
        return cls(languages=languages, path=path)

    def set_default_languages_if_not_set(self):
        if not self.languages:
            self.languages = DEFAULT_LANGUAGES
            self.set_languages(DEFAULT_LANGUAGES)
