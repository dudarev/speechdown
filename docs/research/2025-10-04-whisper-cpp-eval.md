# Whisper.cpp Evaluation
Status: Active
Date: 2025-10-04

## Problem
We want to research whether integrating whisper.cpp can significantly accelerate SpeechDown’s transcription while preserving output quality and compatibility with our current Whisper-based shape. This is a lightweight spike with runnable scripts and no changes to core src/ code.

## Approach
- Create a minimal Python wrapper that shells out to whisper.cpp’s CLI, requests JSON output, and maps it into a structure similar to OpenAI Whisper’s `transcribe()` result.
- Provide a companion comparison script that can optionally run OpenAI Whisper (if installed) and compute a rough similarity score.
- Keep artifacts under `scripts/YYYY-MM-DD-…` per ADR 011; record findings here.

## Scripts
- `scripts/2025-10-04-whisper-cpp-eval/whispercpp_wrapper.py` — runs whisper.cpp `main` binary, collects JSON, prints standardized JSON to stdout.
- `scripts/2025-10-04-whisper-cpp-eval/compare_with_openai.py` — optional comparison with OpenAI Whisper, reporting simple similarity metrics.
- `scripts/2025-10-04-whisper-cpp-eval/README.md` — setup and usage notes.

## Assumptions
- You have built whisper.cpp and have a `main` executable and a `.bin` model file (e.g., `ggml-base.en.bin`).
- Local environment can run the binaries; no network calls are required.

## Findings
- TBD after running on representative audio samples. Capture timing, CPU usage, and text similarity vs. OpenAI Whisper. Note any format differences in JSON output.

## Next Steps
- If results are promising, design an infrastructure `Adapter` implementing our `TranscriptionModelPort` backed by whisper.cpp, with unit tests mirroring the existing Whisper adapter tests.
- Add a CLI switch to select whisper.cpp as a model backend for real workflows.
