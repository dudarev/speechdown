-- List tables in a SQLite database
SELECT 
    name AS "Table Name",
    sql AS "SQL Statement"
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;