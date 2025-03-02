from typing import Protocol
from speechdown.domain.entities import AudioFile, Transcription
from speechdown.domain.value_objects import Language
from speechdown.application.ports.transcription_model_port import TranscriptionModelPort


class TranscriberPort(Protocol):
    """Port for transcription services."""

    def __init__(self, model: TranscriptionModelPort): ...

    def auto_transcribe(self, audio_file: AudioFile) -> Transcription: ...

    def transcribe(self, audio_file: AudioFile, language: Language) -> Transcription: ...
