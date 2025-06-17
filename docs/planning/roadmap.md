# SpeechDown Roadmap

This document outlines the mid-term development plan for SpeechDown, detailing features and improvements planned for the next 3-6 months.

## Replace voice-cli
IN PROGRESS.
The nearest term goal is to replace the existing [`voice-cli`](https://github.com/dudarev/voice-cli) usage with SpeechDown's CLI.  
`voice-cli` is a tool for voice transcription that has limited functionality.
The replacement will provide immediate benefits to users with minimal disruption to existing workflows.

Key differences from the user standpoint in the beginning will be:

- Support of multiple languages (not just English)
- Specifying of output directory in settings during init
- Handling date ranges automatically
- Transcribing today and yesterday's files by default

## UX

- Accept commands from the Markdown files it generated such as:
  - re-transcribe in different language
  - learn correction
- Do not re-write corrections
- Do not re-write text before the first section
- Do not re-write non-transcript sections

## CLI Experience

- Improve progress reporting during transcription

## Performance

- Optimize memory usage for large audio files
- Implement parallel processing for multiple files
