from dataclasses import dataclass
import logging
from typing import List
from pathlib import Path
from datetime import datetime
from speechdown.application.ports.audio_file_port import AudioFilePort
from speechdown.application.ports.output_port import OutputPort
from speechdown.domain.entities import AudioFile, Transcription
from speechdown.application.ports.transcriber_port import TranscriberPort
from speechdown.application.ports.transcription_repository_port import TranscriptionRepositoryPort
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

    def collect_audio_files(self, directory: Path) -> List[AudioFile]:
        logger.debug(f"Collecting audio files from directory: {directory}")
        audio_files = self.audio_file_port.collect_audio_files(directory)
        logger.debug(f"Found {len(audio_files)} audio files")
        return audio_files

    def transcribe_audio_files(self, audio_files: List[AudioFile]) -> List[Transcription]:
        transcriptions = []
        for i, audio_file in enumerate(audio_files, 1):
            logger.debug(f"Transcribing file {i}/{len(audio_files)}: {audio_file.path}")
            best_transcription = None
            for language in self.config_port.get_languages():
                logger.debug(f"Attempting transcription in {language}")
                transcription = self.transcriber_port.transcribe(audio_file, language)
                if (
                    not best_transcription
                    or transcription.metrics.confidence > best_transcription.metrics.confidence
                ):
                    best_transcription = transcription
                    logger.debug(
                        f"New best transcription found (confidence: {transcription.metrics.confidence})"
                    )
            # TODO(AD): Save all transcriptions to the database
            self.repository_port.save_transcription(best_transcription)
            if best_transcription is not None:
                transcriptions.append(best_transcription)
        logger.debug(f"Transcription complete for all {len(audio_files)} files")
        return transcriptions

    def get_file_timestamp(self, path: Path) -> datetime:
        logger.debug(f"Getting timestamp for file: {path}")
        timestamp = datetime.fromtimestamp(path.stat().st_mtime)
        logger.debug(f"File timestamp: {timestamp}")
        return timestamp

    def output_transcriptions(self, transcriptions: list[Transcription], path: Path | None = None):
        self.output_port.output_transcriptions(transcriptions, path)
