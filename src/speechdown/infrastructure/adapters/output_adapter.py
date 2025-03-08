import logging
from pathlib import Path

from speechdown.domain.entities import TranscriptionResult, Transcription, CachedTranscription
from speechdown.application.ports.output_port import OutputPort

logger = logging.getLogger(__name__)


class MarkdownOutputAdapter(OutputPort):
    def output_transcription_results(
        self, transcription_results: list[TranscriptionResult], path: Path | None = None
    ) -> None:
        output_text = ""

        for result in transcription_results:
            # Add filename header
            filename = result.audio_file.path.name
            output_text += f"# {filename}\n\n"

            # Add transcription content
            output_text += f"{result.text}\n\n"

            # Add metadata based on result type
            if isinstance(result, Transcription):
                output_text += f"*Language: {result.language}*\n"
                if result.metrics.confidence is not None:
                    output_text += f"*Confidence: {result.metrics.confidence}*\n"

                # Safely access duration if it exists
                if hasattr(result.metrics, "duration") and result.metrics.duration is not None:
                    output_text += f"*Duration: {result.metrics.audio_duration_seconds} seconds*\n"
                output_text += "\n"
            elif isinstance(result, CachedTranscription):
                # No language field in CachedTranscription
                output_text += "*Retrieved from cache*\n\n"

        # Output to file or stdout
        if path:
            path.write_text(output_text)
            logger.info(f"Transcription results written to {path}")
        else:
            print(output_text)
