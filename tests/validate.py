import sys
from pathlib import Path

# Add the project root to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from speechdown.cli.commands import transcribe, configure_logging

# Constants
TEST_DATA_DIR = Path(__file__).parent / "data"
DRY_RUN = False  # Set to True to avoid writing to DB


def main():
    """
    Run transcribe on the test data directory
    """
    print(f"Running validation on: {TEST_DATA_DIR}")
    configure_logging(debug_mode=True)
    transcribe(directory=TEST_DATA_DIR, dry_run=DRY_RUN)
    print("Validation complete")


if __name__ == "__main__":
    # Simple command line argument parsing
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python validate.py [--dry-run]")
        sys.exit(0)

    # Override dry run from command line if needed
    if "--dry-run" in sys.argv:
        DRY_RUN = True
        print("Dry run mode enabled")

    main()
