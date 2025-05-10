# File Output Design Document

## Summary
This document outlines the design for implementing file output functionality in SpeechDown. The feature will enable storing transcripts in date-based Markdown files, with each transcription organized in timestamped sections. This enhances the existing functionality which currently only outputs results to standard output.

**Date:** 2025-05-08

## Product Requirements

### Objective
Enable the storage of transcripts into files instead of just outputting them to standard output.

### Use Cases
1. Users can save transcripts to files.
2. Each file will have a date-based name.
3. Each audio file's transcript will correspond to an H2-level section in the output file, with sections timestamped.

### Success Metrics
- Transcripts are correctly saved to files with the expected structure.
- File names follow the date-based naming convention.
- Each audio file's transcript is properly organized into timestamped sections.

## UX Design

### User Flows
1. User initializes SpeechDown project in a directory using the command `sd init`.
2. User configures the output directory for transcripts using `sd config output_dir=...` or similar commands.
    - By default, transcripts are saved to a `transcripts/` subdirectory within the initialized SpeechDown project directory unless otherwise specified.
3. User starts transcription by specifying a path:
   - If the path contains a SpeechDown configuration, it uses the configuration to output transcripts to the specified directory.
   - Example commands:
     - `sd .` (uses the current directory)
     - `sd /to/some/dir/` (uses the specified directory).

### Accessibility Considerations
- File names will use the format `YYYY-MM-DD.md` (e.g., `2025-05-08.md`). Configurable naming templates with prefixes or suffixes may be considered in future iterations.
- Provide clear error messages if the configuration is missing or invalid.
- Use the format `YYYY-MM-DD HH:MM:SS` for timestamps (e.g., `2025-05-08 14:30:00`). The timezone is omitted and assumed to be the machine's local timezone. Configuration of timestamps will be considered in future iterations.

## Implementation Decisions & References

### Technical Design

#### File Handling Strategy
##### Timestamp Format
- H2 section timestamps will use the format `YYYY-MM-DD HH:MM:SS` (e.g., `2025-05-08 14:30:00`)
- The timezone is omitted and assumed to be the machine's local timezone
- Configuration of timestamp formats will be considered in future iterations

##### Handling Existing Files
- Existing H2-level headers that cannot be matched to a new transcription will not be replaced
- If a timestamp header already exists, the first line after the header is preserved in the transcript
- The system compares the first line under each timestamp header with the newly generated transcription:
  - If they are identical, no changes are made
  - If they differ, the existing line is stored as a "user-corrected transcript" and marked as such in the output
- Any additional lines under the header are treated as user-added comments or edits and are not overwritten by the system
- Edited transcriptions can serve as feedback for improving the system

##### File Grouping by Date
- Transcripts will be grouped into files based on their dates.
- A single file will be generated for all transcripts that share the same date.
- The current date will not be used to generate a new file; instead, transcripts for the current date will be appended to an existing file if it exists.

#### Overview
The file output functionality will be implemented as a new adapter class, `FileOutputAdapter`, which extends the `OutputPort` interface. This adapter will handle writing transcription results to files in a structured and configurable manner, ensuring compatibility with the existing transcription pipeline.

#### Responsibilities
1. **File Creation and Management**:
   - Create files with date-based names (e.g., `YYYY-MM-DD.md`).
   - Ensure files are written to the correct output directory, as specified in the configuration.
   - Handle file overwrites, appends, or merges based on existing content.

2. **File Grouping**:
   - Group transcripts by their associated dates.
   - Generate or append to a single file for each date.

3. **Content Formatting**:
   - Organize transcription results into H2-level sections with timestamps.
   - Preserve user-edited content and comments in existing files.
   - Mark user-corrected transcripts for feedback purposes.
   - Ensure that transcripts for the same date are grouped under a single file.
   - Append new transcripts to the existing file for the current date, if applicable.

4. **Error Handling**:
   - Provide clear error messages for missing configurations or file write failures.
   - Log errors and warnings for debugging purposes.

5. **Integration**:
   - Integrate seamlessly with the existing transcription pipeline.
   - Use the same data structures (`TranscriptionResult`, `Transcription`, `CachedTranscription`) as the `MarkdownOutputAdapter`.

#### Class Design

**Class Name**: `FileOutputAdapter`

**Base Class**: `OutputPort`

**Methods**:
1. `output_transcription_results(transcription_results: list[TranscriptionResult], path: Path | None = None) -> None`:
   - Write transcription results to files.
   - Use the date-based naming convention for file names.
   - Handle merging with existing files.

2. `merge_with_existing_file(existing_file: Path, new_content: str) -> str`:
   - Compare new transcription results with existing content.
   - Preserve user edits and comments.
   - Mark user-corrected transcripts.

