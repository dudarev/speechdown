from dataclasses import dataclass
import json
from pathlib import Path
from speechdown.application.ports.config_port import ConfigPort
from speechdown.domain.value_objects import Language


DEFAULT_LANGUAGES = [Language("en"), Language("uk"), Language("ru")]
DEFAULT_OUTPUT_DIR = "transcripts"
DEFAULT_MODEL_NAME = "tiny"


@dataclass
class ConfigAdapter(ConfigPort):
    languages: list[Language]
    path: Path
    output_dir: Path | str | None = None
    model_name: str | None = None

    # --- Getters and Setters ---
    def get_languages(self) -> list[Language]:
        return self.languages

    def set_languages(self, languages: list[Language]) -> None:
        self.languages = languages
        self._save_config()

    def get_output_dir(self) -> Path | None:
        if self.output_dir is None:
            return None
        if isinstance(self.output_dir, str):
            return Path(self.output_dir)
        return self.output_dir

    def set_output_dir(self, output_dir: Path | str | None) -> None:
        self.output_dir = output_dir
        self._save_config()

    def get_model_name(self) -> str:
        if self.model_name is None:
            return DEFAULT_MODEL_NAME
        return self.model_name

    def set_model_name(self, model_name: str | None) -> None:
        self.model_name = model_name
        self._save_config()

    # --- Default Setters ---
    def set_default_languages_if_not_set(self):
        if not self.languages:
            self.languages = list(DEFAULT_LANGUAGES)  # Make a copy of DEFAULT_LANGUAGES
            self._save_config()

    def set_default_output_dir_if_not_set(self):
        if not self.output_dir:
            self.output_dir = DEFAULT_OUTPUT_DIR  # DEFAULT_OUTPUT_DIR is already a string
            self._save_config()

    def set_default_model_name_if_not_set(self):
        if self.model_name is None:
            self.model_name = DEFAULT_MODEL_NAME
            self._save_config()

    # --- Config Save/Load ---
    def _save_config(self) -> None:
        """Save current configuration to the config file."""
        with self.path.open("w") as file:
            config_data: dict[str, list[str] | str | int | bool] = {
                "languages": [language.code for language in self.languages],
            }
            if self.output_dir is not None:
                output_dir_str = (
                    str(self.output_dir) if isinstance(self.output_dir, Path) else self.output_dir
                )
                config_data["output_dir"] = output_dir_str
            if self.model_name is not None:
                config_data["model_name"] = self.model_name
            json.dump(config_data, file)

    @classmethod
    def load_config_from_path(cls, path: Path, create=False) -> "ConfigAdapter":
        if not path.exists() and not create:
            raise FileNotFoundError(f"Config file not found at {path}")
        if create:
            with path.open("w") as file:
                json.dump(
                    {
                        "languages": [],
                        "output_dir": DEFAULT_OUTPUT_DIR,
                        "model_name": DEFAULT_MODEL_NAME,
                    },
                    file,
                )
        with path.open("r") as file:
            config_data = json.load(file)
        languages = [Language(language) for language in config_data.get("languages", [])]
        output_dir = config_data.get("output_dir")
        model_name = config_data.get("model_name")
        return cls(
            languages=languages,
            path=path,
            output_dir=output_dir,
            model_name=model_name,
        )
