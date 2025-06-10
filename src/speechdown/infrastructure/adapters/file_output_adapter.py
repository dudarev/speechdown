import logging
import os
import datetime  # Changed import
from pathlib import Path
from typing import Dict, List

from speechdown.domain.value_objects import Timestamp

from speechdown.application.ports.config_port import ConfigPort
from speechdown.application.ports.output_port import OutputPort
from speechdown.domain.entities import TranscriptionResult, Transcription, CachedTranscription
from .markdown_merger import MarkdownMerger

logger = logging.getLogger(__name__)


class FileOutputAdapter(OutputPort):
    def __init__(self, config_port: ConfigPort):
        self.config_port = config_port
        self.markdown_merger = MarkdownMerger()  # Initialize the merger

    def output_transcription_results(
        self,
        transcription_results: list[TranscriptionResult],
        path: Path | None = None,
        timestamp: datetime.datetime | None = None,
    ) -> None:
        # Get the output directory from the configuration or use the provided path
        output_dir = self._get_output_directory(path)

        if not output_dir:
            # If no output directory is available, use standard output
            self._output_to_stdout(transcription_results)
            return

        # Group transcriptions by the date of each result's timestamp
        date_to_transcriptions: Dict[datetime.date, List[TranscriptionResult]] = {}

        for result in transcription_results:
            result_dt = self._extract_result_datetime(result, timestamp)
            transcription_date = result_dt.date()

            if transcription_date not in date_to_transcriptions:
                date_to_transcriptions[transcription_date] = []

            date_to_transcriptions[transcription_date].append(result)

        # Create output directory if it doesn't exist
        self._validate_output_directory(output_dir)

        # Process each date and write to corresponding file
        for transcription_date, results in date_to_transcriptions.items():
            file_path = output_dir / self._generate_file_name(transcription_date)
            self._write_to_file(file_path, results)

    def _get_output_directory(self, path: Path | None) -> Path | None:
        """Get the output directory from the config or use the provided path."""
        if path:
            return path

        output_dir = self.config_port.get_output_dir()
        if output_dir:
            # If the output_dir is relative, make it relative to the working directory
            if not output_dir.is_absolute():
                # Assuming we would want it relative to the current dir
                output_dir = Path.cwd() / output_dir
            return output_dir

        return None

    def _validate_output_directory(self, directory: Path) -> None:
        """Ensure the output directory exists and is writable."""
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created output directory: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Output path {directory} is not a directory")

        # Check if the directory is writable
        if not os.access(directory, os.W_OK):
            raise PermissionError(f"Output directory {directory} is not writable")

    def _extract_result_datetime(
        self, result: TranscriptionResult, default_timestamp: datetime.datetime | None = None
    ) -> datetime.datetime:
        """Return a datetime for a transcription result."""
        ts = getattr(result, "timestamp", None)
        if isinstance(ts, Timestamp):
            ts = ts.value

        if ts is None:
            audio_ts = getattr(getattr(result, "audio_file", None), "timestamp", None)
            if isinstance(audio_ts, Timestamp):
                ts = audio_ts.value
            elif isinstance(audio_ts, datetime.datetime):
                ts = audio_ts

        if ts is None:
            ts = default_timestamp or datetime.datetime.now()

        return ts

    def _generate_file_name(self, date_obj: datetime.date) -> str:  # Changed type
        """Generate a file name based on the date (YYYY-MM-DD.md)."""
        return f"{date_obj.strftime('%Y-%m-%d')}.md"

    def _write_to_file(
        self,
        file_path: Path,
        results: list[TranscriptionResult],
        timestamp: datetime.datetime | None = None,
    ) -> None:
        """Write transcription results to a file, using MarkdownMerger for content."""
        existing_content = ""
        if file_path.exists():
            existing_content = file_path.read_text()

        # Generate new transcriptions in Markdown format
        new_transcriptions_markdown = self._format_results_to_markdown_sections(
            results, timestamp=timestamp
        )

        # Use MarkdownMerger to merge
        merged_content = self.markdown_merger.merge_content(
            existing_content, new_transcriptions_markdown
        )

        file_path.write_text(merged_content)
        logger.info(f"Transcription results written to {file_path}")

    def _format_results_to_markdown_sections(
        self,
        transcription_results: list[TranscriptionResult],
        timestamp: datetime.datetime | None = None,
    ) -> str:
        """
        Formats a list of TranscriptionResult objects into Markdown sections.
        Each section has the format '## TIMESTAMP - FILENAME'.
        Results are sorted in reverse chronological order (most recent first).
        """
        if not transcription_results:
            return ""

        # Prepare tuples of (timestamp, filename, result)
        result_tuples = []
        for result in transcription_results:
            # Derive timestamp for this result
            result_timestamp = self._extract_result_datetime(result, timestamp)
            # Try to get filename if available
            filename = getattr(getattr(result, "audio_file", None), "path", None)
            if filename:
                filename = Path(filename).name
            else:
                filename = "unknown"
            result_tuples.append((result_timestamp, filename, result))

        # Sort by timestamp descending
        result_tuples.sort(key=lambda x: x[0], reverse=True)

        sections = []
        for result_timestamp, filename, result in result_tuples:
            header_line = f"## {result_timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {filename}"
            content_lines = []
            transcript_line = result.text if result.text is not None else ""
            content_lines.append(transcript_line)
            section = f"{header_line}\n" + "\n".join(content_lines)
            sections.append(section)

        # TODO(AD): Remove this once the section title format is finalized
        # Add horizontal rule after each section
        sections_with_rules = [section + "\n\n---" for section in sections]
        return "\n\n".join(sections_with_rules) + "\n"

    def _output_to_stdout(self, transcription_results: list[TranscriptionResult]) -> None:
        """Output transcription results to stdout when no file output is available."""
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
                if result.metrics.audio_duration_seconds is not None:
                    output_text += f"*Duration: {result.metrics.audio_duration_seconds} seconds*\n"
                output_text += "\n"
            elif isinstance(result, CachedTranscription):
                # No language field in CachedTranscription
                output_text += "*Retrieved from cache*\n\n"

        print(output_text)
        logger.info("Transcription results printed to stdout")
