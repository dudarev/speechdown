# Extracting Timestamps from Audio File Metadata
*Status*: Active
*Date*: 2025-05-31

## Problem
Audio files often contain embedded metadata, such as EXIF tags or ID3 tags, which may include creation or modification timestamps. Accessing this metadata can provide a reliable source for an audio file's timestamp, independent of the filename. This research will investigate methods and libraries for extracting timestamps from various audio file metadata formats.

## Approach
1. **Identify Common Audio Formats:** List the common audio file formats that need to be supported (e.g., WAV, MP3, M4A, FLAC).
2. **Research Metadata Libraries:** Identify Python libraries capable of reading metadata from these audio formats (e.g., `mutagen`, `hachoir`, `tinytag`).
3. **Develop Extraction Script:** Create a script to attempt timestamp extraction from a sample set of audio files using the selected libraries.
4. **Identify Relevant Metadata Fields:** Determine which metadata fields commonly store timestamp information (e.g., 'creation_date', 'date', 'encoded_date').
5. **Handle Timezone and Format Variations:** Investigate how timestamps are stored (e.g., UTC, local time, different string formats) and how to normalize them.
6. **Evaluate Reliability:** Assess the reliability and consistency of timestamps obtained from metadata across different formats and recording devices.

## Findings
(To be filled as research progresses)

## Next steps
- Begin by researching and selecting suitable Python libraries for audio metadata extraction.
- Create an initial script to test metadata reading capabilities on sample audio files.
