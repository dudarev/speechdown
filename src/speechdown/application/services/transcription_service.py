from dataclasses import dataclass
import logging
from typing import List
from pathlib import Path
from datetime import datetime
from speechdown.application.ports.audio_file_port import AudioFilePort
from speechdown.application.ports.output_port import OutputPort
from speechdown.domain.entities import AudioFile, TranscriptionResult
from speechdown.application.ports.transcriber_port import TranscriberPort
from speechdown.application.ports.transcription_repository_port import TranscriptionRepositoryPort
from speechdown.application.ports.config_port import ConfigPort
from speechdown.application.ports.timestamp_port import TimestampPort

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionService:
    audio_file_port: AudioFilePort
    config_port: ConfigPort
    output_port: OutputPort
    repository_port: TranscriptionRepositoryPort
    transcriber_port: TranscriberPort
    timestamp_port: TimestampPort

    def collect_audio_files(self, directory: Path) -> List[AudioFile]:
        logger.debug(f"Collecting audio files from directory: {directory}")
        audio_files = self.audio_file_port.collect_audio_files(directory)
        logger.debug(f"Found {len(audio_files)} audio files")
        return audio_files

    def transcribe_audio_files(
        self, audio_files: List[AudioFile], ignore_existing: bool = False
    ) -> List[TranscriptionResult]:
        transcriptions: list[TranscriptionResult] = []
        for i, audio_file in enumerate(audio_files, 1):
            logger.debug(f"Transcribing file {i}/{len(audio_files)}: {audio_file.path}")

            if not ignore_existing:
                # Try to get existing transcription first
                existing = self.repository_port.get_best_transcription(audio_file.path)
                if existing:
                    transcriptions.append(existing)
                    logger.debug(f"Using existing transcription for {audio_file.path}")
                    continue

            # If no existing transcription or ignore_existing=True, perform transcription
            best_transcription = None
            for language in self.config_port.get_languages():
                logger.debug(f"Attempting transcription in {language}")
                transcription = self.transcriber_port.transcribe(audio_file, language)
                # Save each transcription attempt to the database
                self.repository_port.save_transcription(transcription)

                current_confidence = transcription.metrics.confidence
                best_confidence: float | None = (
                    best_transcription.metrics.confidence if best_transcription else None
                )

                if best_transcription is None or (
                    current_confidence is not None
                    and (best_confidence is None or current_confidence > best_confidence)
                ):
                    best_transcription = transcription
                    logger.debug(
                        f"New best transcription found (confidence: {transcription.metrics.confidence})"
                    )

            if best_transcription is not None:
                transcriptions.append(best_transcription)

        logger.debug(f"Transcription complete for all {len(audio_files)} files")
        return transcriptions

    def get_file_timestamp(self, path: Path) -> datetime:
        logger.debug(f"Getting timestamp for file: {path}")
        timestamp = self.timestamp_port.get_timestamp(path)
        logger.debug(f"File timestamp: {timestamp}")
        return timestamp

    def output_transcriptions(
        self, transcriptions: list[TranscriptionResult], path: Path | None = None
    ):
        self.output_port.output_transcription_results(transcriptions, path)
