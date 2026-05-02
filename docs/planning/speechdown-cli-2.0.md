# SpeechDown CLI 2.0 PRD Draft

Status: Draft for brainstorming  
Date: 2026-05-02

## Purpose

SpeechDown 2.0 should become a system-wide, fast, agent-friendly transcription layer for audio notes and dictation files. The product should optimize for usefulness in the first few seconds after an audio file appears, then keep improving quality in the background.

The working shorthand remains `sd`.

## Current Product Snapshot

SpeechDown currently provides:

- A Python CLI installed as `sd`.
- Project-local initialization through `.speechdown/`.
- Project-local config stored in `.speechdown/config.json`.
- SQLite transcription storage in `.speechdown/speechdown.db`.
- Markdown output grouped into daily files.
- Multiple configured languages, currently tried one by one for every file.
- A simple "best transcription" model based on confidence metrics.
- Research/prototype scripts for a macOS file watcher using `fswatch` and LaunchAgent.
- A standalone script for listing latest transcriptions from SQLite.

The current shape is useful, but it behaves like a batch transcriber. If one file is long, slow, modified while being read, or difficult to classify by language, the queue can stall. The UX also makes it hard to treat SpeechDown as a global operating-system service.

## Product Thesis

SpeechDown 2.0 should not start with "produce the perfect transcript." It should start with "make the latest voice input usable almost immediately."

The product should have two quality levels:

- Fast availability: a rough transcript should be available within roughly five seconds after a file is ready.
- Progressive improvement: the transcript can be replaced, extended, annotated, or upgraded as better processing finishes.

This changes SpeechDown from a project-local batch transcription command into a local transcription workbench with a global database, queue, state, heuristics, and useful CLI surfaces.

## Primary Users

### Human User

The human user records audio notes, dictation snippets, and longer spoken thoughts. They want recent transcriptions to appear quickly, be easy to inspect, and be good enough to hand to another tool or agent.

Important expectations:

- "Show me the latest things I said."
- "Do not get stuck on one long file."
- "Use the right language when I already know the language."
- "Keep improving old transcripts without blocking new ones."
- "Preserve my manual corrections."

### AI Agent User

An AI agent should be able to discover and consume recent voice context through a simple command-line interface.

Important expectations:

- List the latest transcriptions without knowing folder internals.
- Read metadata such as source file, language, confidence, status, and timestamps.
- Apply a user-provided replacement dictionary or correction rules.
- Understand whether text is partial, final, improved, or manually edited.
- Export or consume transcript text without depending on human-maintained Markdown files.

## Core Use Cases

### 1. Transcribe a File or Folder Directly

Running `sd <path>` should transcribe the given audio file or discover audio files under the given folder.

Default behavior:

- If `<path>` is an audio file, add or update that file's transcription in the global transcription database.
- If `<path>` is a folder, collect eligible audio files according to default or folder-specific rules.
- Avoid duplicate work when the same file has already been transcribed and has not changed.
- Make the transcription discoverable through `sd` / `sd latest`.
- Do not require the user to initialize a project before transcribing one file.
- Support both fast/progressive and full/blocking transcription modes.
- Continue improvement work in the background when using fast/progressive mode.

Possible options:

- `sd ~/Voice/note.m4a`
- `sd ~/Voice`
- `sd ~/Voice --recursive`
- `sd ~/Voice/note.m4a --language uk`
- `sd ~/Voice/note.m4a --fast`
- `sd ~/Voice/note.m4a --full`
- `sd ~/Voice/note.m4a --progress`
- `sd ~/Voice/note.m4a --improve`

Product goal: SpeechDown should be immediately usable as a system command for any audio file.

For a single file, `sd <audio-file>` should behave like an interactive command, not only like a queue submission. The open product question is whether the default should optimize for fast first output or for the best complete transcript. SpeechDown should support both modes clearly.

### 2. List Recent Transcriptions

Running `sd` with no arguments should show the latest transcriptions by default.

