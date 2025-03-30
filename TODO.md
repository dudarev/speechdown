# SpeechDown TODOs

This file tracks short-term implementation tasks following [ADR 006](docs/adrs/006_task_tracking_approach.md).

## Current Tasks

- [x] [ADR 009](docs/adrs/009_consolidating_transcription_storage.md): Consolidate transcription storage - tell Copilot to implement this
  - [x] Deprecate `TranscriptionCachePort` interface
  - [x] Remove `FileSystemTranscriptionCacheAdapter` implementation
  - [x] Update service classes to use repository instead of cache
  - [x] Update CLI command structure
  - [x] Remove deprecated cache components
  - [x] Update CLI command to use `--ignore-existing` instead of `--force`
  - [x] Make sure tests are passing `make ci-full`
  - [x] Validate with `make debug`
  - [x] Remove `make run` command
  - [x] Deprecate ADR 007, put it to archive subfolder
- [ ] Implement transcription_time_seconds and model_name
- [ ] Unit tests for `transcription_service.py`
- [ ] Implement date range filtering for transcriptions
  - [ ] pass date range in CLI
  - [ ] filter files based on date
  - [ ] output transcriptions based on date range
- [ ] Implement gathering metrics for transcriptions
- [ ] Add configurable model selection
  - [ ] Add model_name field to ConfigAdapter
  - [ ] Update config.json schema to include model selection
  - [ ] Create CLI command to update config with model selection
  - [ ] Pass model_name from config to WhisperModelAdapter in commands.py
- [ ] Improve transcription output handling
  - [ ] Get existing output
  - [ ] Update transcriptions based on existing output
  - [ ] Update the output

## Notes

- Tasks from this file may be promoted to GitHub issues when ready for implementation if they require more detailed tracking or collaboration
- See `docs/planning/` for strategic roadmaps and vision
