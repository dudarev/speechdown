import os
from datetime import datetime
from pathlib import Path

import pytest

from speechdown.infrastructure.services.file_timestamp_service import FileTimestampService


@pytest.fixture
def service():
    return FileTimestampService()


def _create_tmp_file(tmp_path: Path, name: str, mtime: float) -> Path:
    file_path = tmp_path / name
    file_path.touch()
    os.utime(file_path, (mtime, mtime))
    return file_path


def test_extract_timestamp_from_filename(service):
    dt = service.extract_from_filename("recording_20240908_102336.mp3")
    assert dt == datetime(2024, 9, 8, 10, 23, 36)


def test_extract_with_space_pattern(service):
    dt = service.extract_from_filename("20250408 204728.wav")
    assert dt == datetime(2025, 4, 8, 20, 47, 28)


def test_extract_two_digit_year(service):
    dt = service.extract_from_filename("+380999999999_250512_105730.m4a")
    assert dt == datetime(2025, 5, 12, 10, 57, 30)


def test_fallback_to_file_mtime(service, tmp_path):
    mtime = 1_600_000_000  # fixed timestamp
    file_path = _create_tmp_file(tmp_path, "no_timestamp.m4a", mtime)
    result = service.get_timestamp(file_path)
    assert result == datetime.fromtimestamp(mtime)
