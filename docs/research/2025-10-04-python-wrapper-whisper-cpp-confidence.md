# Python Wrapper for Whisper CPP with Confidence Metrics
*Status*: Active
*Date*: 2025-10-04

## Problem
SpeechDown needs a Python wrapper for Whisper CPP that provides confidence metrics in transcription results. The current pywhispercpp wrapper does not include confidence by default, and we require per-segment confidence scores for ML model training to correct language selection among three languages.

## Approach
Research Python wrappers for ggerganov's whisper.cpp that include confidence/probability scores in their output. Evaluate top candidates for integration into SpeechDown's infrastructure layer, implementing the TranscriberPort interface.

## Findings
[To be filled by research AI]

## Next steps
[To be filled by research AI]

---

**Research Prompt: Python Wrapper for Whisper CPP with Confidence Metrics**

I need you to conduct deep research on Python wrappers for the Whisper CPP library (https://github.com/ggerganov/whisper.cpp). This wrapper must be suitable for integration into a Python project called SpeechDown, available at https://github.com/dudarev/speechdown, which follows Domain-Driven Design (DDD) architecture with layers: domain, application, infrastructure, and presentation. The wrapper should provide transcription results with confidence metrics (probability scores) for each segment, as SpeechDown transcribes audio in three languages and needs confidence values as features for an ML model to correct language selection.

**Key Requirements:**
- The wrapper must return confidence metrics as part of the transcription response (not just segments without probabilities).
- It should be embeddable into the infrastructure layer of SpeechDown, implementing a TranscriberPort interface.
- Ensure the wrapper supports CPU-based inference (no GPU requirements) and is compatible with Python 3.11+.
- Verify it can handle multiple languages and provide per-segment confidence scores.

**Research Tasks:**
1. Identify Python wrappers for ggerganov's whisper.cpp that include confidence/probability scores in their output.
2. Analyze the API documentation and source code of promising wrappers to confirm confidence score availability and ease of integration.
3. Check installation methods, dependencies, and compatibility with macOS/Linux.
4. Evaluate performance, licensing (MIT preferred), and community support.
5. Identify any limitations or alternatives if no wrapper fully meets needs.
6. Provide code snippets demonstrating transcription with confidence extraction from the best candidate wrapper.

**Relevant Links:**
- SpeechDown Project: https://github.com/dudarev/speechdown
- Whisper CPP: https://github.com/ggerganov/whisper.cpp

**SpeechDown Interfaces and Example Implementation:**

From `src/speechdown/domain/entities.py` (TranscriptionResult and related entities):
```python
@dataclass
class Transcription:
    audio_file: AudioFile
    text: str
    language: Language
    metrics: TranscriptionMetrics
    transcription_started_at: datetime | None = None

# Type alias for composed transcription type
TranscriptionResult = Union[Transcription, CachedTranscription]
```

From `src/speechdown/domain/value_objects.py` (TranscriptionMetrics):
```python
@dataclass(frozen=True)
class TranscriptionMetrics:
    # The confidence score is a single value that allows comparison between different transcriptions.
    # It's derived from the model's internal metrics (typically avg_logprob values) and represents
    # the overall reliability of the transcription. Higher values (closer to 0) indicate higher confidence.
    # This is the primary metric used when selecting the "best" transcription among alternatives.
    confidence: Optional[float] = None
    # ... other fields
```

From `src/speechdown/application/ports/transcriber_port.py` (TranscriberPort interface):
```python
class TranscriberPort(Protocol):
    """Port for transcription services."""

    def __init__(self, model: TranscriptionModelPort): ...

    def auto_transcribe(self, audio_file: AudioFile) -> Transcription: ...

    def transcribe(self, audio_file: AudioFile, language: Language) -> Transcription: ...
```

From `src/speechdown/infrastructure/adapters/whisper_transcriber_adapter.py` (Example implementation):
```python
class WhisperTranscriberAdapter(TranscriberPort):
    def __init__(self, model: WhisperModelAdapter):
        self.model = model

    def _calculate_confidence(
        self, segments: List[Dict[str, Any]], avg_logprobs: List[float]
    ) -> float | None:
        if not avg_logprobs:
            return None
        return statistics.mean(avg_logprobs)

    def _extract_metrics_from_result(self, result: Dict[str, Any]) -> TranscriptionMetrics:
        segments = result.get("segments", [])
        avg_logprobs = [seg.get("avg_logprob") for seg in segments if "avg_logprob" in seg]
        confidence = self._calculate_confidence(segments, avg_logprobs)
        # ... extract other metrics
        metrics = TranscriptionMetrics(
            confidence=confidence,
            avg_logprob_mean=statistics.mean(avg_logprobs) if avg_logprobs else None,
            # ... other fields
        )
        return metrics

    def transcribe(self, audio_file: AudioFile, language: Language) -> Transcription:
        result = self.model.transcribe(str(audio_file.path), language=language.code)
        metrics = self._extract_metrics_from_result(result)
        return Transcription(
            audio_file=audio_file,
            text=result["text"],
            language=language,
            metrics=metrics,
        )
```

**Expected Output:**
- Summary of findings with pros/cons for the top 2-3 wrappers.
- Integration recommendations for SpeechDown.
- Any code examples or modifications needed.
- Alternative approaches if no suitable wrapper exists.