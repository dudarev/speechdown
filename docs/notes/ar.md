File inspired by [The append-and-review note idea by Andrej Karpathy](https://karpathy.bearblog.dev/the-append-and-review-note/)

- Text before h2 level headers should not be affected.
- Other h2 level headers should not be affected.

- Do not write to output file if nothing changed

- Consider removing integration tests from `make ci` again since they need ffmpeg and it takes time to install. Potentially `make ci` can only check unit tests. They were not part of CI at some point.
  - Sync ADR 005 with integration/README.md
  - Especially since those tests that use whisper are marked as `integration` and `slow`. This marks are disabled in `conftest.py`.

- potentially try https://www.coderabbit.ai/

- modify `configure_logging` function to have only message for info, without file and level etc.

- rename 2025-06-03-copilot-jules-claude-rules.md to ...-ai-assistant-rules.md

- What --debug option is for? Is it really needed?

- `transcribe` command should be optional, if it's not specified it should be assumed

- At some point create a config option to sort by chronological or reverse chronological order
  - Later this should be configured on file level via front matter

- It's okay for some development tasks to be in marketing cycles, and vice versa.

- GOAL: NEXT: Make usable by others

- GOAL: NEXT: Write a blog post about it

- TASK: Generate more output when the script is running for informational purposes. This can be controlled by the verbose flag. 

Organize planning documents (such as ADRs, design, and research) into folders that reflect their status: 
- `planning` for documents that are in the early planning or idea stage,
- `current` for active and up-to-date docs,
- `archive` for deprecated or superseded materials.
This structure helps track the lifecycle and relevance of each document.

- I can create a dedicated ADR describing the planning document structure and also update existing ADRs for each document type to reference this structure.

- When creating a design doc and mentioning tests there a reference to existing ADRs should should be made. I need to think where to put this thought either to the ADR about design docs or into the rules for the copilot. 

- When instructing a copilot to create design doc it needs to be mentioned that it should should stop after the design doc created for me to review, edit it and give feedback. With language settings it was able to create the design doc and implement it. it was okay but in general this doesn't look like the right approach.

## 2025-03-17 11:27

- **Speech Down Project Enhancements:**
  - **Efficient Language Detection:**
    - Transcribe only the first 10 seconds for initial language detection.
    - Iterate through languages, comparing partial transcriptions.
    - Initiate full transcription only after identifying the best language match.
  - **File Updates**
    - Update file after each transcription action.
    - If partial transcription finished, add to a dedicated section.
    - If better partial transcription found, update the section.
    - Full transcription will also update section.

## 2025-03-29 09:55:46

- **Configuration for output mapping:**
  - Configure output directory via config file or command
  - Map speech notes to daily text files with timestamped H2 headers
  - Specify output path, filename prefixes/suffixes,templates
