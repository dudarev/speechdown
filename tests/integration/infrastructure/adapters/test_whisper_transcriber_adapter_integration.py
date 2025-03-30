import pytest
from pathlib import Path

from speechdown.domain.entities import AudioFile
from speechdown.domain.value_objects import Language, Timestamp
from speechdown.infrastructure.adapters.whisper_transcriber_adapter import WhisperTranscriberAdapter
from speechdown.infrastructure.adapters.whisper_model_adapter import WhisperModelAdapter


@pytest.fixture
def test_audio_file():
    """Fixture that creates a valid AudioFile instance using an existing file from the data folder."""
    return AudioFile(
        path=Path("tests/data/subfolder/test-1.m4a"),
        timestamp=Timestamp.from_isoformat("2021-01-01T00:00:00Z"),
    )


@pytest.fixture
def whisper_model():
    """Fixture that provides a real WhisperModelAdapter with 'tiny' model."""
    return WhisperModelAdapter(model_name="tiny")


@pytest.fixture
def whisper_adapter(whisper_model):
    """Fixture that provides a WhisperTranscriberAdapter with the real Whisper model."""
    return WhisperTranscriberAdapter(whisper_model)


@pytest.mark.integration
@pytest.mark.slow
def test_transcribe_integration(whisper_adapter, test_audio_file):
    """Test the integration between the adapter and actual Whisper model for transcribing with specified language."""
    # Arrange
    language = Language("en")

    # Act
    transcription = whisper_adapter.transcribe(test_audio_file, language)

    # Assert
    assert transcription.text, "Transcription should not be empty"
    assert transcription.language.code == "en"
    assert transcription.audio_file == test_audio_file

    # Verify metrics structure (actual values will depend on the audio content)
    assert transcription.metrics.confidence is not None
    assert transcription.metrics.avg_logprob_mean is not None
    assert transcription.metrics.compression_ratio_mean is not None
    assert transcription.metrics.no_speech_prob_mean is not None
    assert transcription.metrics.audio_duration_seconds > 0
    assert transcription.metrics.word_count > 0
    assert transcription.metrics.words_per_second is not None
    assert transcription.metrics.model_name == "whisper-tiny"


@pytest.mark.integration
@pytest.mark.slow
def test_auto_transcribe_integration(whisper_adapter, test_audio_file):
    """Test the integration between the adapter and actual Whisper model for auto-detecting language and transcribing."""
    # Act
    transcription = whisper_adapter.auto_transcribe(test_audio_file)

    # Assert
    assert transcription.text, "Transcription should not be empty"
    assert transcription.language.code, "Language should be detected"
    assert transcription.audio_file == test_audio_file

    # Verify metrics structure
    assert transcription.metrics.confidence is not None
    assert transcription.metrics.word_count > 0
    assert transcription.metrics.audio_duration_seconds > 0
    assert transcription.metrics.model_name == "whisper-tiny"
