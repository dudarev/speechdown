"""Transcribe command handler for speechdown CLI."""
from pathlib import Path
import logging

from speechdown.infrastructure.adapters.audio_file_adapter import AudioFileAdapter
from speechdown.infrastructure.adapters.config_adapter import ConfigAdapter
from speechdown.infrastructure.adapters.file_output_adapter import FileOutputAdapter
from speechdown.infrastructure.adapters.whisper_transcriber_adapter import WhisperTranscriberAdapter
from speechdown.infrastructure.adapters.whisper_model_adapter import WhisperModelAdapter

__all__ = ["transcribe"]
from speechdown.infrastructure.adapters.repository_adapter import SQLiteRepositoryAdapter
from speechdown.application.services.transcription_service import TranscriptionService
from speechdown.presentation.cli.commands.common import SpeechDownPaths


def transcribe(directory: Path, dry_run: bool, ignore_existing: bool) -> int:
    """
    Transcribe audio files in the specified directory.

    Args:
        directory: The directory containing audio files
        dry_run: Whether to perform a dry run without saving to database
        ignore_existing: Whether to ignore existing transcriptions and perform new ones

    Returns:
        Exit code (0 for success)
    """
    try:
        speechdown_paths = SpeechDownPaths.from_working_directory(directory)

        audio_file_adapter = AudioFileAdapter()
        config_adapter = ConfigAdapter.load_config_from_path(speechdown_paths.config)
        config_adapter.set_default_output_dir_if_not_set()
        output_adapter = FileOutputAdapter(config_adapter)
        repository_adapter = SQLiteRepositoryAdapter(speechdown_paths.db)

        # Create model and transcriber
        whisper_model = WhisperModelAdapter()
        transcriber_adapter = WhisperTranscriberAdapter(whisper_model)

        transcription_service = TranscriptionService(
            audio_file_port=audio_file_adapter,
            config_port=config_adapter,
            output_port=output_adapter,
            repository_port=repository_adapter,
            transcriber_port=transcriber_adapter,
        )

        audio_files = transcription_service.collect_audio_files(directory)
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
