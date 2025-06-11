# Design Doc: Audio Filename Timestamp Extraction (SD-17)

**Date:** 2025-06-09  
**Status:** Draft  
**Related Ticket:** SD-17  
**Implementation Ticket:** SD-18  
**Implementation Branch:** `feature/sd-18-implement-grouping-of-voice-notes-into-daily-files-per`  
**Related ADR:** [ADR 010: Introduce Markdown Design Documents](../adrs/current/010_design_docs.md)  
**Related Research:** [2025-05-31-audio-filename-timestamps.md](../../research/2025-05-31-audio-filename-timestamps.md)

---

## 1. Product Requirements

**Objective:**
Reliably extract timestamps from audio file names in various formats, supporting batch and single-file workflows, and integrate this logic into the main SpeechDown application.

**Use Cases:**
- Automatically sort or process audio files by their embedded timestamps.
- Handle files from different sources with varying naming conventions.
- Provide clear error reporting for unparseable files.

**Success Metrics:**
- ≥ 95% of real-world files with timestamps are parsed correctly.
- No false positives (e.g., phone numbers or IDs mistaken for timestamps).
- Batch processing supports thousands of files efficiently.

---

## 2. UX Design

- **CLI Integration:**
  - The CLI utility automatically and recursively finds audio files in directories.
  - Extracts timestamps from filenames using the backwards search approach.
  - Outputs parsed timestamps and unparseable files in a clear, tabular format.
  - Provides summary statistics (parsed/unparseable counts, year distribution, pattern usage).
- **Error Handling:**
  - For files where timestamp extraction fails, use the file's modification time as fallback (consistent with existing codebase).
  - Invalid date combinations (e.g., February 30th) are caught and logged, falling back to file modification time.
  - No crashes on malformed input; always produces a summary.

---

## 3. Technical Design

### 3.1. Approach
- **Backwards Search:**
  - Search for timestamp patterns from the end of the filename backwards, as this is more reliable (see research findings).
- **Pattern Matching:**
  - Support the following patterns:
    - `YYYYMMDD_HHMMSS` (e.g., `20240908_102336`)
    - `YYYYMMDD HHMMSS` (e.g., `20250408 204728`)
    - `YYMMDD_HHMMSS` (e.g., `250512_105730`)
  - Patterns are prioritized in the above order.
