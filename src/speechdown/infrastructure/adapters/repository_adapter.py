from pathlib import Path
from typing import List
from speechdown.application.ports.transcription_repository_port import TranscriptionRepositoryPort
from speechdown.domain.entities import CachedTranscription, Transcription


class SQLiteRepositoryAdapter(TranscriptionRepositoryPort):
    def __init__(self, db_path: Path):
        self.db_path = db_path
        # Initialize database connection

    def save_transcription(self, transcription: Transcription | CachedTranscription | None) -> None:
        # Placeholder for actual database save logic
        # Do nothing if transcription is None or CachedTranscription
        pass

    def get_transcriptions(self, path: Path) -> List[Transcription]:
        # Placeholder for actual database retrieval logic
        return []

    def get_best_transcription(self, path):
        return super().get_best_transcription(path)
