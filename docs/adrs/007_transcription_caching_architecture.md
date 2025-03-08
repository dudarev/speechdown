# ADR 007: Transcription Caching Architecture

**Date:** 2025-03-08
**Status:** Proposed

## Context

SpeechDown currently processes audio files and creates transcriptions without caching results. This leads to redundant processing when the same files are transcribed multiple times, which is inefficient and time-consuming, especially for larger audio files.

## Decision

We will implement a minimalist transcription caching system with the following characteristics:

### Cache Location:
- Store cache in `.speechdown/cache/` directory

### Cache Content:
- Store only the transcription text in plain text files
- Only store the best transcription obtained for each audio file

### Cache Identification:
- Use content-based hash of audio file (SHA-256) as the identifier
- No need to track model, provider, or version information in initial implementation

### File Naming:
- Use the audio file's SHA-256 hash as filename with a .txt extension:
  - `<file_hash>.txt`

### CachedTranscription Domain Entity:

```python
@dataclass
class CachedTranscription:
    audio_file: AudioFile
    text: str
```

### Port Definition:
- Simple cache interface that only deals with file hashes:
```python
class TranscriptionCachePort(Protocol):
    def get_cached_transcription(
        self, 
        audio_file: AudioFile
    ) -> CachedTranscription | None:
        ...
    
    def cache_transcription(
        self, 
        transcription: Transcription
    ) -> None:
        ...
```

### Directory Structure:
```
.speechdown/
├── cache/
│   ├── <file_hash1>.txt
│   ├── <file_hash2>.txt
│   └── ...
```

### CLI Cache Management:

#### Clear Cache Command:
```
speechdown clear-cache [options]
```

Options:
- `--all`: Remove all cached transcriptions
- `--older-than <days>`: Remove transcriptions older than specified days
- `--dry-run`: Show what would be deleted without actually deleting

#### Force Retranscription:
```
speechdown transcribe [file] --force
```

The `--force` flag will bypass cache and perform a new transcription.

## Consequences

### Positive
- Maximum simplicity: Just file hash → transcription mapping
- Zero configuration: No parameters to track or manage
- Minimal storage: Only one transcription per file
- Clear upgrade path: Can add model tracking later if needed
- Faster lookups: Only need to hash the audio file

### Negative
- No model tracking: Can't select specific model results
- No version history: New transcriptions overwrite old ones
- No quality metrics: Can't automatically select "best" transcription
- Limited flexibility: Can't maintain multiple transcriptions per file

## Conclusion

This simplified caching approach focuses on the core need: avoiding redundant processing of the same audio files. By eliminating model and version tracking, we achieve a more straightforward implementation that can be enhanced later if needed. This aligns with the principle of starting simple and adding complexity only when justified by actual usage patterns.
