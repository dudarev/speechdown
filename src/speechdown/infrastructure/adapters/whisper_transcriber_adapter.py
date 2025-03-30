from typing import Dict, Any, List
import statistics

from speechdown.application.ports.transcriber_port import TranscriberPort
from speechdown.domain.entities import AudioFile, Transcription
from speechdown.domain.value_objects import Language, TranscriptionMetrics, MetricSource
from speechdown.infrastructure.adapters.whisper_model_adapter import WhisperModelAdapter


class WhisperTranscriberAdapter(TranscriberPort):
    """
    Adapter for Whisper transcription model.

    This adapter uses Whisper model to transcribe audio files and extract metrics
    from the transcription results. It operates on the output of the Whisper
    transcribe method, which returns a dictionary with the following structure:

    {
        "text": str,        # The full transcribed text of the audio
        "language": str,    # The detected language code (e.g., "en", "fr", etc.)
        "segments": [       # List of segment dictionaries
            {
                "id": int,              # Segment ID (0-indexed)
                "seek": int,            # Frame index where this segment starts
                "start": float,         # Start time in seconds
                "end": float,           # End time in seconds
                "text": str,            # Transcribed text for this segment
                "tokens": List[int],    # Token IDs for the transcribed text
                "temperature": float,   # Temperature used for sampling
                "avg_logprob": float,   # Average log probability of tokens
                "compression_ratio": float,  # Compression ratio of text
                "no_speech_prob": float,     # Probability of no speech
            },
            # ... more segments
        ]
    }

    The adapter extracts metrics from this output and creates a Transcription object
    with relevant metrics for later processing and comparison.
    """

    def __init__(self, model: WhisperModelAdapter):
        self.model = model

    def _calculate_confidence(
        self, segments: List[Dict[str, Any]], avg_logprobs: List[float]
    ) -> float | None:
        """
        Calculate a confidence score from transcription data.

        Currently uses a simple mean of avg_logprobs, but could be enhanced to use:
        - Duration-weighted average (weighting segments by their length)
        - Token-weighted average (weighting by number of tokens/words)

        Args:
            segments: The segments from the transcription result
            avg_logprobs: The average log probabilities from each segment

        Returns:
            A confidence score or None if no data is available
        """
        if not avg_logprobs:
            return None

        # Simple mean of log probabilities (baseline implementation)
        return statistics.mean(avg_logprobs)

        # TODO(AD): Consider implementing more sophisticated confidence calculation
        # For example, weighting by segment duration:
        #
        # if segments and avg_logprobs:
        #     durations = [(seg.get("end", 0) - seg.get("start", 0)) for seg in segments
        #                 if "avg_logprob" in seg]
        #     total_duration = sum(durations)
        #     if total_duration > 0:
        #         return sum(prob * dur for prob, dur in zip(avg_logprobs, durations)) / total_duration
        # return None

    def _extract_metrics_from_result(self, result: Dict[str, Any]) -> TranscriptionMetrics:
        """
        Extract metrics from Whisper transcription result.

        Args:
            result: The dictionary returned by Whisper's transcribe method

        Returns:
            A TranscriptionMetrics object containing extracted metrics
        """
        segments = result.get("segments", [])

        # Calculate aggregate metrics across all segments
        avg_logprobs = [seg.get("avg_logprob") for seg in segments if "avg_logprob" in seg]
        compression_ratios = [
            seg.get("compression_ratio") for seg in segments if "compression_ratio" in seg
        ]
        no_speech_probs = [seg.get("no_speech_prob") for seg in segments if "no_speech_prob" in seg]

        # Calculate audio duration from segments
        audio_duration = 0
        if segments:
            last_segment = segments[-1]
            audio_duration = last_segment.get("end", 0)

        # Count words in the transcript
        word_count = len(result.get("text", "").split()) if "text" in result else 0

        # Calculate confidence using the dedicated method
        confidence = self._calculate_confidence(segments, avg_logprobs)

        # Create metrics object
        metrics = TranscriptionMetrics(
            confidence=confidence,
            avg_logprob_mean=statistics.mean(avg_logprobs) if avg_logprobs else None,
            compression_ratio_mean=statistics.mean(compression_ratios)
            if compression_ratios
            else None,
            no_speech_prob_mean=statistics.mean(no_speech_probs) if no_speech_probs else None,
            audio_duration_seconds=audio_duration,
            word_count=word_count,
            words_per_second=(word_count / audio_duration)
            if audio_duration > 0 and word_count > 0
            else None,
            model_name=self.model.name,
            source=MetricSource.WHISPER,
            additional_metrics={
                "segments_count": len(segments),
                "temperature": segments[0].get("temperature") if segments else None,
            },
        )

        return metrics

    def transcribe(self, audio_file: AudioFile, language: Language) -> Transcription:
        """
        Transcribe an audio file with a specified language.

        This method uses the Whisper model to transcribe the audio file with a
        specified language. The language is passed to the Whisper model to guide
        the transcription process.

        Args:
            audio_file: The audio file to transcribe
            language: The language to use for transcription

        Returns:
            A Transcription object containing the transcribed text and associated metrics
        """
        # Time the transcription process using monotonic for more accurate measurement
        import time

        start_time = time.monotonic()

        # Use the provided model to transcribe with the specified language
        result = self.model.transcribe(str(audio_file.path), language=language.code)

        # Calculate transcription time
        transcription_time_seconds = time.monotonic() - start_time

        # Extract metrics from the result
        metrics = self._extract_metrics_from_result(result)

        # Add transcription time to metrics
        # Create a new TranscriptionMetrics object including all fields from the original
        # metrics object, but with the updated transcription_time_seconds
        metrics_dict = {k: v for k, v in metrics.__dict__.items() if not k.startswith("_")}
        metrics_dict["transcription_time_seconds"] = transcription_time_seconds
        metrics = TranscriptionMetrics(**metrics_dict)

        # Create and return a Transcription object
        return Transcription(
            audio_file=audio_file,
            text=result["text"],
            language=language or Language(result["language"]),
            metrics=metrics,
        )

    def auto_transcribe(self, audio_file: AudioFile) -> Transcription:
        """
        Automatically detect language and transcribe an audio file.

        This method uses the Whisper model to automatically detect the language
        of the audio and transcribe it. No language parameter is provided to the
        model, allowing it to perform language detection.

        Args:
            audio_file: The audio file to transcribe

        Returns:
            A Transcription object containing the transcribed text, detected language,
            and associated metrics
        """
        # Time the transcription process using monotonic for more accurate measurement
        import time

        start_time = time.monotonic()

        # Use the provided model to detect language and transcribe
        result = self.model.transcribe(str(audio_file.path))

        # Calculate transcription time
        transcription_time_seconds = time.monotonic() - start_time

        # Extract metrics from the result
        metrics = self._extract_metrics_from_result(result)

        # Add transcription time to metrics
        # Create a new TranscriptionMetrics object including all fields from the original
        # metrics object, but with the updated transcription_time_seconds
        metrics_dict = {k: v for k, v in metrics.__dict__.items() if not k.startswith("_")}
        metrics_dict["transcription_time_seconds"] = transcription_time_seconds
        metrics = TranscriptionMetrics(**metrics_dict)

        # Create and return a Transcription with detected language
        return Transcription(
            audio_file=audio_file,
            text=result["text"],
            language=Language(result["language"]),
            metrics=metrics,
        )
