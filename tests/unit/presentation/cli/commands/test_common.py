import argparse
import pytest
from speechdown.presentation.cli.commands.common import add_common_arguments

def test_add_common_arguments_directory_default():
    """Test that --directory defaults to '.' when not provided."""
    parser = argparse.ArgumentParser()
    add_common_arguments(parser)
    # Test with minimal other required args if any, or empty list if none
    # For transcribe command, it might be just 'transcribe'
    # For init command, it might be just 'init'
    # We are testing common args, so let's assume no other args are strictly needed for this parser setup
    args = parser.parse_args([]) # No arguments provided
    assert args.directory == "."

def test_add_common_arguments_directory_provided():
    """Test that --directory uses the provided value."""
    parser = argparse.ArgumentParser()
    add_common_arguments(parser)
    args = parser.parse_args(["--directory", "test_dir"])
    assert args.directory == "test_dir"

    args = parser.parse_args(["-d", "another_dir"])
    assert args.directory == "another_dir"

# It's also good to test that the debug flag added by add_common_arguments
# (via add_debug_argument) has a default and can be set.
def test_add_common_arguments_debug_default():
    """Test that --debug defaults to False."""
    parser = argparse.ArgumentParser()
    add_common_arguments(parser)
    args = parser.parse_args([])
    assert args.debug is False

def test_add_common_arguments_debug_provided():
    """Test that --debug is True when provided."""
    parser = argparse.ArgumentParser()
    add_common_arguments(parser)
    args = parser.parse_args(["--debug"])
    assert args.debug is True
