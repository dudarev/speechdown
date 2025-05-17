"""Initialize command handler for speechdown CLI."""
from pathlib import Path
import logging

from speechdown.infrastructure.database import initialize_database
from speechdown.infrastructure.schema import SCHEMA
from speechdown.infrastructure.adapters.config_adapter import ConfigAdapter
from speechdown.presentation.cli.commands.common import SpeechDownPaths

__all__ = ["init"]


def init(directory: Path) -> int:
    """
    Initialize the speechdown project in the specified directory.

    Args:
        directory: The directory to initialize

    Returns:
        Exit code (0 for success)
    """
    try:
        speechdown_paths = SpeechDownPaths.from_working_directory(directory)

        if not speechdown_paths.speechdown_directory.exists():
            speechdown_paths.speechdown_directory.mkdir(parents=True)

        # Cache directory is no longer needed but kept for backward compatibility
        if not speechdown_paths.cache_dir.exists():
            speechdown_paths.cache_dir.mkdir(parents=True)

        if not speechdown_paths.db.exists():
            initialize_database(speechdown_paths.db, SCHEMA)
            print(f"Initialized speech-down project in {directory}")
        else:
            print("Database already exists. Initialization skipped.")

        config_adapter = ConfigAdapter.load_config_from_path(speechdown_paths.config, create=True)
        config_adapter.set_default_languages_if_not_set()
        config_adapter.set_default_output_dir_if_not_set()

        return 0
    except Exception as e:
        logging.error(f"Error during initialization: {e}")
        return 1
