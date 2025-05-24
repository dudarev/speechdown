# SpeechDown TODOs

This file tracks short-term implementation tasks following [ADR 006](docs/adrs/006_task_tracking_approach.md).

Align with [roadmap](docs/planning/roadmap.md) for mid-term planning.

## In Progress

- [ ] Collect relevant notes about SpeechDown in SpeechDown format - ongoing - use [ar](docs/notes/ar.md) notes
- [x] ADR 010: Introduce Markdown Design Documents for Feature Implementation
- [x] First design document: `2025-05-dd-file-output.md` - how to implement file output
  - [x] Support output directory configuration via config file and command
  - [x] Map speech notes to daily text files with timestamped headers
- [x] Introduce `current/` and `archive/` directories for ADRs too
- [x] Ensure language configuration setting exist
  - [x] Add it if it does not
  - [x] Describe it in README.md

## Nearest Future

- Output file is updated as transcription occurs
- [ ] Add configurable model selection
  - [ ] Add model_name field to ConfigAdapter
  - [ ] Update config.json schema to include model selection
  - [ ] Create CLI command to update config with model selection
  - [ ] Pass model_name from config to WhisperModelAdapter in commands.py
- Remove TranscriptionCachePort and what depends on it
- [ ] Improve transcription output handling
  - [ ] Get existing output
  - [ ] Update transcriptions based on existing output
  - [ ] Update the output
- [ ] Unit tests for `transcription_service.py`

## Notes

- Tasks from this file may be promoted to GitHub issues when ready for implementation if they require more detailed tracking or collaboration
- See `docs/planning/` for strategic roadmaps and vision
