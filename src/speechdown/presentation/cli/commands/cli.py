"""Command line interface for speechdown."""
import argparse
import logging
import sys
from pathlib import Path

from speechdown.presentation.cli.commands.common import (
    add_common_arguments, 
    add_debug_argument, 
    add_transcribe_arguments,
    configure_logging
)
from speechdown.presentation.cli.commands.init import init
from speechdown.presentation.cli.commands.transcribe import transcribe
from speechdown.presentation.cli.commands.config import config

__all__ = ["cli"]


def cli() -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(description="SpeechDown CLI")
    subparsers = parser.add_subparsers(dest="command")
    add_debug_argument(parser)

    parser_init = subparsers.add_parser("init", help="Initialize a SpeechDown project")
    add_common_arguments(parser_init)
    
    parser_config = subparsers.add_parser("config", help="Configure the SpeechDown project")
    add_common_arguments(parser_config)

    parser_transcribe = subparsers.add_parser("transcribe", help="Transcribe audio files")
    add_transcribe_arguments(parser_transcribe)

    parser_config.add_argument(
        "--output-dir", 
        type=str, 
        help="Set the output directory for transcription files"
    )
    parser_config.add_argument(
        "--languages",
        type=str,
        help="Set a comma-separated list of language codes (e.g., 'en,fr,de')"
    )
    parser_config.add_argument(
        "--add-language",
        type=str,
        help="Add a single language code to the configuration"
    )
    parser_config.add_argument(
        "--remove-language",
        type=str, 
        help="Remove a single language code from the configuration"
    )
    parser_config.add_argument(
        "--model-name",
        type=str,
        help="Set the default model name for transcription (e.g., 'tiny', 'base', 'small', 'medium', 'large', 'turbo')"
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
        return config(
            directory=Path(args.directory), 
            output_dir=args.output_dir,
            languages=args.languages,
            add_language=args.add_language,
            remove_language=args.remove_language,
            model_name=args.model_name
        )
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(cli())
