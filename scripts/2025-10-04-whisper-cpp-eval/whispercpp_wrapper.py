#!/usr/bin/env python3
"""
Minimal Python wrapper for whisper.cpp CLI that produces a JSON structure
similar to OpenAI Whisper's transcribe() output. This does not touch core src/.

Usage:
  python scripts/2025-10-04-whisper-cpp-eval/whispercpp_wrapper.py \
    --whisper-bin /path/to/whisper.cpp/main \
    --model /path/to/models/ggml-base.en.bin \
    --audio /path/to/audio.wav \
    --language en \
    --threads 8
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional
import sys


def _build_cmd(
    whisper_bin: Path,
    model: Path,
    audio: Path,
    out_prefix: Path,
    language: Optional[str] = None,
    threads: Optional[int] = None,
    extra_args: Optional[List[str]] = None,
) -> List[str]:
    cmd = [str(whisper_bin), "-m", str(model), "-f", str(audio), "-oj", "-of", str(out_prefix)]
    if language:
        # whisper.cpp typically uses -l <lang>
        cmd.extend(["-l", language])
    if threads:
        # whisper.cpp typically uses -t <threads>
        cmd.extend(["-t", str(threads)])
    if extra_args:
        cmd.extend(extra_args)
    return cmd


def _load_json_output(prefix: Path) -> Dict[str, Any]:
    # whisper.cpp "-oj -of <prefix>" conventionally writes "<prefix>.json"
    json_path = Path(f"{prefix}.json")
    if not json_path.exists():
        raise FileNotFoundError(f"Expected JSON output not found: {json_path}")
    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_result(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize whisper.cpp JSON to match OpenAI Whisper's structure.

    Expected keys from whisper.cpp JSON generally include: "text", "language", "segments".
    We pass through known segment fields, tolerating missing optional metrics.
    """
    text = raw.get("text")
    language = raw.get("language")
    segments_in: List[Dict[str, Any]] = raw.get("segments", []) or []

    # Pass through known fields if present; ignore extras to remain forward-compatible.
    normalized_segments: List[Dict[str, Any]] = []
    for seg in segments_in:
        normalized_segments.append(
            {
                k: seg[k]
                for k in (
                    "id",
                    "seek",
                    "start",
                    "end",
                    "text",
                    "tokens",
                    "temperature",
                    "avg_logprob",
                    "compression_ratio",
                    "no_speech_prob",
                )
                if k in seg
            }
        )

    # If top-level text is missing, compose from segments as a fallback.
    if text is None and normalized_segments:
        text = " ".join(s.get("text", "").strip() for s in normalized_segments if s.get("text"))

    return {
        "text": text or "",
        "language": language or None,
        "segments": normalized_segments,
    }


