import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from speechdown.application.ports.config_port import ConfigPort
from speechdown.domain.entities import AudioFile, Transcription
from speechdown.domain.value_objects import Language, TranscriptionMetrics
from speechdown.infrastructure.adapters.file_output_adapter import FileOutputAdapter


class MockConfigPort(ConfigPort):
    def __init__(self, output_dir=None, languages=None):
        self._output_dir = output_dir
        self._languages = languages or []

    def get_languages(self):
        return self._languages

    def set_languages(self, languages):
        self._languages = languages

    def get_output_dir(self):
        return Path(self._output_dir) if self._output_dir else None

    def set_output_dir(self, output_dir):
        self._output_dir = output_dir


@pytest.fixture
def mock_config():
    return MockConfigPort(output_dir="/tmp/transcripts")


@pytest.fixture
def sample_audio_file():
    return AudioFile(path=Path("/path/to/audio/sample.mp3"), timestamp=datetime.now())


@pytest.fixture
def sample_transcription(sample_audio_file):
    metrics = TranscriptionMetrics(confidence=0.95, audio_duration_seconds=60.5)
    return Transcription(
        audio_file=sample_audio_file,
        text="This is a sample transcription.",
        language=Language("en"),
        metrics=metrics,
    )


def test_get_output_directory_from_config(mock_config):
    adapter = FileOutputAdapter(mock_config)
    output_dir = adapter._get_output_directory(None)
    assert output_dir == Path("/tmp/transcripts")


def test_get_output_directory_from_path(mock_config):
    adapter = FileOutputAdapter(mock_config)
    path = Path("/custom/path")
    output_dir = adapter._get_output_directory(path)
    assert output_dir == path


def test_generate_file_name():
    adapter = FileOutputAdapter(Mock())
    date = datetime(2025, 5, 8).date()
    filename = adapter._generate_file_name(date)
    assert filename == "2025-05-08.md"


@patch("os.access")
def test_validate_output_directory_creates_dir(mock_access, tmp_path):
    mock_access.return_value = True

    # Create a path that doesn't exist yet
    test_dir = tmp_path / "new_dir"

    adapter = FileOutputAdapter(Mock())
    adapter._validate_output_directory(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()


@patch("os.access")
def test_validate_output_directory_not_writable(mock_access, tmp_path):
    mock_access.return_value = False

    adapter = FileOutputAdapter(Mock())

    with pytest.raises(PermissionError):
        adapter._validate_output_directory(tmp_path)


def test_format_results_to_markdown_sections_new_content():
    adapter = FileOutputAdapter(Mock())
    current_time_str = "2025-05-08 14:30:00"
    frozen_datetime = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
    audio_file = AudioFile(path=Path("/path/to/audio/sample.mp3"), timestamp=frozen_datetime)
    metrics = TranscriptionMetrics()
    result = Transcription(
        audio_file=audio_file,
        text="This is a sample transcription.",
        language=Language("en"),
        metrics=metrics,
    )
    formatted_markdown = adapter._format_results_to_markdown_sections([result])
    expected_header = f"## {current_time_str} - sample.mp3"
    assert expected_header in formatted_markdown
    assert "This is a sample transcription." in formatted_markdown


@patch("builtins.print")
def test_output_to_stdout(mock_print, sample_transcription):
    adapter = FileOutputAdapter(Mock())

    adapter._output_to_stdout([sample_transcription])

    # Check that print was called with text containing the transcription
    mock_print.assert_called_once()
    output_text = mock_print.call_args[0][0]
    assert "sample.mp3" in output_text
    assert "This is a sample transcription." in output_text
    assert "*Language: en*" in output_text


def test_output_transcription_results_groups_by_date(tmp_path):
    config = MockConfigPort()
    adapter = FileOutputAdapter(config)

    metrics = TranscriptionMetrics()
    ts1 = datetime(2025, 6, 9, 10, 0, 0)
    ts2 = datetime(2025, 6, 10, 12, 0, 0)
    audio1 = AudioFile(path=tmp_path / "file1.m4a", timestamp=ts1)
    audio2 = AudioFile(path=tmp_path / "file2.m4a", timestamp=ts2)
    t1 = Transcription(audio_file=audio1, text="one", language=Language("en"), metrics=metrics)
    t2 = Transcription(audio_file=audio2, text="two", language=Language("en"), metrics=metrics)

    adapter.output_transcription_results([t1, t2], path=tmp_path)

    file1 = tmp_path / "2025-06-09.md"
    file2 = tmp_path / "2025-06-10.md"

    assert file1.exists()
    assert file2.exists()
    assert "one" in file1.read_text()
    assert "two" in file2.read_text()
