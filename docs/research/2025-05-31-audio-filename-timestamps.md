# Extracting Timestamps from Audio File Names
*Status*: Completed - Phase 1
*Date*: 2025-05-31

## Problem
Audio files often have timestamps embedded in their file names, but the formats can vary widely. We need a systematic way to extract these timestamps. This research aims to explore methods for reliably parsing timestamps from file names, including leveraging existing tools and potentially using machine learning for categorization.

## Approach
1. **Gather Audio File Names:** ✅ Developed `list_audio_files.py` to collect audio file names from directories
2. **Analyze Naming Patterns:** ✅ Manually inspected collected file names to identify common timestamp formats
3. **Categorize Formats:** ✅ Identified three main patterns: YYYYMMDD HHMMSS, YYYYMMDD_HHMMSS, and YYMMDD_HHMMSS
4. **Integrate Existing Parser:** ✅ Created comprehensive parsing functions with validation
5. **Develop New Parsers:** ✅ Implemented both comprehensive and backwards search approaches
6. **Evaluate Performance:** ✅ Tested with problematic cases and edge cases

## Findings

### Key Discoveries

1. **Backwards Search is Superior**: The most significant finding is that searching for timestamp patterns from the end of the filename backwards is both simpler to implement and more accurate than traditional forward search approaches.

2. **Pattern Ambiguity is a Major Challenge**: Many filenames contain multiple numeric sequences that match timestamp patterns:
   - Phone numbers (e.g., `+380999999999_250512_105730.m4a`)
   - Sequential IDs and codes
   - Multiple valid timestamp patterns in one filename

3. **Position-Based Logic Works**: Timestamps in audio filenames are typically located near the end, before the file extension, making backwards search naturally more accurate.

4. **Component Validation is Essential**: Range checking (month 1-12, day 1-31, hour 0-23, etc.) is crucial for filtering out false positives that match the pattern structure but contain invalid values.

### Technical Implementation

**Two approaches were developed:**

1. **Comprehensive Approach** (`parse_filenames.py`):
   - Scans all positions in filename for overlapping matches
   - Complex logic with custom match wrappers
   - ~75+ lines of code
   - Works but is complex to maintain

2. **Backwards Search Approach** (`parse_filenames_backwards.py`):
   - Simple loop from end to beginning
   - Stops at first valid match from the end
   - ~40 lines of code
   - More intuitive and maintainable

### Supported Timestamp Patterns

| Pattern | Format | Example | Notes |
|---------|--------|---------|-------|
| YYYYMMDD HHMMSS | Year-Month-Day Hour:Minute:Second | `20250408 204728` | Space separator, unambiguous |
| YYYYMMDD_HHMMSS | Year-Month-Day_Hour:Minute:Second | `20240908_102336` | Underscore separator, unambiguous |
| YYMMDD_HHMMSS | Year-Month-Day_Hour:Minute:Second | `250512_105730` | 2-digit year, requires backwards search |

### Test Cases and Results

All test cases now parse correctly with the backwards search approach:

```
Call recording +380999999999_250512_105730.m4a → 2025-05-12 10:57:30
20250408 204728.m4a → 2025-04-08 20:47:28
.Voice 1306_W_20240908_102336.m4a → 2024-09-08 10:23:36
Voice 241113_202240.m4a → 2024-11-13 20:22:40
prefix_998877_123456_realdate_231020_112233_suffix.m4a → 2023-10-20 11:22:33
```

## Implementation Files

Located in `/scripts/2025-05-31-audio-filename-timestamps/`:

- `list_audio_files.py` - Directory scanning and file collection
- `parse_filenames.py` - Comprehensive parsing with all-position scanning
- `parse_filenames_backwards.py` - **Recommended** backwards search implementation
- `parse_filenames_all.py` - **Production-ready** batch processing with year validation
- `gather_filenames.py` - Filename collection for analysis

### Production Script: parse_filenames_all.py

