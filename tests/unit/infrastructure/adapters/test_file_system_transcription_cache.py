import os
import shutil
import tempfile
from pathlib import Path
import pytest
import time

from speechdown.domain.entities import (
    AudioFile,
    Transcription,
    CachedTranscription,
)
from speechdown.domain.value_objects import (
    Language,
    Timestamp,
    TranscriptionMetrics,
    MetricSource,
)
from speechdown.infrastructure.adapters.file_system_transcription_cache import (
    FileSystemTranscriptionCache,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def cache(temp_dir):
    """Create a cache instance using the temporary directory."""
    return FileSystemTranscriptionCache(base_dir=temp_dir)


@pytest.fixture
def audio_file(temp_dir):
    """Create a temporary audio file for testing."""
    audio_path = Path(temp_dir) / "test_audio.mp3"
    with open(audio_path, "wb") as f:
        f.write(b"test audio content")
    return AudioFile(
        path=audio_path,
        timestamp=Timestamp.from_isoformat("2022-01-01T12:00:00"),
    )


@pytest.fixture
def transcription(audio_file):
    """Create a sample transcription."""
    return Transcription(
        audio_file=audio_file,
        text="This is a test transcription",
        language=Language("en"),
        metrics=TranscriptionMetrics(
            source=MetricSource.WHISPER,
            confidence=0.9,
        ),
    )


def test_cache_directory_creation(temp_dir):
    """Test that the cache directory is created if it doesn't exist."""
    cache_dir = Path(temp_dir) / "custom_cache"
    assert not cache_dir.exists()

    FileSystemTranscriptionCache(base_dir=cache_dir)
    assert cache_dir.exists()


def test_cache_transcription_and_retrieve(cache, transcription):
    """Test caching a transcription and retrieving it."""
    cache.cache_transcription(transcription)

    retrieved = cache.get_cached_transcription(transcription.audio_file)
    assert retrieved is not None
    assert isinstance(retrieved, CachedTranscription)
    assert retrieved.audio_file == transcription.audio_file
    assert retrieved.text == transcription.text


def test_get_nonexistent_cache(cache, audio_file):
    """Test retrieving a non-existent cache entry."""
    retrieved = cache.get_cached_transcription(audio_file)
    assert retrieved is None


def test_compute_file_hash_consistency(cache, temp_dir, audio_file):
    """Test that the file hash is consistent for the same file."""
    audio_file_2 = AudioFile(
        path=Path(temp_dir) / "test_audio2.mp3",
        timestamp=Timestamp.from_isoformat("2022-01-01T12:00:00"),
    )
    with open(audio_file_2.path, "wb") as f:
        f.write(audio_file.path.read_bytes())

    hash1 = cache._compute_file_hash(audio_file)
    hash2 = cache._compute_file_hash(audio_file)
    assert hash1 == hash2

    hash3 = cache._compute_file_hash(audio_file_2)
    assert hash1 == hash3


def test_clear_cache_all(cache, transcription):
    """Test clearing all cache files."""
    # Cache a transcription
    cache.cache_transcription(transcription)

    # Verify it's there
    assert cache.get_cached_transcription(transcription.audio_file) is not None

    # Clear the cache
    deleted = cache.clear_cache()
    assert len(deleted) == 1

    # Verify it's gone
    assert cache.get_cached_transcription(transcription.audio_file) is None


def test_clear_cache_older_than(cache, transcription, temp_dir):
    """Test clearing cache files older than a specific age."""
    # Create an old file and a new file
    cache.cache_transcription(transcription)

    # Create a new audio file with different content
    audio_path2 = Path(temp_dir) / "test_audio2.mp3"
    with open(audio_path2, "wb") as f:
        f.write(b"different test audio content")

    audio_file2 = AudioFile(
        path=audio_path2,
        timestamp=Timestamp.from_isoformat("2022-01-01T12:00:00"),
    )
    transcription2 = Transcription(
        audio_file=audio_file2,
        text="This is another test transcription",
        language=Language("en"),
        metrics=TranscriptionMetrics(
            source=MetricSource.WHISPER,
            confidence=0.8,
        ),
    )

    # Make the first cache file appear older
    cache_path = cache._get_cache_path(transcription.audio_file)
    now = time.time()
    old_time = now - 86400 * 2  # 2 days ago
    os.utime(cache_path, (old_time, old_time))

    # Cache the second file (will have current timestamp)
    cache.cache_transcription(transcription2)

    # Clear files older than 1 day
    deleted = cache.clear_cache(older_than_days=1)
    assert len(deleted) == 1

    # Verify old file is gone and new file remains
    assert cache.get_cached_transcription(transcription.audio_file) is None
    assert cache.get_cached_transcription(transcription2.audio_file) is not None
