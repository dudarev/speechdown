# SpeechDown macOS Dictation App PRD Draft

Status: Draft for brainstorming  
Date: 2026-05-02

## Purpose

SpeechDown macOS should be a minimal personal dictation app for turning short spoken input into usable text in the active macOS context, while preserving every capture as durable audio and transcription history for later inspection, re-transcription, and comparison.

This is a separate product surface from SpeechDown CLI 2.0. The app should use the same underlying transcription records where practical, but it should not try to become the whole SpeechDown CLI, a general notes app, or a polished commercial dictation product in the first version.

## Product Thesis

The biggest personal value is not "transcribe every audio file." It is "press the right shortcut, speak in the intended language, and get text into the place I am already working."

The app should optimize for three things:

- Explicit language intent from the shortcut.
- Fast, visible capture and insertion into the focused app.
- Durable capture history that can be improved later with better engines, models, vocabulary, and comparison tools.

The app can be rough, local, and small at first. Trust matters more than polish: the user should know when recording is active, where the audio went, what text was inserted, and how to find or improve it later.

## Reference App Inspiration

These products are useful references, but SpeechDown macOS should remain narrower than all of them:

- [Handy](https://github.com/cjpais/Handy): local/offline transcription, global shortcuts, push-to-talk or toggle recording, Whisper and Parakeet support, VAD, direct insertion, and CLI control of a running app.
- [Pindrop](https://github.com/watzon/pindrop): small native macOS menu bar app shape, Swift/SwiftUI, WhisperKit, local history, hotkeys, clipboard plus optional direct insertion, and model-size switching.
- [Whispur](https://whispur.app/): speech provider choice by workflow, local default with optional cloud providers, menu bar status, compact recording overlay, and optional cleanup providers.
- [Steno](https://stenovoice.app/): app-aware insertion strategy for terminals, editors, and normal text fields.
- [OpenWhispr](https://github.com/OpenWhispr/openwhispr): broader long-term direction around local/cloud engines, transcript history, APIs, MCP/agent access, and notes.
- [FreeFlow](https://freeflow.zachlatta.com/): custom shortcuts, context-aware cleanup, custom vocabulary, and voice macros.

## Primary Workflows

### 1. Dictate Ukrainian into the Active App

The user focuses a text field, presses the Ukrainian dictation shortcut, speaks, stops recording, and receives Ukrainian text at the cursor or in the clipboard.

Expected behavior:

- Shortcut implies `language=uk`.
- The app gives obvious visual confirmation that Ukrainian dictation is active.
- Audio is saved before transcription starts.
- The resulting transcript is inserted into the focused app when possible.
- The capture is also available through SpeechDown history and future CLI commands.

### 2. Dictate English into the Active App

The user presses a different shortcut for English dictation.

Expected behavior:

- Shortcut implies `language=en`.
- The app should not spend time guessing language when the shortcut already selected it.
- English may use a different engine, model, vocabulary, cleanup profile, or insertion style later, but the minimal version only needs explicit language separation.

### 3. Save a Capture for Later Comparison

Every dictation becomes a stored capture, not a disposable paste operation.

Expected behavior:

- The app saves the original audio file.
- The app stores one or more transcription candidates.
- The user can later re-run transcription on the same audio with a different engine/model/language.
- The user can compare candidates and select a preferred one without losing the raw audio or prior text.

### 4. Optional Interstitial Journal Capture

The user presses a journal shortcut, speaks a quick thought, and does not necessarily want it pasted into the current app.

Expected behavior:

- Capture is routed to a configured journal folder or mode.
- The transcript can later be projected into daily Markdown if configured.
- This should remain optional and out of the minimal first version unless it is cheap to support through the same routing mechanism.

## Minimal First Version

The first useful app should include:

- Menu bar app or tiny background app with menu bar status.
- At least two configurable global shortcuts.
- Shortcut-specific language selection, initially Ukrainian and English.
- Toggle recording or push-to-talk; toggle is likely easier to verify, push-to-talk may feel faster later.
- Visual recording indicator that shows active state and selected language.
- Audio capture saved to a durable location.
- Transcription using one local engine/model path or a call into the existing CLI/shared service.
- Clipboard output for all transcriptions.
- Best-effort direct insertion into the focused app when Accessibility permission is available.
- A simple way to open or reveal the latest capture/history.
- Shared storage or export metadata sufficient for future CLI inspection.

The first version does not need:

- A full preferences UI.
- A full transcript browser.
- Multi-provider cloud support.
- Complex per-app insertion profiles.
- Daily Markdown publishing.
- Polished onboarding.
- Automatic language detection.

## Shortcut and Language Behavior

Shortcuts are not just triggers. They are intent declarations.

Each shortcut should have a named preset:

```text
ukrainian-dictation:
  shortcut: configurable
  language: uk
  mode: insert
  destination: default dictation history

english-dictation:
  shortcut: configurable
  language: en
  mode: insert
  destination: default dictation history

journal-capture:
  shortcut: configurable
  language: configurable
  mode: capture-only
  destination: journal folder
```

Product requirements:

- Language selected by shortcut should override automatic detection.
- The active indicator should show enough context to avoid speaking in the wrong mode, for example `Recording: UK` or `Recording: EN`.
- If a shortcut has no language configured, the app may use a default language or an engine's auto-detect mode, but this should be explicit in the preset.
- Presets should eventually allow engine/model, vocabulary, cleanup, destination, and insertion behavior overrides.
- The minimal version can store presets in a hand-edited config file if building UI would slow the first slice.

## Capture and Visual Feedback Behavior

The app should make recording state unambiguous without stealing focus from the target app.

Required states:

- Idle.
- Recording with selected preset/language.
- Stopping/saving audio.
- Transcribing.
- Inserted/copied.
- Failed, with a way to recover the saved audio.

Visual feedback options:

- Menu bar icon state change.
- Small floating top-center indicator.
- Minimal waveform or timer if cheap.
- Notification only for failure or completion when insertion is not possible.

Rules:

- Starting dictation must not change the focused text field.
- Recording feedback must not break paste-back into the original app.
- The app should save the audio before attempting insertion.
- If transcription fails, the capture should still exist and be discoverable.
- If insertion fails, the transcript should be copied to the clipboard and marked as not inserted.

## Text Insertion Behavior

Text insertion is part of the core product because the user is dictating into an existing workflow, not creating a note in the app.

Minimum behavior:

- Always copy final text to the clipboard.
- If Accessibility permission is available, attempt direct insertion at the active cursor.
- If direct insertion is unreliable, use paste simulation as a fallback.
- Show whether text was inserted or only copied.

Future app-aware behavior:

- Terminals may need clipboard paste or bracketed-paste-safe behavior.
- Editors may benefit from direct typing because it can trigger autocomplete or editor behavior.
- Normal text fields can usually accept paste.
- Browser fields, Electron apps, IDEs, terminals, and secure fields may need separate handling.

The app should record insertion metadata:

- Target app bundle id/name if available.
- Insertion method attempted.
- Whether insertion appeared to succeed.
- Whether clipboard was modified.

This metadata will help decide later whether Steno-style app-aware insertion is worth implementing.

## Storage and Relationship to SpeechDown CLI

Every app capture should create a durable record suitable for CLI access.

Storage should include:

- Audio file path.
- Capture timestamp.
- Shortcut/preset id.
- Intended language.
- Target app metadata if available.
- Transcription candidate id(s).
- Engine/model used.
- Raw transcript text.
- Corrected/substituted transcript text when applicable.
- Insertion status.
- Destination or routing mode.

Preferred product contract:

- SQLite/global SpeechDown storage is the source of truth for metadata and transcription candidates.
- Audio files are stored under a stable global capture directory.
- Markdown is optional projection, not primary storage.
- The CLI and app can both read the same records.

The app may initially call the CLI or write files in a watched folder if that is the fastest path. However, the product goal is shared global records, not a private app silo.

Possible future CLI surfaces:

```text
sd dictations
sd latest --source macos
sd print <id>
sd status <id>
sd improve <id> --engine whisperkit --model large-v3
sd compare <id>
sd substitutions <id>
```

## Retranscription and Comparison Workflow

The app should preserve the raw audio because the first transcript may not be the best transcript.

Core requirements:

- A capture can have multiple transcription candidates.
- Candidates may differ by language, engine, model, vocabulary, cleanup profile, and timestamp.
- One candidate can be selected as current/best.
- The original inserted text should remain visible as a candidate or event, even if a later candidate is better.
- Manual selection should be recorded as an event, not silent mutation.

Comparison should expose:

- Engine/model.
- Language.
- Runtime/latency.
- Raw confidence or quality metrics when available.
- Whether vocabulary/substitutions were applied.
- Whether the candidate was inserted.
- Subjective selection or notes.
- Transcript text for side-by-side review.

Minimal app behavior can defer rich comparison UI to the CLI. The app only needs to save enough data so later comparison is possible.

## Engine and Model Switching Requirements

The macOS app should make engine/model switching possible without requiring it on day one.

Requirements:

- Each transcription candidate should record engine and model provenance.
- A preset may eventually specify engine/model.
- A global default engine/model should exist.
- A capture can be reprocessed by another engine/model later.
- Engine-specific metrics should be preserved rather than flattened away.

Candidate engines:

- Existing SpeechDown CLI engine path, for fastest integration.
- WhisperKit, attractive for a native macOS Swift app.
- whisper.cpp, attractive for local/offline consistency and CLI use.
- Parakeet, worth testing for speed/quality and non-Whisper comparison.
- Cloud providers only as optional future configuration, not a first-version dependency.

Product stance:

- First version should choose one working path and store provenance correctly.
- Switching should be designed into presets and history.
- The app should not become an engine configuration dashboard before the capture loop is working.

## Custom Vocabulary and Substitutions

Custom vocabulary is important for names, projects, tools, acronyms, and repeated phrases.

Vocabulary levels:

- Global vocabulary: applies everywhere. This should be the first supported level.
- Per-language vocabulary: useful for Ukrainian versus English names, spelling, and transliteration behavior.
- Per-shortcut vocabulary: powerful for journal, coding, command, or project-specific modes, but likely too much for the minimal first version.

Substitution principles:

- Keep raw transcript and transformed transcript distinguishable.
- Record which rules were applied.
- Let the user inspect substitutions per capture.
- Let later retranscription run with updated vocabulary without losing the old candidate.
- Avoid invisible mutation that makes comparison impossible.

Examples:

- Project and tool names.
- Ukrainian/English name spelling.
- Acronyms.
- Repeated phrases.
- Dictated punctuation or command phrases.

Possible future behavior:

- A correction made after reviewing a transcript can become a suggested vocabulary or substitution rule.
- Candidate comparison can show whether a better result came from the model or from post-processing.
- Per-language vocabulary can prevent English cleanup rules from damaging Ukrainian text, and vice versa.

## Optional Journaling and Daily Markdown Workflow

SpeechDown macOS should stay connected to the original SpeechDown idea of voice notes projected into daily Markdown, but this should be optional and configuration-driven.

Two capture types should be distinguished:

- Real dictation: insert into the focused app, while still saving audio/history.
- Interstitial journaling: capture into a configured folder/mode, with optional later Markdown projection.

Journaling requirements for later:

- A shortcut can route to a journal destination instead of active-app insertion.
- Captures can be grouped by day.
- Markdown export/projection can be generated from storage.
- Human edits to Markdown should be preserved.
- Journal captures should still be retranscribable and comparable.

This should not turn the app into a note-taking product. The app captures and routes voice input; SpeechDown storage and optional export commands handle durable organization.

## Shortcut Routing to Different Folders or Modes

Shortcut routing is the general mechanism that can support language-specific dictation, journaling, and future workflows.

Each preset may eventually define:

- Shortcut.
- Language.
- Mode: `insert`, `clipboard`, `capture-only`, `journal`.
- Destination folder or storage tag.
- Engine/model profile.
- Vocabulary profile.
- Cleanup profile.
- Insertion behavior.

Examples:

- Ukrainian dictation into active app.
- English dictation into active app.
- Quick journal capture into a non-default folder.
- Coding dictation with developer vocabulary and conservative cleanup.
- Command macro mode, if voice macros become useful later.

Minimal version should support the preset concept even if only `shortcut`, `language`, and `mode` are implemented.

## How This Relates to SpeechDown CLI 2.0

The CLI 2.0 document defines the broader transcription workbench: global storage, queueing, latest/status/print commands, file and folder workflows, engine/model switching, retranscription, candidate comparison, substitutions, watched folders, and optional Markdown export.

The macOS app should depend on that direction but not duplicate its whole scope.

Division of responsibility:

- macOS app: capture ergonomics, shortcuts, language intent, recording feedback, insertion, and routing.
- CLI: inspection, batch transcription, status by id, retranscription, comparison, export, and agent-friendly access.
- Shared storage: audio files, transcription records, candidates, metadata, corrections, and events.

The app should be allowed to start as a thin capture layer over the CLI or watched folders. Over time, it should converge on the same global storage model so any dictation can be inspected and improved with CLI commands.

## Non-Goals

- Full SpeechDown CLI replacement.
- Full note-taking app.
- Meeting transcription.
- Speaker diarization.
- Cloud transcription as a required dependency.
- Complex provider marketplace.
- Polished commercial onboarding.
- Perfect insertion into every app in the first version.
- Automatic language detection as the primary workflow.
- Full custom vocabulary UI in the first version.
- Full Markdown publishing in the first version.
- Forking Handy immediately.

## Open Questions

1. Should the first app be native Swift/SwiftUI, a small wrapper around the CLI, or a hybrid prototype?
2. Should the first transcription path use the existing Python CLI, whisper.cpp, WhisperKit, or another local engine?
3. Should recording be toggle-first, push-to-talk-first, or should both be available from the beginning?
4. What should the default shortcuts be for Ukrainian and English?
5. What visual indicator is least likely to steal focus or break insertion?
6. Should direct insertion be attempted in the first slice, or should clipboard-only come first?
7. Where should global app captures live on disk?
8. What is the smallest shared storage contract the app and CLI can both honor?
9. Should `journal` mode be implemented as a preset immediately or left as a documented future workflow?
10. Should vocabulary be applied during transcription, after transcription, or both depending on engine support?
11. How should manual corrections feed back into vocabulary without making bad automatic rules?
12. How much history UI does the app need if the CLI can inspect records?
13. Should the app expose a local control interface, similar to Handy's CLI control flags, for automation?

## Suggested Next Implementation Slice

A practical first slice:

1. Define the shared capture record shape needed by both app and CLI.
2. Choose a global capture directory and database/storage path.
3. Implement two hardcoded or config-file presets: Ukrainian insert and English insert.
4. Build a minimal menu bar app or launcher that can start/stop recording from global shortcuts.
5. Save each recording as an audio file with sidecar metadata or a database record.
6. Transcribe through one working local engine path.
7. Copy transcript to clipboard and attempt direct insertion only if straightforward.
8. Record the transcript as the first candidate with engine/model/language provenance.
9. Add a minimal CLI inspection path, such as `sd latest --source macos` or equivalent.
10. Add a manual retranscription command for a captured dictation id.

This validates the core loop: shortcut-selected language, visible recording, saved audio, usable text, and durable records for later improvement.

