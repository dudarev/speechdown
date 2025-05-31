# Scripts for Audio Filename Timestamp Research

This directory contains scripts related to the research document:
[Extracting Timestamps from Audio File Names](../../docs/research/2025-05-31-audio-filename-timestamps.md)

## Setup

The scripts in this directory use environment variables for configuration.

1. Copy the example environment file:
   ```bash
   cp .example.env .env
   ```

2. Edit `.env` and set your recordings directory path:
   ```
   RECORDINGS_DIRECTORY=/path/to/your/recordings
   ```

## Scripts

### list_audio_files.py

Lists all files in a specified recordings directory, with options to filter for audio files only.

**Usage from VS Code**: Simply run the script using VS Code's Python runner. It will use the directory specified in your `.env` file.

**Usage from Terminal**:
```bash
# Use default directory from .env
python list_audio_files.py

# Override with specific directory
python list_audio_files.py --directory /path/to/other/directory

# Show only audio/video files
python list_audio_files.py --audio-only

# Save output to file
python list_audio_files.py --output filelist.txt

# Hide file extensions
python list_audio_files.py --no-extensions
```

**Options**:
- `--directory, -d`: Override the default directory
- `--output, -o`: Save the file list to a text file
- `--no-extensions`: Hide file extensions in output
- `--audio-only`: Show only audio/video files

### parse_filenames_first_iteration.py

Extracts timestamps from audio filenames using multiple pattern recognition approaches. This script demonstrates a comprehensive solution that handles overlapping timestamp patterns by scanning all positions in the filename.

**Usage**:
```bash
python parse_filenames_first_iteration.py
```

**Supported Patterns**:
- `YYYYMMDD HHMMSS` (e.g., "20250408 204728")
- `YYYYMMDD_HHMMSS` (e.g., "20240908_102336") 
- `YYMMDD_HHMMSS` (e.g., "250512_105730")

### parse_filenames_backwards.py

A simplified and more elegant approach to timestamp extraction that searches for patterns from the end of the filename backwards. This approach is more efficient and naturally finds the most relevant timestamps (typically located near the file extension).

**Usage**:
```bash
python parse_filenames_backwards.py
```

**Key Advantages**:
- **Simpler implementation**: Single backwards search loop
- **Better accuracy**: Avoids false positives from phone numbers, IDs, etc.
- **Natural logic**: Timestamps are typically at the end of filenames
- **Higher performance**: Stops at first valid match from the end

**Supported Patterns**: Same as `parse_filenames.py` but with more reliable detection.

### parse_filenames_all.py

Processes multiple filenames from text input, extracts timestamps using the backwards search approach, and validates that years are within 2023-2025 range. This script is designed for batch processing of filename lists.

**Usage**:
```bash
# Process filenames from a text file (one filename per line)
python parse_filenames_all.py < filenames.txt

# Interactive mode - enter filenames manually
python parse_filenames_all.py
# (then enter filenames line by line, press Ctrl+D when done)

# Process output from list_audio_files.py
python list_audio_files.py --no-extensions | python parse_filenames_all.py
```

**Features**:
- **Batch processing**: Handles multiple filenames from stdin
- **Year validation**: Only accepts timestamps from 2024-2025
- **Detailed output**: Shows successfully parsed files and unparseable ones
- **Sorted results**: Orders output chronologically by timestamp
- **Summary statistics**: Provides counts and year distribution

**Sample Output**:
```
SUCCESSFULLY PARSED (8 files):
Filename                                  | Pattern              | Timestamp
--------------------------------------------------------------------------
audio_20240101_000000.mp3                | YYYYMMDD_HHMMSS      | 2024-01-01 00:00:00
recording_20241225_143022.wav            | YYYYMMDD_HHMMSS      | 2024-12-25 14:30:22

UNPARSEABLE FILENAMES (2 files):
--------------------------------------------------------------------------------
  Voice 001.m4a
  no_timestamp_file.mp3

SUMMARY:
  Total files processed: 10
  Successfully parsed:  8
  Unparseable:          2
  Years found:          [2024, 2025]
```

## Research Findings

Through this research, we discovered that:

1. **Backwards search is superior**: Searching from the end of filenames backwards provides more accurate timestamp detection with simpler code.

2. **Pattern ambiguity is common**: Many filenames contain multiple numeric sequences that match timestamp patterns (phone numbers, IDs, etc.).

3. **Position matters**: Valid timestamps are typically located near the end of filenames, before the file extension.

4. **Validation is crucial**: Component range checking (month 1-12, hour 0-23, etc.) is essential to filter out false positives.

## Next Steps

- Integrate the backwards search approach into the main speechdown application
- Extend pattern support for additional timestamp formats
- Add fuzzy matching for malformed timestamps
- Consider machine learning approaches for complex cases
