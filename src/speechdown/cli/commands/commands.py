import argparse
from dataclasses import dataclass
import logging
from pathlib import Path
from speechdown.infrastructure.adapters.audio_file_adapter import (
    AudioFileAdapter,
)
from speechdown.infrastructure.adapters.config_adapter import ConfigAdapter
from speechdown.infrastructure.adapters.output_adapter import MarkdownOutputAdapter
from speechdown.infrastructure.database import initialize_database
from speechdown.commons.schema import SCHEMA
from speechdown.application.services.speechdown_service import (
    SpeechDownService,
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
from speechdown.infrastructure.adapters.file_system_transcription_cache import (
    FileSystemTranscriptionCache,
)
from speechdown.cli.commands.clear_cache import add_clear_cache_parser


def configure_logging(debug_mode):
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

    @classmethod
    def from_working_directory(cls, working_directory: Path):
        speechdown_directory = Path(working_directory) / ".speechdown"
        return cls(
            working_directory=working_directory,
            speechdown_directory=speechdown_directory,
            db=speechdown_directory / "speechdown.db",
            config=speechdown_directory / "config.json",
        )


def init(directory):
    """
    Initialize the speechdown project in the specified directory.
    """
    directory = Path(directory)
    speechdown_paths = SpeechDownPaths.from_working_directory(directory)

    if not speechdown_paths.speechdown_directory.exists():
        speechdown_paths.speechdown_directory.mkdir(parents=True)

    if not speechdown_paths.db.exists():
        initialize_database(speechdown_paths.db, SCHEMA)
        print(f"Initialized speech-down project in {directory}")
    else:
        print("Database already exists. Initialization skipped.")

    config_adapter = ConfigAdapter.load_config_from_path(speechdown_paths.config, create=True)
    config_adapter.set_default_languages_if_not_set()


def transcribe(directory: Path, dry_run: bool, force: bool):
    speechdown_paths = SpeechDownPaths.from_working_directory(directory)

    audio_file_adapter = AudioFileAdapter()
    config_adapter = ConfigAdapter.load_config_from_path(speechdown_paths.config)
    output_adapter = MarkdownOutputAdapter()
    repository_adapter = SQLiteRepositoryAdapter(speechdown_paths.db)
    cache_adapter = FileSystemTranscriptionCache()

    # Create model and transcriber
    whisper_model = WhisperModelAdapter()
    transcriber_adapter = WhisperTranscriberAdapter(whisper_model)

    speechdown_service = SpeechDownService(
        audio_file_port=audio_file_adapter,
        config_port=config_adapter,
        output_port=output_adapter,
        repository_port=repository_adapter,
        transcriber_port=transcriber_adapter,
        cache_port=cache_adapter,
    )

    audio_files = speechdown_service.collect_audio_files(directory)
    transcriptions = speechdown_service.transcribe_audio_files(audio_files, force=force)
    # get existing output
    # update transcriptions based on existing output
    # update the output
    speechdown_service.output_transcriptions(transcriptions)

    if dry_run:
        print("Dry run mode enabled. No changes to the database will be made.")
    else:
        for transcription in transcriptions:
            repository_adapter.save_transcription(transcription)


def add_debug_argument(parser):
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode",
    )


def add_common_arguments(parser):
    add_debug_argument(parser)
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        required=True,
        help="Directory to work with",
    )


def add_transcribe_arguments(parser):
    add_common_arguments(parser)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the transcription process without making any changes",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force new transcriptions even if cached versions exist",
    )


def cli():
    parser = argparse.ArgumentParser(description="SpeechDown CLI")
    subparsers = parser.add_subparsers(dest="command")
    add_debug_argument(parser)

    parser_init = subparsers.add_parser("init", help="Initialize the speechdown project")
    add_common_arguments(parser_init)

    parser_transcribe = subparsers.add_parser("transcribe", help="Transcribe audio files")
    add_transcribe_arguments(parser_transcribe)

    # Add clear-cache command
    add_clear_cache_parser(subparsers)

    args = parser.parse_args()

    # Configure logging based on the debug flag
    configure_logging(args.debug)

    if args.command == "init":
        init(args.directory)
    elif args.command == "transcribe":
        if args.debug:
            logging.debug("Debug mode enabled")
            print("Debug mode enabled")
        transcribe(Path(args.directory), args.dry_run, args.force)
    elif args.command == "clear-cache":
        return args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
