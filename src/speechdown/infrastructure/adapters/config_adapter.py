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
    timestamp_extraction_enabled: bool = True
    timestamp_year_min: int = 2000
    timestamp_year_max: int = 2099
    timestamp_fallback_to_modification_time: bool = True

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

    def get_timestamp_extraction_enabled(self) -> bool:
        return self.timestamp_extraction_enabled

    def set_timestamp_extraction_enabled(self, enabled: bool) -> None:
        self.timestamp_extraction_enabled = enabled
        self._save_config()

    def get_timestamp_year_min(self) -> int:
        return self.timestamp_year_min

    def get_timestamp_year_max(self) -> int:
        return self.timestamp_year_max

    def set_timestamp_year_range(self, year_min: int, year_max: int) -> None:
        self.timestamp_year_min = year_min
        self.timestamp_year_max = year_max
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
            config_data["timestamp_extraction_enabled"] = self.timestamp_extraction_enabled
            config_data["timestamp_year_min"] = self.timestamp_year_min
            config_data["timestamp_year_max"] = self.timestamp_year_max
            config_data["timestamp_fallback_to_modification_time"] = (
                self.timestamp_fallback_to_modification_time
            )
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
        timestamp_extraction_enabled = config_data.get("timestamp_extraction_enabled", True)
        timestamp_year_min = config_data.get("timestamp_year_min", 2000)
        timestamp_year_max = config_data.get("timestamp_year_max", 2099)
        timestamp_fallback_to_modification_time = config_data.get(
            "timestamp_fallback_to_modification_time", True
        )
        return cls(
            languages=languages,
            path=path,
            output_dir=output_dir,
            model_name=model_name,
            timestamp_extraction_enabled=timestamp_extraction_enabled,
            timestamp_year_min=timestamp_year_min,
            timestamp_year_max=timestamp_year_max,
            timestamp_fallback_to_modification_time=timestamp_fallback_to_modification_time,
        )
