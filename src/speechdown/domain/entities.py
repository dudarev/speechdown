from dataclasses import dataclass
from pathlib import Path


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
