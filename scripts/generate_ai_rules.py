#!/usr/bin/env python3
"""Generate AI assistant rule files from a master Markdown file."""

from __future__ import annotations

import pathlib
import sys


def main() -> int:
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs/ai/AI-rules.md")
    if not src.is_file():
        sys.stderr.write(f"Source file {src} not found\n")
        return 1
    content = src.read_text()
    dests = [
        pathlib.Path(".github/copilot-instructions.md"),
        pathlib.Path("AGENTS.md"),
        pathlib.Path("CLAUDE.md"),
        pathlib.Path(".cursorrules"),
    ]
    for dest in dests:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)
        print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