3. `generate_file_name(date: datetime.date) -> str`:
   - Generate a file name based on the date (e.g., `2025-05-08.md`).

4. `validate_output_directory(path: Path) -> None`:
   - Ensure the output directory exists and is writable.
   - Create the directory if it does not exist.

5. `log_error(message: str) -> None`:
   - Log errors for debugging and user feedback.

#### Integration Points
- Use the configuration system to determine the output directory and file naming conventions.

#### Example Workflow
1. The transcription pipeline generates a list of `TranscriptionResult` objects.
2. The `FileOutputAdapter` is invoked with the transcription results and the output directory path.
3. The adapter:
   - Validates the output directory.
   - Generates a file name based on the current date.
   - Writes the transcription results to the file, preserving user edits and comments if the file already exists.
4. Transcripts are grouped by their associated dates.
5. For each date:
   - If a file for the date already exists, append the new transcripts to it.
   - If no file exists for the date, create a new file and write the transcripts to it.
6. Transcripts for the current date are appended to the existing file, if available.

### Configuration Design

#### Configuration Option
1. **Output Directory**:
   - **Key**: `output_dir`
   - **Type**: `string`
   - **Description**: Specifies the directory where transcription files will be saved.
   - **Default**: `transcripts/` (relative to the SpeechDown project directory).

#### Integration with ConfigAdapter
- Extend the `ConfigPort` protocol to include an `output_dir` attribute and corresponding getter and setter methods.
- Update the `ConfigAdapter` implementation:
  1. Add an `output_dir` attribute.
  2. Implement methods to get and set the `output_dir`.
  3. Update the `load_config_from_path` method to load the `output_dir` from the configuration file.
  4. Ensure the `output_dir` is included when saving the configuration.

#### Integration with SpeechDownPaths
- The `SpeechDownPaths` class defines the paths for various components of the SpeechDown project, including the configuration file.
- The `config` attribute of `SpeechDownPaths` will be used to locate the configuration file (`config.json`) where the `output_dir` will be stored.
- The `ConfigAdapter` will load the configuration from the path specified by `SpeechDownPaths.config`.

#### Example Configuration File
The configuration will be stored in JSON format. Example:

```json
{
  "languages": ["en", "uk", "ru"],
  "output_dir": "transcripts/"
}
```

#### Example Workflow
1. User initializes a SpeechDown project and creates a configuration file (`config.json`).
2. The `ConfigAdapter` reads the configuration during initialization.
3. The `FileOutputAdapter` retrieves the `output_dir` from the configuration and writes transcription files to the specified directory.

### Testing Approach

#### Unit Tests
- Place unit tests for the `FileOutputAdapter` under `tests/unit/infrastructure/adapters/`.
- Use the naming convention `test_file_output_adapter.py` as per [ADR 002: Unit Test Structure](../../adrs/current/002_unit_test_structure.md).
- Mock dependencies such as `ConfigAdapter` and file system interactions to isolate the `FileOutputAdapter` logic.
- Test cases should include:
  1. Writing transcription results to a new file.
  2. Merging transcription results with an existing file.
  3. Handling invalid or missing `output_dir` configurations.

#### Integration Tests
- Place integration tests for the `FileOutputAdapter` under `tests/integration/infrastructure/adapters/`.
- Use the naming convention `test_file_output_adapter_integration.py` as per [ADR 005: Integration Test Structure](../../adrs/current/005_integration_test_structure.md).
- Test cases should include:
  1. End-to-end workflow from configuration loading to file output.
  2. Interaction with `SpeechDownPaths` and `ConfigAdapter` to retrieve the `output_dir`.
  3. Writing transcription results to the actual file system.

#### Test Execution
- Unit tests will be executed as part of the standard CI pipeline.
- Integration tests will be executed separately using the `test-integration` Makefile command, as defined in [ADR 005](../../adrs/current/005_integration_test_structure.md).

#### Mocking and Fixtures
- Use fixtures to provide mock configurations and transcription data for unit tests.
- Use temporary directories for integration tests to avoid modifying the actual file system.

## Implementation Plan

### Phased Approach Overview
The implementation will follow a phased approach to ensure controlled development, testing, and integration of the file output feature into the existing SpeechDown pipeline.

### Phase 1: Extend Configuration Handling
1. **Update `ConfigPort` Protocol**:
   - Add an `output_dir` attribute.
   - Add `get_output_dir()` and `set_output_dir()` methods.

2. **Update `ConfigAdapter`**:
   - Add an `output_dir` attribute.
   - Implement `get_output_dir()` and `set_output_dir()` methods.
   - Update `load_config_from_path()` to load `output_dir` from the configuration file.
   - Update the method that saves the configuration to include `output_dir`.

