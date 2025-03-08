import hashlib
import logging
import os
from pathlib import Path
from typing import List

from speechdown.application.ports.transcription_cache_port import TranscriptionCachePort
from speechdown.domain.entities import AudioFile, Transcription, CachedTranscription

logger = logging.getLogger(__name__)


class FileSystemTranscriptionCacheAdapter(TranscriptionCachePort):
    """File system implementation of the transcription cache."""

    def __init__(self, base_dir: str | Path):
        """
        Initialize the file system cache.

        Args:
            base_dir: Base directory for the cache. Should be a .speechdown/cache directory
        """
        self.base_dir = self._validate_cache_dir(base_dir)
        self._ensure_cache_dir()

    def _validate_cache_dir(self, base_dir: str | Path) -> Path:
        """
        Validate that the given directory is a proper .speechdown/cache directory.

        Args:
            base_dir: The directory to validate

        Returns:
            Path object for the validated directory

        Raises:
            ValueError: If directory doesn't end with .speechdown/cache
        """
        path = Path(base_dir)
        parts = path.parts

        # Check if path ends with .speechdown/cache
        if len(parts) < 2 or parts[-2] != ".speechdown" or parts[-1] != "cache":
            raise ValueError(f"Cache directory must end with .speechdown/cache, got: {path}")

        return path

    def _ensure_cache_dir(self) -> None:
        """Create the cache directory if it doesn't exist."""
        os.makedirs(self.base_dir, exist_ok=True)
        logger.debug(f"Cache directory: {self.base_dir}")

    def _compute_file_hash(self, audio_file: AudioFile) -> str:
        """
        Compute SHA-256 hash of an audio file.

        Args:
            audio_file: The audio file to hash

        Returns:
            The SHA-256 hash as a hexadecimal string
        """
        try:
            with open(audio_file.path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                logger.debug(f"Computed hash {file_hash} for {audio_file.path}")
                return file_hash
        except (IOError, OSError) as e:
            logger.error(f"Error computing hash for {audio_file.path}: {e}")
            raise

    def _get_cache_path(self, audio_file: AudioFile) -> Path:
        """
        Get the cache file path for an audio file.

        Args:
            audio_file: The audio file to get the cache path for

        Returns:
            Path to the cache file
        """
        file_hash = self._compute_file_hash(audio_file)
        return self.base_dir / f"{file_hash}.txt"

    def get_cached_transcription(self, audio_file: AudioFile) -> CachedTranscription | None:
        """
        Retrieve a cached transcription for an audio file.

        Args:
            audio_file: The audio file to retrieve the transcription for

        Returns:
            The cached transcription if available, None otherwise
        """
        cache_path = self._get_cache_path(audio_file)

        if not cache_path.exists():
            logger.debug(f"No cache found for {audio_file.path}")
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                text = f.read()
                logger.debug(f"Retrieved cached transcription for {audio_file.path}")
                return CachedTranscription(audio_file=audio_file, text=text)
        except (IOError, OSError) as e:
            logger.error(f"Error reading cache file {cache_path}: {e}")
            return None

    def cache_transcription(self, transcription: Transcription) -> None:
        """
        Cache a transcription for future use.

        Args:
            transcription: The transcription to cache
        """
        cache_path = self._get_cache_path(transcription.audio_file)

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(transcription.text)
                logger.debug(f"Cached transcription for {transcription.audio_file.path}")
        except (IOError, OSError) as e:
            logger.error(f"Error writing cache file {cache_path}: {e}")
            raise

    def clear_cache(self, older_than_days: int | None = None) -> List[Path]:
        """
        Clear cache files.

        Args:
            older_than_days: If provided, only delete files older than this many days

        Returns:
            List of deleted file paths
        """
        import time

        deleted_files = []
        current_time = time.time()

        # Calculate cutoff timestamp if needed
        cutoff_timestamp = None
        if older_than_days is not None:
            cutoff_timestamp = current_time - (older_than_days * 86400)  # 86400 seconds in a day

        for cache_file in self.base_dir.glob("*.txt"):
            delete_file = True

            # Check file age if cutoff specified
            if cutoff_timestamp is not None:
                file_mtime = cache_file.stat().st_mtime
                if file_mtime > cutoff_timestamp:
                    delete_file = False

            if delete_file:
                try:
                    cache_file.unlink()
                    deleted_files.append(cache_file)
                    logger.debug(f"Deleted cache file: {cache_file}")
                except OSError as e:
                    logger.error(f"Error deleting cache file {cache_file}: {e}")

        return deleted_files
