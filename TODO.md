# SpeechDown TODOs

This file tracks short-term implementation tasks following [ADR 006](docs/adrs/006_task_tracking_approach.md).

Align with [roadmap](docs/planning/roadmap.md) for mid-term planning.

## In Progress

- Clean-up branches on GitHub https://github.com/dudarev/speechdown
- TASK: RESEARCH: rules for GitHub copilot, Jules, Claude Code etc.
- Research: Audio Timestamp Extraction
  - From file names
  - From file metadata
- If the `-d` (directory) option is not provided when running the CLI, it should default to using the current working directory (the directory from which the command is executed) as the target for processing audio files.
- Voice notes should be grouped to daily files and the timestamps should be correct at least based on file names. 
- Collect relevant notes about SpeechDown - ongoing - use [ar](docs/notes/ar.md) notes

## Nearest Future

- Introduce CHANGELOG.md (ADR for it)
- Output file is updated as transcription occurs
- [ ] Improve transcription output handling
  - [ ] Get existing output
  - [ ] Update transcriptions based on existing output
  - [ ] Update the output
- [ ] Unit tests for `transcription_service.py`

## Notes

- Tasks from this file may be promoted to GitHub issues when ready for implementation if they require more detailed tracking or collaboration
- See `docs/planning/` for strategic roadmaps and vision