Default behavior:

- Show the full transcript text for the five latest eligible source files in watched folders.
- Prefer newest-first display.
- Include enough metadata to understand freshness and quality.
- Make it easy to copy/use the transcript text.
- Show a short selector for each record so the user can print or pipe a specific transcript.
- Include a compact status summary for the transcription system.

Display shape:

- Each record should start with a compact, informative header line.
- A useful header shape could be: `123: note.m4a | 2026-05-02 14:31 | uk | partial | conf=-0.42`.
- Prefer file name or shortened path by default, with full path available in verbose or JSON output.
- The transcript can follow the header as text, especially in the default five-item view.
- A compact one-line mode should be available for scanning, for example `sd latest --compact`.
- Human-readable source timestamps should be shown because source file modification time defines latest ordering.

Definition of "latest":

- Primary ordering should be by source audio file modification time.
- Transcription job time should be available as metadata, but should not be the default meaning of latest.
- This means a recently modified voice file remains latest even if an older file receives a background improvement pass.
- The transcript most recently produced by an explicit `sd <file>` command should still be easy to access, likely through a separate "last command result" selector or option.
- Incremental ids should identify database records and can be queried separately from source-file latest ordering.
- "Latest by id" and "latest by source file modification time" are different views and should not be confused in the UI.

Selector behavior:

- `sd latest` can show numbered rows such as `1`, `2`, `3`, or compact stable ids.
- A selector should be convenient for humans and scripts.
- Selectors should support printing transcript text without list metadata.
- Selectors should support structured output for agents.

Possible options:

- `sd --limit 20`
- `sd latest`
- `sd latest --json`
- `sd latest --folder ~/Voice`
- `sd latest --all`
- `sd latest --compact`
- `sd latest --status partial`
- `sd print 1`
- `sd print <id>`
- `sd print --last`
- `sd latest --plain 1`
- `sd status <id>`
- `sd latest-id`

Product goal: `sd` should be useful even when the user forgets command names.

Piping goal: after listing transcripts, it should be easy to pass one transcript to another command, for example:

```text
sd print 1 | pbcopy
sd print --last | some-agent-command
sd latest --json | jq ...
```

Status summary goal: the default view should include a small operational comment such as counts for `queued`, `partial`, `improving`, `failed`, and `needs-review` records. The user should be able to see that the system is making progress without opening a separate dashboard.

### 3. Inspect and Control a Transcription by ID

Every transcription record should have an id that allows direct inspection and control.

`sd status <id>` should explain what SpeechDown currently considers the best transcript for that source file.

Useful status details:

- Source file name and full path.
- Source file timestamp and transcription timestamps.
- Current status: `queued`, `partial`, `usable`, `improving`, `final`, `failed`, or `needs-review`.
- Chosen/best language.
- Candidate languages that were attempted.
- Confidence or other quality metrics for each candidate when available.
- Selected engine/backend and model.
- Whether the transcript is complete or partial.
- Substitutions or dictionary rules that were applied.
- Whether manual overrides exist.
- Suggested next commands.

Control commands should allow the user to keep iterating on a file even after SpeechDown considers it done.

Possible commands:

- `sd status 123`
- `sd print 123`
- `sd improve 123`
- `sd improve 123 --model small`
- `sd improve 123 --engine whisper-cpp --model small`
- `sd improve 123 --language uk`
- `sd set-language 123 uk`
- `sd choose 123 --candidate uk`
- `sd substitutions 123`
- `sd substitutions 123 --json`

Language override behavior:

- The user should be able to override the chosen language for a given id.
- If multiple language candidates already exist, `sd set-language 123 uk` or `sd choose 123 --candidate uk` can promote an existing candidate to best.
- If the requested language has not been attempted, SpeechDown can queue or run a new transcription pass for that language.
- Overrides should be recorded as events, not silent database mutation.
- Status output should show whether language choice was automatic or user-overridden.

