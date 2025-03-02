# SpeechDown

SpeechDown is a command line tool designed to help you easily transcribe audio files and manage those transcriptions.


## Features

* Transcribe audio files in various formats (mp3, wav, ogg, etc.).
* Automatically detect the language of the audio.
* Save transcriptions to a database for later retrieval.
* Output transcriptions to a file or the console.
* Accept commands from the Markdown files it generated such as:
    * re-transcribe
    * learn correction


## Installation

Currently SpeechDown is not available as a package yet.


## Usage

### Initialization

To initialize a SpeechDown project in a directory, run:

```bash
speechdown init -d <directory>
```

This will create a `.speechdown` directory within the specified directory, which will contain the database and configuration files.

### Transcription

To transcribe all audio files in a directory, run:

```bash
speechdown transcribe -d <directory>
```

This will transcribe all supported audio files found in the specified directory and its subdirectories.

### Options

* `-d, --directory`: The directory to operate in.
* `--debug`: Enable debug mode for more verbose output.
* `--dry-run`: Simulate the transcription process without making any changes to the database.