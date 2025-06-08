#!/usr/bin/env python3
"""
Script to list audio files in a specified recordings directory.
This script gathers audio file names from the specified directory for analysis.
Configure the directory path in a .env file using RECORDINGS_DIRECTORY variable.
"""

import os
from pathlib import Path
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def list_audio_files_in_directory(directory_path, output_file=None, show_extensions=True):
    """
    List all audio files in the specified directory and optionally save to a file.
    
    Args:
        directory_path (str): Path to the directory to scan
        output_file (str, optional): Path to output file to save the list
        show_extensions (bool): Whether to show file extensions
    """
    try:
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"Error: Directory '{directory_path}' does not exist.")
            return
        
        if not directory.is_dir():
            print(f"Error: '{directory_path}' is not a directory.")
            return
        
        # Define audio/video extensions
        audio_extensions = {
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', 
            '.opus', '.mp4', '.mov', '.avi', '.mkv', '.webm'
        }
        
        # Get all audio files (not directories) recursively
        audio_files = []
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                file_ext = file_path.suffix.lower()
                if file_ext in audio_extensions:
                    # Get relative path from the base directory
                    relative_path = file_path.relative_to(directory)
                    audio_files.append(str(relative_path))
        
        # Sort files alphabetically
        audio_files.sort()
        
        print(f"Found {len(audio_files)} audio/video files in '{directory_path}':")
        print("-" * 50)
        
        # Display files
        for file_path in audio_files:
            # Get just the filename (without directory path)
            filename = Path(file_path).name
            if show_extensions:
                print(filename)
            else:
                # Remove extension
                file_without_ext = str(Path(filename).with_suffix(''))
                print(file_without_ext)
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Audio/Video files in {directory_path}\n")
                f.write("=" * 50 + "\n\n")
                for file_path in audio_files:
                    # Get just the filename (without directory path)
                    filename = Path(file_path).name
                    if show_extensions:
                        f.write(f"{filename}\n")
                    else:
                        file_without_ext = str(Path(filename).with_suffix(''))
                        f.write(f"{file_without_ext}\n")
            print(f"\nFile list saved to: {output_path}")
        
        return audio_files
        
    except PermissionError:
        print(f"Error: Permission denied accessing '{directory_path}'")
    except Exception as e:
        print(f"Error: {e}")


def main():
    # Get default directory from environment variable
    default_directory = os.getenv('RECORDINGS_DIRECTORY', './recordings')
    
    parser = argparse.ArgumentParser(description='List audio files in the specified recordings directory')
    parser.add_argument('--directory', '-d', 
                       default=default_directory,
                       help=f'Directory path to scan (default: {default_directory})')
    parser.add_argument('--output', '-o',
                       help='Output file to save the list')
    parser.add_argument('--no-extensions', action='store_true',
                       help='Hide file extensions in output')
    
    args = parser.parse_args()
    
    print(f"Scanning directory: {args.directory}")
    print()
    
    list_audio_files_in_directory(
        args.directory, 
        args.output, 
        show_extensions=not args.no_extensions
    )


if __name__ == "__main__":
    main()