Substitution behavior:

- Substitutions should be visible for a given id.
- Status should distinguish raw transcript, substituted transcript, and any manual override where practical.
- A compact summary can show counts by rule or dictionary.
- JSON output should expose enough detail for agents to understand what changed.

### 4. Watch Folders Globally

SpeechDown should support globally configured watch folders. Each watched folder may have its own rules, but those rules should live in one global config file rather than separate config files inside every folder.

Folder-level settings may include:

- Whether to scan recursively.
- Default language or language candidates.
- Default engine, model, or speed/quality profile.
- Whether files should be transcribed automatically.
- Whether partial transcripts should be stored and exposed.
- Replacement dictionaries or post-processing rules.

Product goal: SpeechDown should work across real capture locations, not only inside one manually initialized project directory.

### 5. Make a Transcript Available Quickly

When a new audio file appears, SpeechDown should produce an initial usable transcript as soon as practical.

Target:

- Within five seconds after the file is stable/available, a first transcript should exist for short recordings or at least a useful partial transcript should exist for longer recordings.

Candidate behavior:

- Detect that the file is finished writing before processing.
- Transcribe a short opening window first, such as 10-30 seconds.
- If the file is long, publish a partial transcript and move on.
- Return later to continue or improve it.
- For explicit `sd <audio-file>`, support either a fast first result or full blocking result depending on selected mode.

Recommended `sd <audio-file>` behavior:

- Provide a fast/progressive mode that tries to return transcript text within a short interactive budget, roughly five seconds.
- In fast/progressive mode, if a useful partial transcript is available in that budget, print it and store it as `partial` or `usable`.
- In fast/progressive mode, if no useful text is available in that budget, return a queued/in-progress status with a stable id and enough context to retrieve it later.
- Provide a full/blocking mode that waits for the best complete transcript and shows progress while running.
- If a background worker is available, fast/progressive mode can continue improving after the command returns.
- If no background worker is available, store the state so `sd improve <id>` or a later watcher run can continue the work.
- Avoid full transcription immediately only when the user is in fast/progressive mode and a faster heuristic can produce useful text.

Possible mode names:

- `sd <file>`: default mode, still to be decided.
- `sd <file> --fast`: return first useful transcript/status quickly and improve later.
- `sd <file> --full`: block until a full transcript is available.
- `sd <file> --full --progress`: block and show progress updates.
- `sd transcribe <file>`: possible explicit alias for full/blocking transcription if the default `sd <file>` becomes fast/progressive.

Configuration:

- The default mode for `sd <file>` should be configurable globally.
- A possible setting is `file_interaction_mode`, with values such as `fast-progressive` and `full`.
- Command-line flags should override the configured default for a single run.
- Watch folders may later have their own default mode, but the first decision is the global default for explicit file interaction.

Product concern:

- The fast/progressive mode is attractive technically, but it may not match the user's real behavior if they almost always want the best full transcript.
- The PRD should keep the fast mode easy to test without forcing it as the final default too early.

Suggested output language:

- Print transcript text as the main output, optimized for copying and reading.
- Put operational status after the transcript, not before it.
- Use a compact status footer in angle brackets, such as `<improving id=123 status: sd status 123>`.
- The footer should explain whether the transcript is partial, queued for improvement, or final.
- The footer should show the command needed to check status for that specific id.
- Prefer writing the transcript to stdout and the status footer to stderr, so piping captures only transcript text.
- Provide an explicit option to include or suppress status in stdout when needed.

Example:

```text
This is the first useful transcript text.

<partial id=123; improving in background; status: sd status 123>
```

Product goal: recent voice input should not disappear into a long-running background task.

### 6. Avoid Queue Starvation

The scheduler should keep moving across files instead of spending all time on one item.

Candidate behavior:

- Process work in small chunks.
- Prioritize new files and incomplete recent files.
- Cap per-file work in one pass.
- Resume long files over multiple passes.
- Track state so interruptions are harmless.

