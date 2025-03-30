from typing import Protocol, Dict, Any


class TranscriptionModelPort(Protocol):
    """Port for transcription models like Whisper."""

    @property
    def name(self) -> str:
        """Return the name of the model"""
        ...

    def transcribe(self, audio_path: str, language: str | None = None) -> Dict[str, Any]:
        """
        Transcribe audio file at the given path.

        Args:
            audio_path: Path to the audio file
            language: Optional language code to use for transcription

        Returns:
            A dictionary containing transcription results.
            For example, in case of Whisper it includes:
            - text: The transcribed text
            - language: Detected language code
            - segments: List of segments with timing, confidence info, etc.
        """
        ...
