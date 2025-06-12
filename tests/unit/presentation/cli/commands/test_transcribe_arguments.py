import argparse
from speechdown.presentation.cli.commands.common import add_transcribe_arguments


def test_within_hours_default_none():
    parser = argparse.ArgumentParser()
    add_transcribe_arguments(parser)
    args = parser.parse_args([])
    assert args.within_hours is None


def test_within_hours_parsed():
    parser = argparse.ArgumentParser()
    add_transcribe_arguments(parser)
    args = parser.parse_args(["--within-hours", "12"])
    assert args.within_hours == 12.0