Useful statuses:

- `queued`
- `partial`
- `usable`
- `improving`
- `final`
- `failed`
- `needs-review`

Product goal: the latest five voice notes should become visible quickly even if yesterday's 90-minute recording is still improving.

### 7. Progressive Quality Improvement

SpeechDown should support a mode that continuously improves a given transcription or a folder of transcriptions.

Candidate improvement passes:

- Extend transcript from partial to full.
- Retry with a better model.
- Retry with a different language.
- Compare candidate languages.
- Apply correction dictionaries.
- Improve punctuation, paragraphing, or speaker readability.
- Mark low-confidence spans for review.
- Re-run or continue improvement for a specific id, including records already marked `final`.
- Promote a different candidate transcript as best when the user chooses it.

Product goal: quality should improve over time without blocking initial availability.

### 8. Language Control and Heuristics

The current approach tries every configured language for every file. That is robust in a narrow sense but slow and wasteful.

SpeechDown 2.0 should combine explicit user intent with learned heuristics.

Candidate inputs:

- Folder default language.
- Shortcut-selected language from macOS capture flows.
- Filename conventions.
- Recent language history for the same folder.
- Fast first-window language probe.
- Confidence metrics from model output.
- Manual correction events.

Product goal: if the user knows they are dictating in Ukrainian, English, or another language, SpeechDown should not spend time discovering what was already known.

### 9. Engine and Model Switching

SpeechDown should make it easy to switch transcription engines and models without changing the core CLI workflow.

Product rationale:

- Different engines may optimize for different tradeoffs: speed, quality, language support, installation friction, confidence metrics, or offline reliability.
- The user should be able to try a better backend for a specific file without losing prior results.
- Agents and future macOS capture workflows should not need to know implementation details of each engine.

Possible engines:

- `openai-whisper`: current Python/reference-style Whisper path.
- `whisper-cpp`: C/C++ Whisper runtime with strong Apple Silicon and cross-platform local support.
- `faster-whisper`: CTranslate2-based Whisper runtime, likely attractive for Python integration and speed.
- `mlx-whisper` / MLX-based Whisper wrappers: Apple Silicon-oriented Whisper path.
- `whisperkit`: Swift/Core ML-oriented Whisper path, likely more relevant for a future macOS app than the Python CLI.
- `parakeet`: NVIDIA Parakeet-family ASR models, especially interesting because they are not Whisper-derived and may be fast/accurate for supported languages.
- Future local or cloud engines, if needed.

Current local ASR landscape notes:

- Superwhisper is best understood as an app/workflow product, not a single model. Its local speech models include Whisper variants through `whisper.cpp` and NVIDIA Parakeet variants.
- Faster Whisper usually refers to `faster-whisper`, a CTranslate2 implementation of Whisper that can be much faster than the OpenAI Python package while preserving Whisper model behavior.
- Whisper.cpp remains a strong default candidate for local CLI use because it is dependency-light, Apple Silicon-friendly, cross-platform, and supports quantized Whisper models.
- Parakeet is worth testing separately from Whisper because it supports Ukrainian and Russian in multilingual v3, includes punctuation/capitalization and timestamps, and may change the speed/quality tradeoff.
- Apple-specific engines such as WhisperKit or MLX-based wrappers may matter more for the macOS app, but the CLI should avoid assuming all engines are Python packages.

Desired behavior:

- Global config can set a default engine and model.
- Folder config can override engine/model for watched folders.
- Commands can override engine/model for a single run.
- Status output should show which engine/model produced the current best transcript.
- Multiple engine outputs for the same source file can coexist as candidates.
- The user can improve a transcription by trying a different engine/model.
- Engine-specific metrics should be preserved, while common fields should be normalized for comparison.

Possible commands:

- `sd engines`
- `sd config set engine whisper-cpp`
- `sd config set model small`
- `sd <file> --engine whisper-cpp --model small`
- `sd improve 123 --engine openai-whisper --model medium`
- `sd status 123 --candidates`

