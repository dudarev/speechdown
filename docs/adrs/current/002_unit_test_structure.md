# ADR 002: Unit Test Structure

**Date:** 2025-03-02
**Status:** Accepted  

## Context

We need a standardized and discoverable structure for unit tests in the SpeechDown project that follows Python conventions and maintains clear organization.

## Decision

We will:
1. Place all unit tests under `tests/unit` directory
2. Mirror the `src` directory structure in `tests/unit`
3. Use the following naming conventions:
   - Standard tests: `test_<source_file_name>.py`
   - Specific behavior tests: `test_<source_file_name>__<behavior>.py`

## Consequences

### Positive
- Direct mapping between source files and test files
- Easy test discovery for new developers
- Organized structure for adding new tests
- Support for multiple test files per source file when needed

### Negative
- Requires discipline to maintain mirrored directory structure
- Additional overhead in creating nested test directories

## Conclusion

This structured approach to unit testing will enhance code maintainability and support the project's growth by providing clear organization and naming conventions.
