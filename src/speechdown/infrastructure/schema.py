SCHEMA = """
CREATE TABLE IF NOT EXISTS transcriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    transcribed_text TEXT,
    language_code TEXT,
    confidence REAL,
    avg_logprob_mean REAL,
    compression_ratio_mean REAL,
    no_speech_prob_mean REAL,
    audio_duration_seconds REAL,
    word_count INTEGER,
    words_per_second REAL,
    model_name TEXT,
    time_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