Plugin stance:

- Treat engines as adapters behind a stable internal engine interface.
- Do not require a full external plugin system in the first 2.0 slice.
- Design the interface so external plugins can be added later if useful.
- First support a small registry of built-in engines, then consider user-installed plugins after the engine contract is proven.

Product goal: engine switching should feel like selecting a tool, not changing SpeechDown's workflow.

### 10. Correction Dictionaries and Events

SpeechDown should support automatic replacement dictionaries, especially for agent workflows.

Examples:

- Replace recurring misheard project names.
- Normalize names, tools, and acronyms.
- Convert dictated command phrases into desired spelling.

Important behavior:

- Keep raw transcript and corrected transcript distinguishable.
- Record correction events.
- Preserve human edits in Markdown.
- Make dictionary application repeatable and explainable.
- Make substitutions inspectable per transcription id.

Product goal: corrections should become part of SpeechDown's feedback loop, not invisible text mutation.

### 11. macOS Dictation Companion

SpeechDown CLI and SpeechDown macOS app should be treated as related but separate products.

CLI 2.0 should provide the transcription engine, storage, queue, file/folder workflows, and re-transcription controls.

The macOS app should be handled in a separate PRD. It is relevant here only because CLI 2.0 should not block future macOS dictation workflows.

The macOS app can focus on capture ergonomics:

- Multiple keyboard shortcuts.
- Shortcut-specific language/model presets.
- Dedicated dictation output location.
- Quick capture without opening the terminal.
- Visual confirmation that dictation is active while the user is focused in another text field.
- Insert or expose dictated text within roughly five seconds after capture stops.

Possible near-term bridge:

- A small CLI-based macOS integration can record audio into a dedicated folder with metadata naming or sidecar config.
- The watcher then transcribes those files using folder-level rules.
- Captured dictation files should be available through the CLI, including `sd latest`, `sd print`, and re-transcription/improvement commands.

Product goal: the CLI should be strong enough that the macOS app can be a thin capture layer at first, but the macOS app itself is not a purpose of this CLI PRD.

## Important Product Decisions

### Global vs Folder-Local Configuration

SpeechDown should use one global config file for the system.

The config should include:

- Global defaults: default display/export preferences, default engine/model profile, default dictionaries, and file interaction mode.
- Folder entries: path, recursive scan, language candidates, engine/model profile overrides, dictionary overrides, priority, and watch behavior.
- Explicit file interaction config: whether `sd <file>` defaults to fast/progressive or full/blocking behavior.

Open product rule:

- Folder entries override global defaults where explicit.
- The global config should make `sd` useful from any directory.
- Avoid requiring `.speechdown/config.json` inside every watched folder for 2.0.

Possible formats:

- YAML: more readable for nested folder entries and comments.
- TOML: stricter and common for tool configuration.

Initial preference:

- Use one human-editable YAML or TOML file. The exact format can be decided during implementation, but the product requirement is a single global config file with folder sections.

Example shape:

```yaml
file_interaction_mode: full
default_engine: whisper-cpp
default_model: large-v3-turbo

folders:
  - path: ~/Voice
    recursive: true
    languages: [uk, en, ru]
    engine: whisper-cpp
    model: large-v3-turbo
    watch: true
```

### Storage Model

SQLite should remain the product-facing source of truth for transcription records, state, metrics, and history.

The global database should be the default destination for all transcriptions, including one-off `sd <audio-file>` usage.

Markdown output should be a human-readable projection, not the primary product contract.

Product implication:

- `sd latest` should query SQLite/state, not scrape Markdown.
- Markdown generation can be optional, command-driven, or configured later.
- Markdown edits matter only when SpeechDown is explicitly managing Markdown output for that destination.

### Markdown Output Philosophy

Markdown output may be useful, but it should not dominate SpeechDown 2.0.

Possible product direction:

