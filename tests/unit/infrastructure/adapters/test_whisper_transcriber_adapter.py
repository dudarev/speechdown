import pytest
from unittest.mock import Mock
from pathlib import Path
import statistics

from speechdown.infrastructure.adapters.whisper_transcriber_adapter import WhisperTranscriberAdapter
from speechdown.domain.entities import AudioFile, Transcription
from speechdown.domain.value_objects import Language, Timestamp, TranscriptionMetrics, MetricSource


@pytest.fixture
def mock_transcription_model():
    """Mock the transcription model"""
    mock_model = Mock()
    mock_model.name = "mock-model"
    return mock_model


@pytest.fixture
def sample_audio_file():
    """Create a sample AudioFile for testing"""
    return AudioFile(
        path=Path("/fake/path/audio.mp3"),
        timestamp=Timestamp.from_isoformat("2022-01-01T12:00:00"),
    )


@pytest.fixture
def sample_transcription_result():
    """Create a sample result as returned by Whisper"""
    return {
        "text": "This is a test transcription.",
        "language": "en",
        "segments": [
            {
                "id": 0,
                "seek": 0,
                "start": 0.0,
                "end": 5.0,
                "text": "This is a test",
                "avg_logprob": -0.5,
                "compression_ratio": 1.2,
                "no_speech_prob": 0.1,
                "temperature": 0.0,
            },
            {
                "id": 1,
                "seek": 100,
                "start": 5.0,
                "end": 10.5,
                "text": "transcription.",
                "avg_logprob": -0.6,
                "compression_ratio": 1.3,
                "no_speech_prob": 0.05,
                "temperature": 0.0,
            },
        ],
    }


def test_extract_metrics_from_result(mock_transcription_model, sample_transcription_result):
    """Test metrics extraction from Whisper result"""
    # Arrange
    adapter = WhisperTranscriberAdapter(model=mock_transcription_model)

    # Act
    metrics = adapter._extract_metrics_from_result(sample_transcription_result)

    # Assert
    assert isinstance(metrics, TranscriptionMetrics)
    assert metrics.source == MetricSource.WHISPER

    # Check calculated values
    avg_logprobs = [-0.5, -0.6]
    compression_ratios = [1.2, 1.3]
    no_speech_probs = [0.1, 0.05]

    assert metrics.confidence == statistics.mean(avg_logprobs)
    assert metrics.avg_logprob_mean == statistics.mean(avg_logprobs)
    assert metrics.compression_ratio_mean == statistics.mean(compression_ratios)
    assert metrics.no_speech_prob_mean == statistics.mean(no_speech_probs)
    assert metrics.audio_duration_seconds == 10.5
    assert metrics.word_count == 5  # "This is a test transcription."
    assert metrics.words_per_second == 5 / 10.5
    assert metrics.additional_metrics["segments_count"] == 2
    assert metrics.additional_metrics["temperature"] == 0.0
    assert metrics.additional_metrics["model_name"] == "mock-model"


def test_transcribe(mock_transcription_model, sample_audio_file, sample_transcription_result):
    """Test the transcribe method with a specific language"""
    # Arrange
    mock_transcription_model.transcribe.return_value = sample_transcription_result
    adapter = WhisperTranscriberAdapter(model=mock_transcription_model)
    language = Language("en")

    # Act
    transcription = adapter.transcribe(sample_audio_file, language)

    # Assert
    mock_transcription_model.transcribe.assert_called_once_with(
        str(sample_audio_file.path), language=language.code
    )

    assert isinstance(transcription, Transcription)
    assert transcription.audio_file == sample_audio_file
    assert transcription.text == sample_transcription_result["text"]
    assert transcription.language.code == "en"


def test_auto_transcribe(mock_transcription_model, sample_audio_file, sample_transcription_result):
    """Test the auto_transcribe method which detects language automatically"""
    # Arrange
    mock_transcription_model.transcribe.return_value = sample_transcription_result
    adapter = WhisperTranscriberAdapter(model=mock_transcription_model)

    # Act
    transcription = adapter.auto_transcribe(sample_audio_file)

    # Assert
    mock_transcription_model.transcribe.assert_called_once_with(str(sample_audio_file.path))

    assert isinstance(transcription, Transcription)
    assert transcription.audio_file == sample_audio_file
    assert transcription.text == sample_transcription_result["text"]
    assert transcription.language.code == "en"


def test_extract_metrics_empty_segments(mock_transcription_model):
    """Test metrics extraction with empty segments"""
    # Arrange
    adapter = WhisperTranscriberAdapter(model=mock_transcription_model)
    result = {"text": "Empty test", "language": "en", "segments": []}

    # Act
    metrics = adapter._extract_metrics_from_result(result)

    # Assert
    assert metrics.confidence is None
    assert metrics.avg_logprob_mean is None
    assert metrics.compression_ratio_mean is None
    assert metrics.no_speech_prob_mean is None
    assert metrics.audio_duration_seconds == 0
    assert metrics.word_count == 2  # "Empty test"
    assert metrics.words_per_second is None
    assert metrics.additional_metrics["segments_count"] == 0
    assert metrics.additional_metrics["temperature"] is None
