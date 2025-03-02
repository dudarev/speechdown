import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from speechdown.infrastructure.adapters.whisper_model_adapter import WhisperModelAdapter


@pytest.fixture
def mock_whisper():
    """Mock the whisper library"""
    with patch("speechdown.infrastructure.adapters.whisper_model_adapter.whisper") as mock_whisper:
        # Create a mock model that will be returned by whisper.load_model
        mock_model = Mock()
        mock_whisper.load_model.return_value = mock_model
        yield mock_whisper, mock_model


def test_init_loads_model(mock_whisper):
    """Test that the adapter loads a whisper model during initialization"""
    mock_whisper_module, _ = mock_whisper

    # Act
    adapter = WhisperModelAdapter(model_name="tiny")

    # Assert
    mock_whisper_module.load_model.assert_called_once_with("tiny")
    assert adapter._model == mock_whisper_module.load_model.return_value


def test_model_name_property(mock_whisper):
    """Test the name property returns the expected format"""
    _, _ = mock_whisper
    adapter = WhisperModelAdapter(model_name="tiny")

    assert adapter.name == "whisper-tiny"


def test_transcribe_method(mock_whisper):
    """Test that the transcribe method correctly calls the underlying model"""
    _, mock_model = mock_whisper
    mock_result = {"text": "Test transcription", "language": "en"}
    mock_model.transcribe.return_value = mock_result

    adapter = WhisperModelAdapter(model_name="tiny")
    result = adapter.transcribe("test.mp3", language="en")

    # Verify model called correctly
    mock_model.transcribe.assert_called_once_with("test.mp3", language="en", fp16=False)

    # Verify result is passed through
    assert result == mock_result


def test_transcribe_method_with_path_object(mock_whisper):
    """Test the transcribe method with Path object as input"""
    _, mock_model = mock_whisper
    mock_model.transcribe.return_value = {"text": "Test", "language": "en"}

    adapter = WhisperModelAdapter(model_name="tiny")
    path = Path("test.mp3")
    adapter.transcribe(path)

    # Verify path is converted to string
    mock_model.transcribe.assert_called_once_with(str(path), fp16=False)


def test_transcribe_passes_additional_kwargs(mock_whisper):
    """Test that additional kwargs are passed to the model"""
    _, mock_model = mock_whisper

    adapter = WhisperModelAdapter(model_name="tiny")
    adapter.transcribe("test.mp3", temperature=0.7, beam_size=5)

    # Verify kwargs are passed
    mock_model.transcribe.assert_called_once_with(
        "test.mp3", fp16=False, temperature=0.7, beam_size=5
    )


def test_fp16_override(mock_whisper):
    """Test that fp16 can be overridden"""
    _, mock_model = mock_whisper

    adapter = WhisperModelAdapter(model_name="tiny")
    adapter.transcribe("test.mp3", fp16=True)

    # Verify fp16 is passed as True
    mock_model.transcribe.assert_called_once_with("test.mp3", fp16=True)
