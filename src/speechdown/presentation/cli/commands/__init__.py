"""CLI commands for speechdown."""
from speechdown.presentation.cli.commands.cli import cli
from speechdown.presentation.cli.commands.init import init
from speechdown.presentation.cli.commands.transcribe import transcribe
from speechdown.presentation.cli.commands.config import config
from speechdown.presentation.cli.commands.common import configure_logging

__all__ = ["cli", "init", "transcribe", "configure_logging", "config"]
