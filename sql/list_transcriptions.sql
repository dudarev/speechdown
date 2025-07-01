-- List transcriptions in the test database
SELECT 
    path as "Path",
    language_code as "Language",
    substr(transcribed_text, 1, 50) || 
        CASE 
            WHEN length(transcribed_text) > 50 
            THEN '...' 
            ELSE '' 
        END as "Text",
    ROUND(confidence, 2) as "Confidence",
    ROUND(audio_duration_seconds, 1) as "Duration(s)",
    word_count as "Words",
    ROUND(transcription_time_seconds, 1) as "Transcription Time(s)",
    CASE 
        WHEN transcription_time_seconds > 0 
        THEN ROUND((word_count / transcription_time_seconds) * 60, 1) 
        ELSE 0 
    END as "Words per Minute",
    datetime(transcription_started_at) as "Created"
FROM transcriptions
ORDER BY transcription_started_at DESC;
