#!/usr/bin/env python3
"""Rename `created_at` column to `transcription_started_at` in SQLite DB."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cursor = conn.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def rename_column(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        if column_exists(conn, "transcriptions", "transcription_started_at"):
            print("Column already renamed; nothing to do.")
            return
        if not column_exists(conn, "transcriptions", "created_at"):
            print("Neither column present. No changes made.")
            return
        conn.execute(
            "ALTER TABLE transcriptions RENAME COLUMN created_at TO transcription_started_at"
        )
        conn.commit()
        print("Column renamed successfully.")
    finally:
        conn.close()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"Usage: {argv[0]} PATH_TO_DB")
        return 1
    db_path = Path(argv[1])
    if not db_path.is_file():
        print(f"Database not found: {db_path}")
        return 1
    rename_column(db_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