- 2.0 can omit automatic Markdown output entirely.
- Or 2.0 can provide a narrow export/projection command.
- Default export can split by date, but this should be a convenience, not a core storage model.
- Destination-specific Markdown rules can come after the core database and queue behavior are stable.

If SpeechDown writes Markdown, it should avoid overwriting human work.

Rules to preserve:

- Do not rewrite text before the first H2 header.
- Do not rewrite unrelated H2 sections.
- Do not erase human edits.
- Do not write output files if nothing changed.

2.0 addition:

- Markdown should communicate whether a transcript is partial, final, corrected, or needs review.

## Possible CLI Shape

This is a product sketch, not a final command contract.

```text
sd
sd ~/Voice/note.m4a
sd ~/Voice
sd latest
sd latest --limit 20
sd latest --json
sd latest --compact
sd print 1
sd print --last
sd status 123
sd latest-id
sd engines
sd config set engine whisper-cpp
sd improve 123 --language uk
sd improve 123 --engine whisper-cpp --model small
sd set-language 123 uk
sd substitutions 123

sd watch add ~/Voice --recursive --language uk
sd watch list
sd watch start
sd watch status

sd transcribe ~/Voice/file.m4a --language uk --fast
sd transcribe ~/Voice/file.m4a --language uk --full --progress
sd transcribe ~/Voice/file.m4a --engine whisper-cpp --model small
sd improve ~/Voice/file.m4a
sd improve --folder ~/Voice --budget 10m

sd export markdown --since today --output ~/Notes/voice
sd export markdown ~/Voice/note.m4a --output ~/Notes/voice/2026-05-02.md

sd dictation preset add ukrainian --language uk --model small
sd dictionary add ~/Voice/dictionary.json
```

The two most important contracts are:

- `sd` without arguments answers: "What did I say recently?"
- `sd <path>` answers: "Transcribe this and remember it globally."
- `sd print <selector>` answers: "Give me just that transcript so I can pipe it somewhere."
- `sd status <id>` answers: "What is happening with this specific transcription?"
- `sd improve <id>` answers: "Keep working on this transcription."
- `sd set-language <id> <language>` answers: "Use this language choice for this transcription."

## Success Criteria

### Speed

- A new short dictation file usually appears in `sd latest` within five seconds after it is stable.
- A long file gets a partial transcript quickly instead of blocking the queue.

### Reliability

- One broken or long file does not stop the system.
- Restarting the watcher does not duplicate work or lose state.
- Files modified during transcription are handled without publishing stale final output.

### Usefulness

- The default `sd` output is useful for both humans and agents.
- The latest five transcriptions can be inspected without knowing where the database lives.
- Latest entries have compact informative headers with id, file name, timestamp, language, status, and quality signal.
- A listed transcript can be selected and printed without metadata for piping.
- A transcription can be inspected and controlled by id.
- The user can override chosen language and keep improving a transcript after it is marked final.
- Substitutions are inspectable, not invisible.
- A one-off audio file can be transcribed without initializing a local project.
- Folder-specific language settings reduce unnecessary language retries.
- The user can switch engines/models globally, per folder, or per command.
- Status output makes engine/model provenance visible.

### Trust

- Human edits are preserved.
- Corrections are auditable.
- Partial vs final output is visible.
- Low-confidence output can be marked for review instead of silently treated as final.

## Non-Goals for First 2.0 Slice

- Replacing every current SpeechDown workflow at once.
- A full polished macOS GUI.
- Cloud transcription as a default dependency.
- Perfect diarization or speaker identification.
- A general note-taking application.
- Full-featured Markdown publishing as a core 2.0 requirement.
- A complex ML language-selection trainer before simpler heuristics are exhausted.

## Migration Consideration

The current `sd` command is already running and being used. During development, it may be safer to expose the new behavior as `sd2` until the 2.0 command semantics are stable.

Migration goals:

