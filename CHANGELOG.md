# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

See [ADR 013](docs/adrs/current/013_use_changelog.md) for more details on the changelog usage.

## [Unreleased]

## [0.2.5] - 2025-06-13

### Fixed

- Fix Hatch build configuration to properly include all package files in wheel distribution
- Correct conflicting build configuration that was causing empty wheel packages

## [0.2.4] - 2025-06-13

### Fixed

- Fix CLI entry point by properly exposing `cli` function at module level in `main.py`
- Add `main()` function as alternative entry point for better compatibility

## [0.2.3] - 2025-06-13

### Fixed

- Fix package installation by adding missing `__init__.py` files throughout the package structure
- Switch from setuptools to Hatch build system for better package discovery and more reliable builds
- Ensure all subpackages (application, domain, infrastructure, presentation) are properly included in wheel distribution

## [0.2.2] - 2025-06-13

### Fixed

- Add missing `__init__.py` file in `speechdown/presentation/` directory to fix `ModuleNotFoundError` when package is installed via pipx

## [0.2.1] - 2025-06-12

### Fixed

- Use audio file modification time instead of timestamp for `--within-hours`

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
