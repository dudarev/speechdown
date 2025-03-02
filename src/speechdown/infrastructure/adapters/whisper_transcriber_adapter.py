from typing import Dict, Any
import statistics

from speechdown.application.ports.transcriber_port import TranscriberPort
from speechdown.application.ports.transcription_model_port import TranscriptionModelPort
from speechdown.domain.entities import AudioFile, Transcription
from speechdown.domain.value_objects import Language, TranscriptionMetrics, MetricSource


class WhisperTranscriberAdapter(TranscriberPort):
    def __init__(self, model: TranscriptionModelPort):
        # Initialize with provided model
        self.model = model

    def _extract_metrics_from_result(self, result: Dict[str, Any]) -> TranscriptionMetrics:
        """Extract metrics from Whisper transcription result"""
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

        # Create metrics object
        metrics = TranscriptionMetrics(
            confidence=statistics.mean(avg_logprobs) if avg_logprobs else None,
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
            source=MetricSource.WHISPER,
            additional_metrics={
                "segments_count": len(segments),
                "temperature": segments[0].get("temperature") if segments else None,
                "model_name": self.model.name,
            },
        )

        return metrics

    def transcribe(self, audio_file: AudioFile, language: Language) -> Transcription:
        # Use the provided model to transcribe the audio file
        result = self.model.transcribe(
            str(audio_file.path),
            language=language.code if language else None,
        )

        # Extract metrics from the result
        metrics = self._extract_metrics_from_result(result)

        # Create and return a Transcription object
        return Transcription(
            audio_file=audio_file,
            text=result["text"],
            language=language or Language(result["language"]),
            metrics=metrics,
        )

    def auto_transcribe(self, audio_file: AudioFile) -> Transcription:
        # Use the provided model to detect language and transcribe
        result = self.model.transcribe(str(audio_file.path))

        # Extract metrics from the result
        metrics = self._extract_metrics_from_result(result)

        # Create and return a Transcription with detected language
        return Transcription(
            audio_file=audio_file,
            text=result["text"],
            language=Language(result["language"]),
            metrics=metrics,
        )
