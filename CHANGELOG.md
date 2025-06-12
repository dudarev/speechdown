# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

See [ADR 013](docs/adrs/current/013_use_changelog.md) for more details on the changelog usage.

## [Unreleased]

## [0.2.0] - 2025-06-12

### Added

- `--within-hours` option for `sd transcribe` command to filter files by modification time
  - Only transcribe files modified within the specified number of hours
  - Supports filtering through the entire transcription pipeline
  - Added time filtering support to audio file port and service layers

### Changed

- Whisper adapter can now be imported without dependency installation requirement

### Fixed

- Improved error handling in Whisper model adapter

## [0.1.0] - 2025-06-11

### Added

- Audio file transcription using OpenAI Whisper model.
- Command line interface with `init`, `config` and `transcribe` commands.
- Automatic language detection for audio files.
- Storage of transcriptions in a SQLite database.
- Output of transcripts to date-based Markdown files.
- Configuration options for languages, output directory and model name.
