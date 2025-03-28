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
    datetime(created_at) as "Created"
FROM transcriptions 
ORDER BY created_at DESC;