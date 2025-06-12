from pathlib import Path
from typing import Protocol
from datetime import datetime
from speechdown.domain.entities import AudioFile


class AudioFilePort(Protocol):
    def get_audio_file(self, path: Path) -> AudioFile: ...

    def collect_audio_files(
        self,
        directory: Path,
        start_dt: datetime | None = None,
        end_dt: datetime | None = None,
    ) -> list[AudioFile]: ...