- **Component Validation:**
  - Each component (year, month, day, hour, minute, second) is range-checked.
  - Year is validated to be in range 2000-2099 (configurable, default matches reference implementation's 2022-2025 for safety).
  - Date validation includes proper month/day combinations (no February 30th, etc.).
- **Batch Processing:**
  - Accepts a list of filenames and processes them efficiently.
  - Results are sorted chronologically.

### 3.2. Implementation Details
- **Reference Implementation:** See [`parse_filenames_all.py`](../../../scripts/2025-05-31-audio-filename-timestamps/parse_filenames_all.py).
- **Extensibility:**
  - Year range validation: accept years 2000-2099 (configurable, aligns with reference implementation for production safety).
  - Supported patterns should be easy to update.
  - Future: allow configuration via environment variable or config file.
- **Fallback Strategy:**
  - When timestamp extraction fails, use file modification time as the timestamp (consistent with existing codebase).
  - Clearly indicate in logs/output which files used fallback vs. extracted timestamps.
- **Testing:**
  - Use real-world and edge-case filenames from research.
  - Ensure all test cases in the research doc parse correctly.

### 3.3. Detailed Implementation Plan

### Core Classes and Methods to Modify

#### 1. `AudioFileAdapter` (Infrastructure Layer)
**File:** `src/speechdown/infrastructure/adapters/audio_file_adapter.py`

**Current State:**
- `get_audio_file()` method uses `datetime.fromtimestamp(os.path.getmtime(path))` (line 19)
- `_get_file_timestamp()` method uses `datetime.fromtimestamp(path.stat().st_mtime)` (line 39)
- TODO comment indicates need for more robust timestamp generation (line 15-17)

**Changes Required:**
- Replace `_get_file_timestamp()` with delegation to new timestamp extraction module
- Update `get_audio_file()` to use the new timestamp extraction service
- Add logging to indicate whether timestamp was extracted from filename or fell back to file time

**Module Architecture Decision:**
After evaluating placement options, the timestamp extraction functionality should be implemented as a separate infrastructure-level service module for the following reasons:

1. **Shared Responsibility**: Multiple adapters need timestamp extraction (`AudioFileAdapter`, `SQLiteRepositoryAdapter`, `TranscriptionService`)
2. **Infrastructure Concern**: File system operations and timestamp parsing are infrastructure-level concerns
3. **Single Responsibility**: Keeps timestamp logic separate from audio file collection logic
4. **Testability**: Easier to unit test timestamp extraction in isolation
5. **Reusability**: Can be used by future file-handling adapters

**Recommended Structure:**
```
src/speechdown/infrastructure/
├── adapters/
│   ├── audio_file_adapter.py
│   └── ...
├── services/
│   └── file_timestamp_service.py  # New module
├── database.py
└── schema.py
```

**Updated AudioFileAdapter Changes:**
- Inject `FileTimestampAdapter` as a dependency
- Delegate timestamp extraction to the service
- Remove direct file system timestamp access

#### 2. `TranscriptionService` (Application Layer)
**File:** `src/speechdown/application/services/transcription_service.py`

**Current State:**
- `get_file_timestamp()` method uses `datetime.fromtimestamp(path.stat().st_mtime)` (line 75)

**Changes Required:**
- Update to delegate timestamp extraction to the `AudioFileAdapter`
- Remove direct file system timestamp access
- This method might become redundant as timestamp logic moves to domain/infrastructure

#### 3. `SQLiteRepositoryAdapter` (Infrastructure Layer)
**File:** `src/speechdown/infrastructure/adapters/repository_adapter.py`

**Current State:**
- `_get_file_timestamp()` method uses `datetime.fromtimestamp(path.stat().st_mtime)` (line 233)

**Changes Required:**
- Update to use the same timestamp extraction logic as `AudioFileAdapter`
- Ensure consistency across all timestamp extraction points

### New Components to Create

#### 4. `FileTimestampAdapter` (Infrastructure Adapter)
**File:** `src/speechdown/infrastructure/services/file_timestamp_service.py` (new file)

**Purpose:**
- Centralize all file timestamp extraction logic
- Implement the backwards search algorithm from research
- Handle pattern matching, validation, and fallback strategies
- Provide a clean interface for all adapters that need timestamp extraction

**Key Methods:**
```python
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

@dataclass
class FileTimestampAdapter:
    """Service for extracting timestamps from files using filename patterns and fallback strategies."""
    
    def get_timestamp(self, path: Path) -> datetime:
        """Get timestamp from filename first, fallback to file modification time."""
        logger = logging.getLogger(__name__)
        
        extracted = self.extract_from_filename(path.name)
        if extracted:
            logger.debug(f"Extracted timestamp from filename {path.name}: {extracted}")
            return extracted
        else:
            fallback = self._get_file_fallback_time(path)
            logger.debug(f"Using fallback modification time for {path.name}: {fallback}")
            return fallback
    
    def extract_from_filename(self, filename: str) -> Optional[datetime]:
        """Extract timestamp using backwards search approach."""
        for config in self.TIMESTAMP_PATTERNS:
            match_results = self._search_pattern_backwards(filename, config["regex"])
            if match_results:
                try:
                    year, month, day, hour, minute, second = self._validate_timestamp_components(
                        match_results, config["is_yy"]
                    )
                    # Additional validation: try creating datetime to catch invalid dates
                    return datetime(year, month, day, hour, minute, second)
                except (ValueError, OverflowError) as e:
                    logging.getLogger(__name__).debug(f"Invalid date components in {filename}: {e}")
                    continue
        return None
        
    def _validate_timestamp_components(self, parts: Dict[str, str], is_yy_format: bool) -> tuple:
        """Validate individual timestamp components and return (year, month, day, hour, minute, second)."""
        year_str = parts['year']
        
        if is_yy_format:
            if not (0 <= int(year_str) <= 99):
                raise ValueError(f"2-digit year '{year_str}' out of 00-99 range.")
            year = int("20" + year_str)
        else:
            if not (1900 <= int(year_str) <= 2099):
                raise ValueError(f"4-digit year '{year_str}' out of 1900-2099 range.")
            year = int(year_str)
        
        # Validate year is in acceptable range (configurable)
        if not (self.VALID_YEAR_RANGE[0] <= year <= self.VALID_YEAR_RANGE[1]):
            raise ValueError(f"Year {year} not in valid range {self.VALID_YEAR_RANGE}")
        
        month = int(parts['month'])
        day = int(parts['day'])
        hour = int(parts['hour'])
        minute = int(parts['minute'])
        second = int(parts['second'])
        
        # Basic range validation
        if not (1 <= month <= 12):
            raise ValueError(f"Month {month} not in range 1-12")
        if not (1 <= day <= 31):
            raise ValueError(f"Day {day} not in range 1-31")
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour {hour} not in range 0-23")
        if not (0 <= minute <= 59):
            raise ValueError(f"Minute {minute} not in range 0-59")
        if not (0 <= second <= 59):
            raise ValueError(f"Second {second} not in range 0-59")
            
        return year, month, day, hour, minute, second
        
    def _search_pattern_backwards(self, text: str, pattern: re.Pattern) -> Optional[Dict[str, str]]:
        """Search for pattern from end of string backwards."""
        matches = list(pattern.finditer(text))
        if matches:
            # Return the last (rightmost) match
            last_match = matches[-1]
            return last_match.groupdict()
        return None
        
    def _get_file_fallback_time(self, path: Path) -> datetime:
        """Get file modification time as fallback when filename parsing fails."""
        # Use modification time consistently with existing codebase
        return datetime.fromtimestamp(path.stat().st_mtime)
```

**Required Constants (include in the service file):**
```python
TIMESTAMP_PATTERNS = [
    {
        "regex": re.compile(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"),
        "is_yy": False,
        "name": "YYYYMMDD_HHMMSS"
    },
    {
        "regex": re.compile(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}) (?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"),
        "is_yy": False,
        "name": "YYYYMMDD HHMMSS"
    },
    {
        "regex": re.compile(r"(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"),
        "is_yy": True,
        "name": "YYMMDD_HHMMSS"
    },
]

# Conservative year range for production safety (expandable via config)
VALID_YEAR_RANGE = (2000, 2099)
```

**Required Directory Creation:**
- Create `src/speechdown/infrastructure/services/` directory
- Add `src/speechdown/infrastructure/services/__init__.py` file

**Critical Implementation Notes:**
1. **Backwards Search Algorithm:** The service must search for timestamp patterns from right to left in the filename to avoid false matches with phone numbers or other numeric sequences that appear earlier in the filename.

2. **Pattern Priority:** Patterns are tried in order of specificity - 4-digit year patterns before 2-digit year patterns to avoid ambiguous matches.

3. **Error Handling:** The service must handle:
   - Invalid date combinations (Feb 30, Apr 31, etc.) by catching `ValueError` from `datetime()` constructor
   - Malformed numeric components (leading zeros, out-of-range values)
   - Multiple pattern matches in the same filename (use rightmost match)

4. **Logging Strategy:** Use DEBUG level for successful extractions and fallbacks, INFO level for summary statistics in batch operations.

5. **Performance Considerations:** For large batch operations, compile regex patterns once as class attributes rather than on each call.

### Integration Points

#### 5. Update Adapter Dependencies
**Files Affected:**
- `src/speechdown/infrastructure/adapters/audio_file_adapter.py`
- `src/speechdown/infrastructure/adapters/repository_adapter.py`
- `src/speechdown/application/services/transcription_service.py`

**Dependency Injection Pattern:**
```python
from ..adapters.file_timestamp_adapter import FileTimestampAdapter

@dataclass
class AudioFileAdapter(AudioFilePort):
    timestamp_service: FileTimestampAdapter = field(default_factory=FileTimestampAdapter)
    
    def get_audio_file(self, path: Path) -> AudioFile:
        dt = self.timestamp_service.get_timestamp(path)
        return AudioFile(path=path, timestamp=Timestamp(value=dt))
```

#### 6. Configuration Support
**File:** `src/speechdown/infrastructure/adapters/config_adapter.py`

**New Configuration Options:**
```python
class Config:
    # ... existing config ...
    timestamp_extraction_enabled: bool = True
    timestamp_year_min: int = 2000
    timestamp_year_max: int = 2099
    timestamp_fallback_to_modification_time: bool = True
```

### Testing Updates

#### 7. Test File Modifications
**Files to Rename:**
- `tests/data/subfolder/test-1.m4a` → `tests/data/subfolder/test-1_20240315_143022.m4a`
- `tests/data/test-2.m4a` → `tests/data/test-2 20240316 101530.m4a`
- Keep `tests/data/test-ru.m4a` and `tests/data/test-ua.m4a` unchanged

**Test Files to Update:**
- `tests/unit/infrastructure/adapters/test_audio_file_adapter.py` (if exists)
- `tests/integration/infrastructure/adapters/test_whisper_transcriber_adapter_integration.py`
- Any test that references the renamed files

#### 8. New Test Files to Create
**File:** `tests/unit/infrastructure/services/test_file_timestamp_service.py`
- Unit tests for pattern matching and validation
- Edge cases from research (phone numbers, multiple patterns, etc.)
- Fallback behavior testing

**File:** `tests/integration/test_timestamp_extraction_integration.py`
- End-to-end tests with real audio files
- Verify filename extraction vs. modification time fallback
- Test that renamed files extract correct timestamps
- Test that unchanged files fall back to modification time

### Migration Strategy

#### Phase 1: Core Implementation
1. Create `FileTimestampAdapter` infrastructure adapter
2. Implement timestamp extraction with backwards search algorithm
3. Add comprehensive unit tests for the service

#### Phase 2: Integration
1. Update `AudioFileAdapter` to use `FileTimestampAdapter` via dependency injection
2. Update `TranscriptionService` and `SQLiteRepositoryAdapter` to use the same service
3. Add configuration support for timestamp patterns and year validation

#### Phase 3: Testing & Validation
1. Rename test files with timestamps and update integration tests
2. Run full test suite and validate against research test cases
3. Performance testing with large file sets

---

## 4. Testing & Rollout

- **Validation Plan:**
  - Unit tests for each pattern and edge case.
  - Integration test: process test audio files and verify timestamp extraction works correctly.
  - **Test File Updates Required:**
    - Rename `test-1.m4a` → `test-1_20240315_143022.m4a` (subfolder test file)
    - Rename `test-2.m4a` → `test-2 20240316 101530.m4a` (main folder test file)
    - Keep `test-ru.m4a` and `test-ua.m4a` unchanged to test fallback to modification time
    - Update corresponding test assertions to validate extracted timestamps vs. modification time fallback
  - Verify no existing functionality is broken, especially around file handling and timestamp usage.
- **Migration:**
  - Replace any legacy timestamp extraction logic with the new backwards search approach.
- **Feature Flag:**
  - (Optional) Roll out as an opt-in feature before making default.

---

## 5. Developer Guide: Adding New Timestamp Formats

**For Developers:** To add new timestamp patterns to the system, modify the following file:

**File:** `src/speechdown/infrastructure/services/file_timestamp_service.py`

**Steps:**
1. Add a new pattern to the `TIMESTAMP_PATTERNS` list:
   ```python
   TIMESTAMP_PATTERNS = [
       # ... existing patterns ...
       {
           "regex": re.compile(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<hour>\d{2})-(?P<minute>\d{2})-(?P<second>\d{2})"),
           "is_yy": False,
           "name": "YYYY-MM-DD_HH-MM-SS"
       },
   ]
   ```

2. **Pattern Requirements:**
   - Must use named groups: `year`, `month`, `day`, `hour`, `minute`, `second`
   - Set `is_yy: True` for 2-digit year formats, `False` for 4-digit years
   - Add patterns in order of preference (most specific first)
   - Include a descriptive `name` for logging and debugging

3. **Testing:** Add test cases to `tests/unit/infrastructure/services/test_file_timestamp_service.py` with example filenames using the new pattern.

4. **Documentation:** Update this design document with the new supported format.

**Example Use Cases:**
- ISO format: `2024-03-15_14-30-22`
- Dot separators: `2024.03.15.143022`
- No separators: `20240315143022`
- Different time formats: `20240315-1430` (no seconds)

---

## 6. References
- [ADR 010: Design Docs](../adrs/current/010_design_docs.md)
- [Research: Timestamp Extraction](../../research/2025-05-31-audio-filename-timestamps.md)
- [Implementation: parse_filenames_all.py](../../../scripts/2025-05-31-audio-filename-timestamps/parse_filenames_all.py)

---

**Conclusion:**
This design implements a robust, maintainable, and extensible approach to extracting timestamps from audio filenames, based on research and real-world testing. The backwards search method is recommended for production use and will be integrated into the main SpeechDown application as part of SD-17.

**Implementation Validation Checklist:**
Before implementing, verify these assumptions from the design:

1. **Existing Code Patterns:**
   - Current `AudioFileAdapter.get_audio_file()` uses `os.path.getmtime()` (line 19)
   - Current `TranscriptionService.get_file_timestamp()` uses `path.stat().st_mtime` (line 75)
   - Current `SQLiteRepositoryAdapter._get_file_timestamp()` uses `path.stat().st_mtime` (line 233)
   - All existing code uses modification time, not creation time

2. **Test File State:**
   - `tests/data/test-2.m4a` exists and needs renaming
   - `tests/data/subfolder/test-1.m4a` exists and needs renaming
   - `tests/data/test-ru.m4a` and `tests/data/test-ua.m4a` should remain unchanged

3. **Import Structure:**
   - Services directory doesn't exist yet - must be created
   - Relative imports from adapters to services must use `..services.file_timestamp_service`

4. **Configuration Integration:**
   - Year range validation should be configurable via the existing Config class
   - Default year range should be conservative (2000-2099) for production safety

## Implementation Context

**Note:** This design document describes the timestamp extraction functionality that will be implemented as part of **SD-18: Implement grouping of voice notes into daily files per design document**. The actual implementation should be done on the branch `feature/sd-18-implement-grouping-of-voice-notes-into-daily-files-per`.

While this document focuses on the timestamp extraction component (SD-17), it serves as the foundation for the broader SD-18 feature which will group transcriptions by date based on these extracted timestamps.
