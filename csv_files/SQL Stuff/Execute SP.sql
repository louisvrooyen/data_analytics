USE incidents;



SET NAMES utf8mb4;
CALL sp_clean_incident_records();
SELECT 'Cleanup SP executed sucessfully!' AS Message;



SELECT Str_Name, count(*) AS Total
FROM incidents.incident_records
GROUP BY Str_Name
ORDER BY Str_Name
LIMIT 20000;

SELECT count(*) AS total, Suburb
FROM incidents.incident_records
WHERE id BETWEEN 0 AND 100000
GROUP BY Suburb
ORDER BY Suburb
LIMIT 4000;


-- Select str_Name, Suburb FROM incidents.incident_records;


-- SELECT HEX(Str_Name), Str_Name
-- FROM incident_records
-- WHERE Str_Name LIKE '%Stormvo%';



-- SELECT count(*) AS total FROM incidents.incident_records;
-- truncate table incident_records;