def transcribe_with_whispercpp(
    whisper_bin: str | os.PathLike[str],
    model: str | os.PathLike[str],
    audio: str | os.PathLike[str],
    *,
    language: Optional[str] = None,
    threads: Optional[int] = None,
    extra_args: Optional[List[str]] = None,
    ffmpeg_convert: bool = False,
    keep_temp: bool = False,
    verbose: bool = False,
) -> Dict[str, Any]:
    whisper_bin_p = Path(whisper_bin)
    model_p = Path(model)
    audio_p = Path(audio)

    if not whisper_bin_p.exists():
        raise FileNotFoundError(f"whisper.cpp binary not found: {whisper_bin_p}")
    if not model_p.exists():
        raise FileNotFoundError(f"Model file not found: {model_p}")
    if not audio_p.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_p}")

    def _run(tmpdir: Path) -> Dict[str, Any]:
        prefix = tmpdir / "out"

        # Optionally pre-convert non-WAV inputs to WAV (16kHz mono) via ffmpeg.
        # This helps when whisper.cpp is built without FFmpeg decoding support.
        audio_for_inference = audio_p
        if ffmpeg_convert and audio_p.suffix.lower() != ".wav":
            ffmpeg = shutil.which("ffmpeg")
            if not ffmpeg:
                raise RuntimeError("ffmpeg not found on PATH; required when --ffmpeg-convert is set")
            converted = tmpdir / "converted.wav"
            cmd_ff = [
                ffmpeg,
                "-y",
                "-i",
                str(audio_p),
                "-ar",
                "16000",
                "-ac",
                "1",
                "-f",
                "wav",
                str(converted),
            ]
            proc_ff = subprocess.run(cmd_ff, capture_output=True, text=True)
            if proc_ff.returncode != 0:
                raise RuntimeError(
                    f"ffmpeg conversion failed (code {proc_ff.returncode})\nSTDOUT:\n{proc_ff.stdout}\nSTDERR:\n{proc_ff.stderr}"
                )
            audio_for_inference = converted
        cmd = _build_cmd(
            whisper_bin=whisper_bin_p,
            model=model_p,
            audio=audio_for_inference,
            out_prefix=prefix,
            language=language,
            threads=threads,
            extra_args=extra_args,
        )
        if verbose:
            print(f"[whispercpp_wrapper] tmpdir: {tmpdir}", file=sys.stderr)
            print(f"[whispercpp_wrapper] cmd: {' '.join(cmd)}", file=sys.stderr)
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            hint = None
            # If non-WAV input without pre-conversion, decoding can fail on some builds/files.
            if audio_p.suffix.lower() != ".wav" and not ffmpeg_convert:
                hint = (
                    "Hint: non-WAV input may fail to decode with some whisper.cpp builds. "
                    "Try adding --ffmpeg-convert to pre-convert to 16kHz mono WAV, or rebuild whisper.cpp with FFmpeg decoding enabled."
                )
            # Surface a targeted hint for common FFmpeg demux errors
            if not hint and "partial file" in (proc.stderr or "").lower():
                hint = (
                    "Hint: FFmpeg reported 'partial file'. The container may be malformed. "
                    "Pre-convert with: ffmpeg -y -i <in.m4a> -ar 16000 -ac 1 <out.wav> and use the WAV file."
                )
            detail = f"whisper.cpp failed (code {proc.returncode})\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
            if hint:
                detail = f"{detail}\n{hint}"
            raise RuntimeError(detail)
        if verbose:
            print(f"[whispercpp_wrapper] expecting JSON: {prefix}.json", file=sys.stderr)
            if proc.stdout:
                print(f"[whispercpp_wrapper] stdout:\n{proc.stdout}", file=sys.stderr)
            if proc.stderr:
                print(f"[whispercpp_wrapper] stderr:\n{proc.stderr}", file=sys.stderr)
        raw = _load_json_output(prefix)
        return _normalize_result(raw)

    if keep_temp:
        td = tempfile.mkdtemp(prefix="whispercpp-")
        return _run(Path(td))
    else:
        with tempfile.TemporaryDirectory() as td:
            return _run(Path(td))


def main() -> None:
    parser = argparse.ArgumentParser(description="whisper.cpp wrapper that prints normalized JSON")
    parser.add_argument("--whisper-bin", required=True, help="Path to whisper.cpp 'main' binary")
    parser.add_argument("--model", required=True, help="Path to ggml model .bin file")
    parser.add_argument("--audio", required=True, help="Path to audio file")
    parser.add_argument("--language", default=None, help="Language code (e.g., en)")
    parser.add_argument("--threads", type=int, default=None, help="Thread count for whisper.cpp")
    parser.add_argument(
        "--ffmpeg-convert",
        action="store_true",
        help="Use ffmpeg to pre-convert non-WAV inputs to 16kHz mono WAV",
    )
    parser.add_argument(
        "--extra-arg",
        action="append",
        default=None,
        help="Additional arg passed through to whisper.cpp (repeatable)",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary directory with intermediate files (for debugging)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print debugging info and whisper.cpp output to stderr",
    )
    args = parser.parse_args()

    result = transcribe_with_whispercpp(
        whisper_bin=args.whisper_bin,
        model=args.model,
        audio=args.audio,
        language=args.language,
        threads=args.threads,
        extra_args=args.extra_arg,
        ffmpeg_convert=args.ffmpeg_convert,
        keep_temp=args.keep_temp,
        verbose=args.verbose,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
