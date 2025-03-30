import whisper  # type: ignore
from typing import Dict, Any, Optional, Union
from pathlib import Path

from speechdown.application.ports.transcription_model_port import TranscriptionModelPort


class WhisperModelAdapter(TranscriptionModelPort):
    """Whisper model adapter implementing the TranscriptionModelPort."""

    def __init__(self, model_name: str = "tiny"):
        """
        Initialize with specified Whisper model.

        See https://github.com/openai/whisper

        Args:
            model_name: Name of Whisper model to load ("tiny", "base", "small", "medium", "large", "turbo")
        """
        self._model_name = model_name
        self._model = whisper.load_model(model_name)

    def transcribe(
        self, audio_path: Union[str, Path], language: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper.

        See https://github.com/openai/whisper/blob/main/whisper/transcribe.py

        Args:
            audio_path: Path to audio file
            language: Optional language code
            **kwargs: Additional parameters passed to Whisper's transcribe method,
                      key parameters include:

                      - verbose (bool): Display decoding details (True=all details, False=minimal)
                      - no_speech_threshold (float): Threshold to consider a segment as silent
                      - logprob_threshold (float): Threshold for average token log probability
                      - compression_ratio_threshold (float): Threshold for gzip compression ratio
                      - condition_on_previous_text (bool): Use previous output as prompt for next window
                      - initial_prompt (str): Optional text to provide as context for first window
                      - word_timestamps (bool): Extract timestamps for each word
                      - clip_timestamps (str|List[float]): Comma-separated list of timestamps to process
                      - **decode_options (dict): Options for the decoder.
                        See https://github.com/openai/whisper/blob/main/whisper/decoding.py
                        - task (str): "transcribe" or "translate" (default: "transcribe")
                        - temperature (float): Sampling temperature (default: 0.0)
                        - best_of (int): Number of independent sample trajectories (if temp > 0)
                        - beam_size (int): Number of beams in beam search (if temp == 0)
                        - patience (float): Patience in beam search
                        - length_penalty (float): Penalty for longer outputs
                        - prompt (str|List[int]): Text or tokens for previous context
                        - prefix (str|List[int]): Text or tokens to prefix current context
                        - suppress_tokens (str|List[int]): Token IDs to suppress
                        - suppress_blank (bool): Whether to suppress blank outputs (default: True)
                        - without_timestamps (bool): Sample text tokens only (default: False)
                        - max_initial_timestamp (float): Max timestamp at the beginning (default: 1.0)
                        - fp16 (bool): Use fp16 for most calculations (default: True)

        Returns:
            Dictionary with transcription results containing:
            {
                "text": str,        # The full transcribed text of the audio
                "language": str,    # The detected language code (e.g., "en", "fr", etc.)
                "segments": List[Dict[str, Any]],  # List of segment dictionaries containing:
                    [
                        {
                            "id": int,              # Segment ID (0-indexed)
                            "seek": int,            # Frame index where segment starts
                            "start": float,         # Start time in seconds
                            "end": float,           # End time in seconds
                            "text": str,            # Transcribed text for the segment
                            "tokens": List[int],    # Token IDs for the transcribed text
                            "temperature": float,   # Temperature used for sampling
                            "avg_logprob": float,   # Average log probability of tokens
                                                   # (higher/closer to 0 = better)
                            "compression_ratio": float,  # Compression ratio of text
                            "no_speech_prob": float,     # Probability that segment contains no speech
                        },
                        # ... more segments
                    ]
            }
        """
        # Default to fp16=False if not specified - longer inference time but more precise
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
