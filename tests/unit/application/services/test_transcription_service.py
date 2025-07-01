import os
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from speechdown.application.services.transcription_service import TranscriptionService
from speechdown.domain.entities import AudioFile, Transcription
from speechdown.domain.value_objects import Language, Timestamp, TranscriptionMetrics


@pytest.fixture
def audio_file(tmp_path):
    file_path = tmp_path / "audio.m4a"
    file_path.write_text("data")
    return AudioFile(path=file_path, timestamp=Timestamp(datetime.now()))


def test_retranscribe_when_file_modified(audio_file):
    # existing transcription older than file modification time
    old_time = datetime.now() - timedelta(minutes=5)
    os.utime(audio_file.path, (datetime.now().timestamp(), datetime.now().timestamp()))

    old_transcription = Transcription(
        audio_file=audio_file,
        text="old",
        language=Language("en"),
        metrics=TranscriptionMetrics(confidence=0.5),
        transcription_started_at=old_time,
    )

    repo = Mock()
    repo.get_best_transcription.return_value = old_transcription
    repo.delete_transcriptions = Mock()
    repo.save_transcription = Mock()

    transcriber = Mock()
    new_transcription = Transcription(
        audio_file=audio_file,
        text="new",
        language=Language("en"),
        metrics=TranscriptionMetrics(confidence=0.9),
        transcription_started_at=datetime.now(),
    )
    transcriber.transcribe.return_value = new_transcription

    config_port = Mock()
    config_port.get_languages.return_value = [Language("en")]

    service = TranscriptionService(
        audio_file_port=Mock(),
        config_port=config_port,
        output_port=Mock(),
        repository_port=repo,
        transcriber_port=transcriber,
        timestamp_port=Mock(),
    )

    results = service.transcribe_audio_files([audio_file])

    repo.delete_transcriptions.assert_called_once_with(audio_file.path)
    transcriber.transcribe.assert_called_once_with(audio_file, Language("en"))
    assert results == [new_transcription]
