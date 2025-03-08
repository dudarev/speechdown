import argparse
import logging
import os
from typing import List
from pathlib import Path

from speechdown.infrastructure.adapters.file_system_transcription_cache_adapter import (
    FileSystemTranscriptionCacheAdapter,
)

logger = logging.getLogger(__name__)


def add_clear_cache_parser(subparsers):
    """Add clear-cache command parser to the given subparsers object."""
    parser = subparsers.add_parser(
        "clear-cache",
        help="Clear the transcription cache",
        description="Remove cached transcriptions to free up space or force regeneration.",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=None,
        help="Directory containing the .speechdown/cache folder to clear",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Remove all cached transcriptions",
    )
    parser.add_argument(
        "--older-than",
        type=int,
        metavar="DAYS",
        help="Remove transcriptions older than specified days",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.set_defaults(func=clear_cache_command)


def clear_cache_command(args: argparse.Namespace) -> int:
    """
    Execute the clear-cache command.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success)
    """
    # Determine cache directory path
    cache_dir = _resolve_cache_directory(args.directory)
    if not cache_dir:
        print("Error: Cannot find or create .speechdown/cache directory")
        return 1

    cache = FileSystemTranscriptionCacheAdapter(base_dir=cache_dir)

    # Validate arguments
    if not args.all and args.older_than is None:
        print("Error: Must specify either --all or --older-than")
        return 1

    older_than = int(args.older_than) if args.older_than is not None else None

    # If dry run, just list the files that would be deleted
    if args.dry_run:
        try:
            files_to_delete = _get_files_to_delete(cache, older_than)
            if not files_to_delete:
                print("No cache files would be deleted.")
            else:
                print(f"Would delete {len(files_to_delete)} cache files:")
                for file in files_to_delete:
                    print(f"  - {file}")
            return 0
        except Exception as e:
            logger.error(f"Error during dry run: {e}")
            print(f"Error during dry run: {e}")
            return 1

    # Actual deletion
    try:
        deleted_files = cache.clear_cache(older_than_days=older_than)
        if not deleted_files:
            print("No cache files were deleted.")
        else:
            print(f"Deleted {len(deleted_files)} cache files.")
        return 0
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        print(f"Error clearing cache: {e}")
        return 1


def _resolve_cache_directory(directory: str | None) -> Path | None:
    """
    Resolve the cache directory path based on the provided directory.

    Args:
        directory: User-specified directory containing .speechdown/cache
                  If None, uses current directory

    Returns:
        Path to the cache directory or None if it doesn't exist and can't be created
    """
    if directory is None:
        base_path = Path.cwd()
    else:
        base_path = Path(directory)

    if not base_path.exists() or not base_path.is_dir():
        logger.error(f"Directory not found: {base_path}")
        return None

    cache_dir = base_path / ".speechdown" / "cache"
    try:
        os.makedirs(cache_dir, exist_ok=True)
        logger.debug(f"Using cache directory: {cache_dir}")
        return cache_dir
    except Exception as e:
        logger.error(f"Failed to create cache directory: {cache_dir}, error: {e}")
        return None


def _get_files_to_delete(
    cache: FileSystemTranscriptionCacheAdapter, older_than_days: int | None = None
) -> List[Path]:
    """
    Get list of cache files that would be deleted based on criteria.
    Used for dry run mode.

    Args:
        cache: The cache instance
        older_than_days: Filter to files older than this many days

    Returns:
        List of file paths that would be deleted
    """
    import time

    files_to_delete = []

    # Calculate cutoff timestamp if needed
    cutoff_timestamp = None
    if older_than_days is not None:
        cutoff_timestamp = time.time() - (older_than_days * 86400)  # 86400 seconds in a day

    for cache_file in cache.base_dir.glob("*.txt"):
        delete_file = True

        # Check file age if cutoff specified
        if cutoff_timestamp is not None:
            file_mtime = cache_file.stat().st_mtime
            if file_mtime > cutoff_timestamp:
                delete_file = False

        if delete_file:
            files_to_delete.append(cache_file)

    return files_to_delete
