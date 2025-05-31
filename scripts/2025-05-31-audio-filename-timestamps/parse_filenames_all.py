"""
Audio filename timestamp parser for processing multiple filenames.

This script processes multiple filenames from text input (one per line),
extracts timestamps using backwards search, validates that years are 2024-2025,
and outputs both successfully parsed filenames and unparseable ones.

Usage:
    python parse_filenames_all.py < filenames.txt
    python parse_filenames_all.py
    (then enter filenames line by line, press Ctrl+D when done)
"""

import re
import datetime
import sys
from typing import List, Dict, Optional, Tuple

PATTERNS_CONFIG = [
    {
        "regex": re.compile(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}) (?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"),
        "is_yy": False,
        "name": "YYYYMMDD HHMMSS"
    },
    {
        "regex": re.compile(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"),
        "is_yy": False,
        "name": "YYYYMMDD_HHMMSS"
    },
    {
        "regex": re.compile(r"(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"),
        "is_yy": True,
        "name": "YYMMDD_HHMMSS"
    }
]

VALID_YEARS = {2023, 2024, 2025}


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

    # Check if year is in the valid range (2024-2025)
    if year not in VALID_YEARS:
        raise ValueError(f"Year {year} is not in the valid range {sorted(VALID_YEARS)}.")

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


def search_pattern_backwards(text, pattern):
    """
    Search for pattern from the end of the string backwards.
    This searches every position starting from the end, going backwards.
    """
    # Search from the end backwards
    for i in range(len(text) - 1, -1, -1):
        match = pattern.match(text[i:])
        if match:
            # Create match info with the actual matched text and groups
            return {
                'matched_text': match.group(0),
                'groups': match.groupdict(),
                'start_pos': i
            }
    return None


def find_timestamp_matches(filename, pattern_config):
    """Find potential timestamp matches using backwards search."""
    regex = pattern_config["regex"]
    
    # Always search from the end backwards - this is more reliable for timestamps
    match_info = search_pattern_backwards(filename, regex)
    if match_info:
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


def process_filenames(filenames: List[str]) -> Tuple[List[Dict], List[str]]:
    """
    Process a list of filenames and return parsed timestamps and unparseable filenames.
    
    Args:
        filenames: List of filename strings to process
        
    Returns:
        Tuple of (successfully_parsed, unparseable_filenames)
    """
    successfully_parsed = []
    unparseable_filenames = []
    
    for filename in filenames:
        filename = filename.strip()
        if not filename:  # Skip empty lines
            continue
            
        timestamp_info = extract_timestamp_from_filename(filename)
        if timestamp_info:
            timestamp_info['filename'] = filename
            successfully_parsed.append(timestamp_info)
        else:
            unparseable_filenames.append(filename)
    
    return successfully_parsed, unparseable_filenames


def print_results(successfully_parsed: List[Dict], unparseable_filenames: List[str]):
    """Print the results in a formatted way."""
    print(f"\n{'='*80}")
    print(f"PROCESSING RESULTS")
    print(f"{'='*80}")
    
    if successfully_parsed:
        print(f"\n✅ SUCCESSFULLY PARSED ({len(successfully_parsed)} files):")
        print(f"{'Filename':<60} | {'Pattern':<20} | {'Timestamp'}")
        print("-" * 110)
        
        # Sort by datetime for better readability
        successfully_parsed.sort(key=lambda x: x['datetime_obj'])
        
        for info in successfully_parsed:
            print(f"{info['filename']:<60} | {info['pattern_name']:<20} | {info['datetime_obj']}")
    
    if unparseable_filenames:
        print(f"\n❌ UNPARSEABLE FILENAMES ({len(unparseable_filenames)} files):")
        print("-" * 80)
        for filename in unparseable_filenames:
            print(f"  {filename}")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total files processed: {len(successfully_parsed) + len(unparseable_filenames)}")
    print(f"  Successfully parsed:  {len(successfully_parsed)}")
    print(f"  Unparseable:          {len(unparseable_filenames)}")
    
    if successfully_parsed:
        years = set(info['year'] for info in successfully_parsed)
        print(f"  Years found:          {sorted(years)}")


def main():
    """Main function to process filenames from stdin."""
    print("Audio Filename Timestamp Parser")
    print("=" * 40)
    print("Enter filenames (one per line), press Ctrl+D when done:")
    print("Or pipe from a file: python parse_filenames_all.py < filenames.txt")
    print()
    
    try:
        # Read all lines from stdin
        filenames = []
        for line in sys.stdin:
            filenames.append(line.strip())
        
        if not filenames:
            print("No filenames provided.")
            return
        
        # Process the filenames
        successfully_parsed, unparseable_filenames = process_filenames(filenames)
        
        # Print results
        print_results(successfully_parsed, unparseable_filenames)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
