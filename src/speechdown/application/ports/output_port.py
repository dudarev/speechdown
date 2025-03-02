from pathlib import Path
from typing import Protocol
from speechdown.domain.entities import Transcription


class OutputPort(Protocol):
    def output_transcriptions(self, transcription: list[Transcription], path: Path | None = None):
        pass
