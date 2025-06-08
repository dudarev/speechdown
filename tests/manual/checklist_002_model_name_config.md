# Manual QA Checklist – Model Name Configuration

- Navigate to test data directory (e.g., `tests/data`).
  - Action: `cd tests/data`

- Ensure no local `.speechdown/config.json` exists in the test directory.
  - Action: `rm .speechdown/config.json` (if it exists)

- Ensure global model is set to a known default.
  - Action: `sd config --model-name tiny` (or your preferred default)

- Clean up any existing transcript files in `transcripts/`.
  - Action: `rm transcripts/*.md` (adjust path if needed)

- Transcribe using the model.
  - Action: `sd transcribe --ignore-existing`

- Verify transcription output.
  - Action: `cat transcripts/<YYYY-MM-DD>.md`

- Modify the model.
  - Action: `sd config --model-name turbo` (or other)

- Clean up any existing transcript files in `transcripts/`.
  - Action: `rm transcripts/*.md` (adjust path if needed)

- Transcribe using the model.
  - Action: `sd transcribe --ignore-existing`

- Verify transcription output.
  - Action: `cat transcripts/<YYYY-MM-DD>.md`
