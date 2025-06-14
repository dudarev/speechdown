#!/usr/bin/env python3
"""Generate AI assistant rule files from a master Markdown file."""

from __future__ import annotations

import pathlib
import re
import sys


def filter_content_for_target(content: str, target: str) -> str:
    """Filter content based on target AI assistant type."""
    lines = content.split('\n')
    filtered_lines = []
    skip_section = False
    skip_maintainer_note = False
    
    for line in lines:
        # Check for maintainer note markers
        if '<!-- MAINTAINER NOTE START -->' in line:
            skip_maintainer_note = True
            continue
        elif '<!-- MAINTAINER NOTE END -->' in line:
            skip_maintainer_note = False
            continue
        
        # Skip lines within maintainer note
        if skip_maintainer_note:
            continue
            
        # Check if this is a section header with target-specific marker
        if line.startswith('###') and '(Remote AI Agents Only)' in line:
            if target in ['copilot', 'cursor']:  # Local AI assistants only
                skip_section = True
                continue
            else:  # Remote/hybrid agents (AGENTS.md, CLAUDE.md) - include the section
                # Remove the marker for output files
                line = line.replace(' (Remote AI Agents Only)', '')
                skip_section = False
        elif line.startswith('###') or line.startswith('##'):
            # New section - reset skip flag
            skip_section = False
        
        if not skip_section:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def main() -> int:
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs/ai/AI-rules.md")
    if not src.is_file():
        sys.stderr.write(f"Source file {src} not found\n")
        return 1
    
    content = src.read_text()
    
    # Define target configurations: (path, target_type)
    targets = [
        (pathlib.Path(".github/copilot-instructions.md"), "copilot"),
        (pathlib.Path("AGENTS.md"), "remote"),
        (pathlib.Path("CLAUDE.md"), "claude"),  # Claude can be both remote and local
        (pathlib.Path(".cursorrules"), "cursor"),
    ]
    
    for dest_path, target_type in targets:
        filtered_content = filter_content_for_target(content, target_type)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(filtered_content)
        print(f"Wrote {dest_path} (filtered for {target_type})")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
