#!/usr/bin/env python3
"""
Optional comparison script to run whisper.cpp and OpenAI Whisper side-by-side and
report a rough similarity metric. Skips OpenAI Whisper if not installed.

This is a research-only utility; no changes are made to src/ code.
"""

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
from typing import Any, Dict, Optional

from whispercpp_wrapper import transcribe_with_whispercpp


def try_openai_whisper(audio: Path, model_name: str, language: Optional[str]) -> Optional[Dict[str, Any]]:
    try:
        import whisper  # type: ignore
    except ModuleNotFoundError:
        return None

    model = whisper.load_model(model_name)
    kwargs: Dict[str, Any] = {"fp16": False}
    if language:
        kwargs["language"] = language
    return model.transcribe(str(audio), **kwargs)


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(a=a, b=b).ratio()


def main() -> None:
    p = argparse.ArgumentParser(description="Compare whisper.cpp vs OpenAI Whisper (if available)")
    p.add_argument("--whisper-bin", required=True)
    p.add_argument("--model", required=True, help="Path to whisper.cpp ggml model .bin")
    p.add_argument("--audio", required=True)
    p.add_argument("--openai-model", default="base", help="OpenAI Whisper model name (e.g., tiny, base)")
    p.add_argument("--language", default=None)
    p.add_argument("--threads", type=int, default=None)
    args = p.parse_args()

    audio = Path(args.audio)
    wcpp = transcribe_with_whispercpp(
        whisper_bin=args.whisper_bin,
        model=args.model,
        audio=audio,
        language=args.language,
        threads=args.threads,
    )

    oai = try_openai_whisper(audio=audio, model_name=args.openai_model, language=args.language)

    print("whisper.cpp result:")
    print(json.dumps({k: (v if k != "segments" else f"{len(v)} segments") for k, v in wcpp.items()}, ensure_ascii=False))

    if oai is None:
        print("OpenAI Whisper not installed; skipping comparison.")
        return

    print("OpenAI Whisper result:")
    print(json.dumps({k: (v if k != "segments" else f"{len(v)} segments") for k, v in oai.items()}, ensure_ascii=False))

    s = similarity(wcpp.get("text", ""), oai.get("text", ""))
    print(f"Text similarity ratio: {s:.4f}")


if __name__ == "__main__":
    main()

