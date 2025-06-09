import sqlite3
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from speechdown.application.ports.transcription_repository_port import TranscriptionRepositoryPort
from speechdown.domain.entities import CachedTranscription, Transcription
from speechdown.domain.value_objects import Language, Timestamp, TranscriptionMetrics, MetricSource
from speechdown.infrastructure.schema import SCHEMA
from ..services.file_timestamp_service import FileTimestampService

logger = logging.getLogger(__name__)


@dataclass
class SQLiteRepositoryAdapter(TranscriptionRepositoryPort):
    """SQLite implementation of the TranscriptionRepositoryPort."""

    db_path: Path
    timestamp_service: FileTimestampService = field(default_factory=FileTimestampService)

    def __post_init__(self) -> None:
        """Initialize database schema."""
        self.create_transcription_table()

    def create_transcription_table(self) -> None:
        """Create the transcription table if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.executescript(SCHEMA)
            conn.commit()
            logger.debug(f"Initialized transcription table in {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error creating transcription table: {e}")
        finally:
            if conn:
                conn.close()

    def save_transcription(
        self, transcription: Optional[Transcription | CachedTranscription]
    ) -> None:
        """
        Save a transcription to the database.

        Args:
            transcription: The transcription to save, or None
        """
        if transcription is None:
            return

        # Skip CachedTranscription objects as they don't have metrics
        if isinstance(transcription, CachedTranscription):
            logger.debug("Skipping CachedTranscription - no metrics to save")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Extract metrics
            metrics = transcription.metrics

            # Insert transcription into database
            cursor.execute(
                """
                INSERT INTO transcriptions (
                    path, transcribed_text, language_code, confidence,
                    avg_logprob_mean, compression_ratio_mean, no_speech_prob_mean,
                    audio_duration_seconds, word_count, words_per_second,
                    model_name, transcription_time_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(transcription.audio_file.path),
                    transcription.text,
                    transcription.language.code,
                    metrics.confidence,
                    metrics.avg_logprob_mean,
                    metrics.compression_ratio_mean,
                    metrics.no_speech_prob_mean,
                    metrics.audio_duration_seconds,
                    metrics.word_count,
                    metrics.words_per_second,
                    metrics.model_name,
                    metrics.transcription_time_seconds,
                ),
            )

            conn.commit()
            logger.debug(f"Saved transcription for {transcription.audio_file.path}")
        except sqlite3.Error as e:
            logger.error(f"Error saving transcription: {e}")
        finally:
            if conn:
                conn.close()

    def get_transcriptions(self, path: Path) -> List[Transcription]:
        """
        Get all transcriptions for a specific audio file path.

        Args:
            path: Path to the audio file

        Returns:
            List of Transcription objects
        """
        transcriptions = []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable row factory for named columns
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM transcriptions
                WHERE path = ?
                ORDER BY confidence DESC
                """,
                (str(path),),
            )

            rows = cursor.fetchall()

            for row in rows:
                # Create domain objects from database rows
                metrics = TranscriptionMetrics(
                    confidence=row["confidence"],
                    avg_logprob_mean=row["avg_logprob_mean"],
                    compression_ratio_mean=row["compression_ratio_mean"],
                    no_speech_prob_mean=row["no_speech_prob_mean"],
                    audio_duration_seconds=row["audio_duration_seconds"],
                    word_count=row["word_count"],
                    words_per_second=row["words_per_second"],
                    model_name=row["model_name"],
                    transcription_time_seconds=row["transcription_time_seconds"],
                    source=MetricSource.WHISPER,
                )

                # Create AudioFile with path and extract timestamp from file
                from speechdown.domain.entities import AudioFile

                file_path = Path(row["path"])
                timestamp = Timestamp(self._get_file_timestamp(file_path))
                audio_file = AudioFile(path=file_path, timestamp=timestamp)

                transcription = Transcription(
                    audio_file=audio_file,
                    text=row["transcribed_text"],
                    language=Language(row["language_code"]),
                    metrics=metrics,
                )

                transcriptions.append(transcription)

        except sqlite3.Error as e:
            logger.error(f"Error retrieving transcriptions: {e}")
        finally:
            if conn:
                conn.close()

        return transcriptions

    def get_best_transcription(self, path: Path) -> Optional[Transcription]:
        """
        Get the best transcription for a given audio file based on confidence.

        Args:
            path: Path to the audio file

        Returns:
            The best Transcription if available, otherwise None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM transcriptions
                WHERE path = ?
                ORDER BY confidence DESC
                LIMIT 1
                """,
                (str(path),),
            )

            row = cursor.fetchone()

            if row:
                metrics = TranscriptionMetrics(
                    confidence=row["confidence"],
                    avg_logprob_mean=row["avg_logprob_mean"],
                    compression_ratio_mean=row["compression_ratio_mean"],
                    no_speech_prob_mean=row["no_speech_prob_mean"],
                    audio_duration_seconds=row["audio_duration_seconds"],
                    word_count=row["word_count"],
                    words_per_second=row["words_per_second"],
                    model_name=row["model_name"],
                    transcription_time_seconds=row["transcription_time_seconds"],
                    source=MetricSource.WHISPER,
                )

                # Create AudioFile with path and extract timestamp from file
                from speechdown.domain.entities import AudioFile

                file_path = Path(row["path"])
                timestamp = Timestamp(self._get_file_timestamp(file_path))
                audio_file = AudioFile(path=file_path, timestamp=timestamp)

                return Transcription(
                    audio_file=audio_file,
                    text=row["transcribed_text"],
                    language=Language(row["language_code"]),
                    metrics=metrics,
                )

            return None

        except sqlite3.Error as e:
            logger.error(f"Error retrieving best transcription: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def _get_file_timestamp(self, path: Path):
        """Get timestamp from file using the timestamp service."""
        return self.timestamp_service.get_timestamp(path)
