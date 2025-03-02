import sqlite3
from pathlib import Path


def initialize_database(db_path: Path, schema: str) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()
