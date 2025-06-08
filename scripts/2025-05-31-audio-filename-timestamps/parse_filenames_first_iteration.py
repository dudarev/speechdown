"""
Audio filename timestamp parser.

This script extracts timestamps from audio filenames using various patterns:
- YYYYMMDD HHMMSS (e.g., "20250408 204728")
- YYYYMMDD_HHMMSS (e.g., "20240908_102336") 
- YYMMDD_HHMMSS (e.g., "250512_105730")

For YYMMDD patterns, the script scans all positions in the filename to find
valid timestamps, since these patterns can appear anywhere and may be
confused with other numeric sequences (like phone numbers).
"""

import re
import datetime

FILENAMES_TO_TEST = [
    "Call recording +380999999999_250512_105730.m4a", # Problematic one
    "20250408 204728.m4a",
    ".Voice 1306_W_20240908_102336.m4a",
    "Voice 241113_202240.m4a",
    "Voice 001.m4a",
    "prefix_998877_123456_realdate_231020_112233_suffix.m4a" # Multiple potential YYMMDD_HHMMSS
]

PATTERNS_CONFIG = [
    {
        "regex": re.compile(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}) (?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"),
        "is_yy": False,
        "name": "YYYYMMDD HHMMSS",
        "scan_all_positions": False  # Only search for first occurrence
    },
    {
        "regex": re.compile(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"),
        "is_yy": False,
        "name": "YYYYMMDD_HHMMSS",
        "scan_all_positions": False  # Only search for first occurrence
    },
    {
        "regex": re.compile(r"(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"),
        "is_yy": True,
        "name": "YYMMDD_HHMMSS",
        "scan_all_positions": True   # Scan all positions to find valid timestamps
    }
]

def validate_timestamp_components(parts, is_yy_format):
    """Validate individual timestamp components for plausible ranges."""
    year_str = parts['year']
    
    if is_yy_format:
        if not (0 <= int(year_str) <= 99):
            raise ValueError(f"2-digit year '{year_str}' out of 00-99 range.")
        year = int("20" + year_str)
    else:
        if not (1900 <= int(year_str) <= 2099):
            raise ValueError(f"4-digit year '{year_str}' out of 1900-2099 range.")
        year = int(year_str)

    month = int(parts['month'])
    if not (1 <= month <= 12):
        raise ValueError(f"Month '{parts['month']}' out of 1-12 range.")

    day = int(parts['day'])
    if not (1 <= day <= 31):
        raise ValueError(f"Day '{parts['day']}' out of 1-31 range.")

    hour = int(parts['hour'])
    if not (0 <= hour <= 23):
        raise ValueError(f"Hour '{parts['hour']}' out of 0-23 range.")

    minute = int(parts['minute'])
    if not (0 <= minute <= 59):
        raise ValueError(f"Minute '{parts['minute']}' out of 0-59 range.")

    second = int(parts['second'])
    if not (0 <= second <= 59):
        raise ValueError(f"Second '{parts['second']}' out of 0-59 range.")

    return year, month, day, hour, minute, second


def find_timestamp_matches(filename, pattern_config):
    """Find potential timestamp matches based on the pattern configuration."""
    regex = pattern_config["regex"]
    
    if pattern_config["scan_all_positions"]:
        # Scan all positions in the filename to find overlapping matches
        matches = []
        for i in range(len(filename)):
            match = regex.match(filename[i:])
            if match:
                # Create a simple match-like object with the matched text and groups
                match_info = {
                    'matched_text': match.group(0),
                    'groups': match.groupdict()
                }
                matches.append(match_info)
        return matches
    else:
        # Find only the first match
        match = regex.search(filename)
        if match:
            match_info = {
                'matched_text': match.group(0),
                'groups': match.groupdict()
            }
            return [match_info]
        return []


def extract_timestamp_from_filename(filename):
    """Extract the first valid timestamp found in the filename."""
    for config in PATTERNS_CONFIG:
        matches = find_timestamp_matches(filename, config)
        
        for match_info in matches:
            try:
                year, month, day, hour, minute, second = validate_timestamp_components(
                    match_info['groups'], config["is_yy"]
                )
                
                # Final validation by creating the datetime object
                dt_obj = datetime.datetime(year, month, day, hour, minute, second)
                
                # Return the first valid timestamp found
                return {
                    "year": year, "month": month, "day": day,
                    "hour": hour, "minute": minute, "second": second,
                    "pattern_name": config["name"],
                    "datetime_obj": dt_obj,
                    "matched_string": match_info['matched_text']
                }
            except ValueError:
                # Invalid timestamp, continue to next match
                continue
    
    return None


print(f"{'Filename':<70} | {'Pattern Matched':<20} | {'Matched String':<20} | {'Extracted Datetime'}")
print("-" * 150)

for fname in FILENAMES_TO_TEST:
    timestamp_info = extract_timestamp_from_filename(fname)
    if timestamp_info:
        print(f"{fname:<70} | {timestamp_info['pattern_name']:<20} | {timestamp_info['matched_string']:<20} | {timestamp_info['datetime_obj']}")
    else:
        print(f"{fname:<70} | {'No Match':<20} | {'N/A':<20} |")