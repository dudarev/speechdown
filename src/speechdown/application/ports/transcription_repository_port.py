from pathlib import Path
from typing import Protocol, List
from speechdown.domain.entities import CachedTranscription, Transcription


class TranscriptionRepositoryPort(Protocol):
    def save_transcription(self, transcription: Transcription | CachedTranscription | None) -> None:
        pass

    def get_transcriptions(self, path: Path) -> List[Transcription]:
        pass

    def get_best_transcription(self, path: Path) -> Transcription | None:
        pass

    def delete_transcriptions(self, path: Path) -> None:
        """Delete all transcriptions for the given audio file."""
        pass
