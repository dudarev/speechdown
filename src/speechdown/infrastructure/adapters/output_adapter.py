import logging
from pathlib import Path
from speechdown.application.ports.output_port import OutputPort
from speechdown.domain.entities import Transcription


logger = logging.getLogger(__name__)


class OutputAdapter(OutputPort):
    def output_transcriptions(self, transcriptions: list[Transcription], path: Path | None = None):
        logger.debug("Outputting transcriptions")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                for transcription in transcriptions:
                    f.write(f"File: {transcription.audio_file.path}\n")
                    f.write(f"Language: {transcription.language.code}\n")
                    f.write(f"Transcription: {transcription.text}\n\n")
            logger.info(f"Transcriptions written to {path}")
        else:
            for transcription in transcriptions:
                print(f"File: {transcription.audio_file.path}")
                print(f"Language: {transcription.language.code}")
                print(f"Transcription: {transcription.text}")
                print()
        logger.debug(f"Output complete for {len(transcriptions)} transcriptions")
