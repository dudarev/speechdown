from pathlib import Path
from typing import Protocol
from speechdown.domain.entities import AudioFile


class AudioFilePort(Protocol):
    def get_audio_file(self, path: Path) -> AudioFile: ...

    def collect_audio_files(self, directory: Path) -> list[AudioFile]: ...
