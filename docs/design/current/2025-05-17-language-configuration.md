# Language Configuration Design Document

## Summary
This document outlines the design for ensuring that language configuration settings exist and are properly documented in the SpeechDown project. The language configuration allows users to specify which languages they want to work with for transcription, which is essential for improving accuracy and performance.

**Date:** 2025-05-17

## Product Requirements

### Objective
Ensure language configuration settings exist and are properly documented, making it easy for users to specify and manage the languages they want to use for transcription.

### Use Cases
1. Users can view currently configured languages.
2. Users can configure preferred languages for transcription.
3. Users can add/remove specific languages from the configuration.
4. New users understand how to configure languages through documentation.

### Success Metrics
- Language configuration settings are properly initialized during project setup.
- Default languages are automatically set when none are specified.
- Users can successfully modify language settings through the CLI.
- Documentation provides clear instructions on language configuration.

## UX Design

### User Flows
1. **Initial Setup Flow**
   - User initializes a SpeechDown project using `sd init`.
   - The system creates a default configuration with a predefined set of languages.
   - User receives feedback about the default configuration, including languages.

2. **View Configuration Flow**
   - User runs `sd config` to view current configuration.
   - System displays the currently configured languages.

3. **Modify Languages Flow**
   - User runs `sd config --languages en,fr,de` to set specific languages.
   - System updates the configuration and confirms changes.
   - Alternatively, user can add a language: `sd config --add-language ja`.
   - Or remove a language: `sd config --remove-language fr`.

### Accessibility Considerations
- Provide clear error messages for invalid language codes.
- Support common language code formats (ISO 639-1 two-letter codes).
- Ensure compatibility with existing workflows and configurations.
- Make language setting commands intuitive and consistent with other configuration commands.

## Implementation Decisions & References

### Technical Design

#### Language Code Handling
- Continue using the existing `Language` value object in `domain/value_objects.py`.
- Ensure validation against the extensive `LANGUAGES` dictionary already defined in the code.
- Preserve the existing `TO_LANGUAGE_CODE` mapping for supporting language name aliases.

#### Configuration Storage
- Store language configuration in the existing `config.json` file.
- Maintain the current format: `"languages": ["en", "uk", "ru"]` for compatibility.
- The default language set will include English, Ukrainian, and Russian as already defined in `DEFAULT_LANGUAGES`.

#### Command Line Interface
- Enhance the existing `config` command in `presentation/cli/commands/handlers.py`.
- Add parameters to modify language settings:
  - `--languages` to set the complete list of languages.
  - `--add-language` to add a single language.
  - `--remove-language` to remove a specific language.

#### ConfigAdapter Implementation
- The current `ConfigAdapter` implementation already has the necessary methods:
  - `get_languages()` and `set_languages()` for retrieving and updating language settings.
  - `set_default_languages_if_not_set()` to initialize with defaults.

#### Integration with Transcription Service
- No changes needed to the transcription service as it already uses the configured languages.
- The `WhisperTranscriberAdapter` and `WhisperModelAdapter` already handle language parameters correctly.

### Documentation Updates
- Update the README.md section on Configuration to explicitly mention language settings.
- Include example commands for setting, adding, and removing languages.
- List the supported language codes or provide a reference to where they can be found.
- Explain how language settings affect transcription accuracy and performance.

## Testing & Rollout

### Unit Tests
- Update existing tests in `test_config_command.py` to cover new language command parameters.
- Ensure `ConfigAdapter` tests verify language setting operations work correctly.
- Test validation of language codes against the supported languages list.

### Integration Tests
- Add integration tests to verify the end-to-end workflow of:
  - Setting languages via CLI and confirming they persist in configuration.
  - Using those languages in transcription operations.

### Validation Plan
1. Manually verify all language command options work as expected.
2. Confirm documentation accuracy by following the instructions as a new user.
3. Test with various combinations of valid and invalid language codes.
4. Verify default languages are set correctly when none are specified.

## Implementation Plan

### Phase 1: Verify Current Implementation
1. **Review Existing Code**:
   - Confirm `ConfigPort` and `ConfigAdapter` properly handle language settings.
   - Check if `set_default_languages_if_not_set()` is called during initialization.

2. **Test Current Functionality**:
   - Verify that default languages are set if not explicitly provided.
   - Ensure existing methods for getting and setting languages work correctly.

### Phase 2: Enhance CLI Command
1. **Update Config Command**:
   - Add `--languages` parameter to set the complete list of languages.
   - Add `--add-language` parameter to add a single language.
   - Add `--remove-language` parameter to remove a specific language.

2. **Implement Command Handlers**:
   - Update the `config()` function in `handlers.py` to process new language parameters.
   - Ensure proper validation and error handling for language codes.

3. **Write Unit Tests**:
   - Add tests for new CLI command parameters.
   - Test invalid inputs and edge cases.

### Phase 3: Documentation Updates
1. **Update README.md**:
   - Add specific section on language configuration.
   - Include example commands and explanations.

2. **Code Documentation**:
   - Ensure functions have clear docstrings explaining language parameters.
   - Add comments explaining validation logic where necessary.

### Phase 4: Testing and Finalization
1. **Run All Tests**:
   - Run unit and integration tests to ensure functionality works as expected.
   - Fix any issues discovered.

2. **Manual Validation**:
   - Perform manual testing of all language configuration commands.
   - Verify documentation accuracy.

3. **Final Review**:
   - Perform code review to ensure quality and adherence to project standards.
   - Check for any remaining TODOs or unresolved issues.

## Open Questions / References

### Key Questions
1. Should we consider adding a command to list all supported languages?
2. Is there a need for language-specific model configurations in the future?
3. Should we consider locale-specific language codes (e.g., "en-US" vs "en-GB")?

### References
- [Whisper model documentation](https://github.com/openai/whisper)
- [ISO 639-1 language codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
- [ADR 010: Introduce Markdown Design Documents](../../adrs/current/010_design_docs.md)
