# Manual QA Checklist – Daily Grouping of Voice Notes (SD-19)

## Test Data Preparation

- Navigate to test data directory.
  - Action: `cd tests/data`
  - Expected: Directory contains existing test files:
    - `test-1_20240315_143022.m4a` (YYYYMMDD_HHMMSS format)
    - `test-2 20240316 101530.m4a` (YYYYMMDD HHMMSS format)
    - `test-ru.m4a` (no timestamp pattern)
    - `test-ua.m4a` (no timestamp pattern)

- Backup existing transcripts for restoration.
  - Action: `cp -r transcripts transcripts_backup`
  - Expected: Backup created successfully

- Clean up existing transcript files to start fresh.
  - Action: `rm transcripts/*.md`
  - Expected: Transcript directory is empty

## Timestamp Extraction Verification

- Test basic timestamp extraction with existing files.
  - Action: `sd transcribe --ignore-existing`
  - Expected: Files `test-1_20240315_143022.m4a` and `test-2 20240316 101530.m4a` are processed successfully

- Verify timestamp extraction accuracy.
  - Action: Check transcript files:
    - `cat transcripts/2024-03-15.md`
    - `cat transcripts/2024-03-16.md`
  - Expected: Timestamps match filename patterns (14:30:22 and 10:15:30 respectively)

- Test fallback timestamp for unparseable filenames.
  - `ls transcripts`
  - Expected: Files `test-ru.m4a`, `test-ua.m4a` processed using file modification time as fallback

## Daily Grouping Verification

- Verify timestamp display in output format.
  - Action: Check that each voice note section shows format: `## YYYY-MM-DD HH:MM:SS - filename.ext`
  - Expected: Format matches design specifications for daily grouping
