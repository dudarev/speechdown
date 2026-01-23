# Whisper.cpp Research Scripts (2025-10-04)

This folder contains minimal, throw-away research utilities to evaluate whisper.cpp performance and output compatibility without changing core code.

- `whispercpp_wrapper.py` — shells out to whisper.cpp `main`, requests JSON output, and prints a standardized JSON similar to OpenAI Whisper’s `transcribe()` result.
- `compare_with_openai.py` — optionally compares whisper.cpp output to OpenAI Whisper (if installed) and prints a simple similarity score.

## Prerequisites
- Built whisper.cpp `main` binary (path provided via `--whisper-bin`)
- A whisper.cpp model (e.g., `ggml-base.en.bin`) (path via `--model`)
- Python 3.11+
- Optional: `openai-whisper` installed for comparison in `compare_with_openai.py`

## Usage

Run whisper.cpp transcription and print standardized JSON to stdout (supports WAV, M4A, MP3, etc., as supported by your whisper.cpp build):

```
python scripts/2025-10-04-whisper-cpp-eval/whispercpp_wrapper.py \
  --whisper-bin /path/to/whisper.cpp/main \
  --model /path/to/models/ggml-base.en.bin \
  --audio /path/to/audio.wav \
  --language en \
  --threads 8
```

If your whisper.cpp build lacks FFmpeg decoding support, you can force a pre-conversion step for non-WAV inputs:

```
python scripts/2025-10-04-whisper-cpp-eval/whispercpp_wrapper.py \
  --whisper-bin /path/to/whisper.cpp/main \
  --model /path/to/models/ggml-base.en.bin \
  --audio tests/data/subfolder/test-1_20240315_143022.m4a \
  --language en \
  --threads 8 \
  --ffmpeg-convert
```

Compare with OpenAI Whisper (if installed):

```
python scripts/2025-10-04-whisper-cpp-eval/compare_with_openai.py \
  --whisper-bin /path/to/whisper.cpp/main \
  --model /path/to/models/ggml-base.en.bin \
  --audio /path/to/audio.wav \
  --openai-model base \
  --language en
```

Notes:
- The wrapper reads the JSON produced by whisper.cpp (`-oj -of <prefix>`) and prints a normalized shape. It does not modify SpeechDown’s codebase.
- Non-WAV audio (e.g., `.m4a`) works if your whisper.cpp binary has FFmpeg decoding enabled. Otherwise, use `--ffmpeg-convert` or pre-convert via `ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav`.
- If OpenAI Whisper is not installed, the comparison script will skip the API run and warn.

### Troubleshooting
- Error code -6 with FFmpeg messages like `partial file` typically means the container is malformed or the build’s FFmpeg cannot parse the file. Workarounds:
  - Re-run with `--ffmpeg-convert` to transcode to 16kHz mono WAV.
  - Or manually convert: `ffmpeg -y -i input.m4a -ar 16000 -ac 1 output.wav` and pass the WAV.
  - If you want to feed non-WAV directly, ensure whisper.cpp is built with FFmpeg support: `cmake -B build -DWHISPER_FFMPEG=ON && cmake --build build -j`.

- Empty JSON (`{"text": "", "language": null, "segments": []}`):
  - The input may decode to near-empty/silent audio. These test fixtures are very small and may not contain decodable speech.
  - Debug with: `--verbose --keep-temp` to see the invoked command and inspect `<tmp>/out.json`.
  - Validate audio duration: `ffprobe -v error -show_entries format=duration -of csv=p=0 <file>`.
  - Try a known-good sample (a few seconds of clear speech) or convert explicitly to WAV and run the binary directly.

## Data
A local `data/` directory may be used for outputs. It is gitignored in this folder.
