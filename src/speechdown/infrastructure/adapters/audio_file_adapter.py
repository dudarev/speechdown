from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from speechdown.application.ports.audio_file_port import AudioFilePort
from speechdown.domain.entities import AudioFile
from speechdown.domain.value_objects import Timestamp
from speechdown.application.ports.timestamp_port import TimestampPort


# TODO(AD): Consider renaming this class to AudioFileCollector or AudioFileFinder
# The name of this class is misleading. It should be something like
# AudioFileCollector or AudioFileFinder. The name AudioFileAdapter suggests
# that it is an adapter for a specific audio file format or library, which is not
# the case. It is a utility class for collecting and processing audio files.
# The renaming should be done on Port level as well to avoid confusion.
@dataclass
class AudioFileAdapter(AudioFilePort):
    timestamp_port: TimestampPort

    def get_audio_file(self, path: Path) -> AudioFile:
        dt = self.timestamp_port.get_timestamp(path)
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
                and self._is_modified_between(start_dt, end_dt, path)
            ):
                audio_files.append(self.get_audio_file(path))
        return audio_files

    def _get_file_timestamp(self, path: Path) -> datetime:
        return self.timestamp_port.get_timestamp(path)

    def _is_modified_between(
        self, start_dt: datetime | None, end_dt: datetime | None, path: Path
    ) -> bool:
        mod_time = datetime.fromtimestamp(path.stat().st_mtime)

        if start_dt is None and end_dt is None:
            return True
        if start_dt is None and end_dt is not None:
            return mod_time <= end_dt
        if end_dt is None and start_dt is not None:
            return start_dt <= mod_time
        return start_dt <= mod_time <= end_dt  # type: ignore[operator]
