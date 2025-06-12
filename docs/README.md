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


To initialize a SpeechDown project, run:

```bash
sd init
```

This will create a `.speechdown` directory in the current working directory, which will contain the database and configuration files. The configuration file (`config.json`) will include a default `output_dir` setting (`transcripts/`) where transcription files will be saved.

**Note:** It is possible to specify a different directory for most commands using the `-d` or `--directory` option, if you want to operate in a directory other than the current working directory. See the Options section below for details.

### Configuration


You can configure the output directory for transcripts using the `sd config` command:

```bash
sd config --output-dir path/to/your/transcripts
```

If `output_dir` is not set, or if the path is invalid, SpeechDown will output transcriptions to the standard output. By default, transcripts are saved to a `transcripts/` subdirectory within the initialized SpeechDown project directory unless otherwise specified.

#### Language Configuration

SpeechDown supports multiple languages for transcription. You can configure which languages to use with the following commands:


1. View current language configuration:
```bash
sd config
```

2. Set specific languages (replaces existing languages):
```bash
sd config --languages en,fr,de
```

3. Add a single language to the configuration:
```bash
sd config --add-language ja
```

4. Remove a language from the configuration:
```bash
sd config --remove-language fr
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


To transcribe all audio files in the current directory, run:

```bash
sd transcribe
```

This will transcribe all supported audio files found in the current directory and its subdirectories. Transcripts will be saved to files in the configured `output-dir`.


### Options

- `--debug`: Enable debug mode for more verbose output.
- `--dry-run`: Simulate the transcription process without making any changes to the database or file system.
- `--within-hours`: Only transcribe files modified within the last N hours.

#### Directory Option

For most commands, you can specify a directory to operate in using the `-d` or `--directory` option, for example:

```bash
sd transcribe -d path/to/your/project
```

If you do not specify this option, SpeechDown will use the current working directory by default.

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
