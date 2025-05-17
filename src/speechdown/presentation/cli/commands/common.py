"""Common utilities and data structures for CLI commands."""
from dataclasses import dataclass
import logging
from pathlib import Path
import argparse

__all__ = ["configure_logging", "SpeechDownPaths", "add_debug_argument", 
          "add_common_arguments", "add_transcribe_arguments"]


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


def add_debug_argument(parser: argparse.ArgumentParser) -> None:
    """Add debug argument to parser."""
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode",
    )


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add common arguments to parser."""
    add_debug_argument(parser)
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        required=True,
        help="Directory to work with",
    )


def add_transcribe_arguments(parser: argparse.ArgumentParser) -> None:
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
