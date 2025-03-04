# Integration Tests

This directory contains integration tests that validate the interaction between multiple components in the SpeechDown project.

See ADR 005 for more information about integration tests in SpeechDown.

## Running Tests

Integration tests can be run with:

```bash
make test-integration
```

This will execute all tests in the integration directory with the appropriate markers.

## Test Structure

Tests are organized to mirror the structure of the `src` directory, making it easy to find tests for specific components.

## Whisper Model Integration Tests

The Whisper integration tests use actual Whisper models to transcribe audio files. Due to the computational requirements:

1. These tests are marked as `@pytest.mark.integration` and `@pytest.mark.slow`
2. By default, they will be skipped unless explicitly enabled
3. They require an actual audio file in the `tests/data/audio_files` directory

## Adding New Integration Tests

When creating new integration tests:

1. Place them in the appropriate subdirectory mirroring the `src` structure
2. Use the naming convention `test_*_integration.py`
3. Mark slow or resource-intensive tests with `@pytest.mark.slow`
4. Mark all integration tests with `@pytest.mark.integration`
