from dataclasses import dataclass
from pathlib import Path
from typing import Union
from datetime import datetime

from speechdown.domain.value_objects import Language, Timestamp, TranscriptionMetrics


@dataclass
class AudioFile:
    path: Path
    timestamp: Timestamp


@dataclass
class Transcription:
    audio_file: AudioFile
    text: str
    language: Language
    metrics: TranscriptionMetrics
    transcription_started_at: datetime | None = None


@dataclass
class CachedTranscription:
    """Represents a transcription that was retrieved from cache."""

    audio_file: AudioFile
    text: str


# Type alias for composed transcription type
TranscriptionResult = Union[Transcription, CachedTranscription]
