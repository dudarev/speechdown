# WhisperCPP Migration Plan (Speed-Focused Iteration)

## Context
SpeechDown's current transcription pipeline is perceived as slow, and the UI does not surface notes until after full transcription completes. The next iteration should focus on improving end-to-end latency (especially time-to-first-text) and validating whether partial notes can appear while audio is still being processed. This plan prioritizes migrating from the current Whisper integration to **WhisperCPP** as the main speed optimization, with Parakeet kept as a fallback option for evaluation.

## Goals
- Reduce transcription latency, especially **time-to-first-token** and overall transcription time.
- Enable **incremental note rendering** so notes appear as soon as segments are available.
- Preserve existing domain/application boundaries and configuration patterns.
- Provide clear measurement and rollback criteria.

## Non-Goals
- Major UI redesign (only incremental rendering changes).
- Broad refactors unrelated to transcription performance.
- Adding new transcription features beyond speed and streaming output.

## Assumptions & Constraints
- The new transcription adapter must fit the existing port/interface structure.
- Python 3.11+ and current tooling remain unchanged.
- If WhisperCPP integration proves unstable or incomplete, Parakeet evaluation will be used as a fallback path.

## Current State Validation (First Step)
Before implementing changes, verify whether the current UI already supports incremental notes (user uncertainty noted). If incremental rendering already exists but is gated, identify and document what blocks it.

## Plan Overview

### Phase 1: Discovery & Baseline
1. **Benchmark current Whisper pipeline**
   - Capture baseline latency metrics:
     - Time-to-first-segment
     - Total transcription duration
     - CPU/GPU utilization (if accessible)
   - Record against representative audio files.
2. **Verify incremental note rendering**
   - Inspect presentation layer and note pipeline to confirm whether partial segments can be emitted.
   - If not, identify where output is buffered and why.

### Phase 2: WhisperCPP Integration (Primary Path)
1. **Library evaluation and interface mapping**
   - Identify a Python integration path for WhisperCPP (native bindings or subprocess invocation).
   - Map configuration options (model selection, language, device, beam size) to existing config schema.
2. **Infrastructure adapter**
   - Add a new `WhisperCppTranscriberAdapter` implementing the existing transcription port.
   - Ensure the adapter supports streaming/segment callbacks if possible.
3. **Application service updates**
   - Update transcription services to optionally emit partial results.
   - Keep current adapter as fallback behind configuration.
4. **Presentation updates**
   - Implement incremental rendering of notes as segments arrive.
   - Ensure ordering, deduplication, and finalization of partial segments.

### Phase 3: Validation & Rollout
1. **Performance validation**
   - Repeat baseline benchmarks with WhisperCPP.
   - Compare time-to-first-segment and overall throughput.
2. **User-visible behavior checks**
   - Confirm notes appear progressively in CLI/UI.
   - Validate output parity with the current adapter.
3. **Fallback path**
   - Maintain ability to switch back to the existing adapter via config.

### Phase 4: Parakeet Evaluation (Fallback Path)
If WhisperCPP does not meet performance or stability goals:
- Evaluate Parakeet using the same benchmarks.
- Decide whether to prioritize Parakeet integration in the next iteration.

## Implementation Notes
- Follow the layered architecture:
  - **Infrastructure**: WhisperCPP adapter implementation.
  - **Application**: service orchestration and streaming output handling.
  - **Presentation**: incremental rendering logic.
- Keep the domain layer unchanged.

## Risks & Mitigations
- **WhisperCPP integration complexity**: start with a minimal working adapter and expand config support incrementally.
- **Streaming output mismatch**: design a buffering strategy to keep output stable while allowing partial updates.
- **Performance regression**: keep configuration-based fallback to current adapter.

## Deliverables
- New design/plan document (this file).
- WhisperCPP adapter implementation with configuration switch.
- Updated application and presentation layers to support incremental note rendering.
- Benchmark report (before/after) captured in documentation or release notes.

## Success Criteria
- Time-to-first-segment reduced by a measurable margin (target to be set during baseline phase).
- Notes appear progressively during transcription.
- Comparable or better transcription accuracy vs current adapter.

