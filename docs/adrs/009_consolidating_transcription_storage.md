# ADR 009: Consolidating Transcription Storage

**Date:** 2025-03-18
**Status:** Accepted
**Supersedes:** [ADR 007](archive/007_transcription_caching_architecture.md)

## Context

Currently, SpeechDown uses two separate mechanisms for storing transcriptions:

1. A file-based cache system (described in ADR 007) for avoiding redundant processing
2. A SQLite repository for storing transcription data, including metrics

This dual approach leads to:

- Redundant code paths for storing/retrieving transcriptions
- Increased complexity for maintaining two storage mechanisms
- Duplicated transcription text in both systems

## Decision

We will deprecate the separate file-based caching system and consolidate all transcription storage into the repository pattern. The [`SQLiteRepositoryAdapter`](../../src/speechdown/infrastructure/adapters/repository_adapter.py) already implements the functionality needed:

- `get_best_transcription()` serves the same purpose as cache lookup
- `save_transcription()` handles persisting transcription data

### Changes:

1. Deprecate the [`TranscriptionCachePort`](../../src/speechdown/application/ports/transcription_cache_port.py) interface
2. Remove [`FileSystemTranscriptionCacheAdapter`](../../src/speechdown/infrastructure/adapters/file_system_transcription_cache_adapter.py) implementation
3. Update service classes to use repository instead of cache
4. Do not create migrations since the project is still in development

### CLI Commands:

The CLI commands will be updated:

- `speechdown transcribe --force` → `speechdown transcribe --ignore-existing`

## Consequences

### Positive

- Single source of truth for transcriptions
- Simplified architecture
- Reduced code complexity
- Better metrics-based selection of "best" transcription
- Unified storage interface

### Negative

- Potential performance difference between file-based and SQLite access
- SQLite dependency for all transcription storage

## Implementation Plan

1. Extend repository interface to include cache-equivalent functionality
2. Update services to use repository instead of cache
3. Update CLI command structure
4. Remove deprecated cache components
