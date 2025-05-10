import json
import os
import pytest
from datetime import datetime
from pathlib import Path

from speechdown.domain.entities import AudioFile, Transcription
from speechdown.domain.value_objects import Language, TranscriptionMetrics
from speechdown.infrastructure.adapters.config_adapter import ConfigAdapter
from speechdown.infrastructure.adapters.file_output_adapter import FileOutputAdapter


@pytest.fixture
def temp_config_dir(tmp_path):
    # This fixture now only provides the directory where config and transcripts will live
    # to ensure consistency in path resolution if needed.
    # The actual output_dir path will be absolute, derived from tmp_path.
    return tmp_path

@pytest.fixture
def temp_config_file(temp_config_dir):
    config_file = temp_config_dir / "config.json"
    # Ensure output_dir in config is an absolute path string
    output_dir_path = temp_config_dir / "transcripts"
    
    # Create the directory that the config points to, as FileOutputAdapter expects it to be creatable/writable
    # This is also done in the test, but doing it here ensures the config is valid from the start.
    os.makedirs(output_dir_path, exist_ok=True) 
    
    with open(config_file, "w") as f:
        json.dump({"languages": ["en", "uk", "ru"], "output_dir": str(output_dir_path)}, f)
    
    return config_file


@pytest.fixture
def config_adapter(temp_config_file):
    return ConfigAdapter.load_config_from_path(temp_config_file)


@pytest.fixture
def output_adapter(config_adapter):
    return FileOutputAdapter(config_adapter)


@pytest.fixture
def sample_audio_files():
    return [
        AudioFile(path=Path("/path/to/audio/sample1.mp3"), timestamp=datetime.now()),
        AudioFile(path=Path("/path/to/audio/sample2.mp3"), timestamp=datetime.now())
    ]


@pytest.fixture
def sample_transcriptions(sample_audio_files):
    return [
        Transcription(
            audio_file=sample_audio_files[0],
            text="This is the first sample transcription.",
            language=Language("en"),
            metrics=TranscriptionMetrics(
                confidence=0.95,
                audio_duration_seconds=30.5
            )
        ),
        Transcription(
            audio_file=sample_audio_files[1],
            text="This is the second sample transcription.",
            language=Language("uk"),
            metrics=TranscriptionMetrics(
                confidence=0.90,
                audio_duration_seconds=45.0
            )
        )
    ]


def test_output_transcription_results_creates_file(output_adapter, sample_transcriptions, temp_config_dir):
    """Test that transcription results are written to a file with the correct format."""
    # Freeze time for testing
    current_datetime = datetime(2025, 5, 8, 10, 30, 0) 
    expected_filename_date_part = current_datetime.strftime("%Y-%m-%d")
    expected_h2_timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Determine the expected output directory from the adapter's config port
    configured_output_dir = output_adapter.config_port.get_output_dir()
    assert configured_output_dir is not None, "Configured output directory should not be None"
    
    os.makedirs(configured_output_dir, exist_ok=True)

    expected_file = configured_output_dir / f"{expected_filename_date_part}.md"
    
    # Call with explicit timestamp
    output_adapter.output_transcription_results(sample_transcriptions, timestamp=current_datetime)

    assert expected_file.exists(), f"Expected file {expected_file} does not exist."
    content = expected_file.read_text()
    assert content.strip() != "", f"File {expected_file} is empty." # Added check for empty content
    expected_header_1 = f"## {expected_h2_timestamp}"
    assert expected_header_1 in content
    assert "This is the first sample transcription." in content
    assert "*Language: en*" in content
    assert "*Confidence: 0.95*" in content 
    assert "*Duration: 30.50 seconds*" in content 
    assert "This is the second sample transcription." in content
    assert "*Language: uk*" in content
    assert "*Confidence: 0.90*" in content 
    assert "*Duration: 45.00 seconds*" in content


def test_merge_with_existing_file(output_adapter, sample_transcriptions, temp_config_dir):
    """Test that new transcriptions are correctly merged with existing content."""
    configured_output_dir = output_adapter.config_port.get_output_dir()
    assert configured_output_dir is not None, "Configured output directory should not be None"
    os.makedirs(configured_output_dir, exist_ok=True)
    
    existing_content_timestamp_str = "2025-05-08 09:00:00"
    file_date_str = "2025-05-08" # Date for the filename
    existing_file = configured_output_dir / f"{file_date_str}.md"

    existing_content = f"""## {existing_content_timestamp_str}\n\nThis is an existing transcription that should be preserved.\n\n*Language: ru*\n*Confidence: 0.85*\n*Duration: 15.00 seconds*\n"""
    existing_file.write_text(existing_content)
    
    new_transcriptions_datetime = datetime.strptime("2025-05-08 10:30:00", "%Y-%m-%d %H:%M:%S")
    new_transcriptions_h2_timestamp = new_transcriptions_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Call with explicit timestamp
    output_adapter.output_transcription_results(sample_transcriptions, timestamp=new_transcriptions_datetime)

    content = existing_file.read_text()
    assert content.strip() != "", f"File {existing_file} became empty after merge." # Added check
    assert f"## {existing_content_timestamp_str}" in content
    assert "This is an existing transcription that should be preserved." in content
    assert "*Confidence: 0.85*" in content 
    assert "*Duration: 15.00 seconds*" in content 
    expected_new_header = f"## {new_transcriptions_h2_timestamp}"
    assert expected_new_header in content
    assert "This is the first sample transcription." in content
    assert "*Language: en*" in content
    assert "*Confidence: 0.95*" in content
    assert "*Duration: 30.50 seconds*" in content
    assert "This is the second sample transcription." in content
    assert "*Language: uk*" in content
    assert "*Confidence: 0.90*" in content
    assert "*Duration: 45.00 seconds*" in content