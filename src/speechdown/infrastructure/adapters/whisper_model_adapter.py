import whisper  # type: ignore
from typing import Dict, Any, Optional, Union
from pathlib import Path

from speechdown.application.ports.transcription_model_port import TranscriptionModelPort


class WhisperModelAdapter(TranscriptionModelPort):
    """Whisper model adapter implementing the TranscriptionModelPort."""

    def __init__(self, model_name: str = "tiny"):
        """
        Initialize with specified Whisper model.

        Args:
            model_name: Name of Whisper model to load ("tiny", "base", "small", "medium", "large")
        """
        self._model_name = model_name
        self._model = whisper.load_model(model_name)

    def transcribe(
        self, audio_path: Union[str, Path], language: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper.

        Args:
            audio_path: Path to audio file
            language: Optional language code
            **kwargs: Additional parameters passed to Whisper's transcribe method
                      (e.g., fp16, temperature, etc.)

        Returns:
            Dictionary with transcription results
        """
        # Default to fp16=False if not specified
        if "fp16" not in kwargs:
            kwargs["fp16"] = False

        # Add language if provided
        if language:
            kwargs["language"] = language

        return self._model.transcribe(str(audio_path), **kwargs)

    @property
    def name(self) -> str:
        """Return the name of the loaded Whisper model."""
        return f"whisper-{self._model_name}"