- Avoid breaking the current workflow while the new global database and queue model are being tested.
- Let `sd2` validate new defaults such as `sd2`, `sd2 <file>`, `sd2 latest`, and `sd2 print`.
- Move `sd2` behavior back to `sd` when the user decides the new command is ready, since SpeechDown is currently a single-user tool.

## First Product Slice

A practical first slice could be:

1. `sd <audio-file>` transcribes one file into the global database.
2. `sd <audio-file>` supports both fast/progressive and full/blocking transcription modes.
3. `sd` / `sd latest` lists the five latest transcription records from watched folders, ordered by source file modification time.
4. `sd print <selector>` prints one selected transcript for piping.
5. `sd status <id>` explains best transcript selection, language choice, status, candidates, metrics, and substitutions.
6. `sd improve <id>` can continue work on a specific transcription, including a record already marked final.
7. `sd set-language <id> <language>` can override or queue a language-specific pass.
8. `sd engines` lists available transcription engines.
9. `sd improve <id> --engine <engine> --model <model>` can add another candidate for a specific file.
10. `sd <folder>` discovers eligible audio files and queues/transcribes them.
11. Global config can register watched folders.
12. Single global config file supports folder entries with recursive scanning, language defaults, and engine/model defaults.
13. Watch mode processes files in short, fair units of work.
14. Initial partial transcript is stored and visible.
15. Later passes can promote partial transcripts toward final.
16. Status and quality metadata are exposed in CLI and SQLite.
17. Markdown output is omitted or limited to an explicit export command.

This slice would validate the core shift: SpeechDown as a fast, always-available transcription system rather than a batch command.

## Current Answers and Remaining Questions

Answered:

1. `sd` with no arguments should optimize for full transcript text of the five latest source files from watched folders, while still including selectors and a compact status summary.
2. The five-second goal does not require full output for long files. A partial transcript or clear incomplete status is acceptable.
3. Automatic Markdown output should be omitted from the first 2.0 slice or limited to an explicit optional export. It may become a watched-folder configuration later.
4. macOS SpeechDown should focus on dictation with different shortcuts for different languages, visual capture confirmation, and fast insertion/exposure of dictated text. It should have a separate PRD.
5. The CLI should support future macOS workflows by exposing captured dictations through global storage, latest listing, printing, and re-transcription/improvement commands.
6. For `sd <audio-file>`, the command can use heuristics to return partial text quickly and send deeper transcription to background improvement, but this should be a mode rather than the only behavior.
7. `latest` should focus on source file modification time. Incremental ids are a separate access path.
8. `sd2` can remain the migration command until the user decides it is safe to replace current `sd`.
9. The user needs ID-based control: inspect why a transcript is considered best, see chosen language and substitutions, override language, and keep improving a file after completion.
10. Transcription engine/model switching should be easy, but the first 2.0 slice should use a small built-in engine registry rather than a full external plugin system.

Remaining:

1. Should `sd <audio-file>` default to fast/progressive mode or full/blocking mode?
2. How should one-off files transcribed manually with `sd <audio-file>` appear in default latest views: only through `sd print --last`, through `sd latest --all`, or mixed into the default watched-folder list?
3. Should `sd latest-id` be a real command, or should latest-id access be handled through `sd status --latest-id` / `sd print --latest-id`?
4. What exact status footer format should be used after partial transcripts?
5. Should default `sd latest` show full transcript bodies, or compact headers plus snippets with `sd print <id>` for full text?

## Notes from Existing Project

- The current `transcribe` flow processes collected files sequentially.
- For each file, it loops through configured languages and saves all attempts.
- The best transcript is selected by confidence.
- Output is currently written after the transcription batch returns, not after each useful unit of progress.
- The existing watcher research is relevant but still treats `sd transcribe` as the processing unit.
- `scripts/list_latest_transcriptions.py` already points toward the desired default `sd latest` experience.
- Existing planning notes already mention fast first-window language detection and incremental file updates.
