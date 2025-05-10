import argparse
from dataclasses import dataclass
import logging
from pathlib import Path
import sys

from speechdown.infrastructure.adapters.audio_file_adapter import (
    AudioFileAdapter,
)
from speechdown.infrastructure.adapters.config_adapter import ConfigAdapter
from speechdown.infrastructure.adapters.file_output_adapter import FileOutputAdapter
from speechdown.infrastructure.database import initialize_database
from speechdown.infrastructure.schema import SCHEMA
from speechdown.application.services.transcription_service import (
    TranscriptionService,
)
from speechdown.infrastructure.adapters.whisper_transcriber_adapter import (
    WhisperTranscriberAdapter,
)
from speechdown.infrastructure.adapters.whisper_model_adapter import (
    WhisperModelAdapter,
)
from speechdown.infrastructure.adapters.repository_adapter import (
    SQLiteRepositoryAdapter,
)


def configure_logging(debug_mode: bool) -> None:
    """Configure logging level based on debug flag."""
    logging.basicConfig(
        level=logging.DEBUG if debug_mode else logging.INFO,
        format="%(name)s - %(levelname)s - %(message)s",
    )


@dataclass(frozen=True, kw_only=True)
class SpeechDownPaths:
    working_directory: Path
    speechdown_directory: Path
    db: Path
    config: Path
    cache_dir: Path

    @classmethod
    def from_working_directory(cls, working_directory: Path):
        speechdown_directory = Path(working_directory) / ".speechdown"
        return cls(
            working_directory=working_directory,
            speechdown_directory=speechdown_directory,
            db=speechdown_directory / "speechdown.db",
            config=speechdown_directory / "config.json",
            cache_dir=speechdown_directory / "cache",
        )


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


def transcribe(directory: Path, dry_run: bool, ignore_existing: bool) -> int:
    """
    Transcribe audio files in the specified directory.

    Args:
        directory: The directory containing audio files
        dry_run: Whether to perform a dry run without saving to database
        ignore_existing: Whether to ignore existing transcriptions and perform new ones

    Returns:
        Exit code (0 for success)
    """
    try:
        speechdown_paths = SpeechDownPaths.from_working_directory(directory)

        audio_file_adapter = AudioFileAdapter()
        config_adapter = ConfigAdapter.load_config_from_path(speechdown_paths.config)
        config_adapter.set_default_output_dir_if_not_set()
        output_adapter = FileOutputAdapter(config_adapter)
        repository_adapter = SQLiteRepositoryAdapter(speechdown_paths.db)

        # Create model and transcriber
        whisper_model = WhisperModelAdapter()
        transcriber_adapter = WhisperTranscriberAdapter(whisper_model)

        transcription_service = TranscriptionService(
            audio_file_port=audio_file_adapter,
            config_port=config_adapter,
            output_port=output_adapter,
            repository_port=repository_adapter,
            transcriber_port=transcriber_adapter,
        )

        audio_files = transcription_service.collect_audio_files(directory)
        transcriptions = transcription_service.transcribe_audio_files(
            audio_files, ignore_existing=ignore_existing
        )
        # get existing output
        # update transcriptions based on existing output
        # update the output
        transcription_service.output_transcriptions(transcriptions)

        if dry_run:
            print("Dry run mode enabled. No changes to the database were made.")
        else:
            print(f"Processed {len(transcriptions)} audio file(s)")

        return 0
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        return 1


def add_debug_argument(parser) -> None:
    """Add debug argument to parser."""
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode",
    )


def add_common_arguments(parser) -> None:
    """Add common arguments to parser."""
    add_debug_argument(parser)
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        required=True,
        help="Directory to work with",
    )


def add_transcribe_arguments(parser) -> None:
    """Add transcribe-specific arguments to parser."""
    add_common_arguments(parser)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the transcription process without making any changes",
    )
    parser.add_argument(
        "--ignore-existing",
        action="store_true",
        help="Ignore existing transcriptions and perform new ones",
    )


def config(directory: Path, output_dir: str | None = None) -> int:
    """
    Configure the speechdown project settings.

    Args:
        directory: The directory containing the speechdown project
        output_dir: The directory to store transcription output files

    Returns:
        Exit code (0 for success)
    """
    try:
        speechdown_paths = SpeechDownPaths.from_working_directory(directory)
        config_adapter = ConfigAdapter.load_config_from_path(speechdown_paths.config)
        
        if output_dir is not None:
            config_adapter.set_output_dir(output_dir)
            print(f"Output directory set to: {output_dir}")
            
        # Display current configuration
        print("Current configuration:")
        print(f"  Languages: {', '.join([lang.code for lang in config_adapter.get_languages()])}")
        output_dir_value = config_adapter.get_output_dir()
        print(f"  Output directory: {output_dir_value if output_dir_value else 'Not set'}")
        
        return 0
    except Exception as e:
        logging.error(f"Error during configuration: {e}")
        return 1


def cli() -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(description="SpeechDown CLI")
    subparsers = parser.add_subparsers(dest="command")
    add_debug_argument(parser)

    parser_init = subparsers.add_parser("init", help="Initialize the speechdown project")
    add_common_arguments(parser_init)

    parser_transcribe = subparsers.add_parser("transcribe", help="Transcribe audio files")
    add_transcribe_arguments(parser_transcribe)
    
    parser_config = subparsers.add_parser("config", help="Configure the speechdown project")
    add_common_arguments(parser_config)
    parser_config.add_argument(
        "--output-dir", 
        type=str, 
        help="Set the output directory for transcription files"
    )

    args = parser.parse_args()

    # Configure logging based on the debug flag
    configure_logging(args.debug)

    if args.command == "init":
        return init(Path(args.directory))
    elif args.command == "transcribe":
        if args.debug:
            logging.debug("Debug mode enabled")
        return transcribe(Path(args.directory), args.dry_run, args.ignore_existing)
    elif args.command == "config":
        return config(Path(args.directory), args.output_dir)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(cli())
