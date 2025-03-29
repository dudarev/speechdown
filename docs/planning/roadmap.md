# SpeechDown Roadmap

This document outlines the mid-term development plan for SpeechDown, detailing features and improvements planned for the next 3-6 months.

## Transcription Enhancements

- Implement transcription caching system
  - Store processed audio hashes to avoid redundant transcription
  - Allow ignore-existing option in CLI
- Add configurable Whisper model selection
  - Support multiple model sizes (tiny, base, small, medium, large)
  - Allow language-specific model configuration

## Output Improvements

- Add multiple output format options (Markdown, TXT, SRT)
- Implement smart formatting with speaker detection
- Add post-processing options for improving transcription readability

## CLI Experience

- Improve progress reporting during transcription
- Add batch processing capabilities
- Create interactive config editor

## Performance

- Optimize memory usage for large audio files
- Implement parallel processing for multiple files

## Dependencies

- The caching system and model selection are highest priorities based on current needs
- CLI improvements will follow after core functionality enhancements
