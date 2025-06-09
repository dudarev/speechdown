from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from speechdown.application.ports.audio_file_port import AudioFilePort
from speechdown.domain.entities import AudioFile
from speechdown.domain.value_objects import Timestamp
from ..services.file_timestamp_service import FileTimestampService


# TODO(AD): Consider renaming this class to AudioFileCollector or AudioFileFinder
# The name of this class is misleading. It should be something like
# AudioFileCollector or AudioFileFinder. The name AudioFileAdapter suggests
# that it is an adapter for a specific audio file format or library, which is not
# the case. It is a utility class for collecting and processing audio files.
@dataclass
class AudioFileAdapter(AudioFilePort):
    timestamp_service: FileTimestampService = field(default_factory=FileTimestampService)

    def get_audio_file(self, path: Path) -> AudioFile:
        dt = self.timestamp_service.get_timestamp(path)
        return AudioFile(path=path, timestamp=Timestamp(value=dt))

    def collect_audio_files(
        self, directory: Path, start_dt: datetime | None = None, end_dt: datetime | None = None
    ) -> list[AudioFile]:
        SOUND_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".webm"}
        audio_files = []
        directory = Path(directory)
        for path in directory.glob("**/*"):
            if (
                path.is_file()
                and path.suffix.lower() in SOUND_EXTENSIONS
                and not path.stem.startswith(".")
                and self._is_between(start_dt, end_dt, self._get_file_timestamp(path))
            ):
                audio_files.append(self.get_audio_file(path))
        return audio_files

    def _get_file_timestamp(self, path: Path) -> datetime:
        return self.timestamp_service.get_timestamp(path)

    def _is_between(
        self, start_dt: datetime | None, end_dt: datetime | None, timestamp: datetime
    ) -> bool:
        if start_dt is None and end_dt is None:
            return True
        if start_dt is None and end_dt is not None:
            return timestamp <= end_dt
        if end_dt is None and start_dt is not None:
            return start_dt <= timestamp
        return start_dt <= timestamp <= end_dt  # type: ignore[operator]
