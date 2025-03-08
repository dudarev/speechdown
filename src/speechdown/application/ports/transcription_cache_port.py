from typing import Protocol
from speechdown.domain.entities import AudioFile, Transcription, CachedTranscription


class TranscriptionCachePort(Protocol):
    """Port for caching transcriptions to avoid redundant processing."""

    def get_cached_transcription(self, audio_file: AudioFile) -> CachedTranscription | None:
        """
        Retrieves a cached transcription for the audio file if available.

        Args:
            audio_file: The audio file to look up in the cache

        Returns:
            The cached transcription if found, None otherwise
        """
        ...

    def cache_transcription(self, transcription: Transcription) -> None:
        """
        Caches the transcription for future use.

        Args:
            transcription: The transcription to cache
        """
        ...
