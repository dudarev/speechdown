#!/usr/bin/env python3
"""
Test script for extracting metadata from audio files.
Part of the research for extracting timestamps from audio file metadata.
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

def test_with_mutagen():
    """Test metadata extraction using Mutagen library."""
    try:
        from mutagen import File
        from mutagen.id3 import ID3NoHeaderError
        print("=== Testing with Mutagen ===")
        return True
    except ImportError:
        print("Mutagen not available. Install with: pip install mutagen")
        return False

def test_with_tinytag():
    """Test metadata extraction using TinyTag library."""
    try:
        from tinytag import TinyTag
        print("=== Testing with TinyTag ===")
        return True
    except ImportError:
        print("TinyTag not available. Install with: pip install tinytag")
        return False

def extract_metadata_mutagen(file_path: Path) -> Dict[str, Any]:
    """Extract metadata using Mutagen."""
    try:
        from mutagen import File
        audio_file = File(file_path)
        if audio_file is None:
            return {"error": "File not supported or corrupted"}
        
        metadata = {}
        
        # Get all tags
        if hasattr(audio_file, 'tags') and audio_file.tags:
            for key, value in audio_file.tags.items():
                if isinstance(value, list):
                    metadata[key] = [str(v) for v in value]
                else:
                    metadata[key] = str(value)
        
        # Get file info
        if hasattr(audio_file, 'info'):
            metadata['_duration'] = getattr(audio_file.info, 'length', None)
            metadata['_bitrate'] = getattr(audio_file.info, 'bitrate', None)
            metadata['_sample_rate'] = getattr(audio_file.info, 'sample_rate', None)
        
        return metadata
        
    except Exception as e:
        return {"error": str(e)}

def extract_metadata_tinytag(file_path: Path) -> Dict[str, Any]:
    """Extract metadata using TinyTag."""
    try:
        from tinytag import TinyTag
        tag = TinyTag.get(str(file_path))
        
        metadata = {}
        # Get all available attributes
        for attr in ['album', 'albumartist', 'artist', 'audio_offset', 'bitrate', 
                    'comment', 'composer', 'disc', 'disc_total', 'duration', 
                    'filesize', 'genre', 'samplerate', 'title', 'track', 
                    'track_total', 'year']:
            value = getattr(tag, attr, None)
            if value is not None:
                metadata[attr] = value
        
        # Look for extended metadata
        for attr in ['barcode', 'bpm', 'catalog_number', 'conductor', 'copyright', 
                    'director', 'encoded_by', 'encoder_settings', 'initial_key', 
                    'isrc', 'language', 'license', 'lyricist', 'lyrics', 'media', 
                    'publisher', 'set_subtitle', 'url']:
            value = getattr(tag, attr, None)
            if value is not None:
                metadata[attr] = value
        
        return metadata
        
    except Exception as e:
        return {"error": str(e)}

def extract_timestamp_fields(metadata: Dict[str, Any]) -> List[str]:
    """Identify fields that might contain timestamps."""
    timestamp_fields = []
    
    # Common timestamp field patterns
    timestamp_patterns = [
        'date', 'year', 'time', 'created', 'modified', 'recorded', 
        'encoded', 'TDRC', 'TYER', 'TDAT', 'TIME', 'TRDA', 'TORY',
        'creation_time', 'encoding_time', 'date_created', 'date_recorded'
    ]
    
    for key, value in metadata.items():
        if any(pattern.lower() in key.lower() for pattern in timestamp_patterns):
            timestamp_fields.append(f"{key}: {value}")
    
    return timestamp_fields

def analyze_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single audio file with all available methods."""
    print(f"\n--- Analyzing: {file_path.name} ---")
    
    results = {
        'file_path': str(file_path),
        'file_size': file_path.stat().st_size,
        'file_mtime': datetime.fromtimestamp(file_path.stat().st_mtime),
        'mutagen_metadata': None,
        'tinytag_metadata': None,
        'timestamp_fields': []
    }
    
    # Test with Mutagen if available
    if test_with_mutagen():
        results['mutagen_metadata'] = extract_metadata_mutagen(file_path)
        if not results['mutagen_metadata'].get('error'):
            results['timestamp_fields'].extend(
                extract_timestamp_fields(results['mutagen_metadata'])
            )
    
    # Test with TinyTag if available
    if test_with_tinytag():
        results['tinytag_metadata'] = extract_metadata_tinytag(file_path)
        if not results['tinytag_metadata'].get('error'):
            results['timestamp_fields'].extend(
                extract_timestamp_fields(results['tinytag_metadata'])
            )
    
    # Print results
    print(f"File size: {results['file_size']} bytes")
    print(f"File modification time: {results['file_mtime']}")
    
    if results['mutagen_metadata']:
        print(f"Mutagen metadata: {len(results['mutagen_metadata'])} fields")
        if results['mutagen_metadata'].get('error'):
            print(f"  Error: {results['mutagen_metadata']['error']}")
        else:
            print("  Available fields:")
            for key, value in sorted(results['mutagen_metadata'].items()):
                if not key.startswith('_'):  # Skip internal fields
                    print(f"    {key}: {value}")
    
    if results['tinytag_metadata']:
        print(f"TinyTag metadata: {len(results['tinytag_metadata'])} fields")
        if results['tinytag_metadata'].get('error'):
            print(f"  Error: {results['tinytag_metadata']['error']}")
        else:
            print("  Available fields:")
            for key, value in sorted(results['tinytag_metadata'].items()):
                print(f"    {key}: {value}")
    
    if results['timestamp_fields']:
        print("Potential timestamp fields:")
        for field in results['timestamp_fields']:
            print(f"  {field}")
    else:
        print("No timestamp fields found in metadata")
    
    return results

def main():
    """Main function to test metadata extraction."""
    print("Audio Metadata Extraction Test")
    print("=" * 40)
    
    # Test data directory
    test_data_dir = Path(__file__).parent.parent / "tests" / "data"
    
    if not test_data_dir.exists():
        print(f"Test data directory not found: {test_data_dir}")
        sys.exit(1)
    
    # Find all audio files
    audio_extensions = ['.m4a', '.mp3', '.wav', '.flac', '.ogg']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(test_data_dir.rglob(f"*{ext}"))
    
    if not audio_files:
        print("No audio files found in test data directory")
        sys.exit(1)
    
    print(f"Found {len(audio_files)} audio files")
    
    # Analyze each file
    all_results = []
    for file_path in sorted(audio_files):
        result = analyze_file(file_path)
        all_results.append(result)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    files_with_metadata = 0
    files_with_timestamps = 0
    
    for result in all_results:
        has_metadata = (
            (result['mutagen_metadata'] and not result['mutagen_metadata'].get('error')) or
            (result['tinytag_metadata'] and not result['tinytag_metadata'].get('error'))
        )
        has_timestamps = len(result['timestamp_fields']) > 0
        
        if has_metadata:
            files_with_metadata += 1
        if has_timestamps:
            files_with_timestamps += 1
    
    print(f"Total files analyzed: {len(all_results)}")
    print(f"Files with metadata: {files_with_metadata}")
    print(f"Files with timestamp fields: {files_with_timestamps}")
    print(f"Success rate: {files_with_timestamps}/{len(all_results)} ({files_with_timestamps/len(all_results)*100:.1f}%)")
    
    if files_with_timestamps == 0:
        print("\nNo timestamp metadata found in any files.")
        print("This suggests that the audio files in the test dataset do not contain")
        print("embedded timestamp information, making filename-based extraction the")
        print("primary method for timestamp recovery.")

if __name__ == "__main__":
    main()