The latest addition is a production-ready script designed for batch processing multiple filenames with additional validation:

**Key Features:**
- **Batch Processing**: Reads filenames from stdin (pipe or interactive)
- **Year Validation**: Restricts parsing to 2024-2025 timestamps only
- **Comprehensive Output**: Shows both successfully parsed and unparseable files
- **Sorted Results**: Orders output chronologically
- **Summary Statistics**: Provides processing counts and year distribution

**Usage Examples:**
```bash
# Process from file
python parse_filenames_all.py < filenames.txt

# Chain with directory listing
python list_audio_files.py --no-extensions | python parse_filenames_all.py

# Interactive input
python parse_filenames_all.py
```

This script demonstrates how the backwards search approach can be effectively deployed for real-world batch processing scenarios.

## Old Approach

In `voice-cli` repository the [following approach](https://github.com/dudarev/voice-cli/blob/main/main.py#L152C1-L176C56) was used:

```
def get_file_timestamp(path: Path) -> datetime:
    """
    Try to extract timestamp from file name.
    If not found, use modified time of file.

    Examples of file names:
    Voice 1571_W_20230806_020851.mp3
    20230804 214200.m4a
    """
    try:
        elements = re.split(r"[_\.]", path.name)
        timestamp_elements = [e for e in elements if len(e) >= 6 and e.isdigit()]
        return parse(" ".join(timestamp_elements))
    except ParserError:
        pass

    try:
        # split on white space
        elements = re.split(r"[\s\.]", path.name)
        timestamp_elements = [e for e in elements if len(e) >= 6 and e.isdigit()]
        return parse(" ".join(timestamp_elements))
    except ParserError:
        pass

    return datetime.fromtimestamp(path.stat().st_mtime)
```

**Problems with the Old Approach:**

This approach has several significant limitations that led to the development of the new backwards search method:

1. **No Position Awareness**: The old method splits on delimiters and collects all numeric sequences ≥6 digits, then relies on an external parser to make sense of them. This fails with files like `+380999999999_250512_105730.m4a` where phone numbers get mixed with actual timestamps.

2. **Ambiguous Pattern Matching**: When multiple valid numeric sequences exist, there's no logic to determine which represents the actual timestamp. The approach essentially guesses and hopes the external parser can figure it out.

3. **External Dependency**: Relies on the `dateutil.parse()` function which can be overly permissive and may accept invalid combinations or parse the wrong sequence when multiple candidates exist.

4. **Limited Format Support**: Only handles underscore, dot, and whitespace delimiters, missing other common patterns like space-separated timestamps (`20250408 204728.m4a`).

5. **No Validation**: Lacks component-level validation (e.g., month 1-12, day 1-31), allowing invalid dates to pass through or be misinterpreted.

The new backwards search approach addresses all these issues by using position-based logic, explicit pattern matching, and proper component validation, resulting in much more reliable timestamp extraction.

## Next steps

### Phase 2 - Integration and Enhancement
- [ ] Integrate backwards search approach into main speechdown application
- [x] ~~Add batch processing for multiple filenames~~ ✅ Completed with `parse_filenames_all.py`
- [x] ~~Add year validation for recent recordings~~ ✅ Implemented 2024-2025 validation
- [ ] Add support for additional timestamp formats discovered in real-world data
- [ ] Implement fuzzy matching for malformed timestamps
- [ ] Add confidence scoring for timestamp extraction

### Phase 3 - Advanced Features  
- [ ] Machine learning approach for complex/ambiguous cases
- [ ] Audio metadata correlation for timestamp validation
- [x] ~~Batch processing optimization for large file collections~~ ✅ Completed
- [ ] Integration with speech recognition pipeline

### Immediate Recommendation
**Use the batch processing script** (`parse_filenames_all.py`) for production workflows as it combines the backwards search approach with year validation and comprehensive reporting suitable for real-world scenarios.
