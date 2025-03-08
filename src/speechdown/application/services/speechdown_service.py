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
from speechdown.application.ports.transcription_cache_port import TranscriptionCachePort
from speechdown.application.ports.config_port import ConfigPort

SOUND_EXTENSIONS = (".mp3", ".wav", ".ogg", ".m4a", ".flac", "", ".webm")

logger = logging.getLogger(__name__)


@dataclass
class SpeechDownService:
    audio_file_port: AudioFilePort
    config_port: ConfigPort
    output_port: OutputPort
    repository_port: TranscriptionRepositoryPort
    transcriber_port: TranscriberPort
    cache_port: TranscriptionCachePort

    def collect_audio_files(self, directory: Path) -> List[AudioFile]:
        logger.debug(f"Collecting audio files from directory: {directory}")
        audio_files = self.audio_file_port.collect_audio_files(directory)
        logger.debug(f"Found {len(audio_files)} audio files")
        return audio_files

    def transcribe_audio_files(
        self, audio_files: List[AudioFile], force: bool = False
    ) -> List[TranscriptionResult]:
        transcriptions: list[TranscriptionResult] = []
        for i, audio_file in enumerate(audio_files, 1):
            logger.debug(f"Transcribing file {i}/{len(audio_files)}: {audio_file.path}")

            if not force:
                # Try to get from cache first
                cached = self.cache_port.get_cached_transcription(audio_file)
                if cached:
                    transcriptions.append(cached)
                    continue

            # If not in cache or force=True, perform transcription
            best_transcription = None
            for language in self.config_port.get_languages():
                logger.debug(f"Attempting transcription in {language}")
                transcription = self.transcriber_port.transcribe(audio_file, language)

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
            # TODO(AD): Save all transcriptions to the database
            self.repository_port.save_transcription(best_transcription)
            if best_transcription is not None:
                self.cache_port.cache_transcription(best_transcription)
                transcriptions.append(best_transcription)

        logger.debug(f"Transcription complete for all {len(audio_files)} files")
        return transcriptions

    def get_file_timestamp(self, path: Path) -> datetime:
        logger.debug(f"Getting timestamp for file: {path}")
        timestamp = datetime.fromtimestamp(path.stat().st_mtime)
        logger.debug(f"File timestamp: {timestamp}")
        return timestamp

    def output_transcriptions(
        self, transcriptions: list[TranscriptionResult], path: Path | None = None
    ):
        self.output_port.output_transcription_results(transcriptions, path)
