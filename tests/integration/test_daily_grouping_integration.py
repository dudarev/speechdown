"""
Integration tests for daily grouping of voice notes with timestamp extraction.

Tests the end-to-end workflow of:
1. Audio file timestamp extraction from filenames
2. Daily file grouping based on extracted timestamps
3. File output with correct chronological ordering
4. Fallback behavior for files without parseable timestamps

This integration test validates the interaction between:
- FileTimestampAdapter (timestamp extraction)
- FileOutputAdapter (daily file creation and grouping)
- ConfigAdapter (configuration management)
"""

import json
import os
import pytest
from datetime import datetime
from pathlib import Path

from speechdown.domain.entities import AudioFile, Transcription
from speechdown.domain.value_objects import Language, TranscriptionMetrics
from speechdown.infrastructure.adapters.config_adapter import ConfigAdapter
from speechdown.infrastructure.adapters.file_output_adapter import FileOutputAdapter
from speechdown.infrastructure.adapters.file_timestamp_adapter import FileTimestampAdapter

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary directory for config and output files."""
    return tmp_path


@pytest.fixture
def temp_config_file(temp_config_dir):
    """Create temporary config file with output directory configuration."""
    config_file = temp_config_dir / "config.json"
    output_dir_path = temp_config_dir / "transcripts"
    
    # Create the output directory
    os.makedirs(output_dir_path, exist_ok=True)
    
    with open(config_file, "w") as f:
        json.dump({
            "languages": ["en", "uk", "ru"], 
            "output_dir": str(output_dir_path)
        }, f)
    
    return config_file


@pytest.fixture
def config_adapter(temp_config_file):
    """Create ConfigAdapter instance from temporary config file."""
    return ConfigAdapter.load_config_from_path(temp_config_file)


@pytest.fixture
def output_adapter(config_adapter):
    """Create FileOutputAdapter instance."""
    return FileOutputAdapter(config_adapter)


@pytest.fixture
def timestamp_adapter():
    """Create FileTimestampAdapter instance."""
    return FileTimestampAdapter()


@pytest.fixture
def sample_audio_files_with_timestamps(tmp_path):
    """Create sample audio files with different timestamp patterns in filenames."""
    # Create test files with different timestamp patterns
    files_data = [
        # Same day - different times (should group in same daily file)
        ("recording_20240315_143022.m4a", datetime(2024, 3, 15, 14, 30, 22)),
        ("voice_20240315_091500.m4a", datetime(2024, 3, 15, 9, 15, 0)),
        
        # Different day
        ("meeting_20240316_101530.m4a", datetime(2024, 3, 16, 10, 15, 30)),
        
        # 2-digit year pattern
        ("call_250317_195545.m4a", datetime(2025, 3, 17, 19, 55, 45)),
        
        # Space-separated pattern
        ("interview_20240318 204728.m4a", datetime(2024, 3, 18, 20, 47, 28)),
        
        # File without parseable timestamp (should use modification time)
        ("voice_memo_no_timestamp.m4a", None),  # Will be set to modification time
    ]
    
    audio_files = []
    for filename, expected_timestamp in files_data:
        file_path = tmp_path / filename
        file_path.touch()
        
        # For file without timestamp, we'll let the adapter determine it
        if expected_timestamp is None:
            # Set specific modification time for predictable testing
            mod_time = datetime(2024, 3, 19, 12, 0, 0).timestamp()
            os.utime(file_path, (mod_time, mod_time))
            expected_timestamp = datetime(2024, 3, 19, 12, 0, 0)
        
        audio_files.append(AudioFile(path=file_path, timestamp=expected_timestamp))
    
    return audio_files


@pytest.fixture
def sample_transcriptions(sample_audio_files_with_timestamps):
    """Create sample transcriptions for the audio files."""
    transcriptions = []
    for i, audio_file in enumerate(sample_audio_files_with_timestamps):
        transcription = Transcription(
            audio_file=audio_file,
            text=f"This is transcription {i+1} for {audio_file.path.name}.",
            language=Language("en"),
            metrics=TranscriptionMetrics(
                confidence=0.90 + (i * 0.01),  # Varying confidence
                audio_duration_seconds=30.0 + (i * 5.0)  # Varying duration
            )
        )
        transcriptions.append(transcription)
    
    return transcriptions


def test_timestamp_extraction_accuracy(timestamp_adapter, sample_audio_files_with_timestamps):
    """Test that timestamp extraction works correctly for various filename patterns."""
    expected_results = [
        ("recording_20240315_143022.m4a", datetime(2024, 3, 15, 14, 30, 22)),
        ("voice_20240315_091500.m4a", datetime(2024, 3, 15, 9, 15, 0)),
        ("meeting_20240316_101530.m4a", datetime(2024, 3, 16, 10, 15, 30)),
        ("call_250317_195545.m4a", datetime(2025, 3, 17, 19, 55, 45)),
        ("interview_20240318 204728.m4a", datetime(2024, 3, 18, 20, 47, 28)),
    ]
    
    for filename, expected_timestamp in expected_results:
        extracted = timestamp_adapter._extract_from_filename(filename)
        assert extracted == expected_timestamp, f"Failed to extract correct timestamp from {filename}"


def test_timestamp_fallback_behavior(timestamp_adapter, sample_audio_files_with_timestamps):
    """Test that files without parseable timestamps fall back to modification time."""
    # Find the file without parseable timestamp
    no_timestamp_file = None
    for audio_file in sample_audio_files_with_timestamps:
        if "no_timestamp" in audio_file.path.name:
            no_timestamp_file = audio_file
            break
    
    assert no_timestamp_file is not None, "Could not find test file without timestamp"
    
    # Test filename extraction returns None
    extracted = timestamp_adapter._extract_from_filename(no_timestamp_file.path.name)
    assert extracted is None, "Should not extract timestamp from filename without pattern"
    
    # Test full get_timestamp method uses fallback
    timestamp = timestamp_adapter.get_timestamp(no_timestamp_file.path)
    expected_fallback = datetime(2024, 3, 19, 12, 0, 0)
    
    # Allow small tolerance for timestamp comparison due to file system precision
    time_diff = abs((timestamp - expected_fallback).total_seconds())
    assert time_diff < 1.0, f"Fallback timestamp {timestamp} should be close to {expected_fallback}"


def test_daily_grouping_integration(output_adapter, sample_transcriptions, temp_config_dir):
    """Test end-to-end daily grouping with timestamp extraction and file output."""
    configured_output_dir = output_adapter.config_port.get_output_dir()
    assert configured_output_dir is not None, "Output directory should be configured"
     # Process all transcriptions
    output_adapter.output_transcription_results(sample_transcriptions)

    # Verify expected daily files are created
    expected_files = [
        configured_output_dir / "2024-03-15.md",  # Two files from same day
        configured_output_dir / "2024-03-16.md",  # One file
        configured_output_dir / "2024-03-18.md",  # One file
        configured_output_dir / "2024-03-19.md",  # Fallback timestamp file
        configured_output_dir / "2025-03-17.md",  # 2-digit year pattern
    ]

    for expected_file in expected_files:
        assert expected_file.exists(), f"Expected daily file {expected_file} was not created"

    # Verify content of file with multiple transcriptions (2024-03-15)
    march_15_file = configured_output_dir / "2024-03-15.md"
    content = march_15_file.read_text()

    # Should contain both transcriptions from that date
    assert "recording_20240315_143022.m4a" in content
    assert "voice_20240315_091500.m4a" in content

    # Verify chronological ordering within the daily file
    # Earlier transcription (09:15:00) should appear before later one (14:30:22) - chronological order
    early_pos = content.find("2024-03-15 09:15:00")
    late_pos = content.find("2024-03-15 14:30:22")
    assert early_pos < late_pos, "Transcriptions should be ordered chronologically (earliest first)"


def test_mixed_timestamp_patterns_integration(output_adapter, temp_config_dir):
    """Test integration with mixed timestamp patterns and edge cases."""
    # Create transcriptions with various patterns
    mixed_files = [
        # Valid patterns
        AudioFile(path=Path("test_20240401_120000.m4a"), timestamp=datetime(2024, 4, 1, 12, 0, 0)),
        AudioFile(path=Path("test_20240401 130000.m4a"), timestamp=datetime(2024, 4, 1, 13, 0, 0)),
        AudioFile(path=Path("test_240401_140000.m4a"), timestamp=datetime(2024, 4, 1, 14, 0, 0)),
        
        # Edge case: phone number + timestamp (should extract timestamp, not phone number)
        AudioFile(path=Path("+380999999999_240401_150000.m4a"), timestamp=datetime(2024, 4, 1, 15, 0, 0)),
    ]
    
    transcriptions = []
    for i, audio_file in enumerate(mixed_files):
        transcriptions.append(Transcription(
            audio_file=audio_file,
            text=f"Mixed pattern test {i+1}",
            language=Language("en"),
            metrics=TranscriptionMetrics()
        ))
    
    # Process transcriptions
    output_adapter.output_transcription_results(transcriptions)
    
    # Verify all transcriptions are grouped in the same daily file
    configured_output_dir = output_adapter.config_port.get_output_dir()
    daily_file = configured_output_dir / "2024-04-01.md"
    
    assert daily_file.exists(), "Daily file for mixed patterns should be created"
    
    content = daily_file.read_text()
    
    # Verify all transcriptions are present
    assert "Mixed pattern test 1" in content
    assert "Mixed pattern test 2" in content  
    assert "Mixed pattern test 3" in content
    assert "Mixed pattern test 4" in content
     # Verify chronological ordering (earliest first)
    timestamps = [
        "2024-04-01 12:00:00",  # Should be first (earliest)
        "2024-04-01 13:00:00",
        "2024-04-01 14:00:00",
        "2024-04-01 15:00:00",  # Should be last (latest)
    ]

    positions = [content.find(ts) for ts in timestamps]

    # All timestamps should be found
    for i, pos in enumerate(positions):
        assert pos != -1, f"Timestamp {timestamps[i]} not found in output"

    # Verify chronological order (earlier positions = earlier times)
    for i in range(len(positions) - 1):
        assert positions[i] < positions[i + 1], f"Timestamps not in chronological order: {timestamps[i]} should come before {timestamps[i + 1]}"


def test_error_handling_integration(output_adapter, timestamp_adapter, tmp_path):
    """Test integration error handling for invalid timestamps and fallback scenarios."""
    # Create files with invalid timestamp patterns
    invalid_files = [
        # Invalid date components
        (tmp_path / "invalid_20241301_120000.m4a", "invalid month"),  # Month 13
        (tmp_path / "invalid_20240230_120000.m4a", "February 30th"),  # Invalid day
        (tmp_path / "invalid_20240101_250000.m4a", "invalid hour"),   # Hour 25
    ]
    
    for file_path, description in invalid_files:
        file_path.touch()
        
        # Test that filename extraction fails gracefully
        extracted = timestamp_adapter._extract_from_filename(file_path.name)
        assert extracted is None, f"Should not extract timestamp from {description}: {file_path.name}"
        
        # Test that full timestamp extraction falls back to modification time
        timestamp = timestamp_adapter.get_timestamp(file_path)
        assert timestamp is not None, f"Should provide fallback timestamp for {description}"
        assert isinstance(timestamp, datetime), f"Fallback should return datetime object for {description}"


def test_performance_with_multiple_files(output_adapter, temp_config_dir):
    """Test performance and correctness with larger number of files."""
    # Create many transcriptions spanning multiple days
    transcriptions = []
    base_date = datetime(2024, 6, 1)
    
    for day_offset in range(10):  # 10 days
        for hour in range(0, 24, 3):  # Every 3 hours = 8 files per day
            timestamp = base_date.replace(
                day=base_date.day + day_offset,
                hour=hour,
                minute=0,
                second=0
            )
            
            filename = f"bulk_test_{timestamp.strftime('%Y%m%d_%H%M%S')}.m4a"
            audio_file = AudioFile(path=Path(filename), timestamp=timestamp)
            
            transcriptions.append(Transcription(
                audio_file=audio_file,
                text=f"Bulk test transcription for {timestamp}",
                language=Language("en"),
                metrics=TranscriptionMetrics()
            ))
    
    # Process all transcriptions (80 total)
    output_adapter.output_transcription_results(transcriptions)
    
    # Verify correct number of daily files created
    configured_output_dir = output_adapter.config_port.get_output_dir()
    daily_files = list(configured_output_dir.glob("2024-06-*.md"))
    
    assert len(daily_files) == 10, f"Should create 10 daily files, but found {len(daily_files)}"
    
    # Verify each daily file contains the expected number of transcriptions
    for daily_file in daily_files:
        content = daily_file.read_text()
        
        # Count H2 headers (one per transcription)
        h2_count = content.count("## 2024-06-")
        assert h2_count == 8, f"Each daily file should contain 8 transcriptions, but {daily_file.name} has {h2_count}"
