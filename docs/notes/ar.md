File inspired by [The append-and-review note idea by Andrej Karpathy](https://karpathy.bearblog.dev/the-append-and-review-note/)

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

## 2025-03-27 09:02:22

- **Current goal: Publish and make usable**
- **Primary functionality needed:**
  - Transcribe daily notes in three different languages
  - Integrate with personal workflow (`cron`)
  - Support daily voice notes

## 2025-03-29 09:55:46

- **Configuration for output mapping:**
  - Configure output directory via config file or command
  - Map speech notes to daily text files with timestamped H2 headers
  - Specify output path, filename prefixes/suffixes,templates
