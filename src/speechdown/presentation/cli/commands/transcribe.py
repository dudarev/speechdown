"""Transcribe command handler for speechdown CLI."""

from pathlib import Path
import logging

from speechdown.infrastructure.adapters.audio_file_adapter import AudioFileAdapter
from speechdown.infrastructure.adapters.config_adapter import ConfigAdapter
from speechdown.infrastructure.adapters.file_output_adapter import FileOutputAdapter
from speechdown.infrastructure.adapters.whisper_transcriber_adapter import WhisperTranscriberAdapter
from speechdown.infrastructure.adapters.whisper_model_adapter import WhisperModelAdapter
from speechdown.infrastructure.adapters.file_timestamp_adapter import FileTimestampAdapter
from speechdown.infrastructure.adapters.repository_adapter import SQLiteRepositoryAdapter
from speechdown.application.services.transcription_service import TranscriptionService
from speechdown.presentation.cli.commands.common import SpeechDownPaths


from datetime import datetime, timedelta


def transcribe(
    directory: Path,
    dry_run: bool,
    ignore_existing: bool,
    within_hours: float | None = None,
) -> int:
    """
    Transcribe audio files in the specified directory.

    Args:
        directory: The directory containing audio files
        dry_run: Whether to perform a dry run without saving to database
        ignore_existing: Whether to ignore existing transcriptions and perform new ones
        within_hours: If set, only transcribe files modified within this many hours

    Returns:
        Exit code (0 for success)
    """
    try:
        speechdown_paths = SpeechDownPaths.from_working_directory(directory)

        # Create timestamp adapter
        timestamp_adapter = FileTimestampAdapter()

        audio_file_adapter = AudioFileAdapter(timestamp_port=timestamp_adapter)
        config_adapter = ConfigAdapter.load_config_from_path(speechdown_paths.config)
        config_adapter.set_default_output_dir_if_not_set()
        config_adapter.set_default_model_name_if_not_set()
        output_adapter = FileOutputAdapter(config_adapter)
        repository_adapter = SQLiteRepositoryAdapter(
            speechdown_paths.db, timestamp_port=timestamp_adapter
        )

        # Create model and transcriber
        model_name = config_adapter.get_model_name()
        # model_name is guaranteed to be set by set_default_model_name_if_not_set.
        whisper_model = WhisperModelAdapter(model_name=model_name)
        transcriber_adapter = WhisperTranscriberAdapter(whisper_model)

        transcription_service = TranscriptionService(
            audio_file_port=audio_file_adapter,
            config_port=config_adapter,
            output_port=output_adapter,
            repository_port=repository_adapter,
            transcriber_port=transcriber_adapter,
            timestamp_port=timestamp_adapter,
        )

        start_dt = None
        if within_hours is not None:
            start_dt = datetime.now() - timedelta(hours=within_hours)

        audio_files = transcription_service.collect_audio_files(directory, start_dt=start_dt)
        transcriptions = transcription_service.transcribe_audio_files(
            audio_files, ignore_existing=ignore_existing
        )
        # get existing output
        # update transcriptions based on existing output
        # update the output
        transcription_service.output_transcriptions(transcriptions)

        if dry_run:
            print("Dry run mode enabled. No changes to the database were made.")
        else:
            print(f"Processed {len(transcriptions)} audio file(s)")

        return 0
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        return 1
