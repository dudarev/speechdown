import sys
from speechdown.presentation.cli.commands import cli

# Make cli available at module level for entry point
__all__ = ["cli"]


def main():
    """Main entry point for the speechdown CLI."""
    return cli()


if __name__ == "__main__":
    sys.exit(main())
