from pathlib import Path
from typing import Protocol
from speechdown.domain.entities import TranscriptionResult


class OutputPort(Protocol):
    def output_transcription_results(
        self, transcription_results: list[TranscriptionResult], path: Path | None = None
    ) -> None: ...
