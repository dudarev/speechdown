# Rename `created_at` column

This script renames the `created_at` column to `transcription_started_at` in an existing SQLite database.

```
python rename_created_at.py /path/to/speechdown.db
```

It is safe to run multiple times; if the column was already renamed, the script does nothing.
