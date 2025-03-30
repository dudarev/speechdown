# SpeechDown Roadmap

This document outlines the mid-term development plan for SpeechDown, detailing features and improvements planned for the next 3-6 months.

## Replace voice-cli

The nearest term goal is to replace the existing `voice-cli` usage with SpeechDown's CLI.
`voice-cli` is our current tool for voice transcription that has limited functionality.
The replacement will provide immediate benefits to users with minimal disruption to existing workflows.

Key differences from the user standpoint in the beginning will be:

- Support of multiple languages (not just English)
- Specifying of output directory in settings during init
- Handling date ranges automatically
- Transcribing today and yesterday's files by default

## Transcription Enhancements

TODO(AD): Review what's below

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
