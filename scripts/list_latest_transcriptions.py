#!/usr/bin/env python3
"""
List N latest transcriptions with best confidence per file.

This script queries the transcriptions database to find the N most recent
transcriptions, selecting the best confidence score for each unique file path.
Results are displayed in chronological order.

Usage:
    python scripts/list_latest_transcriptions.py <database_path>

Example:
    python scripts/list_latest_transcriptions.py data/transcriptions.db
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Configuration
DEFAULT_LIMIT = 20


def get_latest_transcriptions(db_path: str, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
    """
    Get the latest transcriptions with best confidence per file path.
    
    Args:
        db_path: Path to the SQLite database
        limit: Number of latest transcriptions to return
        
    Returns:
        List of transcription records, each as a dictionary
    """
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    
    try:
        cursor = conn.cursor()
        
        # Query to get the best transcription (highest confidence) for each file path,
        # then select the N most recent based on transcription_started_at
        query = """
        WITH best_transcriptions AS (
            SELECT 
                t1.id,
                t1.path,
                t1.transcribed_text,
                t1.language_code,
                t1.confidence,
                t1.avg_logprob_mean,
                t1.compression_ratio_mean,
                t1.no_speech_prob_mean,
                t1.audio_duration_seconds,
                t1.word_count,
                t1.words_per_second,
                t1.model_name,
                t1.transcription_time_seconds,
                t1.transcription_started_at,
                ROW_NUMBER() OVER (
                    PARTITION BY t1.path 
                    ORDER BY t1.confidence DESC, t1.transcription_started_at DESC
                ) as rn
            FROM transcriptions t1
        )
        SELECT 
            id,
            path,
            transcribed_text,
            language_code,
            confidence,
            avg_logprob_mean,
            compression_ratio_mean,
            no_speech_prob_mean,
            audio_duration_seconds,
            word_count,
            words_per_second,
            model_name,
            transcription_time_seconds,
            transcription_started_at
        FROM best_transcriptions 
        WHERE rn = 1
        ORDER BY transcription_started_at DESC
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        # Convert Row objects to dictionaries
        return [dict(row) for row in results]
        
    finally:
        conn.close()


def display_transcriptions(transcriptions: List[Dict[str, Any]]) -> None:
    """Display transcriptions as full text with horizontal lines in chronological order."""
    if not transcriptions:
        print("No transcriptions found.")
        return
    
    # Reverse the order to show in normal chronological order (oldest to newest)
    for t in reversed(transcriptions):
        # Output the file path first
        print(t['path'])
        # Output the full transcription text
        transcription_text = t['transcribed_text'] or ""
        print(transcription_text)
        print("-" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/list_latest_transcriptions.py <database_path>")
        print("Example: python scripts/list_latest_transcriptions.py data/transcriptions.db")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    try:
        transcriptions = get_latest_transcriptions(db_path)
        display_transcriptions(transcriptions)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
