# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `--within-hours` option for `sd transcribe` command to filter files by modification time
  - Only transcribe files modified within the specified number of hours
  - Supports filtering through the entire transcription pipeline
  - Added time filtering support to audio file port and service layers

### Changed
- Whisper adapter can now be imported without dependency installation requirement

### Fixed
- Improved error handling in Whisper model adapter

## [0.1.0] - Initial Release

### Added
- Initial SpeechDown CLI implementation
- Audio file transcription using OpenAI Whisper
- Multi-language support
- SQLite database for transcription storage
- Configuration management
- Markdown output formatting
- Project initialization with `sd init`
- Basic CLI commands: `init`, `transcribe`, `config`