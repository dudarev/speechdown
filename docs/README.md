# SpeechDown

SpeechDown is a command line tool that transcribes audio files and organizes the results into structured Markdown files.

## Features

- Transcribe audio files in various formats (mp3, wav, ogg, etc.).
- Automatically detect the language of the audio.
- Save transcriptions to a database for later retrieval.
- Output transcriptions to a file or the console.
  - Transcripts can be saved to date-based Markdown files (e.g., `YYYY-MM-DD.md`).
  - Each audio file's transcript is organized into timestamped H2-level sections within the output file.
- Accept commands from the Markdown files it generated such as:
  - re-transcribe
  - learn correction

## Installation

Currently SpeechDown is not available as a package yet. You can install it locally for development using:

```bash
make requirements
```

This will install the required dependencies including development tools.

## Usage

### Initialization

To initialize a SpeechDown project in a directory, run:

```bash
sd init -d <directory>
```

This will create a `.speechdown` directory within the specified directory, which will contain the database and configuration files. The configuration file (`config.json`) will include a default `output_dir` setting (`transcripts/`) where transcription files will be saved.

### Configuration

You can configure the output directory for transcripts using the `sd config` command:

```bash
sd config -d <directory> --output-dir path/to/your/transcripts
```

If `output_dir` is not set, or if the path is invalid, SpeechDown will output transcriptions to the standard output. By default, transcripts are saved to a `transcripts/` subdirectory within the initialized SpeechDown project directory unless otherwise specified.

#### Language Configuration

SpeechDown supports multiple languages for transcription. You can configure which languages to use with the following commands:

1. View current language configuration:
```bash
sd config -d <directory>
```

2. Set specific languages (replaces existing languages):
```bash
sd config -d <directory> --languages en,fr,de
```

3. Add a single language to the configuration:
```bash
sd config -d <directory> --add-language ja
```

4. Remove a language from the configuration:
```bash
sd config -d <directory> --remove-language fr
```

The default languages are English (en), Ukrainian (uk). SpeechDown supports all languages available in the Whisper model, including but not limited to:
- English (en)
- French (fr)
- German (de)
- Spanish (es)
- Chinese (zh)
- Japanese (ja)
- Ukrainian (uk)
- And many more

Using the correct language codes improves transcription accuracy and performance.

### Transcription

To transcribe all audio files in a directory, run:

```bash
sd transcribe -d <directory>
```

This will transcribe all supported audio files found in the specified directory and its subdirectories. Transcripts will be saved to files in the configured `output-dir`.

### Options

- `-d, --directory`: The directory to operate in.
- `--debug`: Enable debug mode for more verbose output.
- `--dry-run`: Simulate the transcription process without making any changes to the database or file system.

## Development

See `Makefile` for development commands.

### Task Tracking

For information on how tasks and features are tracked and prioritized, see [ADR-006](adrs/current/006_task_tracking_approach.md)

### Continuous Integration

When changes are pushed to GitHub, a CI pipeline runs the `make ci` command to validate the code.

For local development, it's recommended to run:

```bash
make ci-full
```

This command runs all tests, including additional integration tests that aren't included in the standard CI pipeline.
