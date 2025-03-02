from pathlib import Path
from typing import Protocol, List
from speechdown.domain.entities import Transcription


class TranscriptionRepositoryPort(Protocol):
    def save_transcription(self, transcription: Transcription | None) -> None:
        pass

    def get_transcriptions(self, path: Path) -> List[Transcription]:
        pass

    def get_best_transcription(self, path: Path) -> Transcription | None:
        pass
