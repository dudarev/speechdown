import pytest
import tempfile
import shutil
from pathlib import Path

from speechdown.domain.entities import AudioFile, Transcription
from speechdown.domain.value_objects import Language, Timestamp, TranscriptionMetrics, MetricSource
from speechdown.infrastructure.adapters.file_system_transcription_cache import (
    FileSystemTranscriptionCache,
)


@pytest.fixture
def temp_cache_dir():
    """Create a real temporary directory for the cache."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def real_audio_file():
    """Use an existing audio file from the tests data directory."""
    return AudioFile(
        path=Path("tests/data/subfolder/test-1.m4a"),
        timestamp=Timestamp.from_isoformat("2021-01-01T00:00:00Z"),
    )


@pytest.fixture
def sample_transcription(real_audio_file):
    """Create a sample transcription for the real audio file."""
    return Transcription(
        audio_file=real_audio_file,
        text="This is an integration test transcription",
        language=Language("en"),
        metrics=TranscriptionMetrics(
            source=MetricSource.WHISPER,
            confidence=0.95,
            avg_logprob_mean=-0.3,
            compression_ratio_mean=1.4,
            no_speech_prob_mean=0.05,
            audio_duration_seconds=5.0,
            word_count=6,
            words_per_second=1.2,
            additional_metrics={
                "model_name": "test-model",
                "segments_count": 1,
            },
        ),
    )


@pytest.mark.integration
def test_cache_integration_flow(temp_cache_dir, sample_transcription, real_audio_file):
    """Test the complete cache workflow in a real file system."""
    # Arrange
    cache = FileSystemTranscriptionCache(base_dir=temp_cache_dir)

    # Act - Cache a transcription
    cache.cache_transcription(sample_transcription)

    # Assert - Check the cache file exists
    cache_files = list(Path(temp_cache_dir).glob("*.txt"))
    assert len(cache_files) == 1

    # Act - Retrieve from cache
    cached_transcription = cache.get_cached_transcription(real_audio_file)

    # Assert - Check retrieved data
    assert cached_transcription is not None
    assert cached_transcription.text == sample_transcription.text


@pytest.mark.integration
def test_cache_persistence(temp_cache_dir, sample_transcription, real_audio_file):
    """Test that cache persists across different instances."""
    # Arrange & Act - Create a cache and store a transcription
    first_cache = FileSystemTranscriptionCache(base_dir=temp_cache_dir)
    first_cache.cache_transcription(sample_transcription)

    # Act - Create a new cache instance pointing to the same directory
    second_cache = FileSystemTranscriptionCache(base_dir=temp_cache_dir)
    cached_transcription = second_cache.get_cached_transcription(real_audio_file)

    # Assert
    assert cached_transcription is not None
    assert cached_transcription.text == sample_transcription.text


@pytest.mark.integration
def test_cache_clear_integration(temp_cache_dir, sample_transcription):
    """Test clearing the cache in a real file system."""
    # Arrange
    cache = FileSystemTranscriptionCache(base_dir=temp_cache_dir)
    cache.cache_transcription(sample_transcription)

    # Verify file exists
    assert len(list(Path(temp_cache_dir).glob("*.txt"))) == 1

    # Act
    deleted_files = cache.clear_cache()

    # Assert
    assert len(deleted_files) == 1
    assert len(list(Path(temp_cache_dir).glob("*.txt"))) == 0