3. **Update `SpeechDownPaths`**:
   - Ensure the `config` attribute points to the correct configuration file path.

4. **Write Unit Tests**:
   - Test `ConfigAdapter` for loading, saving, and retrieving `output_dir`.
   - Mock file system interactions to isolate logic.

5. **Verify**:
   - Run unit tests to ensure the configuration handling works as expected.

#### Phase 2: Implement `FileOutputAdapter`
1. **Create `FileOutputAdapter`**:
   - Extend `OutputPort`.
   - Implement `output_transcription_results()` to write transcription results to files.
   - Add helper methods:
     - `validate_output_directory()`: Ensure the directory exists or create it.
     - `generate_file_name()`: Generate file names based on the current date.
     - `merge_with_existing_file()`: Handle merging with existing files.

2. **Integrate with `ConfigAdapter`**:
   - Retrieve `output_dir` from the configuration and use it in `FileOutputAdapter`.

3. **Write Unit Tests**:
   - Test `FileOutputAdapter` methods in isolation.
   - Mock dependencies like `ConfigAdapter` and file system interactions.

4. **Verify**:
   - Run unit tests to ensure the adapter works as expected.

#### Phase 3: Integrate with Transcription Pipeline
1. **Update `transcribe()` Function**:
   - Replace `MarkdownOutputAdapter` with `FileOutputAdapter`.
   - Ensure `FileOutputAdapter` uses the `output_dir` from the configuration.

2. **Update CLI Commands**:
   - Ensure the `init` command creates a default `output_dir` in the configuration.
   - Ensure the `transcribe` command uses the `output_dir` for file output.

3. **Write Integration Tests**:
   - Test the end-to-end workflow:
     - Initialize a project.
     - Configure the `output_dir`.
     - Transcribe audio files and verify the output in the specified directory.

4. **Verify**:
   - Run integration tests to ensure the pipeline works as expected.

#### Phase 4: Add Error Handling
1. **Handle Missing or Invalid `output_dir`**:
   - Add error messages for missing or invalid `output_dir` in `FileOutputAdapter`.
   - Log errors and provide user-friendly feedback.

2. **Write Unit Tests**:
   - Test error handling for invalid or missing `output_dir`.

3. **Verify**:
   - Run unit tests to ensure error handling works as expected.

#### Phase 5: Finalize Testing
1. **Add Mocking and Fixtures**:
   - Use fixtures to provide mock configurations and transcription data for unit tests.
   - Use temporary directories for integration tests.

2. **Ensure CI Integration**:
   - Add unit tests to the standard CI pipeline.
   - Add a `test-integration` Makefile command for integration tests.

3. **Verify**:
   - Run all tests (unit and integration) to ensure everything works as expected.

#### Phase 6: Documentation and Cleanup
1. **Update Documentation**:
   - Update the README and any relevant documentation to reflect the new `output_dir` feature.

2. **Code Cleanup**:
   - Refactor and clean up code to ensure readability and maintainability.

3. **Verify**:
   - Perform a final review and run all tests to ensure the implementation is complete.

## Future Considerations

### Summary
The following considerations outline potential enhancements for future iterations of the file output feature. These improvements would address scalability, user experience, error handling, and security concerns that are beyond the scope of the initial implementation.

### Feature Enhancements

#### File Locking Enhancements
- Explore more robust file locking mechanisms to handle concurrency across distributed systems (e.g., using a distributed lock service like Redis or Zookeeper).
- Investigate optimistic concurrency control strategies to reduce contention when multiple processes write to the same file.

#### Configurable Timestamp Formats
- Allow users to configure timestamp formats for H2-level headers and file names.
- Support additional time zones and localization options for timestamps.

#### Enhanced Error Handling
- Implement retry mechanisms for transient errors (e.g., file system issues or temporary lock contention).
- Provide detailed error reporting and diagnostics for debugging.

#### Real-Time Transcription Updates
- Enable real-time updates to transcription files as audio is processed.
- Consider using streaming APIs or event-driven architectures for real-time workflows.

#### User Feedback Integration
- Use user-corrected transcripts as feedback to improve transcription accuracy.
- Implement a feedback loop to train machine learning models based on user edits.

#### Scalability Improvements
- Optimize the system for handling large-scale transcription workloads.
- Investigate parallel processing and distributed architectures to improve performance.

#### Security and Access Control
- Add support for encrypting transcription files to protect sensitive data.
- Implement access control mechanisms to restrict who can read or write transcription files.

## Supporting Documentation
- [ADR 010: Introduce Markdown Design Documents for Feature Implementation](../../adrs/current/010_design_docs.md)
- [ADR 002: Unit Test Structure](../../adrs/current/002_unit_test_structure.md)
- [ADR 005: Integration Test Structure](../../adrs/current/005_integration_test_structure.md)
